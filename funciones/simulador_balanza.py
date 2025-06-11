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

            self.conexion.setDTR(self.activar_dtr)
            self.conexion.setRTS(self.activar_rts)
            self.conexion.reset_input_buffer()
            self.conexion.reset_output_buffer()
            
            self.conectada = True
            self.ultimo_error = None
            print(f"✅ Balanza conectada: {self.puerto} @ {self.baudrate} bps")
            
        except Exception as e:
            self.conexion = None
            self.conectada = False
            self.ultimo_error = str(e)
            print(f"⚠️ Balanza no disponible: {self.puerto} - {str(e)}")
            # NO tirar error, solo marcar como desconectada

    def obtener_peso(self) -> float:
        """Obtiene el peso actual - SIEMPRE devuelve un valor"""
        # Si no está conectada, devolver 0
        if not self.conectada or not self.conexion or not self.conexion.is_open:
            return 0.0

        try:
            # Leer peso según protocolo
            if self.protocolo.upper() == 'CONTINUO':
                peso = self._leer_continuo()
            else:
                peso = self._leer_con_comando()
            
            self.peso_actual = peso
            return peso
            
        except Exception as e:
            print(f"⚠️ Error al leer peso: {str(e)}")
            self.ultimo_error = str(e)
            return 0.0

    def _leer_continuo(self) -> float:
        """Lee datos de balanza continua - GENÉRICO para cualquier balanza"""
        tiempo_inicio = time.time()
        
        while time.time() - tiempo_inicio < 1.5:  # Timeout más corto
            if self.conexion.in_waiting:
                try:
                    byte = self.conexion.read().decode('ascii', errors='ignore')
                    
                    if byte in ['\r', '\n']:
                        if self.buffer.strip():
                            linea = self.buffer.strip()
                            self._agregar_dato_recibido(linea)
                            
                            # Extraer peso de cualquier formato
                            peso = self._extraer_peso_universal(linea)
                            self.buffer = ""
                            return peso
                        self.buffer = ""
                    else:
                        self.buffer += byte
                        
                except Exception:
                    continue
            else:
                time.sleep(0.01)
        
        return 0.0

    def _leer_con_comando(self) -> float:
        """Lee peso enviando comando"""
        try:
            self.conexion.reset_input_buffer()
            
            # Comandos básicos por protocolo
            comandos = {
                "TOLEDO": b'W\r\n',
                "AND": b'Q\r\n',
                "OHAUS": b'IP\r\n',
                "METTLER": b'S\r\n',
                "CAS": b'R\r\n',
                "GAMA": b'\r\n'
            }
            
            comando = comandos.get(self.protocolo.upper(), b'P\r\n')
            self.conexion.write(comando)
            time.sleep(0.1)
            
            respuesta = self.conexion.readline().decode('utf-8', errors='ignore').strip()
            
            if respuesta:
                self._agregar_dato_recibido(respuesta)
                return self._extraer_peso_universal(respuesta)
            
            return 0.0
            
        except Exception:
            return 0.0

    def _extraer_peso_universal(self, cadena: str) -> float:
        """Extrae peso de CUALQUIER formato de balanza"""
        try:
            cadena_limpia = cadena.strip()
            
            # Detectar peso cero (común en muchas balanzas)
            patrones_cero = ["000000", "0000000", "+000000", "+0000000", 
                           "no weight", "sin peso", "stable", "st,gs,+000000"]
            if any(patron in cadena_limpia.lower() for patron in patrones_cero):
                return 0.0
            
            # Patrón 1: Números con punto decimal (ej: 25.34, +25.34, -25.34)
            match = re.search(r'[-+]?\d+\.\d+', cadena_limpia)
            if match:
                return float(match.group())
            
            # Patrón 2: Números grandes (posiblemente en gramos/decigramos)
            match = re.search(r'[-+]?\d{4,}', cadena_limpia)
            if match:
                numero = float(match.group())
                # Si es muy grande, probablemente esté en gramos
                if numero > 1000:
                    return numero / 1000.0  # Convertir a kg
                elif numero > 100:
                    return numero / 100.0   # Convertir desde decigramos
                else:
                    return numero
            
            # Patrón 3: Cualquier número
            match = re.search(r'[-+]?\d+', cadena_limpia)
            if match:
                return float(match.group())
            
            return 0.0
            
        except Exception:
            return 0.0

    def _agregar_dato_recibido(self, dato):
        """Agrega dato al log"""
        timestamp = time.strftime("%H:%M:%S")
        entrada = f"[{timestamp}] {dato}"
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
                'peso': 0.0
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
                'peso': 0.0
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
