#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurador de Red - Sistema de Pesaje de Fardos
Herramienta para configurar el acceso en red a la base de datos

Autor: Sistema de Pesaje
Fecha: 2024
"""

import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3

class ConfiguradorRed:
    """Configurador para acceso en red"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Configurador de Red - Sistema de Pesaje")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz del configurador"""
        # Título
        titulo = tk.Label(self.root, text="🌐 Configurador de Red", 
                         font=('Arial', 16, 'bold'))
        titulo.pack(pady=20)
        
        # Notebook para pestañas
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Pestaña 1: Servidor
        self.crear_pestaña_servidor(notebook)
        
        # Pestaña 2: Cliente
        self.crear_pestaña_cliente(notebook)
        
        # Pestaña 3: Instrucciones
        self.crear_pestaña_instrucciones(notebook)
    
    def crear_pestaña_servidor(self, notebook):
        """Crea la pestaña de configuración del servidor"""
        frame_servidor = ttk.Frame(notebook)
        notebook.add(frame_servidor, text="🖥️ Servidor")
        
        # Instrucciones
        instrucciones = tk.Text(frame_servidor, height=8, wrap=tk.WORD)
        instrucciones.pack(fill='x', padx=10, pady=10)
        
        texto_servidor = """CONFIGURACIÓN DEL SERVIDOR (PC Principal):

1. El PC servidor debe tener el sistema principal instalado
2. Crear una carpeta compartida en red para la base de datos
3. Configurar permisos de lectura/escritura para usuarios de red
4. Copiar la base de datos a la carpeta compartida

Pasos recomendados:
• Crear carpeta: C:\\SistemaPesaje\\Compartida\\
• Compartir la carpeta en red con nombre "SistemaPesaje"
• Dar permisos de "Lectura y escritura" a usuarios autorizados
• Copiar pesaje_fardos.db a esta carpeta"""
        
        instrucciones.insert(1.0, texto_servidor)
        instrucciones.configure(state='disabled')
        
        # Botones
        botones_frame = tk.Frame(frame_servidor)
        botones_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(botones_frame, text="📁 Crear Carpeta Compartida", 
                 command=self.crear_carpeta_compartida,
                 bg='#2E86AB', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
        
        tk.Button(botones_frame, text="📋 Copiar Base de Datos", 
                 command=self.copiar_base_datos,
                 bg='#A23B72', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
        
        tk.Button(botones_frame, text="🔧 Abrir Configuración de Red", 
                 command=self.abrir_config_red,
                 bg='#F18F01', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
    
    def crear_pestaña_cliente(self, notebook):
        """Crea la pestaña de configuración del cliente"""
        frame_cliente = ttk.Frame(notebook)
        notebook.add(frame_cliente, text="💻 Cliente")
        
        # Instrucciones
        instrucciones = tk.Text(frame_cliente, height=6, wrap=tk.WORD)
        instrucciones.pack(fill='x', padx=10, pady=10)
        
        texto_cliente = """CONFIGURACIÓN DEL CLIENTE (PC Visor):

1. Instalar solo el visor de tickets en este PC
2. Conectarse a la carpeta compartida del servidor
3. Configurar la ruta de la base de datos
4. Probar la conexión

El visor solo permite ver, exportar e imprimir tickets (no modificar)."""
        
        instrucciones.insert(1.0, texto_cliente)
        instrucciones.configure(state='disabled')
        
        # Configuración de ruta
        config_frame = tk.LabelFrame(frame_cliente, text="Configuración de Conexión")
        config_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(config_frame, text="Ruta de la base de datos:").pack(anchor='w', padx=10, pady=5)
        
        ruta_frame = tk.Frame(config_frame)
        ruta_frame.pack(fill='x', padx=10, pady=5)
        
        self.entry_ruta = tk.Entry(ruta_frame, width=50)
        self.entry_ruta.pack(side='left', fill='x', expand=True)
        self.entry_ruta.insert(0, "//SERVIDOR/SistemaPesaje/pesaje_fardos.db")
        
        tk.Button(ruta_frame, text="📁", command=self.seleccionar_ruta).pack(side='right', padx=(5, 0))
        
        # Botones de prueba
        botones_frame = tk.Frame(config_frame)
        botones_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(botones_frame, text="🔍 Probar Conexión", 
                 command=self.probar_conexion,
                 bg='#28A745', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
        
        tk.Button(botones_frame, text="🚀 Iniciar Visor", 
                 command=self.iniciar_visor,
                 bg='#2E86AB', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
        
        tk.Button(botones_frame, text="💾 Crear Acceso Directo", 
                 command=self.crear_acceso_directo,
                 bg='#A23B72', fg='white', font=('Arial', 10)).pack(side='left', padx=5)
    
    def crear_pestaña_instrucciones(self, notebook):
        """Crea la pestaña de instrucciones detalladas"""
        frame_instrucciones = ttk.Frame(notebook)
        notebook.add(frame_instrucciones, text="📖 Instrucciones")
        
        # Texto con scroll
        text_frame = tk.Frame(frame_instrucciones)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        texto = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=texto.yview)
        texto.configure(yscrollcommand=scrollbar.set)
        
        instrucciones_completas = """GUÍA COMPLETA DE CONFIGURACIÓN EN RED

