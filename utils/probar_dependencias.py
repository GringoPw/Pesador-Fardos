#!/usr/bin/env python3
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
    
    print("\n🎉 Prueba completada!")
    print("Si ve '✅ OK' en todas las líneas, el sistema está listo para usar.")
    input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    probar_dependencias()
