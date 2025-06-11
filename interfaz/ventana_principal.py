import tkinter as tk
from tkinter import ttk, messagebox
from interfaz.estilos import EstilosModernos, WidgetsPersonalizados
from config.configuracion import COLORES, FUENTES, DIMENSIONES, MENSAJES, BALANZA_CONFIG
from funciones.gestor_fardos import GestorFardos
from funciones.base_datos import BaseDatos
from funciones.conexion_internet import VerificadorInternet

class VentanaPrincipal:
    def __init__(self):
        self.root = tk.Tk()
        self.gestor = GestorFardos()
        self.bd = BaseDatos()
        self.verificador_internet = VerificadorInternet(self.actualizar_estado_internet)
        self.ticket_actual = None
        self.ticket_guardado = False
        
        # Inicializar atributos importantes
        self.panel_fardos = None
        self.panel_estadisticas = None
        self.label_estado = None
        self.indicador_internet = None
        
        self.configurar_ventana()
        self.configurar_estilos()
        self.crear_interfaz()
        self.configurar_eventos()
        
        # Iniciar verificación de internet
        self.verificador_internet.iniciar_verificacion_continua(30)
        
    def configurar_ventana(self):
        """Configura la ventana principal"""
        self.root.title("Sistema de Pesaje de Fardos - v2.0")
        
        # Hacer la ventana adaptable según la resolución
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        if screen_width >= 1920:  # Full HD o mayor
            window_width, window_height = 1400, 800
        elif screen_width >= 1366:  # HD
            window_width, window_height = 1200, 700
        else:  # Pantallas menores
            window_width, window_height = 1000, 600
        
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.configure(bg=COLORES['fondo_principal'])
        self.root.resizable(True, True)
        
        # Configurar tamaño mínimo
        self.root.minsize(1000, 600)
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Configurar grid weights para responsive
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=2)  # Panel fardos más ancho
        self.root.grid_columnconfigure(1, weight=1)  # Panel estadísticas más estrecho
        
        # Icono (opcional)
        try:
            self.root.iconbitmap('icono.ico')
        except:
            pass
        
        # Manejar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
    
    def configurar_estilos(self):
        """Configura los estilos de la aplicación"""
        EstilosModernos.configurar_estilos()
    
    def crear_interfaz(self):
        """Crea la interfaz principal"""
        # === BARRA DE ESTADO (crear primero para que esté disponible) ===
        self.crear_barra_estado()
        
        # === BARRA SUPERIOR ===
        self.crear_barra_superior()
        
        # === ÁREA PRINCIPAL ===
        self.crear_area_principal()
    
    def crear_barra_superior(self):
        """Crea la barra superior con título y controles principales"""
        # Frame principal de la barra
        barra_frame = tk.Frame(self.root, bg=COLORES['primario'], height=80)
        barra_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=0, pady=0)
        barra_frame.grid_propagate(False)
        
        # Contenido de la barra
        contenido_frame = tk.Frame(barra_frame, bg=COLORES['primario'])
        contenido_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Título principal
        titulo_label = tk.Label(contenido_frame, 
                               text="🏭 Sistema de Pesaje de Fardos",
                               bg=COLORES['primario'],
                               fg=COLORES['texto_blanco'],
                               font=FUENTES['extra_grande'])
        titulo_label.pack(side='left')
        
        # Frame para controles del ticket
        ticket_frame = tk.Frame(contenido_frame, bg=COLORES['primario'])
        ticket_frame.pack(side='right')
        
        # Botón historial
        self.btn_historial = WidgetsPersonalizados.crear_boton_moderno(
            ticket_frame, "📋 Historial", self.abrir_historial, 'Moderno.TButton')
        self.btn_historial.pack(side='left', padx=(0, 15))
        
        # Label y entrada para número de ticket
        tk.Label(ticket_frame, text="N° Ticket:",
                bg=COLORES['primario'],
                fg=COLORES['texto_blanco'],
                font=FUENTES['normal']).pack(side='left', padx=(0, 10))
        
        self.entry_ticket = WidgetsPersonalizados.crear_entrada_moderna(
            ticket_frame, width=15, font=FUENTES['grande'])
        self.entry_ticket.pack(side='left', padx=(0, 10))
        
        # Botón crear ticket
        self.btn_crear_ticket = WidgetsPersonalizados.crear_boton_moderno(
            ticket_frame, "Crear Ticket", self.crear_ticket, 'Exito.TButton')
        self.btn_crear_ticket.pack(side='left')
    
    def crear_area_principal(self):
        """Crea el área principal con layout fijo sin barras divisorias"""
        # === PANEL IZQUIERDO - FARDOS (2/3 del espacio) ===
        panel_fardos_frame = tk.Frame(self.root, bg=COLORES['fondo_principal'])
        panel_fardos_frame.grid(row=1, column=0, sticky='nsew', padx=(15, 7), pady=15)
        
        # === PANEL DERECHO - ESTADÍSTICAS (1/3 del espacio) ===
        # Crear un canvas con scrollbar para el panel de estadísticas
        stats_container = tk.Frame(self.root, bg=COLORES['fondo_principal'])
        stats_container.grid(row=1, column=1, sticky='nsew', padx=(7, 15), pady=15)
        
        # Canvas para permitir scroll
        canvas = tk.Canvas(stats_container, bg=COLORES['fondo_principal'], 
                          highlightthickness=0)
        canvas.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(stats_container, orient='vertical', 
                                 command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        
        # Configurar canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame dentro del canvas para el contenido
        panel_stats_frame = tk.Frame(canvas, bg=COLORES['fondo_principal'])
        canvas_window = canvas.create_window((0, 0), window=panel_stats_frame, anchor='nw')
        
        # Función para actualizar el scroll region
        def configurar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            # Ajustar el ancho del frame interno al canvas
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', configurar_scroll)
        panel_stats_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        
        # Importar aquí para evitar importaciones circulares
        from interfaz.panel_fardos import PanelFardos
        from interfaz.panel_estadisticas import PanelEstadisticas
        
        # Inicializar los paneles
        self.panel_fardos = PanelFardos(panel_fardos_frame, self.gestor, self)
        self.panel_estadisticas = PanelEstadisticas(panel_stats_frame, self.gestor)
    
    def crear_barra_estado(self):
        """Crea la barra de estado en la parte inferior"""
        self.barra_estado = tk.Frame(self.root, bg=COLORES['borde_principal'], height=50)
        self.barra_estado.grid(row=2, column=0, columnspan=2, sticky='ew')
        self.barra_estado.grid_propagate(False)
        
        # Estado de la balanza - MEJORADO para mostrar estado real
        self.actualizar_indicador_balanza()
        
        # Estado de internet
        self.indicador_internet = EstilosModernos.crear_indicador_estado(
            self.barra_estado, "Internet: Verificando...", COLORES['inactivo'])
        self.indicador_internet.pack(side='left', padx=10, pady=8)
        
        # Botón guardar
        self.btn_guardar = WidgetsPersonalizados.crear_boton_moderno(
            self.barra_estado, "💾 Guardar", self.guardar_ticket,
            'BarraEstado.TButton', state='disabled')
        self.btn_guardar.pack(side='left', padx=10, pady=8)
        
        # Botón prueba balanza
        self.btn_prueba_balanza = WidgetsPersonalizados.crear_boton_moderno(
            self.barra_estado, "⚖️ Probar Balanza", self.abrir_prueba_balanza,
            'BarraEstado.TButton')
        self.btn_prueba_balanza.pack(side='left', padx=10, pady=8)
        
        # Botón acerca de
        self.btn_acerca_de = WidgetsPersonalizados.crear_boton_moderno(
            self.barra_estado, "📞 Contacto", self.abrir_acerca_de,
            'BarraEstado.TButton')
        self.btn_acerca_de.pack(side='left', padx=10, pady=8)
        
        # Estado del sistema
        self.label_estado = tk.Label(self.barra_estado, 
                                text="Sistema listo",
                                bg=COLORES['borde_principal'],
                                fg=COLORES['texto_secundario'],
                                font=FUENTES['pequena'])
        self.label_estado.pack(side='right', padx=10, pady=8)
    
    def actualizar_indicador_balanza(self):
        """Actualiza el indicador de estado de la balanza"""
        try:
            estado = self.gestor.balanza.obtener_estado()
            
            if estado['conectada']:
                texto = f"Balanza: {estado['puerto']} OK"
                color = COLORES['activo']
            else:
                texto = f"Balanza: {estado['puerto']} Desconectada"
                color = COLORES['peligro']
            
            # Si ya existe el indicador, actualizarlo
            if hasattr(self, 'indicador_balanza'):
                for widget in self.indicador_balanza.winfo_children():
                    if isinstance(widget, tk.Canvas):
                        widget.delete("all")
                        widget.create_oval(2, 2, 10, 10, fill=color, outline=color)
                    elif isinstance(widget, tk.Label):
                        widget.configure(text=texto)
            else:
                # Crear indicador por primera vez
                self.indicador_balanza = EstilosModernos.crear_indicador_estado(
                    self.barra_estado, texto, color)
                self.indicador_balanza.pack(side='left', padx=10, pady=8)
                
        except Exception as e:
            print(f"Error al actualizar indicador balanza: {e}")
            # Crear indicador de error
            if not hasattr(self, 'indicador_balanza'):
                self.indicador_balanza = EstilosModernos.crear_indicador_estado(
                    self.barra_estado, "Balanza: Error", COLORES['peligro'])
                self.indicador_balanza.pack(side='left', padx=10, pady=8)
        
        # Programar próxima actualización
        self.root.after(5000, self.actualizar_indicador_balanza)  # Cada 5 segundos
    
    def configurar_eventos(self):
        """Configura los eventos de teclado"""
        self.root.bind('<Return>', self.manejar_enter)
        self.root.bind('<Control-s>', lambda e: self.guardar_ticket())
        self.root.bind('<Control-h>', lambda e: self.abrir_historial())
        self.root.bind('<F1>', lambda e: self.abrir_acerca_de())
        self.root.bind('<F2>', lambda e: self.abrir_prueba_balanza())
        self.entry_ticket.bind('<Return>', lambda e: self.crear_ticket())
        self.entry_ticket.focus()
    
    def abrir_prueba_balanza(self):
        """Abre la ventana de prueba de balanza"""
        from interfaz.ventana_prueba_balanza import VentanaPruebaBalanza
        VentanaPruebaBalanza(self.root, self.gestor)
    
    def abrir_acerca_de(self):
        """Abre la ventana de información de contacto"""
        from interfaz.ventana_acerca_de import VentanaAcercaDe
        VentanaAcercaDe(self.root)
    
    def actualizar_estado_internet(self, conectado: bool):
        """Actualiza el estado de la conexión a internet"""
        if self.indicador_internet:
            if conectado:
                # Actualizar indicador
                for widget in self.indicador_internet.winfo_children():
                    if isinstance(widget, tk.Canvas):
                        widget.delete("all")
                        widget.create_oval(2, 2, 10, 10, fill=COLORES['activo'], outline=COLORES['activo'])
                    elif isinstance(widget, tk.Label):
                        widget.configure(text="Internet: Online")
            else:
                # Actualizar indicador
                for widget in self.indicador_internet.winfo_children():
                    if isinstance(widget, tk.Canvas):
                        widget.delete("all")
                        widget.create_oval(2, 2, 10, 10, fill=COLORES['peligro'], outline=COLORES['peligro'])
                    elif isinstance(widget, tk.Label):
                        widget.configure(text="Internet: Offline")
    
    def manejar_enter(self, event):
        """Maneja la tecla Enter según el contexto"""
        widget_actual = self.root.focus_get()
        
        if widget_actual == self.entry_ticket:
            self.crear_ticket()
        elif self.panel_fardos and self.ticket_actual:
            self.panel_fardos.procesar_fardo()
    
    def crear_ticket(self):
        """Crea un nuevo ticket"""
        numero_ticket = self.entry_ticket.get().strip()
        
        if not numero_ticket:
            messagebox.showwarning("Advertencia", "Ingrese un número de ticket")
            self.entry_ticket.focus()
            return
        
        try:
            self.ticket_actual = self.gestor.crear_ticket(numero_ticket)
            self.ticket_guardado = False
            
            # Verificar que los paneles estén inicializados
            if self.panel_fardos:
                self.panel_fardos.activar_modo_pesaje()
            
            if self.panel_estadisticas:
                self.panel_estadisticas.actualizar_datos(self.ticket_actual)
            
            if self.label_estado:
                self.actualizar_estado(MENSAJES['ticket_creado'])
            
            # Habilitar botón guardar
            self.btn_guardar.configure(state='normal')
            
            # Deshabilitar entrada de ticket
            self.entry_ticket.configure(state='disabled')
            self.btn_crear_ticket.configure(state='disabled')
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def guardar_ticket(self):
        """Guarda el ticket actual en la base de datos"""
        if not self.ticket_actual:
            messagebox.showwarning("Advertencia", "No hay ticket para guardar")
            return
        
        if len(self.ticket_actual.fardos) == 0:
            if not messagebox.askyesno("Confirmar", "El ticket no tiene fardos. ¿Desea guardarlo de todos modos?"):
                return
        
        try:
            # Obtener datos adicionales del panel de estadísticas
            datos_adicionales = None
            if self.panel_estadisticas:
                datos_adicionales = self.panel_estadisticas.obtener_datos_adicionales()
            
            # Guardar en base de datos
            if self.bd.guardar_ticket(self.ticket_actual, datos_adicionales):
                self.ticket_guardado = True
                messagebox.showinfo("Éxito", f"Ticket {self.ticket_actual.numero} guardado correctamente")
                self.actualizar_estado("Ticket guardado en base de datos")
                
                # Cambiar color del botón para indicar que está guardado
                self.btn_guardar.configure(text="✅ Guardado")
                self.root.after(2000, lambda: self.btn_guardar.configure(text="💾 Guardar"))
            else:
                messagebox.showerror("Error", "No se pudo guardar el ticket")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar ticket: {str(e)}")
    
    def abrir_historial(self):
        """Abre la ventana de historial"""
        from interfaz.ventana_historial import VentanaHistorial
        VentanaHistorial(self.root, self.gestor, self.cargar_ticket_desde_historial)
    
    def cargar_ticket_desde_historial(self, numero_ticket: str):
        """Carga un ticket desde el historial"""
        try:
            # Verificar si hay un ticket actual sin guardar
            if self.ticket_actual and not self.ticket_guardado:
                if not messagebox.askyesno("Confirmar", 
                                         "Hay un ticket sin guardar. ¿Desea continuar sin guardarlo?"):
                    return
            
            # Cargar ticket desde base de datos
            ticket_cargado = self.bd.cargar_ticket(numero_ticket)
            if not ticket_cargado:
                messagebox.showerror("Error", f"No se pudo cargar el ticket {numero_ticket}")
                return
            
            # Configurar ticket actual
            self.ticket_actual = ticket_cargado
            self.ticket_guardado = True
            
            # Actualizar interfaz
            self.entry_ticket.configure(state='normal')
            self.entry_ticket.delete(0, tk.END)
            self.entry_ticket.insert(0, ticket_cargado.numero)
            self.entry_ticket.configure(state='disabled')
            self.btn_crear_ticket.configure(state='disabled')
            self.btn_guardar.configure(state='normal', text="💾 Actualizar")
            
            # Activar modo pesaje y cargar datos
            if self.panel_fardos:
                self.panel_fardos.activar_modo_pesaje()
                self.panel_fardos.cargar_fardos_desde_ticket(ticket_cargado)
            
            if self.panel_estadisticas:
                self.panel_estadisticas.actualizar_datos(ticket_cargado)
                self.panel_estadisticas.cargar_datos_adicionales(ticket_cargado)
            
            self.actualizar_estado(f"Ticket {numero_ticket} cargado desde base de datos")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar ticket: {str(e)}")
    
    def reiniciar_ticket(self):
        """Reinicia para crear un nuevo ticket"""
        # Verificar si hay cambios sin guardar
        if self.ticket_actual and not self.ticket_guardado:
            if not messagebox.askyesno("Confirmar", 
                                     "Hay cambios sin guardar. ¿Desea continuar sin guardarlos?"):
                return
        
        self.ticket_actual = None
        self.ticket_guardado = False
        self.entry_ticket.configure(state='normal')
        self.btn_crear_ticket.configure(state='normal')
        self.btn_guardar.configure(state='disabled', text="💾 Guardar")
        self.entry_ticket.delete(0, tk.END)
        self.entry_ticket.focus()
        
        if self.panel_fardos:
            self.panel_fardos.desactivar_modo_pesaje()
        
        if self.panel_estadisticas:
            self.panel_estadisticas.limpiar_datos()
        
        self.actualizar_estado("Sistema listo")
    
    def actualizar_estado(self, mensaje):
        """Actualiza el mensaje de estado"""
        if self.label_estado:
            self.label_estado.configure(text=mensaje)
            self.root.after(3000, lambda: self.label_estado.configure(text="Sistema listo"))
    
    def cerrar_aplicacion(self):
        """Cierra la aplicación"""
        # Verificar si hay cambios sin guardar
        if self.ticket_actual and not self.ticket_guardado:
            respuesta = messagebox.askyesnocancel("Confirmar Cierre", 
                                                "Hay cambios sin guardar. ¿Desea guardar antes de salir?")
            if respuesta is None:  # Cancelar
                return
            elif respuesta:  # Sí, guardar
                self.guardar_ticket()
        
        # Detener verificación de internet
        self.verificador_internet.detener_verificacion()
        
        # Cerrar conexiones
        self.gestor.cerrar()
        
        # Cerrar ventana
        self.root.destroy()
    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = VentanaPrincipal()
    app.ejecutar()