═══════════════════════════════════════════════════════════════

🖥️ CONFIGURACIÓN DEL SERVIDOR (PC Principal)

1. PREPARAR EL SISTEMA:
   • Instalar el sistema completo de pesaje
   • Asegurarse de que funciona correctamente en local
   • Crear algunos tickets de prueba

2. CREAR CARPETA COMPARTIDA:
   • Crear carpeta: C:\\SistemaPesaje\\Compartida\\
   • Clic derecho → Propiedades → Compartir
   • Compartir con nombre "SistemaPesaje"
   • Dar permisos de "Lectura y escritura" a usuarios específicos
   • O "Todos" si la red es segura

3. CONFIGURAR BASE DE DATOS:
   • Copiar pesaje_fardos.db a la carpeta compartida
   • Verificar que el archivo se puede acceder desde la red
   • El sistema principal debe usar esta base de datos compartida

4. CONFIGURAR FIREWALL:
   • Permitir "Compartir archivos e impresoras"
   • Agregar excepción para Python si es necesario

═══════════════════════════════════════════════════════════════

💻 CONFIGURACIÓN DEL CLIENTE (PC Visor)

1. INSTALAR VISOR:
   • Copiar solo los archivos necesarios del visor
   • No necesita el sistema completo
   • Instalar dependencias: pip install reportlab

2. CONECTAR A LA RED:
   • Mapear unidad de red (opcional): \\\\SERVIDOR\\SistemaPesaje
   • O usar ruta UNC directa: \\\\SERVIDOR\\SistemaPesaje\\pesaje_fardos.db
   • Probar acceso manual al archivo

3. CONFIGURAR VISOR:
   • Ejecutar: python visor_tickets.py --db "\\\\SERVIDOR\\SistemaPesaje\\pesaje_fardos.db"
   • O modificar la ruta en el código
   • Probar conexión y visualización

═══════════════════════════════════════════════════════════════

🔧 SOLUCIÓN DE PROBLEMAS COMUNES

ERROR: "No se puede conectar a la base de datos"
• Verificar que la carpeta está compartida
• Comprobar permisos de red
• Probar acceso manual al archivo
• Verificar firewall

ERROR: "Base de datos bloqueada"
• SQLite permite múltiples lectores pero un solo escritor
• El visor solo lee, no debería haber problemas
• Cerrar el sistema principal si hay conflictos

ERROR: "Archivo no encontrado"
• Verificar ruta exacta
• Usar \\\\ en lugar de \\ en rutas UNC
• Probar con IP en lugar de nombre: \\\\192.168.1.100\\SistemaPesaje

═══════════════════════════════════════════════════════════════

🌐 ALTERNATIVAS AVANZADAS

Para mayor robustez, considerar:

1. SERVIDOR DE BASE DE DATOS:
   • PostgreSQL o MySQL en lugar de SQLite
   • Mejor manejo de concurrencia
   • Acceso simultáneo sin problemas

2. SERVICIO WEB:
   • API REST para acceder a los datos
   • Mayor seguridad y control
   • Acceso desde cualquier dispositivo

3. VPN:
   • Para acceso remoto seguro
   • Conexión desde fuera de la red local

═══════════════════════════════════════════════════════════════

📞 SOPORTE

