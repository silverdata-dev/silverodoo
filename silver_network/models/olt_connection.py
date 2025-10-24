# -*- coding: utf-8 -*-

import paramiko
import telnetlib
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
        'config_mode': re.compile(r"([\w.-]+)\(config[^\)]*\)# ?$"), # Ej: OLT(config-if-gpon-0/1)#
        'enable_mode': re.compile(r"([\w.-]+)# ?$"),         # Ej: OLT#
    }
    # ---------------------------------------------------------

    def __init__(self, host, username, password, port=22, connection_type='ssh'):
        self.host = host
       # self.port = int(port) if port else (23 if connection_type == 'telnet' else 22)
        self.port =  (23 if connection_type == 'telnet' else 22)
        self.username = username
        self.password = password
        self.connection_type = connection_type
        self.client = None
        self.shell = None
        self.current_prompt = None
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

            for prompt_name, pattern in self.PROMPT_PATTERNS.items():
                match = pattern.search(output)
                if match:
                    self.current_prompt = pattern
                    # Dividimos la salida en "antes del prompt" y "el prompt"
                    output_before_prompt = output[:match.start()]
                    prompt_text = match.group(0)  # El texto que coincide con el prompt
                    return output_before_prompt.strip(), prompt_text.strip()

            time.sleep(0.1)  # Evitar busy-waiting

        raise TimeoutError(f"Timeout esperando un prompt conocido. Salida recibida:\n{output}")

    def connect(self):
        _logger.info(f"Conectando a {self.host}:{self.port} usando {self.connection_type}")
        try:
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
                output_before_prompt, prompt = self._read_until_prompt()
                print((f"outputlogin {i+1}", output_before_prompt, prompt))
                last_output = output_before_prompt + "\n" + prompt

                current_prompt_obj = self.current_prompt

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
            output_before_prompt, prompt = self._read_until_prompt(timeout)
            print(("outputcommand", output_before_prompt, prompt, command))

            # --- Limpieza de la Salida ---
            # 1. Dividir la salida en líneas
            lines = output_before_prompt.replace('\r\n', '\n').split('\n')

            # 2. Eliminar la primera línea si es el eco del comando
            # A veces el eco no es exacto, así que somos un poco flexibles.
            if lines and lines[0].strip().startswith(command.strip()):
                lines = lines[1:]
            clean_output = "\n".join(lines).strip()
            _logger.info(f"Salida limpia del comando '{command}':\n{clean_output}")

            # --- Detección de Errores Basada en Salida Inesperada ---
            # La "detección de errores" se basa en el contenido de la salida
            # ya que los comandos de shell raramente devuelven un código de error.

            # Según el feedback, cualquier salida de texto para comandos de configuración
            # se considera un error o un mensaje que debe detener el flujo.
            if clean_output:
                return False, clean_output  # Falla si hay cualquier salida

            return True, clean_output  # Éxito solo si no hay ninguna salida
        except Exception as e:
            _logger.error(f"Fallo al ejecutar el comando '{command}' en {self.host}: {e}")
            return False, str(e)

    def __enter__(self):
        success, message = self.connect()
        if not success:
            raise ConnectionError(message)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()