#!/usr/bin/env python3
"""
vsol_olt_client.py

Esqueleto para interactuar con una OLT vía HTTPS (WebUI/API no-documented).
Funciones:
 - login / logout
 - session persist (pickle)
 - list_onus, get_onu, register_onu, delete_onu
 - low-level _request que normaliza headers, token, errores

Adaptar las rutas y el parsing de respuestas según el WebUI de tu VSOL.
"""

import requests
import time
import pickle
import os
from typing import Optional, Dict, Any, List, Tuple

# -----------------------------
# Configuración base (ajusta)
# -----------------------------
BASE_URL = "https://OLT_IP"  # ej: https://192.168.1.1
LOGIN_PATH = "/login"        # página o endpoint de login
LOGOUT_PATH = "/logout"
API_LIST_ONUS = "/api/onus"          # endpoint hipotético (ajusta)
API_REGISTER_ONU = "/api/onu/register"
API_GET_ONU = "/api/onu"             # GET /api/onu/{id}
API_DELETE_ONU = "/api/onu/delete"   # POST /api/onu/delete or DELETE /api/onu/{id}

# Donde guardamos la sesión (cookies + token)
SESSION_FILE = "olt_session.pkl"

# Timeout por defecto en requests
REQUEST_TIMEOUT = 10.0

# -----------------------------
# Excepciones propias
# -----------------------------
class OLTError(Exception):
    pass

class AuthError(OLTError):
    pass

class APIError(OLTError):
    pass

