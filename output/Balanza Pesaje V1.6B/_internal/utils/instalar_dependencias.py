#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para instalar automáticamente las dependencias del Sistema de Pesaje de Fardos
Compatible con Windows 7+ y Python 3.6+
"""

import subprocess
import sys
import os

def ejecutar_comando(comando):
    """Ejecuta un comando y muestra el resultado"""
    try:
        print(f"Ejecutando: {comando}")
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print("✅ Éxito")
            if resultado.stdout:
                print(resultado.stdout)
        else:
            print("❌ Error")
            if resultado.stderr:
                print(resultado.stderr)
        
        return resultado.returncode == 0
    except Exception as e:
        print(f"❌ Error al ejecutar comando: {e}")
        return False

def verificar_python():
    """Verifica la versión de Python"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("⚠️ ADVERTENCIA: Se recomienda Python 3.6 o superior")
        print("   El sistema puede funcionar pero algunas características podrían no estar disponibles")
        return False
    else:
        print("✅ Versión de Python compatible")
        return True

def verificar_pip():
    """Verifica que pip esté disponible"""
    print("\n📦 Verificando pip...")
    try:
        import pip
        print("✅ pip está disponible")
        return True
    except ImportError:
        print("❌ pip no está disponible")
        print("   Instale pip desde: https://pip.pypa.io/en/stable/installation/")
        return False

def actualizar_pip():
    """Actualiza pip a la última versión"""
    print("\n🔄 Actualizando pip...")
    comando = f"{sys.executable} -m pip install --upgrade pip"
    return ejecutar_comando(comando)

def instalar_dependencias():
    """Instala las dependencias principales"""
    print("\n📚 Instalando dependencias principales...")
    
    dependencias = [
        "reportlab>=3.6.0",
        "pyserial>=3.5"
    ]
    
    exito_total = True
    
    for dependencia in dependencias:
        print(f"\n📦 Instalando {dependencia}...")
        comando = f"{sys.executable} -m pip install {dependencia}"
        
        if not ejecutar_comando(comando):
            exito_total = False
            print(f"❌ Error al instalar {dependencia}")
        else:
            print(f"✅ {dependencia} instalado correctamente")
    
    return exito_total

def instalar_dependencias_opcionales():
    """Instala dependencias opcionales para funcionalidades avanzadas"""
    print("\n🎯 ¿Desea instalar dependencias opcionales para funcionalidades avanzadas?")
    print("   - pandas: Para análisis de datos avanzado")
    print("   - matplotlib: Para gráficos y visualizaciones")
    print("   - openpyxl: Para exportar a Excel")
    
    respuesta = input("\n¿Instalar dependencias opcionales? (s/N): ").lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        dependencias_opcionales = [
            "pandas>=1.3.0",
            "matplotlib>=3.5.0",
            "openpyxl>=3.0.0"
        ]
        
        for dependencia in dependencias_opcionales:
            print(f"\n📦 Instalando {dependencia}...")
            comando = f"{sys.executable} -m pip install {dependencia}"
            ejecutar_comando(comando)
    else:
        print("⏭️ Saltando dependencias opcionales")

def verificar_instalacion():
    """Verifica que las dependencias se instalaron correctamente"""
    print("\n🔍 Verificando instalación...")
    
    dependencias_verificar = [
        ("reportlab", "ReportLab para generar PDFs"),
        ("serial", "PySerial para comunicación con balanzas")
    ]
    
    todas_ok = True
    
    for modulo, descripcion in dependencias_verificar:
        try:
            __import__(modulo)
            print(f"✅ {descripcion} - OK")
        except ImportError:
            print(f"❌ {descripcion} - NO DISPONIBLE")
            todas_ok = False
    
    return todas_ok

def crear_archivo_prueba():
    """Crea un archivo de prueba para verificar que todo funciona"""
    print("\n🧪 Creando archivo de prueba...")
    
    codigo_prueba = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archivo de prueba para verificar que las dependencias están instaladas correctamente
"""

def probar_dependencias():
    """Prueba que todas las dependencias funcionen"""
    print("🧪 Probando dependencias...")
    
    try:
        import reportlab
        print("✅ ReportLab - OK")
    except ImportError as e:
        print(f"❌ ReportLab - Error: {e}")
    
    try:
        import serial
        print("✅ PySerial - OK")
    except ImportError as e:
        print(f"❌ PySerial - Error: {e}")
    
    # Probar bibliotecas estándar
    try:
        import tkinter
        print("✅ Tkinter (GUI) - OK")
    except ImportError as e:
        print(f"❌ Tkinter - Error: {e}")
    
    try:
        import csv, datetime, os, random, time
        print("✅ Bibliotecas estándar - OK")
    except ImportError as e:
        print(f"❌ Bibliotecas estándar - Error: {e}")
    
    print("\\n🎉 Prueba completada!")
    print("Si ve '✅ OK' en todas las líneas, el sistema está listo para usar.")
    input("\\nPresione Enter para continuar...")

if __name__ == "__main__":
    probar_dependencias()
'''
    
    try:
        with open("probar_dependencias.py", "w", encoding="utf-8") as archivo:
            archivo.write(codigo_prueba)
        print("✅ Archivo de prueba creado: probar_dependencias.py")
        print("   Ejecute 'python probar_dependencias.py' para verificar la instalación")
        return True
    except Exception as e:
        print(f"❌ Error al crear archivo de prueba: {e}")
        return False

def main():
    """Función principal del instalador"""
    print("=" * 60)
    print("🏭 INSTALADOR DE DEPENDENCIAS")
    print("   Sistema de Pesaje de Fardos v2.0")
    print("=" * 60)
    
    # Verificar Python
    if not verificar_python():
        print("\n⚠️ Continuando con la instalación...")
    
    # Verificar pip
    if not verificar_pip():
        print("\n❌ No se puede continuar sin pip")
        input("Presione Enter para salir...")
        return
    
    # Actualizar pip
    print("\n" + "=" * 40)
    actualizar_pip()
    
    # Instalar dependencias principales
    print("\n" + "=" * 40)
    if instalar_dependencias():
        print("\n✅ Dependencias principales instaladas correctamente")
    else:
        print("\n⚠️ Algunas dependencias no se pudieron instalar")
        print("   El sistema puede funcionar con funcionalidad limitada")
    
    # Instalar dependencias opcionales
    print("\n" + "=" * 40)
    instalar_dependencias_opcionales()
    
    # Verificar instalación
    print("\n" + "=" * 40)
    if verificar_instalacion():
        print("\n🎉 ¡Instalación completada exitosamente!")
    else:
        print("\n⚠️ Instalación completada con advertencias")
        print("   Revise los errores anteriores")
    
    # Crear archivo de prueba
    print("\n" + "=" * 40)
    crear_archivo_prueba()
    
    # Instrucciones finales
    print("\n" + "=" * 60)
    print("🚀 INSTALACIÓN COMPLETADA")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("1. Ejecute 'python probar_dependencias.py' para verificar")
    print("2. Ejecute 'python main.py' para iniciar el sistema")
    print("3. Configure la balanza en config/configuracion.py si es necesario")
    print("\n📖 Consulte el README.md para más información")
    
    input("\nPresione Enter para salir...")

if __name__ == "__main__":
    main()
