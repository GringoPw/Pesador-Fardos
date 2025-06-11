import serial
import serial.tools.list_ports
import time
import re
import json
import os
from config.configuracion_manager import config_manager

class ConexionBalanza:
    """Clase para manejar la conexión con balanza real"""

    def __init__(self):
        self.conexion = None
        self.peso_actual = 0.0
        self.ultimo_error = None
        self.buffer = ""
        self.datos_recibidos = []
        self.max_datos_log = 50  # Máximo de datos en el log
        
        # Cargar configuración desde JSON
        self.cargar_configuracion()
        self._inicializar_conexion()

    def cargar_configuracion(self):
        """Carga la configuración desde configuracion.json"""
        try:
            config = config_manager.obtener_balanza()
            
            # Si no hay configuración, usar valores por defecto de configuracion.py
            if not config:
                from config.configuracion import BALANZA_CONFIG
                self.puerto = BALANZA_CONFIG.get('puerto_serie', 'COM1')
                self.baudrate = BALANZA_CONFIG.get('baudrate', 9600)
                self.timeout = BALANZA_CONFIG.get('timeout', 1)
                self.protocolo = BALANZA_CONFIG.get('protocolo', 'CONTINUO')
                self.activar_dtr = BALANZA_CONFIG.get('activar_dtr', True)
                self.activar_rts = BALANZA_CONFIG.get('activar_rts', True)
            else:
                self.puerto = config.get('puerto_serie', 'COM1')
                self.baudrate = config.get('baudrate', 9600)
                self.timeout = config.get('timeout', 1)
                self.protocolo = config.get('protocolo', 'CONTINUO')
                self.activar_dtr = config.get('activar_dtr', True)
                self.activar_rts = config.get('activar_rts', True)
            
            print(f"📋 Configuración cargada: {self.puerto} @ {self.baudrate} bps, Protocolo: {self.protocolo}")
            
        except Exception as e:
            print(f"❌ Error al cargar configuración: {e}")
            # Valores por defecto
            self.puerto = 'COM1'
            self.baudrate = 9600
            self.timeout = 1
            self.protocolo = 'CONTINUO'
            self.activar_dtr = True
            self.activar_rts = True

    def guardar_configuracion(self):
        """Guarda la configuración actual en configuracion.json"""
        try:
            nueva_config = {
                'puerto_serie': self.puerto,
                'baudrate': self.baudrate,
                'timeout': self.timeout,
                'protocolo': self.protocolo,
                'activar_dtr': self.activar_dtr,
                'activar_rts': self.activar_rts
            }
            
            if config_manager.actualizar_balanza(nueva_config):
                print("✅ Configuración guardada exitosamente")
                return True
            else:
                print("❌ Error al guardar configuración")
                return False
                
        except Exception as e:
            print(f"❌ Error al guardar configuración: {e}")
            return False

    def _inicializar_conexion(self):
        """Inicializa la conexión con la balanza"""
        try:
            if self.conexion and self.conexion.is_open:
                self.conexion.close()
                
            self.conexion = serial.Serial(
                port=self.puerto,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            )

            # Configurar DTR y RTS
            self.conexion.setDTR(self.activar_dtr)
            self.conexion.setRTS(self.activar_rts)

            print(f"✅ Balanza conectada en {self.puerto}")
            print(f"   Configuración: {self.baudrate} bps, DTR: {self.activar_dtr}, RTS: {self.activar_rts}")
            print(f"   Protocolo: {self.protocolo}")
            
            # Limpiar buffers
            self.conexion.reset_input_buffer()
            self.conexion.reset_output_buffer()
            
        except Exception as e:
            print(f"❌ Error al conectar balanza: {str(e)}")
            self.conexion = None
            self.ultimo_error = str(e)
            raise

    def obtener_peso(self) -> float:
        """Obtiene el peso actual de la balanza - SIEMPRE devuelve el peso actual"""
        if not self.conexion or not self.conexion.is_open:
            print("❌ Conexión no disponible")
            return 0.0

        try:
            if self.protocolo == 'CONTINUO':
                peso = self._leer_protocolo_continuo()
            else:
                peso = self._leer_protocolo_comando()
            
            # SIEMPRE actualizar el peso actual - no mantener valores antiguos
            self.peso_actual = peso
            
            # Log para debugging
            print(f"⚖️ Peso actual: {self.peso_actual:.2f} kg")
            
            return self.peso_actual
            
        except Exception as e:
            print(f"❌ Error al leer peso: {str(e)}")
            self.ultimo_error = str(e)
            # En caso de error, devolver 0, no el último peso
            self.peso_actual = 0.0
            return 0.0

    def _leer_protocolo_continuo(self) -> float:
        """Lee peso de balanza que envía datos continuamente"""
        tiempo_inicio = time.time()
        peso_detectado = 0.0
        
        print(f"🔍 Leyendo datos continuos de {self.puerto}...")
        
        # Leer durante máximo 2 segundos
        while time.time() - tiempo_inicio < 2:
            if self.conexion.in_waiting:
                try:
                    byte = self.conexion.read().decode('ascii', errors='ignore')
                    
                    if byte in ['\r', '\n']:  # Fin de línea
                        if self.buffer.strip():
                            linea = self.buffer.strip()
                            
                            # Agregar al log de datos recibidos
                            self._agregar_dato_recibido(linea)
                            
                            print(f"📡 Línea recibida: '{linea}'")
                            
                            # Extraer peso de la línea
                            peso = self._extraer_peso_de_cadena(linea)
                            
                            # IMPORTANTE: Siempre devolver el peso actual, incluso si es 0
                            peso_detectado = peso
                            print(f"📊 Peso extraído: {peso_detectado:.2f} kg")
                            
                            self.buffer = ""
                            return peso_detectado
                        self.buffer = ""
                    else:
                        self.buffer += byte
                        
                except Exception as e:
                    print(f"⚠️ Error al decodificar: {e}")
                    continue
            else:
                time.sleep(0.01)
        
        # Si no hay datos nuevos, devolver 0 (no hay peso)
        print(f"⏰ Sin datos nuevos - Peso: 0.00 kg")
        return 0.0

    def _leer_protocolo_comando(self) -> float:
        """Lee peso enviando comando a la balanza"""
        try:
            # Limpiar buffer de entrada
            self.conexion.reset_input_buffer()

            # Obtener y enviar comando
            comando = self._obtener_comando_protocolo()
            if comando:
                self.conexion.write(comando)
                time.sleep(0.1)

            # Leer respuesta
            respuesta = self.conexion.readline().decode('utf-8', errors='ignore').strip()
            
            if respuesta:
                # Agregar al log
                self._agregar_dato_recibido(respuesta)
                print(f"📡 Respuesta: '{respuesta}'")
                
                peso = self._extraer_peso_de_cadena(respuesta)
                print(f"📊 Peso extraído: {peso:.2f} kg")
                return peso
            else:
                print("📡 Sin respuesta del comando")
                return 0.0

        except Exception as e:
            print(f"⚠️ Error en protocolo comando: {e}")
            return 0.0

    def _extraer_peso_de_cadena(self, cadena: str) -> float:
        """Extrae el peso de una cadena - MEJORADO para balanza GAMA"""
        try:
            print(f"🔍 Analizando: '{cadena}' (len: {len(cadena)})")
            
            # Limpiar la cadena
            cadena_limpia = cadena.strip()
            
            # Patrones específicos para balanza GAMA
            if "ST,GS," in cadena_limpia:
                # Formato GAMA: ST,GS,+000000 o ST,GS,+001234
                match = re.search(r'ST,GS,([+-]?\d+)', cadena_limpia)
                if match:
                    numero = int(match.group(1))
                    # Convertir a kg (asumiendo que viene en gramos o decigramos)
                    peso = numero / 100.0  # Ajustar según tu balanza
                    print(f"✅ Formato GAMA detectado: {numero} -> {peso:.2f} kg")
                    return peso
            
            # Detectar mensajes de "sin peso" o peso cero
            patrones_cero = ["000000", "0000000", "+000000", "+0000000", "no weight", "sin peso"]
            if any(patron in cadena_limpia.lower() for patron in patrones_cero):
                print("🔄 Mensaje de peso cero detectado")
                return 0.0
            
            # Buscar números con punto decimal
            patron_decimal = r'[-+]?\s*\d+\.\d+'
            match = re.search(patron_decimal, cadena_limpia)
            if match:
                numero_str = match.group().replace(' ', '')
                peso = float(numero_str)
                print(f"✅ Patrón decimal: '{numero_str}' -> {peso:.2f} kg")
                return peso
            
            # Buscar números enteros grandes (posiblemente en gramos)
            patron_entero = r'[-+]?\s*\d{4,}'  # 4 o más dígitos
            match = re.search(patron_entero, cadena_limpia)
            if match:
                numero_str = match.group().replace(' ', '')
                numero = float(numero_str)
                # Si es un número grande, probablemente esté en gramos
                if numero > 1000:
                    peso = numero / 1000.0  # Convertir a kg
                    print(f"✅ Número grande (gramos): '{numero_str}' -> {peso:.2f} kg")
                    return peso
                else:
                    print(f"✅ Número entero: '{numero_str}' -> {numero:.2f} kg")
                    return numero
            
            # Buscar cualquier número
            patron_cualquier = r'[-+]?\s*\d+'
            match = re.search(patron_cualquier, cadena_limpia)
            if match:
                numero_str = match.group().replace(' ', '')
                peso = float(numero_str)
                print(f"✅ Número encontrado: '{numero_str}' -> {peso:.2f} kg")
                return peso
            
            print(f"❌ No se pudo extraer peso de: '{cadena}'")
            return 0.0
            
        except Exception as e:
            print(f"⚠️ Error al extraer peso: {e}")
            return 0.0

    def _obtener_comando_protocolo(self):
        """Obtiene el comando para solicitar peso según el protocolo"""
        comandos = {
            "ESTANDAR": b'P\r\n',
            "TOLEDO": b'W\r\n',
            "AND": b'Q\r\n',
            "OHAUS": b'IP\r\n',
            "METTLER": b'S\r\n',
            "CAS": b'R\r\n',
            "DIBAL": b'P\r',
            "DIGI": b'W',
            "GAMA": b'\r\n',
            "CONTINUO": b''  # No envía comando
        }
        return comandos.get(self.protocolo.upper(), b'P\r\n')

    def _agregar_dato_recibido(self, dato):
        """Agrega un dato al log de datos recibidos"""
        timestamp = time.strftime("%H:%M:%S")
        entrada = f"[{timestamp}] {dato}"
        
        self.datos_recibidos.append(entrada)
        
        # Mantener solo los últimos N datos
        if len(self.datos_recibidos) > self.max_datos_log:
            self.datos_recibidos.pop(0)

    def obtener_datos_recibidos(self):
        """Obtiene el log de datos recibidos"""
        return self.datos_recibidos.copy()

    def limpiar_datos_recibidos(self):
        """Limpia el log de datos recibidos"""
        self.datos_recibidos.clear()

    def obtener_puertos_disponibles(self):
        """Obtiene una lista de puertos COM disponibles"""
        try:
            puertos = []
            for port in serial.tools.list_ports.comports():
                puertos.append({
                    'puerto': port.device,
                    'descripcion': port.description,
                    'fabricante': port.manufacturer or 'Desconocido'
                })
            return puertos
        except Exception as e:
            print(f"Error al obtener puertos: {e}")
            return []

    def cambiar_configuracion(self, puerto=None, baudrate=None, protocolo=None, 
                            activar_dtr=None, activar_rts=None, timeout=None):
        """Cambia la configuración de la balanza y la guarda"""
        try:
            # Actualizar configuración
            if puerto is not None:
                self.puerto = puerto
            if baudrate is not None:
                self.baudrate = baudrate
            if protocolo is not None:
                self.protocolo = protocolo
            if activar_dtr is not None:
                self.activar_dtr = activar_dtr
            if activar_rts is not None:
                self.activar_rts = activar_rts
            if timeout is not None:
                self.timeout = timeout

            # Guardar configuración
            if self.guardar_configuracion():
                # Reinicializar conexión
                self.cerrar()
                self._inicializar_conexion()
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error al cambiar configuración: {e}")
            return False

    def probar_conexion(self):
        """Prueba la conexión con la balanza"""
        try:
            if not self.conexion or not self.conexion.is_open:
                return {
                    'exito': False,
                    'mensaje': 'Conexión no disponible'
                }
            
            # Intentar leer peso
            peso = self.obtener_peso()
            
            return {
                'exito': True,
                'peso': peso,
                'mensaje': f'Conexión OK - Peso actual: {peso:.2f} kg',
                'datos_recibidos': self.obtener_datos_recibidos()[-5:]  # Últimos 5 datos
            }
            
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error: {str(e)}'
            }

    def obtener_estado(self):
        """Obtiene el estado actual de la balanza"""
        return {
            'conectada': self.conexion is not None and self.conexion.is_open,
            'puerto': self.puerto,
            'baudrate': self.baudrate,
            'protocolo': self.protocolo,
            'peso_actual': self.peso_actual,
            'ultimo_error': self.ultimo_error,
            'dtr': self.activar_dtr,
            'rts': self.activar_rts,
            'datos_recibidos': len(self.datos_recibidos)
        }

    def cerrar(self):
        """Cierra la conexión con la balanza"""
        if self.conexion and self.conexion.is_open:
            try:
                self.conexion.close()
                print("✅ Conexión con balanza cerrada")
            except Exception as e:
                print(f"⚠️ Error al cerrar conexión: {e}")
