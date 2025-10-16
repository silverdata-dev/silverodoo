import requests
import json
import re, sys

template = "2d6f.6ea5ff3994a2d856.k1.75f53350-a9d4-11f0-974b-765e7256bde4.199e84de305"


def extraer_emails_a_lista_de_dicts(nombre_archivo: str) -> list[dict]:
    """
    Lee un archivo línea por línea, extrae nombres y emails y los devuelve
    en una lista de diccionarios con el formato {"name": "nombre", "email": "correo"}.
    El separador puede ser coma o tab.

    Args:
        nombre_archivo: El path (ruta) al archivo de texto a procesar.

    Returns:
        Una lista de diccionarios con nombres y emails.
        [{"name": "John Doe", "email": "john@ejemplo.com"}, ...]
    """
    contactos_encontrados = []
    patron_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                linea_limpia = linea.strip()
                if not linea_limpia:
                    continue

                nombre = ""
                email = ""

                # Intenta separar por coma o tabulador
                separadores = [',', '\t']
                partes = None
                for sep in separadores:
                    if sep in linea_limpia:
                        partes = [p.strip() for p in linea_limpia.split(sep, 1)]
                        break
                
                if partes and len(partes) == 2:
                    # Asumimos que el email es la segunda parte si coincide con el patrón
                    if re.fullmatch(patron_email, partes[1]):
                        nombre = partes[0]
                        email = partes[1]
                    # A veces el formato es email,nombre
                    elif re.fullmatch(patron_email, partes[0]):
                        nombre = partes[1]
                        email = partes[0]
                
                # Si no se pudo separar o encontrar un email válido en las partes,
                # busca un email en toda la línea.
                if not email:
                    match = re.search(patron_email, linea_limpia)
                    if match:
                        email = match.group(0)
                        # Lo que no es el email, es el nombre
                        nombre = linea_limpia.replace(email, '').strip(' ,	').strip()


                if email:
                    contactos_encontrados.append({"name": nombre, "email": email})

    except FileNotFoundError:
        print(f"👻 Error: El archivo '{nombre_archivo}' no fue encontrado. ¿El path es correcto?")
    except Exception as e:
        print(f"🔥 Error inesperado al procesar el archivo: {e}")

    return contactos_encontrados


# ---------------------------------------------------------------------

## Ejemplo de Uso (el "cómo se come" esto)

# 1. Crea un archivo de prueba llamado 'datos.txt' (con contenido real para testear)
#    ... o usa la ruta a tu archivo.

# 2. Llama a la función y mira la magia:
# resultado = extraer_emails_a_lista_de_dicts('datos.txt')
# print(resultado)
# print(f"Total de emails extraídos: {len(resultado)}")

url = "https://api.zeptomail.com/v1.1/email/template/batch"
TAMANO_LOTE = 100  # Límite de destinatarios por llamada a la API

for a in sys.argv[1:]:
    contactos = extraer_emails_a_lista_de_dicts(a)
    if not contactos:
        print(f"No se encontraron contactos en el archivo {a}. Saltando.")
        continue

    print(f"Archivo '{a}' procesado. Total de contactos: {len(contactos)}.")
    
    # Dividir la lista de contactos en lotes de TAMANO_LOTE
    for i in range(0, len(contactos), TAMANO_LOTE):
        lote = contactos[i:i + TAMANO_LOTE]
        num_lote = i // TAMANO_LOTE + 1
        total_lotes = (len(contactos) + TAMANO_LOTE - 1) // TAMANO_LOTE
        print(f"Enviando lote {num_lote}/{total_lotes} ({len(lote)} contactos)...")

        lista_destinatarios = json.dumps([
            {
                "email_address": {
                    "address": p['email'],
                    "name": p.get('name', '')
                },
                "merge_info": {
                    "name": p.get('name', 'Cliente')
                }
            } for p in lote
        ])

        payload = f'''
              {{
              "mail_template_key":"{template}",
              "from": {{ "address": "noreply@silver-data.net", "name": "No responder"}},
              "to": {lista_destinatarios}
              }}'''

        headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'authorization': "Zoho-enczapikey wSsVR61/+BL4Dq8vmDyrdOc7nA9dBlv1HUh+2Qbw4yWoTarDpsc/kxWfAwHyGPRKFjRqEDVE8e4rnEpUhDQIh9h8nFgECyiF9mqRe1U4J3x17qnvhDzPVm5VmxaMKIILzg9vnGFpEcsi+g==",
        }

        print(payload)
        #continue

        try:
            response = requests.request("POST", url, data=payload.encode('utf-8'), headers=headers)
            response.raise_for_status()
            print(f"Respuesta del lote {num_lote}: {response.text}")
        except requests.exceptions.HTTPError as e:
            print(f"🔥 Error HTTP al enviar el lote {num_lote}: {e}")
            print(f"Respuesta del servidor: {e.response.text}")
        except Exception as e:
            print(f"🔥 Error inesperado al enviar el lote {num_lote}: {e}")