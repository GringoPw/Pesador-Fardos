"""
Gestor de configuración para el sistema de pesaje
Maneja la carga y guardado de configuraciones en JSON
"""
import os
import json
from typing import Dict, Any, Optional

class ConfigManager:
    """Clase para gestionar la configuración del sistema"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'configuracion.json')
        self.config_data = {}
        self.cargar_configuracion()
    
    def cargar_configuracion(self) -> bool:
        """Carga la configuración desde el archivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                print(f"✅ Configuración cargada desde {self.config_file}")
                return True
            else:
                print(f"⚠️ Archivo de configuración no encontrado: {self.config_file}")
                self.config_data = {}
                return False
        except Exception as e:
            print(f"❌ Error al cargar configuración: {str(e)}")
            self.config_data = {}
            return False
    
    def guardar_configuracion(self) -> bool:
        """Guarda la configuración actual en el archivo JSON"""
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            print(f"✅ Configuración guardada en {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ Error al guardar configuración: {str(e)}")
            return False
    
    def obtener(self, seccion: str, defecto: Any = None) -> Any:
        """Obtiene una sección de la configuración"""
        return self.config_data.get(seccion, defecto)
    
    def establecer(self, seccion: str, valor: Any) -> bool:
        """Establece una sección de la configuración y la guarda"""
        self.config_data[seccion] = valor
        return self.guardar_configuracion()
    
    def actualizar_balanza(self, config_balanza: Dict[str, Any]) -> bool:
        """Actualiza la configuración de la balanza"""
        if 'balanza' not in self.config_data:
            self.config_data['balanza'] = {}
        
        self.config_data['balanza'].update(config_balanza)
        return self.guardar_configuracion()
    
    def obtener_balanza(self) -> Dict[str, Any]:
        """Obtiene la configuración de la balanza"""
        return self.config_data.get('balanza', {})

# Instancia global del gestor de configuración
config_manager = ConfigManager()
