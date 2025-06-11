#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visor de Tickets - Sistema de Pesaje de Fardos
Aplicación de solo lectura para visualizar, imprimir y exportar tickets
Compatible con red - Se conecta a la base de datos compartida

Autor: Sistema de Pesaje
Fecha: 2024
Compatibilidad: Windows 7+, Python 3.6+
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import sqlite3
from typing import List, Optional, Tuple

# Agregar el directorio actual al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.configuracion import COLORES, FUENTES, DIMENSIONES
from interfaz.estilos import EstilosModernos, WidgetsPersonalizados
from funciones.modelos import Ticket, Fardo
from funciones.exportador import Exportador

class BaseDatosVisor:
    """Clase para manejar la base de datos en modo solo lectura"""
    
    def __init__(self, ruta_db: str = None):
        if ruta_db:
            self.ruta_db = ruta_db
        else:
            # Buscar la base de datos en varias ubicaciones
            self.ruta_db = self.buscar_base_datos()
        
        self.exportador = Exportador()
        print(f"📍 Conectando a base de datos: {self.ruta_db}")
    
    def buscar_base_datos(self) -> str:
        """Busca la base de datos en varias ubicaciones posibles"""
        posibles_rutas = [
            "pesaje_fardos.db",  # Directorio actual
            os.path.join(os.path.dirname(__file__), "pesaje_fardos.db"),  # Directorio del script
            "//servidor/compartida/pesaje_fardos.db",  # Ejemplo de ruta de red
            "Z:/pesaje_fardos.db",  # Ejemplo de unidad mapeada
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                return ruta
        
        # Si no encuentra ninguna, usar la por defecto
        return "pesaje_fardos.db"
    
    def verificar_conexion(self) -> bool:
        """Verifica que se pueda conectar a la base de datos"""
        try:
            with sqlite3.connect(self.ruta_db, timeout=5.0) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tickets")
                return True
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def obtener_tickets(self, filtro_fecha: str = None, filtro_numero: str = None) -> List[Tuple]:
        """Obtiene la lista de tickets con filtros opcionales"""
        try:
            with sqlite3.connect(self.ruta_db, timeout=10.0) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT t.numero, t.fecha_creacion, COUNT(f.id) as cantidad_fardos,
                           COALESCE(SUM(f.peso), 0) as peso_total, t.fecha_guardado,
                           t.kg_bruto_romaneo, t.agregado, t.resto
                    FROM tickets t
                    LEFT JOIN fardos f ON t.id = f.ticket_id
                    WHERE t.estado = 'ACTIVO'
                '''
                
                params = []
                
                if filtro_numero:
                    query += " AND t.numero LIKE ?"
                    params.append(f"%{filtro_numero}%")
                
                if filtro_fecha:
                    query += " AND DATE(t.fecha_creacion) = ?"
                    params.append(filtro_fecha)
                
                query += '''
                    GROUP BY t.id, t.numero, t.fecha_creacion, t.fecha_guardado
                    ORDER BY t.fecha_guardado DESC
                '''
                
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Exception as e:
            print(f"❌ Error al obtener tickets: {e}")
            return []
    
    def cargar_ticket_completo(self, numero_ticket: str) -> Optional[Ticket]:
        """Carga un ticket completo con todos sus fardos"""
        try:
            with sqlite3.connect(self.ruta_db, timeout=10.0) as conn:
                cursor = conn.cursor()
                
                # Obtener datos del ticket
                cursor.execute('''
                    SELECT numero, fecha_creacion, kg_bruto_romaneo, agregado, resto, observaciones
                    FROM tickets 
                    WHERE numero = ? AND estado = 'ACTIVO'
                ''', (numero_ticket,))
                
                ticket_data = cursor.fetchone()
                if not ticket_data:
                    return None
                
                # Crear objeto ticket
                ticket = Ticket(ticket_data[0])
                ticket.fecha_creacion = datetime.fromisoformat(ticket_data[1])
                ticket.kg_bruto_romaneo = ticket_data[2]
                ticket.agregado = ticket_data[3] if ticket_data[3] is not None else 0.0
                ticket.resto = ticket_data[4] if ticket_data[4] is not None else 0.0
                ticket.observaciones = ticket_data[5] or ""
                
                # Obtener fardos
                cursor.execute('''
                    SELECT id FROM tickets WHERE numero = ?
                ''', (numero_ticket,))
                ticket_id = cursor.fetchone()[0]
                
                cursor.execute('''
                    SELECT numero, peso, hora_pesaje
                    FROM fardos 
                    WHERE ticket_id = ?
                    ORDER BY numero
                ''', (ticket_id,))
                
                fardos_data = cursor.fetchall()
                for fardo_data in fardos_data:
                    fardo = Fardo(fardo_data[0], fardo_data[1])
                    fardo.hora_pesaje = datetime.fromisoformat(fardo_data[2])
                    ticket.fardos.append(fardo)
                
                return ticket
                
        except Exception as e:
            print(f"❌ Error al cargar ticket: {e}")
            return None
    
    def obtener_estadisticas_generales(self) -> dict:
        """Obtiene estadísticas generales"""
        try:
            with sqlite3.connect(self.ruta_db, timeout=10.0) as conn:
                cursor = conn.cursor()
                
                # Total de tickets
                cursor.execute('SELECT COUNT(*) FROM tickets WHERE estado = "ACTIVO"')
                total_tickets = cursor.fetchone()[0]
                
                # Total de fardos
                cursor.execute('''
                    SELECT COUNT(*) FROM fardos f
                    JOIN tickets t ON f.ticket_id = t.id
                    WHERE t.estado = "ACTIVO"
                ''')
                total_fardos = cursor.fetchone()[0]
                
                # Peso total
                cursor.execute('''
                    SELECT COALESCE(SUM(f.peso), 0) FROM fardos f
                    JOIN tickets t ON f.ticket_id = t.id
                    WHERE t.estado = "ACTIVO"
                ''')
                peso_total = cursor.fetchone()[0]
                
                return {
                    'total_tickets': total_tickets,
                    'total_fardos': total_fardos,
                    'peso_total': peso_total
                }
        except Exception as e:
            print(f"❌ Error al obtener estadísticas: {e}")
            return {'total_tickets': 0, 'total_fardos': 0, 'peso_total': 0}

class VisorTickets:
    """Aplicación principal del visor de tickets"""
    
    def __init__(self, ruta_db: str = None):
        self.root = tk.Tk()
        self.bd = BaseDatosVisor(ruta_db)
        self.ticket_seleccionado = None
        
        self.configurar_ventana()
        self.configurar_estilos()
        self.crear_interfaz()
        
        # Verificar conexión inicial
        if not self.bd.verificar_conexion():
            self.mostrar_error_conexion()
    
    def configurar_ventana(self):
        """Configura la ventana principal"""
        self.root.title("Visor de Tickets - Sistema de Pesaje de Fardos")
        
        # Tamaño adaptable
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        if screen_width >= 1920:
            window_width, window_height = 1400, 800
        elif screen_width >= 1366:
            window_width, window_height = 1200, 700
        else:
            window_width, window_height = 1000, 600
        
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.configure(bg=COLORES['fondo_principal'])
        self.root.resizable(True, True)
        self.root.minsize(800, 500)
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Configurar grid
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(1, weight=1)
    
    def configurar_estilos(self):
        """Configura los estilos de la aplicación"""
        EstilosModernos.configurar_estilos()
    
    def crear_interfaz(self):
        """Crea la interfaz principal"""
        # === BARRA SUPERIOR ===
        self.crear_barra_superior()
        
        # === ÁREA PRINCIPAL ===
        self.crear_area_principal()
        
        # === BARRA DE ESTADO ===
        self.crear_barra_estado()
    
    def crear_barra_superior(self):
        """Crea la barra superior"""
        barra_frame = tk.Frame(self.root, bg=COLORES['primario'], height=80)
        barra_frame.grid(row=0, column=0, columnspan=2, sticky='ew')
        barra_frame.grid_propagate(False)
        
        contenido = tk.Frame(barra_frame, bg=COLORES['primario'])
        contenido.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Título
        tk.Label(contenido, text="👁️ Visor de Tickets - Solo Lectura",
                bg=COLORES['primario'], fg=COLORES['texto_blanco'],
                font=FUENTES['extra_grande']).pack(side='left')
        
        # Controles de filtro
        filtros_frame = tk.Frame(contenido, bg=COLORES['primario'])
        filtros_frame.pack(side='right')
        
        # Filtro por número
        tk.Label(filtros_frame, text="Buscar:",
                bg=COLORES['primario'], fg=COLORES['texto_blanco'],
                font=FUENTES['normal']).pack(side='left', padx=(0, 5))
        
        self.entry_filtro = WidgetsPersonalizados.crear_entrada_moderna(
            filtros_frame, width=15)
        self.entry_filtro.pack(side='left', padx=(0, 10))
        self.entry_filtro.bind('<KeyRelease>', self.filtrar_tickets)
        
        # Botón refrescar
        WidgetsPersonalizados.crear_boton_moderno(
            filtros_frame, "🔄 Refrescar", self.cargar_tickets).pack(side='left')
    
    def crear_area_principal(self):
        """Crea el área principal"""
        # === PANEL IZQUIERDO - LISTA DE TICKETS ===
        self.crear_panel_tickets()
        
        # === PANEL DERECHO - DETALLES ===
        self.crear_panel_detalles()
    
    def crear_panel_tickets(self):
        """Crea el panel de lista de tickets"""
        # Frame principal
        panel_frame = tk.Frame(self.root, bg=COLORES['fondo_principal'])
        panel_frame.grid(row=1, column=0, sticky='nsew', padx=(15, 7), pady=15)
        
        # Estadísticas generales
        self.crear_estadisticas_generales(panel_frame)
        
        # Lista de tickets
        shadow_frame, lista_frame = EstilosModernos.crear_frame_con_sombra(panel_frame)
        shadow_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # Título
        titulo_frame = tk.Frame(lista_frame, bg=COLORES['fondo_panel'])
        titulo_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        tk.Label(titulo_frame, text="📋 Lista de Tickets",
                bg=COLORES['fondo_panel'], fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(side='left')
        
        self.label_total_tickets = tk.Label(titulo_frame, text="(0 tickets)",
                                          bg=COLORES['fondo_panel'],
                                          fg=COLORES['texto_secundario'],
                                          font=FUENTES['normal'])
        self.label_total_tickets.pack(side='right')
        
        # Tabla de tickets
        tabla_container = tk.Frame(lista_frame, bg=COLORES['fondo_panel'])
        tabla_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        columnas = ('numero', 'fecha', 'fardos', 'peso', 'rinde')
        self.tabla_frame, self.tabla_tickets = WidgetsPersonalizados.crear_tabla_moderna(
            tabla_container, columnas)
        self.tabla_frame.pack(fill='both', expand=True)
        
        # Configurar columnas
        self.tabla_tickets.heading('numero', text='N° Ticket')
        self.tabla_tickets.heading('fecha', text='Fecha')
        self.tabla_tickets.heading('fardos', text='Fardos')
        self.tabla_tickets.heading('peso', text='Peso Total')
        self.tabla_tickets.heading('rinde', text='Rinde %')
        
        self.tabla_tickets.column('numero', width=100, anchor='center')
        self.tabla_tickets.column('fecha', width=120, anchor='center')
        self.tabla_tickets.column('fardos', width=60, anchor='center')
        self.tabla_tickets.column('peso', width=100, anchor='center')
        self.tabla_tickets.column('rinde', width=80, anchor='center')
        
        # Eventos
        self.tabla_tickets.bind('<<TreeviewSelect>>', self.seleccionar_ticket)
        self.tabla_tickets.bind('<Double-1>', self.ver_detalle_completo)
    
    def crear_estadisticas_generales(self, parent):
        """Crea el panel de estadísticas generales"""
        shadow_frame, stats_frame = EstilosModernos.crear_frame_con_sombra(parent)
        shadow_frame.pack(fill='x', pady=(0, 10))
        
        contenido = tk.Frame(stats_frame, bg=COLORES['fondo_panel'])
        contenido.pack(fill='x', padx=15, pady=15)
        
        tk.Label(contenido, text="📊 Estadísticas Generales",
                bg=COLORES['fondo_panel'], fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(anchor='w', pady=(0, 10))
        
        # Grid para estadísticas
        stats_grid = tk.Frame(contenido, bg=COLORES['fondo_panel'])
        stats_grid.pack(fill='x')
        
        for i in range(3):
            stats_grid.grid_columnconfigure(i, weight=1)
        
        # Crear tarjetas de estadísticas
        self.stats_labels = {}
        self.crear_stat_card(stats_grid, "Total Tickets", "0", 0, 0, 'total_tickets')
        self.crear_stat_card(stats_grid, "Total Fardos", "0", 0, 1, 'total_fardos')
        self.crear_stat_card(stats_grid, "Peso Total", "0.00 kg", 0, 2, 'peso_total')
    
    def crear_stat_card(self, parent, titulo, valor, row, col, key):
        """Crea una tarjeta de estadística"""
        frame = tk.Frame(parent, bg=COLORES['fondo_panel'])
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        tk.Label(frame, text=titulo,
                bg=COLORES['fondo_panel'], fg=COLORES['texto_secundario'],
                font=FUENTES['normal']).pack(anchor='w')
        
        label_valor = tk.Label(frame, text=valor,
                             bg=COLORES['fondo_panel'], fg=COLORES['primario'],
                             font=FUENTES['grande'])
        label_valor.pack(anchor='w')
        
        self.stats_labels[key] = label_valor
    
    def crear_panel_detalles(self):
        """Crea el panel de detalles del ticket"""
        # Frame principal con scroll
        panel_container = tk.Frame(self.root, bg=COLORES['fondo_principal'])
        panel_container.grid(row=1, column=1, sticky='nsew', padx=(7, 15), pady=15)
        
        # Canvas para scroll
        canvas = tk.Canvas(panel_container, bg=COLORES['fondo_principal'], 
                          highlightthickness=0)
        canvas.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(panel_container, orient='vertical', 
                                 command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame de contenido
        self.panel_detalles = tk.Frame(canvas, bg=COLORES['fondo_principal'])
        canvas_window = canvas.create_window((0, 0), window=self.panel_detalles, anchor='nw')
        
        def configurar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', configurar_scroll)
        self.panel_detalles.bind('<Configure>', 
                               lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        # Crear contenido inicial
        self.crear_contenido_detalles()
    
    def crear_contenido_detalles(self):
        """Crea el contenido del panel de detalles"""
        # Título
        tk.Label(self.panel_detalles, text="📄 Detalles del Ticket",
                bg=COLORES['fondo_principal'], fg=COLORES['texto_principal'],
                font=FUENTES['titulo']).pack(anchor='w', pady=(0, 15))
        
        # Información del ticket
        self.crear_info_ticket()
        
        # Botones de acción
        self.crear_botones_accion()
        
        # Tabla de fardos
        self.crear_tabla_fardos()
        
        # Cálculos y rinde
        self.crear_calculos_rinde()
    
    def crear_info_ticket(self):
        """Crea la sección de información del ticket"""
        shadow_frame, info_frame = EstilosModernos.crear_frame_con_sombra(self.panel_detalles)
        shadow_frame.pack(fill='x', pady=(0, 10))
        
        contenido = tk.Frame(info_frame, bg=COLORES['fondo_panel'])
        contenido.pack(fill='x', padx=15, pady=15)
        
        tk.Label(contenido, text="Información General",
                bg=COLORES['fondo_panel'], fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(anchor='w', pady=(0, 10))
        
        # Labels de información
        self.info_labels = {}
        info_items = [
            ('numero', 'N° Ticket:'),
            ('fecha', 'Fecha:'),
            ('cantidad_fardos', 'Cantidad Fardos:'),
            ('peso_total', 'Peso Total:'),
            ('kg_bruto_romaneo', 'Kg Bruto Romaneo:'),
            ('agregado', 'Agregado:'),
            ('resto', 'Resto:')
        ]
        
        for key, titulo in info_items:
            frame = tk.Frame(contenido, bg=COLORES['fondo_panel'])
            frame.pack(fill='x', pady=2)
            
            tk.Label(frame, text=titulo,
                    bg=COLORES['fondo_panel'], fg=COLORES['texto_secundario'],
                    font=FUENTES['normal'], width=20, anchor='w').pack(side='left')
            
            label_valor = tk.Label(frame, text="--",
                                 bg=COLORES['fondo_panel'], fg=COLORES['texto_principal'],
                                 font=FUENTES['normal'], anchor='w')
            label_valor.pack(side='left', fill='x', expand=True)
            
            self.info_labels[key] = label_valor
    
    def crear_botones_accion(self):
        """Crea los botones de acción"""
        shadow_frame, botones_frame = EstilosModernos.crear_frame_con_sombra(self.panel_detalles)
        shadow_frame.pack(fill='x', pady=(0, 10))
        
        contenido = tk.Frame(botones_frame, bg=COLORES['fondo_panel'])
        contenido.pack(fill='x', padx=15, pady=15)
        
        tk.Label(contenido, text="Acciones",
                bg=COLORES['fondo_panel'], fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(anchor='w', pady=(0, 10))
        
        # Frame para botones
        botones_container = tk.Frame(contenido, bg=COLORES['fondo_panel'])
        botones_container.pack(fill='x')
        
        # Primera fila
        fila1 = tk.Frame(botones_container, bg=COLORES['fondo_panel'])
        fila1.pack(fill='x', pady=(0, 5))
        
        self.btn_exportar_csv = WidgetsPersonalizados.crear_boton_moderno(
            fila1, "📊 Exportar CSV", self.exportar_csv, state='disabled')
        self.btn_exportar_csv.pack(side='left', padx=(0, 10))
        
        self.btn_exportar_pdf = WidgetsPersonalizados.crear_boton_moderno(
            fila1, "📄 Exportar PDF", self.exportar_pdf, state='disabled')
        self.btn_exportar_pdf.pack(side='left')
        
        # Segunda fila
        fila2 = tk.Frame(botones_container, bg=COLORES['fondo_panel'])
        fila2.pack(fill='x')
        
        self.btn_imprimir = WidgetsPersonalizados.crear_boton_moderno(
            fila2, "🖨️ Imprimir", self.imprimir_ticket, state='disabled')
        self.btn_imprimir.pack(side='left', padx=(0, 10))
        
        self.btn_detalle_completo = WidgetsPersonalizados.crear_boton_moderno(
            fila2, "🔍 Ver Completo", self.ver_detalle_completo, state='disabled')
        self.btn_detalle_completo.pack(side='left')
    
    def crear_tabla_fardos(self):
        """Crea la tabla de fardos del ticket seleccionado"""
        shadow_frame, tabla_frame = EstilosModernos.crear_frame_con_sombra(self.panel_detalles)
        shadow_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        contenido = tk.Frame(tabla_frame, bg=COLORES['fondo_panel'])
        contenido.pack(fill='both', expand=True, padx=15, pady=15)
        
        tk.Label(contenido, text="Fardos del Ticket",
                bg=COLORES['fondo_panel'], fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(anchor='w', pady=(0, 10))
        
        # Tabla de fardos
        columnas_fardos = ('numero', 'peso', 'hora')
        self.fardos_frame, self.tabla_fardos = WidgetsPersonalizados.crear_tabla_moderna(
            contenido, columnas_fardos, height=8)
        self.fardos_frame.pack(fill='both', expand=True)
        
        # Configurar columnas
        self.tabla_fardos.heading('numero', text='N° Fardo')
        self.tabla_fardos.heading('peso', text='Peso (kg)')
        self.tabla_fardos.heading('hora', text='Hora')
        
        self.tabla_fardos.column('numero', width=80, anchor='center')
        self.tabla_fardos.column('peso', width=100, anchor='center')
        self.tabla_fardos.column('hora', width=120, anchor='center')
    
    def crear_calculos_rinde(self):
        """Crea la sección de cálculos y rinde"""
        shadow_frame, rinde_frame = EstilosModernos.crear_frame_con_sombra(self.panel_detalles)
        shadow_frame.pack(fill='x')
        
        contenido = tk.Frame(rinde_frame, bg=COLORES['fondo_panel'])
        contenido.pack(fill='x', padx=15, pady=15)
        
        tk.Label(contenido, text="Cálculo de Rinde",
                bg=COLORES['fondo_panel'], fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(anchor='w', pady=(0, 10))
        
        # Rinde calculado
        self.label_rinde = tk.Label(contenido, text="Rinde: -- %",
                                  bg=COLORES['fondo_panel'], fg=COLORES['exito'],
                                  font=FUENTES['extra_grande'])
        self.label_rinde.pack(anchor='w')
        
        # Desglose
        self.label_desglose = tk.Label(contenido, text="",
                                     bg=COLORES['fondo_panel'], fg=COLORES['texto_secundario'],
                                     font=FUENTES['pequena'], justify='left')
        self.label_desglose.pack(anchor='w', pady=(5, 0))
    
    def crear_barra_estado(self):
        """Crea la barra de estado"""
        self.barra_estado = tk.Frame(self.root, bg=COLORES['borde_principal'], height=40)
        self.barra_estado.grid(row=2, column=0, columnspan=2, sticky='ew')
        self.barra_estado.grid_propagate(False)
        
        # Estado de conexión
        self.indicador_conexion = EstilosModernos.crear_indicador_estado(
            self.barra_estado, "Base de datos: Conectada", COLORES['activo'])
        self.indicador_conexion.pack(side='left', padx=10, pady=8)
        
        # Ruta de la base de datos
        self.label_ruta_db = tk.Label(self.barra_estado, 
                                    text=f"DB: {self.bd.ruta_db}",
                                    bg=COLORES['borde_principal'],
                                    fg=COLORES['texto_secundario'],
                                    font=FUENTES['pequena'])
        self.label_ruta_db.pack(side='right', padx=10, pady=8)
    
    def mostrar_error_conexion(self):
        """Muestra error de conexión"""
        messagebox.showerror("Error de Conexión", 
                           f"No se pudo conectar a la base de datos:\n{self.bd.ruta_db}\n\n"
                           "Verifique que:\n"
                           "1. El archivo existe\n"
                           "2. Tiene permisos de lectura\n"
                           "3. La red está funcionando")
        
        # Actualizar indicador
        for widget in self.indicador_conexion.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.delete("all")
                widget.create_oval(2, 2, 10, 10, fill=COLORES['peligro'], outline=COLORES['peligro'])
            elif isinstance(widget, tk.Label):
                widget.configure(text="Base de datos: Error")
    
    def cargar_tickets(self):
        """Carga la lista de tickets"""
        try:
            # Obtener filtro
            filtro = self.entry_filtro.get().strip()
            
            # Cargar tickets
            tickets = self.bd.obtener_tickets(filtro_numero=filtro if filtro else None)
            
            # Limpiar tabla
            for item in self.tabla_tickets.get_children():
                self.tabla_tickets.delete(item)
            
            # Llenar tabla
            for ticket_data in tickets:
                numero, fecha_creacion, cantidad_fardos, peso_total, fecha_guardado, kg_bruto_romaneo, agregado, resto = ticket_data
                
                # Formatear fecha
                try:
                    fecha_dt = datetime.fromisoformat(fecha_creacion)
                    fecha_str = fecha_dt.strftime("%d/%m/%Y")
                except:
                    fecha_str = fecha_creacion
                
                # Calcular rinde
                rinde_str = "--"
                if kg_bruto_romaneo and kg_bruto_romaneo > 0:
                    tara_fardos = cantidad_fardos * 2.0
                    agregado = agregado or 0.0
                    resto = resto or 0.0
                    numerador = peso_total + resto - agregado - tara_fardos
                    rinde = (numerador / kg_bruto_romaneo) * 100
                    rinde_str = f"{rinde:.1f}%"
                
                self.tabla_tickets.insert('', 'end', values=(
                    numero,
                    fecha_str,
                    cantidad_fardos,
                    f"{peso_total:.2f} kg",
                    rinde_str
                ))
            
            # Actualizar contador
            self.label_total_tickets.configure(text=f"({len(tickets)} tickets)")
            
            # Actualizar estadísticas generales
            self.actualizar_estadisticas_generales()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar tickets: {e}")
    
    def actualizar_estadisticas_generales(self):
        """Actualiza las estadísticas generales"""
        try:
            stats = self.bd.obtener_estadisticas_generales()
            
            self.stats_labels['total_tickets'].configure(text=str(stats['total_tickets']))
            self.stats_labels['total_fardos'].configure(text=str(stats['total_fardos']))
            self.stats_labels['peso_total'].configure(text=f"{stats['peso_total']:.2f} kg")
            
        except Exception as e:
            print(f"Error al actualizar estadísticas: {e}")
    
    def filtrar_tickets(self, event=None):
        """Filtra los tickets según el texto ingresado"""
        # Recargar con filtro después de una pequeña pausa
        self.root.after(500, self.cargar_tickets)
    
    def seleccionar_ticket(self, event):
        """Maneja la selección de un ticket"""
        seleccion = self.tabla_tickets.selection()
        if not seleccion:
            self.limpiar_detalles()
            return
        
        item = seleccion[0]
        numero_ticket = self.tabla_tickets.item(item)['values'][0]
        
        # Cargar ticket completo
        self.ticket_seleccionado = self.bd.cargar_ticket_completo(numero_ticket)
        
        if self.ticket_seleccionado:
            self.mostrar_detalles_ticket()
            self.habilitar_botones()
        else:
            self.limpiar_detalles()
    
    def mostrar_detalles_ticket(self):
        """Muestra los detalles del ticket seleccionado"""
        if not self.ticket_seleccionado:
            return
        
        ticket = self.ticket_seleccionado
        
        # Información general
        self.info_labels['numero'].configure(text=ticket.numero)
        self.info_labels['fecha'].configure(text=ticket.fecha_creacion.strftime("%d/%m/%Y %H:%M"))
        self.info_labels['cantidad_fardos'].configure(text=str(ticket.obtener_cantidad_fardos()))
        self.info_labels['peso_total'].configure(text=f"{ticket.obtener_peso_total():.2f} kg")
        
        # Datos adicionales
        kg_bruto = ticket.kg_bruto_romaneo if ticket.kg_bruto_romaneo else "--"
        self.info_labels['kg_bruto_romaneo'].configure(text=f"{kg_bruto} kg" if kg_bruto != "--" else kg_bruto)
        self.info_labels['agregado'].configure(text=f"{ticket.agregado:.2f} kg")
        self.info_labels['resto'].configure(text=f"{ticket.resto:.2f} kg")
        
        # Tabla de fardos
        for item in self.tabla_fardos.get_children():
            self.tabla_fardos.delete(item)
        
        for fardo in ticket.fardos:
            self.tabla_fardos.insert('', 'end', values=(
                fardo.numero,
                f"{fardo.peso:.2f}",
                fardo.hora_pesaje.strftime("%H:%M:%S")
            ))
        
        # Calcular y mostrar rinde
        self.calcular_rinde()
    
    def calcular_rinde(self):
        """Calcula y muestra el rinde"""
        if not self.ticket_seleccionado:
            return
        
        ticket = self.ticket_seleccionado
        
        if ticket.kg_bruto_romaneo and ticket.kg_bruto_romaneo > 0:
            bruto_fardos = ticket.obtener_peso_total()
            cantidad_fardos = ticket.obtener_cantidad_fardos()
            tara_fardos = cantidad_fardos * 2.0
            agregado = ticket.agregado
            resto = ticket.resto
            
            numerador = bruto_fardos + resto - agregado - tara_fardos
            rinde = (numerador / ticket.kg_bruto_romaneo) * 100
            
            self.label_rinde.configure(text=f"Rinde: {rinde:.2f} %")
            
            desglose = (f"Cálculo: ({bruto_fardos:.2f} + {resto:.2f} - {agregado:.2f} - {tara_fardos:.2f}) / {ticket.kg_bruto_romaneo:.2f} × 100\n"
                       f"= {numerador:.2f} / {ticket.kg_bruto_romaneo:.2f} × 100 = {rinde:.2f}%")
            self.label_desglose.configure(text=desglose)
        else:
            self.label_rinde.configure(text="Rinde: -- %")
            self.label_desglose.configure(text="Kg Bruto Romaneo no disponible")
    
    def limpiar_detalles(self):
        """Limpia los detalles mostrados"""
        self.ticket_seleccionado = None
        
        # Limpiar información
        for label in self.info_labels.values():
            label.configure(text="--")
        
        # Limpiar tabla de fardos
        for item in self.tabla_fardos.get_children():
            self.tabla_fardos.delete(item)
        
        # Limpiar rinde
        self.label_rinde.configure(text="Rinde: -- %")
        self.label_desglose.configure(text="")
        
        self.deshabilitar_botones()
    
    def habilitar_botones(self):
        """Habilita los botones de acción"""
        self.btn_exportar_csv.configure(state='normal')
        self.btn_exportar_pdf.configure(state='normal')
        self.btn_imprimir.configure(state='normal')
        self.btn_detalle_completo.configure(state='normal')
    
    def deshabilitar_botones(self):
        """Deshabilita los botones de acción"""
        self.btn_exportar_csv.configure(state='disabled')
        self.btn_exportar_pdf.configure(state='disabled')
        self.btn_imprimir.configure(state='disabled')
        self.btn_detalle_completo.configure(state='disabled')
    
    def exportar_csv(self):
        """Exporta el ticket seleccionado a CSV"""
        if not self.ticket_seleccionado:
            return
        
        try:
            archivo = self.bd.exportador.exportar_ticket_csv(self.ticket_seleccionado)
            messagebox.showinfo("Éxito", f"Archivo CSV exportado:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar CSV: {e}")
    
    def exportar_pdf(self):
        """Exporta el ticket seleccionado a PDF"""
        if not self.ticket_seleccionado:
            return
        
        try:
            archivo = self.bd.exportador.exportar_ticket_pdf(self.ticket_seleccionado)
            messagebox.showinfo("Éxito", f"Archivo PDF exportado:\n{archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar PDF: {e}")
    
    def imprimir_ticket(self):
        """Imprime el ticket seleccionado"""
        if not self.ticket_seleccionado:
            return
        
        try:
            # Crear PDF temporal para imprimir
            archivo_pdf = self.bd.exportador.exportar_ticket_pdf(self.ticket_seleccionado)
            
            # Intentar abrir con el programa por defecto para imprimir
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                subprocess.run(['start', archivo_pdf], shell=True)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', archivo_pdf])
            else:  # Linux
                subprocess.run(['xdg-open', archivo_pdf])
            
            messagebox.showinfo("Imprimir", f"Se abrió el archivo para imprimir:\n{archivo_pdf}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al imprimir: {e}")
    
    def ver_detalle_completo(self, event=None):
        """Muestra una ventana con el detalle completo del ticket"""
        if not self.ticket_seleccionado:
            return
        
        # Crear ventana de detalle
        ventana_detalle = tk.Toplevel(self.root)
        ventana_detalle.title(f"Detalle Completo - Ticket {self.ticket_seleccionado.numero}")
        ventana_detalle.geometry("600x500")
        ventana_detalle.configure(bg=COLORES['fondo_principal'])
        ventana_detalle.transient(self.root)
        
        # Contenido scrollable
        canvas = tk.Canvas(ventana_detalle, bg=COLORES['fondo_principal'])
        scrollbar = ttk.Scrollbar(ventana_detalle, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORES['fondo_principal'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        
        canvas.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')
        
        # Mostrar información completa
        ticket = self.ticket_seleccionado
        
        # Título
        tk.Label(scrollable_frame, text=f"Ticket #{ticket.numero}",
                bg=COLORES['fondo_principal'], fg=COLORES['texto_principal'],
                font=FUENTES['extra_grande']).pack(pady=(0, 20))
        
        # Información detallada
        info_text = f"""
INFORMACIÓN GENERAL:
• Número: {ticket.numero}
• Fecha de creación: {ticket.fecha_creacion.strftime("%d/%m/%Y %H:%M:%S")}
• Cantidad de fardos: {ticket.obtener_cantidad_fardos()}
• Peso total fardos: {ticket.obtener_peso_total():.2f} kg

DATOS ADICIONALES:
• Kg Bruto Romaneo: {ticket.kg_bruto_romaneo if ticket.kg_bruto_romaneo else 'No especificado'} kg
• Agregado: {ticket.agregado:.2f} kg
• Resto: {ticket.resto:.2f} kg

CÁLCULOS:
• Tara total: {ticket.obtener_cantidad_fardos() * 2.0:.2f} kg
• Peso promedio por fardo: {ticket.obtener_peso_total() / ticket.obtener_cantidad_fardos() if ticket.obtener_cantidad_fardos() > 0 else 0:.2f} kg
"""
        
        # Calcular rinde si es posible
        if ticket.kg_bruto_romaneo and ticket.kg_bruto_romaneo > 0:
            bruto_fardos = ticket.obtener_peso_total()
            tara_fardos = ticket.obtener_cantidad_fardos() * 2.0
            numerador = bruto_fardos + ticket.resto - ticket.agregado - tara_fardos
            rinde = (numerador / ticket.kg_bruto_romaneo) * 100
            
            info_text += f"""
RINDE:
• Cálculo: ({bruto_fardos:.2f} + {ticket.resto:.2f} - {ticket.agregado:.2f} - {tara_fardos:.2f}) / {ticket.kg_bruto_romaneo:.2f} × 100
• Resultado: {rinde:.2f}%
"""
        
        # Observaciones
        if ticket.observaciones:
            info_text += f"\nOBSERVACIONES:\n{ticket.observaciones}"
        
        tk.Label(scrollable_frame, text=info_text,
                bg=COLORES['fondo_principal'], fg=COLORES['texto_principal'],
                font=FUENTES['normal'], justify='left').pack(pady=10)
        
        # Lista de fardos
        tk.Label(scrollable_frame, text="DETALLE DE FARDOS:",
                bg=COLORES['fondo_principal'], fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(pady=(20, 10))
        
        for fardo in ticket.fardos:
            fardo_text = f"Fardo #{fardo.numero}: {fardo.peso:.2f} kg - {fardo.hora_pesaje.strftime('%H:%M:%S')}"
            tk.Label(scrollable_frame, text=fardo_text,
                    bg=COLORES['fondo_principal'], fg=COLORES['texto_secundario'],
                    font=FUENTES['normal']).pack(anchor='w', padx=20)
        
        # Botón cerrar
        tk.Button(scrollable_frame, text="Cerrar", command=ventana_detalle.destroy,
                 bg=COLORES['primario'], fg=COLORES['texto_blanco'],
                 font=FUENTES['normal'], padx=20, pady=5).pack(pady=20)
    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        # Cargar datos iniciales
        self.cargar_tickets()
        
        # Iniciar loop principal
        self.root.mainloop()

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visor de Tickets - Sistema de Pesaje de Fardos')
    parser.add_argument('--db', type=str, help='Ruta a la base de datos')
    args = parser.parse_args()
    
    try:
        print("👁️ Iniciando Visor de Tickets...")
        app = VisorTickets(args.db)
        app.ejecutar()
    except Exception as e:
        print(f"❌ Error al iniciar aplicación: {e}")
        input("Presione Enter para salir...")

if __name__ == "__main__":
    main()
