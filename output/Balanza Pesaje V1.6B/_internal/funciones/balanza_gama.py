import serial
import time
import re
from config.configuracion import BALANZA_CONFIG

class BalanzaGama:
    """Clase específica para manejar la balanza GAMA D2002E"""
    
    def __init__(self):
        self.puerto = BALANZA_CONFIG['puerto_serie']
        self.baudrate = BALANZA_CONFIG['baudrate']
        self.timeout = BALANZA_CONFIG['timeout']
        self.conexion = None
        self.ultimo_peso_valido = 0.0
        self.buffer = ""
        
        self._inicializar_conexion()
    
    def _inicializar_conexion(self):
        """Inicializa la conexión con la balanza GAMA"""
        try:
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
            
            # Activar DTR y RTS
            if BALANZA_CONFIG.get('activar_dtr', True):
                self.conexion.setDTR(True)
            if BALANZA_CONFIG.get('activar_rts', True):
                self.conexion.setRTS(True)
            
            print(f"✅ Balanza GAMA conectada en puerto {self.puerto}")
            print(f"   DTR: {self.conexion.dtr}, RTS: {self.conexion.rts}")
            
        except Exception as e:
            print(f"❌ Error al conectar balanza GAMA: {str(e)}")
            self.conexion = None
            raise
    
    def obtener_peso(self) -> float:
        """Obtiene el peso actual de la balanza GAMA"""
        if not self.conexion or not self.conexion.is_open:
            print("❌ Conexión no disponible")
            return self.ultimo_peso_valido
        
        try:
            return self._leer_peso_continuo()
        except Exception as e:
            print(f"❌ Error al leer peso: {str(e)}")
            return self.ultimo_peso_valido
    
    def _leer_peso_continuo(self) -> float:
        """Lee peso de la balanza que envía datos continuamente"""
        tiempo_inicio = time.time()
        
        # Leer durante máximo 2 segundos
        while time.time() - tiempo_inicio < 2:
            if self.conexion.in_waiting:
                try:
                    byte = self.conexion.read().decode('ascii', errors='ignore')
                    
                    if byte in ['\r', '\n']:  # Fin de línea
                        if self.buffer.strip():
                            linea = self.buffer.strip()
                            print(f"📋 Línea recibida: '{linea}'")
                            
                            # Procesar la línea
                            peso = self._extraer_peso_de_linea(linea)
                            
                            # Solo actualizar si es un peso válido > 0
                            if peso > 0:
                                self.ultimo_peso_valido = peso
                                print(f"✅ Peso actualizado: {self.ultimo_peso_valido} kg")
                            elif "ST,GS,+000000" in linea or "ST,GS,+0000000" in linea:
                                # Mensaje específico de "sin peso" - mantener último peso
                                print(f"🔄 Sin peso en balanza, manteniendo: {self.ultimo_peso_valido} kg")
                            
                            self.buffer = ""
                            return self.ultimo_peso_valido
                        self.buffer = ""
                    else:
                        self.buffer += byte
                        
                except Exception as e:
                    print(f"⚠️ Error al decodificar: {e}")
                    continue
            else:
                time.sleep(0.01)
        
        # Si no hay datos nuevos, devolver último peso válido
        print(f"⏰ Sin datos nuevos, peso actual: {self.ultimo_peso_valido} kg")
        return self.ultimo_peso_valido
    
    def _extraer_peso_de_linea(self, linea: str) -> float:
        """Extrae el peso de una línea de la balanza GAMA"""
        try:
            print(f"🔍 Analizando: '{linea}'")
            
            # Detectar mensaje de "sin peso"
            if "ST,GS,+000000" in linea or "ST,GS,+0000000" in linea:
                print("🔄 Mensaje de sin peso detectado")
                return 0.0
            
            # Buscar números con punto decimal
            patron_decimal = r'[-+]?\s*\d+\.\d+'
            match = re.search(patron_decimal, linea)
            if match:
                numero_str = match.group().replace(' ', '')
                peso = float(numero_str)
                print(f"✅ Peso extraído: {peso} kg")
                return peso
            
            # Buscar números enteros
            patron_entero = r'[-+]?\s*\d+'
            match = re.search(patron_entero, linea)
            if match:
                numero_str = match.group().replace(' ', '')
                peso = float(numero_str)
                print(f"✅ Peso entero extraído: {peso} kg")
                return peso
            
            print(f"❌ No se pudo extraer peso de: '{linea}'")
            return 0.0
            
        except Exception as e:
            print(f"⚠️ Error al extraer peso: {e}")
            return 0.0
    
    def probar_conexion(self) -> dict:
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
                'mensaje': f'Conexión OK - Peso: {peso} kg'
            }
            
        except Exception as e:
            return {
                'exito': False,
                'mensaje': f'Error: {str(e)}'
            }
    
    def cerrar(self):
        """Cierra la conexión con la balanza"""
        if self.conexion and self.conexion.is_open:
            try:
                self.conexion.close()
                print("✅ Conexión con balanza GAMA cerrada")
            except Exception as e:
                print(f"⚠️ Error al cerrar conexión: {e}")
