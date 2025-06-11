import serial
import serial.tools.list_ports
import time
import re
from config.configuracion import BALANZA_CONFIG

class ConexionBalanza:
    """Clase modular para manejar cualquier balanza"""

    def __init__(self):
        self.conexion = None
        self.peso_actual = 0.0
        self.peso_anterior = None  # Para detectar cambios
        self.conectada = False
        self.ultimo_error = None
        self.buffer = ""
        self.datos_recibidos = []
        self.max_datos_log = 50
        
        # Cargar configuración
        self.cargar_configuracion()
        
        # Intentar conectar (sin tirar error si falla)
        self.intentar_conexion()

    def cargar_configuracion(self):
        """Carga la configuración desde BALANZA_CONFIG"""
        self.puerto = BALANZA_CONFIG.get('puerto_serie', 'COM1')
        self.baudrate = BALANZA_CONFIG.get('baudrate', 9600)
        self.timeout = BALANZA_CONFIG.get('timeout', 1)
        self.protocolo = BALANZA_CONFIG.get('protocolo', 'CONTINUO')
        self.activar_dtr = BALANZA_CONFIG.get('activar_dtr', True)
        self.activar_rts = BALANZA_CONFIG.get('activar_rts', True)

    def intentar_conexion(self):
        """Intenta conectar con la balanza SIN tirar error si falla"""
        try:
            if self.conexion and self.conexion.is_open:
                self.conexion.close()
                
            # EXACTAMENTE como tu función
            self.conexion = serial.Serial(
                port=self.puerto,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout,
                xonxoff=False,      # Soft handshake OFF
                rtscts=False,       # RTS/CTS OFF (hardware handshake OFF)
                dsrdtr=False        # DSR/DTR OFF
            )

            # Activar DTR y RTS manualmente - EXACTAMENTE como tu función
            self.conexion.setDTR(True)
            self.conexion.setRTS(True)
            
            self.conectada = True
            self.ultimo_error = None
            print(f"✅ Balanza conectada: {self.puerto} @ {self.baudrate} bps")
            
        except Exception as e:
            self.conexion = None
            self.conectada = False
            self.ultimo_error = str(e)
            print(f"⚠️ Balanza no disponible: {self.puerto} - {str(e)}")

    def extraer_peso(self, texto):
        """Extrae el valor numérico del peso del texto recibido - EXACTAMENTE tu función"""
        # Buscar números con posibles decimales
        match = re.search(r'[-+]?\d*\.?\d+', texto)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        return None

    def obtener_peso(self) -> float:
        """Obtiene el peso actual usando EXACTAMENTE tu lógica"""
        # Si no está conectada, devolver peso actual
        if not self.conectada or not self.conexion or not self.conexion.is_open:
            return self.peso_actual

        try:
            # EXACTAMENTE tu lógica de lectura
            if self.conexion.in_waiting:
                byte = self.conexion.read().decode('ascii', errors='ignore')
                
                if byte in ['\r', '\n']:  # Detectar fin de línea - EXACTAMENTE como tu función
                    if self.buffer.strip():
                        linea_completa = self.buffer.strip()
                        
                        # Agregar al log
                        self._agregar_dato_recibido(linea_completa)
                        
                        # EXACTAMENTE tu función extraer_peso
                        peso_actual = self.extraer_peso(linea_completa)
                        
                        # Solo actualizar si el peso cambió - EXACTAMENTE como tu función
                        if peso_actual is not None and peso_actual != self.peso_anterior:
                            print(f"Peso: {peso_actual} kg")
                            self.peso_actual = peso_actual
                            self.peso_anterior = peso_actual
                            
                    self.buffer = ""
                else:
                    self.buffer += byte
            
            return self.peso_actual
            
        except Exception as e:
            print(f"⚠️ Error al leer peso: {str(e)}")
            self.ultimo_error = str(e)
            return self.peso_actual

    def _agregar_dato_recibido(self, dato):
        """Agrega dato al log"""
        timestamp = time.strftime("%H:%M:%S")
        entrada = f"{dato}"
        
        # Solo agregar si es diferente al último
        if not self.datos_recibidos or self.datos_recibidos[-1] != entrada:
            self.datos_recibidos.append(entrada)
            
            if len(self.datos_recibidos) > self.max_datos_log:
                self.datos_recibidos.pop(0)

    def obtener_datos_recibidos(self):
        """Obtiene el log de datos"""
        return self.datos_recibidos.copy()

    def limpiar_datos_recibidos(self):
        """Limpia el log"""
        self.datos_recibidos.clear()

    def obtener_puertos_disponibles(self):
        """Obtiene puertos COM disponibles"""
        try:
            puertos = []
            for port in serial.tools.list_ports.comports():
                puertos.append({
                    'puerto': port.device,
                    'descripcion': port.description,
                    'fabricante': port.manufacturer or 'Desconocido'
                })
            return puertos
        except Exception:
            return []

    def cambiar_configuracion(self, puerto=None, baudrate=None, protocolo=None, 
                            activar_dtr=None, activar_rts=None, timeout=None):
        """Cambia configuración y reconecta"""
        try:
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

            # Cerrar conexión actual
            self.cerrar()
            
            # Intentar nueva conexión
            self.intentar_conexion()
            
            return self.conectada
                
        except Exception as e:
            print(f"Error al cambiar configuración: {e}")
            return False

    def probar_conexion(self):
        """Prueba la conexión"""
        if not self.conectada:
            return {
                'exito': False,
                'mensaje': f'Balanza desconectada - Puerto: {self.puerto}',
                'peso': self.peso_actual
            }
        
        try:
            peso = self.obtener_peso()
            return {
                'exito': True,
                'peso': peso,
                'mensaje': f'Conexión OK - Peso: {peso:.2f} kg'
            }
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error: {str(e)}',
                'peso': self.peso_actual
            }

    def obtener_estado(self):
        """Obtiene estado actual"""
        return {
            'conectada': self.conectada,
            'puerto': self.puerto,
            'baudrate': self.baudrate,
            'protocolo': self.protocolo,
            'peso_actual': self.peso_actual,
            'ultimo_error': self.ultimo_error,
            'dtr': self.activar_dtr,
            'rts': self.activar_rts
        }

    def cerrar(self):
        """Cierra conexión"""
        if self.conexion and self.conexion.is_open:
            try:
                self.conexion.close()
            except Exception:
                pass
        self.conectada = False
        self.conexion = None
