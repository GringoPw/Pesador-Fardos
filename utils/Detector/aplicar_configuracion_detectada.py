#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicador de Configuración Detectada - Sistema de Pesaje de Fardos
Aplica la configuración de balanza detectada automáticamente al sistema principal

Autor: Sistema de Pesaje
Fecha: 2024
"""

import json
import os
import shutil
from datetime import datetime

def mostrar_banner():
    """Muestra el banner del programa"""
    print("=" * 70)
    print("🔧 APLICADOR DE CONFIGURACIÓN DETECTADA")
    print("   Sistema de Pesaje de Fardos v2.0")
    print("=" * 70)
    print()

def cargar_configuracion_detectada():
    """Carga la configuración detectada"""
    archivos_config = [
        'balanza_config_detectada.json',
        'balanza_config_detectada.py'
    ]
    
    config_detectada = None
    
    # Intentar cargar desde JSON
    if os.path.exists('balanza_config_detectada.json'):
        try:
            with open('balanza_config_detectada.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                config_detectada = data.get('BALANZA_CONFIG', {})
                info_deteccion = data.get('DETECCION_INFO', {})
                
            print("✅ Configuración detectada cargada desde JSON")
            print(f"   Fecha detección: {info_deteccion.get('fecha_deteccion', 'Desconocida')}")
            print(f"   Calidad: {info_deteccion.get('calidad', 'N/A')}%")
            print(f"   Peso detectado: {info_deteccion.get('peso_detectado', 'N/A')} kg")
            
            return config_detectada, info_deteccion
            
        except Exception as e:
            print(f"❌ Error al cargar JSON: {e}")
    
    # Intentar cargar desde Python
    elif os.path.exists('balanza_config_detectada.py'):
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("config_detectada", "balanza_config_detectada.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            config_detectada = module.BALANZA_CONFIG
            info_deteccion = getattr(module, 'DETECCION_INFO', {})
            
            print("✅ Configuración detectada cargada desde Python")
            return config_detectada, info_deteccion
            
        except Exception as e:
            print(f"❌ Error al cargar Python: {e}")
    
    else:
        print("❌ No se encontró archivo de configuración detectada")
        print("   Ejecute primero 'detector_balanza.py'")
    
    return None, None

def cargar_configuracion_actual():
    """Carga la configuración actual del sistema"""
    try:
        config_path = os.path.join('config', 'configuracion.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print("❌ No se encontró configuracion.json")
            return None
    except Exception as e:
        print(f"❌ Error al cargar configuración actual: {e}")
        return None

def mostrar_comparacion(config_actual, config_detectada):
    """Muestra la comparación entre configuraciones"""
    print("\n" + "=" * 50)
    print("📊 COMPARACIÓN DE CONFIGURACIONES")
    print("=" * 50)
    
    balanza_actual = config_actual.get('balanza', {}) if config_actual else {}
    
    campos = [
        ('puerto_serie', 'Puerto COM'),
        ('baudrate', 'Baudrate'),
        ('protocolo', 'Protocolo'),
        ('activar_dtr', 'DTR'),
        ('activar_rts', 'RTS'),
        ('timeout', 'Timeout')
    ]
    
    print(f"{'Campo':<15} {'Actual':<15} {'Detectada':<15} {'Cambio'}")
    print("-" * 60)
    
    cambios = 0
    for campo, nombre in campos:
        actual = balanza_actual.get(campo, 'N/A')
        detectada = config_detectada.get(campo, 'N/A')
        
        if actual != detectada:
            cambios += 1
            cambio = "✅ SÍ"
        else:
            cambio = "❌ NO"
        
        print(f"{nombre:<15} {str(actual):<15} {str(detectada):<15} {cambio}")
    
    print(f"\nTotal de cambios: {cambios}")
    return cambios > 0

def aplicar_configuracion(config_actual, config_detectada):
    """Aplica la configuración detectada"""
    try:
        # Hacer backup de la configuración actual
        backup_path = f"config/configuracion_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if config_actual:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(config_actual, f, indent=4, ensure_ascii=False)
            print(f"✅ Backup creado: {backup_path}")
        
        # Actualizar configuración
        if not config_actual:
            config_actual = {"balanza": {}}
        
        # Actualizar solo la sección de balanza
        config_actual['balanza'].update(config_detectada)
        
        # Guardar configuración actualizada
        config_path = os.path.join('config', 'configuracion.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_actual, f, indent=4, ensure_ascii=False)
        
        print("✅ Configuración aplicada exitosamente")
        print(f"   Archivo actualizado: {config_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al aplicar configuración: {e}")
        return False

def main():
    """Función principal"""
    mostrar_banner()
    
    # Cargar configuración detectada
    config_detectada, info_deteccion = cargar_configuracion_detectada()
    if not config_detectada:
        input("\nPresione Enter para salir...")
        return
    
    # Cargar configuración actual
    config_actual = cargar_configuracion_actual()
    
    # Mostrar configuración detectada
    print("\n🎯 CONFIGURACIÓN DETECTADA:")
    for campo, valor in config_detectada.items():
        print(f"   {campo}: {valor}")
    
    # Mostrar comparación si hay configuración actual
    if config_actual:
        hay_cambios = mostrar_comparacion(config_actual, config_detectada)
        if not hay_cambios:
            print("\n✅ La configuración detectada es igual a la actual")
            respuesta = input("\n¿Desea aplicarla de todas formas? (s/N): ").lower()
            if respuesta != 's':
                print("👋 Operación cancelada")
                return
    else:
        print("\n⚠️ No hay configuración actual, se creará una nueva")
    
    # Confirmar aplicación
    print("\n" + "=" * 50)
    print("⚠️ CONFIRMACIÓN")
    print("=" * 50)
    print("Esta operación:")
    print("• Creará un backup de la configuración actual")
    print("• Actualizará la configuración de balanza")
    print("• Requerirá reiniciar el sistema principal")
    print()
    
    respuesta = input("¿Desea continuar? (s/N): ").lower()
    if respuesta == 's':
        if aplicar_configuracion(config_actual, config_detectada):
            print("\n🎉 ¡CONFIGURACIÓN APLICADA EXITOSAMENTE!")
            print("\n📋 PRÓXIMOS PASOS:")
            print("1. Reinicie el sistema principal de pesaje")
            print("2. Verifique que la balanza funcione correctamente")
            print("3. Pruebe algunas pesadas para confirmar")
            
            # Limpiar archivos temporales
            try:
                if os.path.exists('balanza_config_detectada.json'):
                    os.remove('balanza_config_detectada.json')
                if os.path.exists('balanza_config_detectada.py'):
                    os.remove('balanza_config_detectada.py')
                print("\n🧹 Archivos temporales limpiados")
            except:
                pass
        else:
            print("\n❌ Error al aplicar configuración")
    else:
        print("\n👋 Operación cancelada")
    
    input("\nPresione Enter para salir...")

if __name__ == "__main__":
    main()