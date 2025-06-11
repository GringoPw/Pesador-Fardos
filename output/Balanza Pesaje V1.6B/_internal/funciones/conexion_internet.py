import socket
import threading
import time
from typing import Callable

class VerificadorInternet:
    """Clase para verificar el estado de la conexión a internet"""
    
    def __init__(self, callback: Callable[[bool], None] = None):
        self.callback = callback
        self.estado_actual = False
        self.verificando = False
        self.thread = None
    
    def verificar_conexion(self) -> bool:
        """Verifica si hay conexión a internet"""
        try:
            # Intentar conectar a Google DNS (8.8.8.8) en puerto 53
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            try:
                # Intentar con Cloudflare DNS como respaldo
                socket.create_connection(("1.1.1.1", 53), timeout=3)
                return True
            except OSError:
                return False
    
    def iniciar_verificacion_continua(self, intervalo: int = 30):
        """Inicia la verificación continua de conexión"""
        if self.verificando:
            return
        
        self.verificando = True
        self.thread = threading.Thread(target=self._verificar_loop, args=(intervalo,))
        self.thread.daemon = True
        self.thread.start()
    
    def _verificar_loop(self, intervalo: int):
        """Loop de verificación en hilo separado"""
        while self.verificando:
            nuevo_estado = self.verificar_conexion()
            
            if nuevo_estado != self.estado_actual:
                self.estado_actual = nuevo_estado
                if self.callback:
                    self.callback(nuevo_estado)
            
            time.sleep(intervalo)
    
    def detener_verificacion(self):
        """Detiene la verificación continua"""
        self.verificando = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
    
    def obtener_estado(self) -> bool:
        """Obtiene el estado actual de la conexión"""
        return self.estado_actual