Si necesita ayuda adicional:
• Documentar el error exacto
• Verificar configuración de red
• Probar conectividad básica primero
"""
        
        texto.insert(1.0, instrucciones_completas)
        texto.configure(state='disabled')
        
        texto.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def crear_carpeta_compartida(self):
        """Crea la carpeta compartida recomendada"""
        try:
            carpeta = "C:\\SistemaPesaje\\Compartida"
            os.makedirs(carpeta, exist_ok=True)
            
            messagebox.showinfo("Éxito", 
                              f"Carpeta creada: {carpeta}\n\n"
                              "Ahora debe:\n"
                              "1. Clic derecho en la carpeta\n"
                              "2. Propiedades → Compartir\n"
                              "3. Compartir con usuarios de red")
            
            # Abrir la carpeta
            os.startfile(carpeta)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la carpeta: {e}")
    
    def copiar_base_datos(self):
        """Copia la base de datos a la carpeta compartida"""
        try:
            origen = filedialog.askopenfilename(
                title="Seleccionar base de datos",
                filetypes=[("Base de datos", "*.db"), ("Todos", "*.*")])
            
            if not origen:
                return
            
            destino = "C:\\SistemaPesaje\\Compartida\\pesaje_fardos.db"
            
            if not os.path.exists(os.path.dirname(destino)):
                os.makedirs(os.path.dirname(destino), exist_ok=True)
            
            shutil.copy2(origen, destino)
            
            messagebox.showinfo("Éxito", 
                              f"Base de datos copiada a:\n{destino}\n\n"
                              "Ahora configure el sistema principal para usar esta base de datos.")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar la base de datos: {e}")
    
    def abrir_config_red(self):
        """Abre la configuración de red de Windows"""
        try:
            os.system("control netconnections")
        except:
            messagebox.showinfo("Información", 
                              "Abra manualmente:\n"
                              "Panel de Control → Red e Internet → Centro de redes y recursos compartidos")
    
    def seleccionar_ruta(self):
        """Selecciona la ruta de la base de datos"""
        ruta = filedialog.askopenfilename(
            title="Seleccionar base de datos en red",
            filetypes=[("Base de datos", "*.db"), ("Todos", "*.*")])
        
        if ruta:
            self.entry_ruta.delete(0, tk.END)
            self.entry_ruta.insert(0, ruta)
    
    def probar_conexion(self):
        """Prueba la conexión a la base de datos"""
        ruta = self.entry_ruta.get().strip()
        
        if not ruta:
            messagebox.showwarning("Advertencia", "Ingrese una ruta de base de datos")
            return
        
        try:
            with sqlite3.connect(ruta, timeout=5.0) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tickets")
                count = cursor.fetchone()[0]
                
                messagebox.showinfo("Conexión Exitosa", 
                                  f"¡Conexión establecida!\n"
                                  f"Base de datos contiene {count} tickets.")
                
        except Exception as e:
            messagebox.showerror("Error de Conexión", 
                               f"No se pudo conectar a la base de datos:\n{e}\n\n"
                               "Verifique:\n"
                               "1. La ruta es correcta\n"
                               "2. Tiene permisos de acceso\n"
                               "3. La red está funcionando")
    
    def iniciar_visor(self):
        """Inicia el visor con la ruta configurada"""
        ruta = self.entry_ruta.get().strip()
        
        if not ruta:
            messagebox.showwarning("Advertencia", "Ingrese una ruta de base de datos")
            return
        
        try:
            import subprocess
            subprocess.Popen(["python", "visor_tickets.py", "--db", ruta])
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el visor: {e}")
    
    def crear_acceso_directo(self):
        """Crea un acceso directo para el visor"""
        ruta = self.entry_ruta.get().strip()
        
        if not ruta:
            messagebox.showwarning("Advertencia", "Ingrese una ruta de base de datos")
            return
        
        try:
            # Crear archivo BAT
            with open("Iniciar_Visor.bat", "w") as f:
                f.write(f'@echo off\n')
                f.write(f'echo Iniciando Visor de Tickets...\n')
                f.write(f'python visor_tickets.py --db "{ruta}"\n')
                f.write(f'pause\n')
            
            messagebox.showinfo("Éxito", 
                              "Acceso directo creado: Iniciar_Visor.bat\n\n"
                              "Puede copiarlo al escritorio para fácil acceso.")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el acceso directo: {e}")
    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ConfiguradorRed()
    app.ejecutar()
