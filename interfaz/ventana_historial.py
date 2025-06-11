import tkinter as tk
from tkinter import ttk, messagebox
from interfaz.estilos import EstilosModernos, WidgetsPersonalizados
from config.configuracion import COLORES, FUENTES, DIMENSIONES
from funciones.base_datos import BaseDatos
from datetime import datetime

class VentanaHistorial:
    """Ventana para mostrar el historial de tickets"""
    
    def __init__(self, parent, gestor, callback_cargar_ticket=None):
        self.parent = parent
        self.gestor = gestor
        self.callback_cargar_ticket = callback_cargar_ticket
        self.bd = BaseDatos()
        
        self.ventana = tk.Toplevel(parent)
        self.configurar_ventana()
        self.crear_interfaz()
        self.cargar_historial()
    
    def configurar_ventana(self):
        """Configura la ventana de historial"""
        self.ventana.title("Historial de Tickets")
        self.ventana.geometry("900x600")
        self.ventana.configure(bg=COLORES['fondo_principal'])
        self.ventana.resizable(True, True)
        self.ventana.transient(self.parent)
        self.ventana.grab_set()
        
        # Centrar ventana
        self.ventana.update_idletasks()
        x = (self.ventana.winfo_screenwidth() // 2) - 450
        y = (self.ventana.winfo_screenheight() // 2) - 300
        self.ventana.geometry(f"+{x}+{y}")
    
    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # === TÍTULO ===
        titulo_frame = tk.Frame(self.ventana, bg=COLORES['primario'], height=60)
        titulo_frame.pack(fill='x')
        titulo_frame.pack_propagate(False)
        
        tk.Label(titulo_frame, text="📋 Historial de Tickets",
                bg=COLORES['primario'],
                fg=COLORES['texto_blanco'],
                font=FUENTES['titulo']).pack(expand=True)
        
        # === ESTADÍSTICAS GENERALES ===
        self.crear_panel_estadisticas()
        
        # === TABLA DE HISTORIAL ===
        self.crear_tabla_historial()
        
        # === BOTONES ===
        self.crear_botones()
    
    def crear_panel_estadisticas(self):
        """Crea el panel de estadísticas generales"""
        stats_frame = tk.Frame(self.ventana, bg=COLORES['fondo_principal'])
        stats_frame.pack(fill='x', padx=15, pady=10)
        
        # Obtener estadísticas
        stats = self.bd.obtener_estadisticas_generales()
        
        # Crear tarjetas de estadísticas
        tarjetas_frame = tk.Frame(stats_frame, bg=COLORES['fondo_principal'])
        tarjetas_frame.pack(fill='x')
        
        # Configurar grid
        for i in range(3):
            tarjetas_frame.grid_columnconfigure(i, weight=1)
        
        # Total tickets
        self.crear_tarjeta_stat(tarjetas_frame, "Total Tickets", 
                               stats['total_tickets'], 0, 0)
        
        # Total fardos
        self.crear_tarjeta_stat(tarjetas_frame, "Total Fardos", 
                               stats['total_fardos'], 0, 1)
        
        # Peso total
        self.crear_tarjeta_stat(tarjetas_frame, "Peso Total", 
                               f"{stats['peso_total']:.2f} kg", 0, 2)
    
    def crear_tarjeta_stat(self, parent, titulo, valor, row, col):
        """Crea una tarjeta de estadística"""
        shadow_frame, main_frame = EstilosModernos.crear_frame_con_sombra(parent)
        shadow_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        content = tk.Frame(main_frame, bg=COLORES['fondo_panel'])
        content.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(content, text=titulo,
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_secundario'],
                font=FUENTES['normal']).pack()
        
        tk.Label(content, text=str(valor),
                bg=COLORES['fondo_panel'],
                fg=COLORES['primario'],
                font=FUENTES['grande']).pack()
    
    def crear_tabla_historial(self):
        """Crea la tabla de historial"""
        # Frame con sombra
        shadow_frame, tabla_frame = EstilosModernos.crear_frame_con_sombra(self.ventana)
        shadow_frame.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Título
        titulo_frame = tk.Frame(tabla_frame, bg=COLORES['fondo_panel'])
        titulo_frame.pack(fill='x', padx=15, pady=(15, 10))
        
        tk.Label(titulo_frame, text="Tickets Guardados",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(side='left')
        
        # Botón refrescar
        btn_refrescar = WidgetsPersonalizados.crear_boton_moderno(
            titulo_frame, "🔄 Refrescar", self.cargar_historial, 'Moderno.TButton')
        btn_refrescar.pack(side='right')
        
        # Contenedor tabla
        tabla_container = tk.Frame(tabla_frame, bg=COLORES['fondo_panel'])
        tabla_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Crear tabla
        columnas = ('numero', 'fecha', 'fardos', 'peso', 'guardado')
        self.tabla_frame, self.tabla = WidgetsPersonalizados.crear_tabla_moderna(
            tabla_container, columnas)
        self.tabla_frame.pack(fill='both', expand=True)
        
        # Configurar columnas
        self.tabla.heading('numero', text='N° Ticket')
        self.tabla.heading('fecha', text='Fecha Creación')
        self.tabla.heading('fardos', text='Fardos')
        self.tabla.heading('peso', text='Peso Total')
        self.tabla.heading('guardado', text='Guardado')
        
        self.tabla.column('numero', width=100, anchor='center')
        self.tabla.column('fecha', width=150, anchor='center')
        self.tabla.column('fardos', width=80, anchor='center')
        self.tabla.column('peso', width=120, anchor='center')
        self.tabla.column('guardado', width=150, anchor='center')
        
        # Eventos
        self.tabla.bind('<Double-1>', self.cargar_ticket_seleccionado)
        self.tabla.bind('<Button-3>', self.mostrar_menu_contextual)
    
    def crear_botones(self):
        """Crea los botones de acción"""
        botones_frame = tk.Frame(self.ventana, bg=COLORES['fondo_principal'])
        botones_frame.pack(fill='x', padx=15, pady=10)
        
        # Botón cargar
        self.btn_cargar = WidgetsPersonalizados.crear_boton_moderno(
            botones_frame, "📂 Cargar Ticket", self.cargar_ticket_seleccionado,
            'Exito.TButton', state='disabled')
        self.btn_cargar.pack(side='left', padx=(0, 10))
        
        # Botón eliminar
        self.btn_eliminar = WidgetsPersonalizados.crear_boton_moderno(
            botones_frame, "🗑️ Eliminar", self.eliminar_ticket_seleccionado,
            'Peligro.TButton', state='disabled')
        self.btn_eliminar.pack(side='left')
        
        # Botón cerrar
        btn_cerrar = WidgetsPersonalizados.crear_boton_moderno(
            botones_frame, "❌ Cerrar", self.cerrar_ventana)
        btn_cerrar.pack(side='right')
        
        # Evento de selección
        self.tabla.bind('<<TreeviewSelect>>', self.on_seleccionar_ticket)
    
    def cargar_historial(self):
        """Carga el historial de tickets"""
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Obtener datos
        historial = self.bd.obtener_historial_tickets()
        
        for ticket_data in historial:
            numero, fecha_creacion, cantidad_fardos, peso_total, fecha_guardado = ticket_data
            
            # Formatear fechas
            try:
                fecha_creacion_dt = datetime.fromisoformat(fecha_creacion)
                fecha_creacion_str = fecha_creacion_dt.strftime("%d/%m/%Y %H:%M")
            except:
                fecha_creacion_str = fecha_creacion
            
            try:
                fecha_guardado_dt = datetime.fromisoformat(fecha_guardado)
                fecha_guardado_str = fecha_guardado_dt.strftime("%d/%m/%Y %H:%M")
            except:
                fecha_guardado_str = fecha_guardado
            
            self.tabla.insert('', 'end', values=(
                numero,
                fecha_creacion_str,
                cantidad_fardos,
                f"{peso_total:.2f} kg",
                fecha_guardado_str
            ))
    
    def on_seleccionar_ticket(self, event):
        """Maneja la selección de un ticket"""
        seleccion = self.tabla.selection()
        if seleccion:
            self.btn_cargar.configure(state='normal')
            self.btn_eliminar.configure(state='normal')
        else:
            self.btn_cargar.configure(state='disabled')
            self.btn_eliminar.configure(state='disabled')
    
    def cargar_ticket_seleccionado(self, event=None):
        """Carga el ticket seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un ticket para cargar")
            return
        
        item = seleccion[0]
        numero_ticket = self.tabla.item(item)['values'][0]
        
        if self.callback_cargar_ticket:
            self.callback_cargar_ticket(numero_ticket)
            self.cerrar_ventana()
    
    def eliminar_ticket_seleccionado(self):
        """Elimina el ticket seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un ticket para eliminar")
            return
        
        item = seleccion[0]
        numero_ticket = self.tabla.item(item)['values'][0]
        
        if messagebox.askyesno("Confirmar Eliminación", 
                              f"¿Está seguro de eliminar el ticket {numero_ticket}?\n"
                              "Esta acción no se puede deshacer."):
            if self.bd.eliminar_ticket(numero_ticket):
                messagebox.showinfo("Éxito", "Ticket eliminado correctamente")
                self.cargar_historial()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el ticket")
    
    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual"""
        menu = tk.Menu(self.ventana, tearoff=0)
        
        seleccion = self.tabla.selection()
        if seleccion:
            menu.add_command(label="📂 Cargar Ticket", command=self.cargar_ticket_seleccionado)
            menu.add_command(label="🗑️ Eliminar", command=self.eliminar_ticket_seleccionado)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def cerrar_ventana(self):
        """Cierra la ventana"""
        self.ventana.destroy()