# -----------------------------
# Cliente
# -----------------------------
class OLTClient:
    def __init__(self, base_url: str = BASE_URL, session_file: str = SESSION_FILE, verify_ssl: bool = False):
        self.base_url = base_url.rstrip("/")
        self.session_file = session_file
        self.session = requests.Session()
        self.csrf_token: Optional[str] = None
        self.verify_ssl = verify_ssl  # en entornos controlados a veces false
        # Headers por defecto
        self.session.headers.update({
            "User-Agent": "vsol-olt-client/0.1",
            "Accept": "application/json, text/plain, */*",
        })

    # ---------- Session persistence ----------
    def save_session(self) -> None:
        payload = {
            "cookies": self.session.cookies.get_dict(),
            "headers": dict(self.session.headers),
            "csrf_token": self.csrf_token
        }
        with open(self.session_file, "wb") as fh:
            pickle.dump(payload, fh)
        print(f"[+] sesión guardada en {self.session_file}")

    def load_session(self) -> bool:
        if not os.path.exists(self.session_file):
            return False
        with open(self.session_file, "rb") as fh:
            payload = pickle.load(fh)
        # Restaurar cookies y headers
        self.session.cookies.update(payload.get("cookies", {}))
        self.session.headers.update(payload.get("headers", {}))
        self.csrf_token = payload.get("csrf_token")
        return True

    # ---------- Low-level request helper ----------
    def _request(self, method: str, path: str, *, params: dict = None, json: dict = None, data: dict = None,
                 headers: dict = None, require_auth: bool = True) -> requests.Response:
        url = f"{self.base_url}{path}"
        hdrs = {}
        if headers:
            hdrs.update(headers)
        # Si hay CSRF token conocido, añadirlo en header o en json según prefiera el API
        if self.csrf_token:
            # Variante común: X-CSRF-Token
            hdrs.setdefault("X-CSRF-Token", self.csrf_token)
            # Si el webui espera token en json/data, el caller debe pasarlo explícitamente.
        try:
            resp = self.session.request(method, url, params=params, json=json, data=data, headers=hdrs,
                                        timeout=REQUEST_TIMEOUT, verify=self.verify_ssl)
        except requests.RequestException as exc:
            raise OLTError(f"Fallo HTTP ({method} {url}): {exc}") from exc

        # Manejo básico de errores HTTP
        if resp.status_code == 401:
            raise AuthError("No autorizado (401). Sesión inválida o credenciales incorrectas.")
        if resp.status_code >= 400:
            raise APIError(f"Error API HTTP {resp.status_code}: {resp.text[:200]}")

        return resp

    # ---------- Login / Logout ----------
    def login(self, username: str, password: str) -> None:
        """
        Ejecuta el login y extrae cookie + token CSRF si aplica.
        NOTA: adaptar payload/form-data o JSON según el WebUI.
        """
        # 1) Obtener la página de login (por si hay token en un campo oculto)
        try:
            page = self._request("GET", LOGIN_PATH, require_auth=False)
        except OLTError as e:
            raise AuthError(f"No se pudo contactar la página de login: {e}") from e

        # 2) Extraer token si existe (heurística: buscar cabeceras o JSON)
        #  - Algunos webUIs devuelven token en la cookie; otros lo inyectan en HTML.
        #  - Aquí dejamos un hook: si tu webui usa HTML, parsea page.text y asigna self.csrf_token.
        self._try_extract_token_from_response(page)

        # 3) Enviar credenciales. Muchos WebUI aceptan form-data; otros JSON.
        # Prueba primero JSON, si no funciona, cambia a form data.
        login_payload_json = {"username": username, "password": password}
        login_payload_form = {"username": username, "password": password}

        # Intento 1: JSON
        try:
            resp = self._request("POST", LOGIN_PATH, json=login_payload_json, require_auth=False)
        except APIError:
            # Intento fallback: form-data
            resp = self._request("POST", LOGIN_PATH, data=login_payload_form, require_auth=False)

        # Verificar login: depende del API — aquí asumimos JSON con success:true o redirect con cookie
        if resp.headers.get("Content-Type", "").lower().startswith("application/json"):
            data = resp.json()
            success = data.get("success") or data.get("ok") or data.get("result")
            if not success:
                raise AuthError(f"Login falló: {data}")
            # extraer token si lo devuelve
            if "csrf" in data:
                self.csrf_token = data["csrf"]
        else:
            # Si no JSON, mirar cookies o html
            # si hay cookie de sesión, asumimos login exitoso
            if not self.session.cookies:
                raise AuthError("Login no retornó cookie de sesión; revisar credenciales y payload.")
            # Intentar extraer token del cuerpo HTML si es necesario
            self._try_extract_token_from_response(resp)

        # Guardar sesión automática
        self.save_session()
        print("[+] Login OK")

    def _try_extract_token_from_response(self, resp: requests.Response) -> None:
        """
        Heurística para localizar token CSRF en HTML o JSON.
        Adapta o expande según el WebUI real.
        """
        # caso JSON
        ct = resp.headers.get("Content-Type", "")
        if "application/json" in ct:
            try:
                j = resp.json()
                token = j.get("csrf") or j.get("token")
                if token:
                    self.csrf_token = token
                    return
            except Exception:
                pass

        # caso HTML: buscar meta tag o input hidden
        text = resp.text
        # busco patrones comunes muy simples
        for marker in ['name="csrf_token"', 'name="_csrf"', 'id="csrf-token"', 'csrf-token']:
            if marker in text:
                # aproximación: extraer entre markers
                # usuario debe personalizar esta sección con regex más robusta si es necesario
                import re
                m = re.search(r'(?:name="csrf_token"|name="_csrf"|id="csrf-token"|csrf-token)[^>]*value=["\']([^"\']+)["\']', text)
                if m:
                    self.csrf_token = m.group(1)
                    return
        # si llega aquí, no se extrajo token — puede no ser necesario.

    def logout(self) -> None:
        try:
            self._request("GET", LOGOUT_PATH, require_auth=False)
        except Exception:
            pass
        # limpiar sesión local
        try:
            os.remove(self.session_file)
        except Exception:
            pass
        self.session.cookies.clear()
        self.csrf_token = None
        print("[+] Logged out / session cleared")

    # ---------- Helpers de autenticación ----------
    def ensure_logged_in(self, username: str, password: str) -> None:
        """
        Intenta cargar sesión desde disco; si no hay o está rota, hace login.
        """
        if self.load_session():
            # Podrías validar una petición corta para confirmar que la sesión sigue válida.
            try:
                r = self._request("GET", "/api/whoami", require_auth=True)
                # Si responde OK, ya estamos logueados. Si falla, volvemos a login.
                return
            except Exception:
                print("[!] Sesión persistida inválida; relogueando.")
        # No hay sesión válida: hacer login
        self.login(username, password)

    # ---------- CRUD ONUs (ajusta payloads y parsing) ----------
    def list_onus(self) -> List[Dict[str, Any]]:
        """
        Lista ONUs. Adaptar a la estructura JSON que devuelve el WebUI.
        """
        resp = self._request("GET", API_LIST_ONUS)
        # Ejemplo: respuesta JSON típica: {"result": [{"id": 1, "pon":"0/5", "serial":"ABCD"}, ...]}
        try:
            data = resp.json()
        except ValueError:
            raise APIError("Respuesta de list_onus no es JSON")
        # heurística para buscar la lista
        if isinstance(data, dict) and ("result" in data or "data" in data):
            lst = data.get("result") or data.get("data")
            if isinstance(lst, list):
                return lst
        if isinstance(data, list):
            return data
        raise APIError(f"Estructura inesperada en list_onus: {data}")

    def get_onu(self, onu_id: str) -> Dict[str, Any]:
        path = f"{API_GET_ONU}/{onu_id}"
        resp = self._request("GET", path)
        try:
            return resp.json()
        except ValueError:
            raise APIError("Respuesta de get_onu no es JSON")

    def register_onu(self, pon: str, onu_index: int, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registra/configura una ONU.
        - pon: "0/5"
        - onu_index: 47
        - config: dict con los parámetros (ssid, key, auth_mode, enc_type, etc.)
        """
        payload = {
            "pon": pon,
            "onu_index": onu_index,
            **config
        }
        # Si el API requiere CSRF en el body, lo añadimos
        if self.csrf_token:
            payload.setdefault("csrf", self.csrf_token)

        resp = self._request("POST", API_REGISTER_ONU, json=payload)
        try:
            return resp.json()
        except ValueError:
            raise APIError("Respuesta de register_onu no es JSON")

    def delete_onu(self, onu_id: str) -> Dict[str, Any]:
        """
        Borra una ONU. Dependiendo del API puede ser DELETE /api/onu/{id} o POST a un endpoint.
        """
        # Intentar DELETE
        try:
            resp = self._request("DELETE", f"{API_GET_ONU}/{onu_id}")
            # si no falla, devolvemos json
            return resp.json()
        except APIError:
            # fallback: POST a endpoint de borrado
            payload = {"onu_id": onu_id}
            if self.csrf_token:
                payload["csrf"] = self.csrf_token
            resp = self._request("POST", API_DELETE_ONU, json=payload)
            try:
                return resp.json()
            except ValueError:
                raise APIError("Respuesta de delete_onu no es JSON")

# -----------------------------
# CLI / Ejemplo de uso
# -----------------------------
def main_demo():
    # Ejemplo de cómo usar el cliente (ajusta credenciales y URL)
    client = OLTClient(base_url="https://192.168.1.1", verify_ssl=False)
    username = "admin"
    password = "changeme"

    # Asegura login (carga sesión si existe)
    try:
        client.ensure_logged_in(username, password)
    except AuthError as e:
        print("Login falló:", e)
        return

    # Listar ONUs
    try:
        onus = client.list_onus()
        print("ONUs encontradas:", len(onus))
        for o in onus[:10]:
            print("  ", o)
    except APIError as e:
        print("Error listando ONUs:", e)

    # Registrar ejemplo
    example_cfg = {
        "ssid_index": 1,
        "ssid_name": "Suena-5G",
        "auth_mode": "wpapsk/wpa2psk",
        "encrypt_type": "tkipaes",
        "shared_key": "Jalu_1024.5367372",
        "rekey_interval": 0,
    }
    try:
        res = client.register_onu(pon="0/5", onu_index=47, config=example_cfg)
        print("Resultado register_onu:", res)
    except APIError as e:
        print("Error registrando ONU:", e)

    # Borrar ejemplo
    try:
        res = client.delete_onu("47")
        print("Resultado delete_onu:", res)
    except APIError as e:
        print("Error borrando ONU:", e)

    # Guardar estado final
    client.save_session()

if __name__ == "__main__":
    main_demo()
