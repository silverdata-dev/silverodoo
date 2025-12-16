# -*- coding: utf-8 -*-

import paramiko
from telnetlib3 import telnetlib
import socket
import logging
import re
import time

_logger = logging.getLogger(__name__)

class OLTConnection:
    """
    Clase de conexión mejorada para OLTs que utiliza un shell persistente
    y detección de prompts para una interacción robusta.
    """
    # --- AJUSTAR ESTOS PATRONES SEGÚN EL PROMPT DE TU OLT ---
    PROMPT_PATTERNS = {
        'login': re.compile(r"Login: ?$"),
        'password': re.compile(r"Password: ?$"),
        'user_mode': re.compile(r"([\w.-]+)> ?$"),          # Ej: OLT>
        'config_mode': re.compile(r"([\w.-]+)\([^\)]+\)# ?$"), # Ej: OLT(config-if-gpon-0/1)# or OLT(profile-onu:10)#
        'enable_mode': re.compile(r"([\w.-]+)# ?$"),         # Ej: OLT#
    }
    # ---------------------------------------------------------

    def __init__(self, host, username, password, port=None, connection_type='ssh'):
        self.host = host
       # self.port = int(port) if port else (23 if connection_type == 'telnet' else 22)
        self.port =  port or (23 if connection_type == 'telnet' else 22)
        self.username = username
        self.password = password
        self.connection_type = connection_type
        self.client = None
        self.shell = None
        self.prompt_re = None  # Regex del prompt actual
        self.prompt = None     # Texto del prompt actual
        self.hostname_olt = None
        self.terminal_length_set = False
        self.terminal_width_set = False

    def _read_until_prompt(self, timeout=10):
        """
        Lee el buffer del shell hasta que se encuentra uno de los prompts definidos.
        Devuelve el texto ANTES del prompt y el prompt en sí.
        """
        output = ""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.connection_type == 'ssh':
                if self.shell.recv_ready():
                    output += self.shell.recv(65535).decode('utf-8', errors='ignore')
            elif self.connection_type == 'telnet':
                output += self.client.read_very_eager().decode('utf-8', errors='ignore')

            print(("output", output))

            for prompt_name, pattern in self.PROMPT_PATTERNS.items():
                match = pattern.search(output)
                if match:
                    self.prompt_re = pattern
                    self.prompt = match.group(0).strip() # Guardar el texto del prompt
                    # GEMINI: Capturar hostname si no lo hemos hecho ya
                    if not self.hostname_olt and prompt_name in ['user_mode', 'enable_mode', 'config_mode']:
                        self.hostname_olt = match.group(1)
                        _logger.info(f"Hostname de OLT detectado: {self.hostname_olt}")

                    # Dividimos la salida en "antes del prompt" y "el prompt"
                    output_before_prompt = output[:match.start()]
                    return output_before_prompt.strip(), self.prompt, output

            time.sleep(0.1)  # Evitar busy-waiting

        raise TimeoutError(f"Timeout esperando un prompt conocido. Salida recibida:\n{output}")

    def connect(self):
        _logger.info(f"Conectando a {self.host}:{self.port} usando {self.connection_type}, {self.username}")
        try:
        #if 1:
            if self.connection_type == 'ssh':
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.client.connect(self.host, port=self.port, username=self.username, password=self.password, timeout=10, look_for_keys=False, allow_agent=False)
                print(("conectado", self.client))
                self.shell = self.client.invoke_shell()
                print(("shell", self.shell))
            elif self.connection_type == 'telnet':
                self.client = telnetlib.Telnet(self.host, self.port, timeout=10)
                self.shell = self.client
            else:
                raise ValueError("Tipo de conexión no soportado")

            # Reset flags for this connection attempt
            self.terminal_length_set = False
            self.terminal_width_set = False

            # Bucle de login y configuración de terminal
            max_retries = 10 # Aumentado para permitir más pasos
            last_output = ""

            for i in range(max_retries):
                output_before_prompt, prompt, out = self._read_until_prompt()
                print((f"outputlogin {i+1}", output_before_prompt, prompt, out))
                last_output = output_before_prompt + "\n" + prompt

                current_prompt_obj = self.prompt_re

                if current_prompt_obj == self.PROMPT_PATTERNS['login']:
                    _logger.info(f"Enviando usuario: {self.username}")
                    self.shell.send(self.username + '\n')

                elif current_prompt_obj == self.PROMPT_PATTERNS['password']:
                    _logger.info("Enviando contraseña")
                    self.shell.send(self.password + '\n')

                # Una vez que llegamos a un prompt de comando, manejamos la configuración
                elif current_prompt_obj in [self.PROMPT_PATTERNS['user_mode'], self.PROMPT_PATTERNS['enable_mode'], self.PROMPT_PATTERNS['config_mode']]:

                    # 1. Establecer longitud de terminal
                    if not self.terminal_length_set:
                        _logger.info("Configurando 'terminal length 0'.")
                        self.shell.send("terminal length 0\n")
                        self.terminal_length_set = True # Asumimos éxito y dejamos que el siguiente bucle lo verifique

                    # 2. Establecer ancho de terminal
                    elif not self.terminal_width_set:
                        _logger.info("Configurando 'terminal width 511'.")
                        self.shell.send("terminal width 511\n")
                        self.terminal_width_set = True # Asumimos éxito

                    # 3. Elevar a modo 'enable' si es necesario
                    elif current_prompt_obj == self.PROMPT_PATTERNS['user_mode']:
                        _logger.info("Modo usuario detectado. Enviando 'enable'.")
                        self.shell.send('enable\n')

                    # 4. Si ya estamos en modo 'enable' y todo está configurado, hemos terminado.
                    else:
                        _logger.info(f"Login y configuración de terminal exitosos en {self.host}.")
                        return True, "Conexión exitosa"

                else:
                    _logger.debug(f"Prompt no manejado durante login: {current_prompt_obj.pattern}. Esperando siguiente prompt.")

            # Si el bucle termina sin una salida exitosa, es un error.
            raise ConnectionError(f"Fallo en el login o configuración después de {max_retries} intentos. Última salida:\n{last_output}")

        #else:
        except Exception as e:
            _logger.error(f"Fallo al conectar a {self.host}: {e}")
            self.disconnect()  # Asegurarse de cerrar la conexión si falla el login
            return False, str(e)

    def disconnect(self):
        if self.client:
            self.client.close()
            _logger.info(f"Desconectado de {self.host}")
        self.shell = None
        self.client = None

    def execute_command(self, command, timeout=10):
        if not self.shell:
            raise ConnectionError("No hay un shell activo. Conéctese primero.")

        _logger.info(f"Ejecutando comando: {command}")
        try:
            self.shell.send(command + '\n')
            output_before_prompt, prompt, full_output = self._read_until_prompt(timeout)

            # La logica de exito/fallo ahora se basara en si la salida contiene indicadores de error o exito.
            error_indicators = ['error', 'fail', 'invalid', 'incomplete command']
            success_indicators = ['ok.', 'configuration saved', 'oltindex', '##onu profile##', 'success']  # Indicadores de exito conocidos.

            # La salida se considera "limpia" si no contiene el eco del comando.
            lines = output_before_prompt.replace('\r\n', '\n').split('\n')
            if lines and lines[0].strip().startswith(command.strip()):
                clean_response = "\n".join(lines[1:]).strip()
            else:
                clean_response = "\n".join(lines).strip()

            # Determinar éxito o fallo

            if command == 'exit':
                return True, full_output, clean_response

            # 3. Comprobar si la respuesta contiene un indicador de exito explicito.
            if any(indicator in clean_response.lower() for indicator in success_indicators):
                print("si")
                return True, full_output, clean_response

            # 1. Comprobar si la respuesta limpia contiene algun indicador de error.
            if any(indicator in clean_response.lower() for indicator in error_indicators):
               # print("no")
                return False, full_output, clean_response

            # 2. Si no hay errores, comprobar si la respuesta esta vacia (exito implicito).
            if not clean_response:
              #  print("nsi")
                return True, full_output, clean_response

          #  print("sno")
            # 4. Si hay respuesta, pero no es un indicador de exito conocido, se considera un fallo.
            return False, full_output, clean_response
            #success = not any(indicator in clean_response.lower() for indicator in error_indicators)

            return success, full_output, clean_response

        except Exception as e:
            if command == 'exit':
                return True, "", ""

            _logger.error(f"Fallo al ejecutar el comando '{command}' en {self.host}: {e}")
            # Devolvemos el error y una salida vacia
            return False, str(e), ""

    def __enter__(self):
        print(("enter"))
        success, message = self.connect()
        if not success:
            raise ConnectionError(message)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()