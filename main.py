#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Pesaje de Fardos - Versión 2.0
Aplicación principal con interfaz moderna y mejorada

Autor: Sistema de Pesaje
Fecha: 2024
Compatibilidad: Windows 7+, Python 3.6+
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Agregar el directorio actual al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas"""
    dependencias_faltantes = []
    
    try:
        import reportlab
    except ImportError:
        dependencias_faltantes.append('reportlab')
    
    try:
        import serial
    except ImportError:
        dependencias_faltantes.append('pyserial')
    
    if dependencias_faltantes:
        mensaje = f"""
Faltan las siguientes dependencias:
{', '.join(dependencias_faltantes)}

Para instalarlas, ejecute:
pip install {' '.join(dependencias_faltantes)}

O ejecute el archivo 'instalar_dependencias.py'
        """
        print(mensaje)
        
        # Mostrar mensaje en ventana si es posible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Dependencias Faltantes", mensaje)
            root.destroy()
        except:
            pass
        
        return False
    
    return True

def main():
    """Función principal de la aplicación"""
    try:
        # Verificar dependencias
        if not verificar_dependencias():
            input("Presione Enter para salir...")
            return
        
        # Importar y ejecutar la aplicación
        from interfaz.ventana_principal import VentanaPrincipal
        
        print("🏭 Iniciando Sistema de Pesaje de Fardos v2.0...")
        print("✅ Dependencias verificadas")
        print("🚀 Cargando interfaz...")
        
        # Crear y ejecutar la aplicación
        app = VentanaPrincipal()
        app.ejecutar()
        
    except ImportError as e:
        error_msg = f"""
Error al importar módulos: {str(e)}

Posibles soluciones:
1. Verificar que todos los archivos estén en su lugar
2. Ejecutar desde el directorio correcto
3. Instalar dependencias faltantes

Estructura de archivos requerida:
- main.py
- config/configuracion.py
- funciones/
- interfaz/
        """
        print(error_msg)
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error de Importación", error_msg)
            root.destroy()
        except:
            pass
        
        input("Presione Enter para salir...")
    
    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        print(error_msg)
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", error_msg)
            root.destroy()
        except:
            pass
        
        input("Presione Enter para salir...")

if __name__ == "__main__":
    main()
