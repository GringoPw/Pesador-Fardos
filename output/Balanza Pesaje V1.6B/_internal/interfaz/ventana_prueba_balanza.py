import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import serial.tools.list_ports
from interfaz.estilos import EstilosModernos, WidgetsPersonalizados
from config.configuracion import COLORES, FUENTES, config_manager, DIMENSIONES

class VentanaPruebaBalanza:
    """Ventana para probar la conexión con la balanza"""
    
    def __init__(self, parent, gestor):
        self.parent = parent
        self.gestor = gestor
        self.balanza = gestor.balanza
        self.ventana = None
        self.monitoreo_activo = False
        self.thread_monitoreo = None
        
        self.crear_ventana()
    
    def crear_ventana(self):
        """Crea la ventana de prueba de balanza"""
        self.ventana = tk.Toplevel(self.parent)
        self.ventana.title("Prueba de Balanza")
        self.ventana.geometry("800x600")
        self.ventana.resizable(True, True)
        self.ventana.configure(bg=COLORES['fondo_principal'])
        
        # Hacer modal
        self.ventana.transient(self.parent)
        self.ventana.grab_set()
        
        # Manejar cierre
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Centrar ventana
        self.ventana.update_idletasks()
        ancho = self.ventana.winfo_width()
        alto = self.ventana.winfo_height()
        x = (self.ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (alto // 2)
        self.ventana.geometry(f"+{x}+{y}")
        
        # Iniciar monitoreo
        self.iniciar_monitoreo()
    
    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # Frame principal con padding
        main_frame = tk.Frame(self.ventana, bg=COLORES['fondo_principal'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        titulo = tk.Label(main_frame, 
                         text="Prueba de Conexión con Balanza",
                         font=FUENTES['titulo'],
                         bg=COLORES['fondo_principal'],
                         fg=COLORES['texto_principal'])
        titulo.pack(pady=(0, 20))
        
        # Panel de configuración
        self.crear_panel_configuracion(main_frame)
        
        # Panel de monitoreo
        self.crear_panel_monitoreo(main_frame)
        
        # Panel de datos recibidos
        self.crear_panel_datos_recibidos(main_frame)
        
        # Botones inferiores
        self.crear_botones_inferiores(main_frame)
    
    def crear_panel_configuracion(self, parent):
        """Crea el panel de configuración de la balanza"""
        # Frame con borde y título
        frame = EstilosModernos.crear_panel_moderno(
            parent, "Configuración de Balanza")
        frame.pack(fill='x', pady=(0, 15))
        
        # Grid para los controles
        config_frame = tk.Frame(frame, bg=COLORES['fondo_panel'])
        config_frame.pack(fill='x', padx=15, pady=15)
        
        # Configurar grid
        config_frame.columnconfigure(0, weight=0)  # Etiqueta
        config_frame.columnconfigure(1, weight=1)  # Control
        config_frame.columnconfigure(2, weight=0)  # Etiqueta 2
        config_frame.columnconfigure(3, weight=1)  # Control 2
        
        # Fila 1: Puerto y Baudrate
        tk.Label(config_frame, text="Puerto:", 
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['normal']).grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)
        
        # Combobox para puertos
        self.combo_puertos = ttk.Combobox(config_frame, width=15, state='readonly')
        self.combo_puertos.grid(row=0, column=1, sticky='ew', padx=(0, 20), pady=5)
        
        tk.Label(config_frame, text="Baudrate:", 
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['normal']).grid(row=0, column=2, sticky='w', padx=(0, 10), pady=5)
        
        # Combobox para baudrate
        self.combo_baudrate = ttk.Combobox(config_frame, width=10, state='readonly',
                                         values=["1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200"])
        self.combo_baudrate.grid(row=0, column=3, sticky='ew', pady=5)
        
        # Fila 2: Protocolo y Timeout
        tk.Label(config_frame, text="Protocolo:", 
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['normal']).grid(row=1, column=0, sticky='w', padx=(0, 10), pady=5)
        
        # Combobox para protocolo
        self.combo_protocolo = ttk.Combobox(config_frame, width=15, state='readonly',
                                          values=["CONTINUO", "ESTANDAR", "TOLEDO", "AND", "OHAUS", 
                                                 "METTLER", "CAS", "DIBAL", "DIGI", "GAMA"])
        self.combo_protocolo.grid(row=1, column=1, sticky='ew', padx=(0, 20), pady=5)
        
        tk.Label(config_frame, text="Timeout:", 
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['normal']).grid(row=1, column=2, sticky='w', padx=(0, 10), pady=5)
        
        # Spinbox para timeout
        self.spin_timeout = ttk.Spinbox(config_frame, from_=0.1, to=10.0, increment=0.1, width=10)
        self.spin_timeout.grid(row=1, column=3, sticky='ew', pady=5)
        
        # Fila 3: DTR y RTS
        tk.Label(config_frame, text="Control de flujo:", 
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['normal']).grid(row=2, column=0, sticky='w', padx=(0, 10), pady=5)
        
        # Frame para checkboxes
        flow_frame = tk.Frame(config_frame, bg=COLORES['fondo_panel'])
        flow_frame.grid(row=2, column=1, columnspan=3, sticky='w', pady=5)
        
        # Variables para checkboxes
        self.var_dtr = tk.BooleanVar(value=True)
        self.var_rts = tk.BooleanVar(value=True)
        
        # Checkboxes
        self.check_dtr = ttk.Checkbutton(flow_frame, text="DTR", variable=self.var_dtr)
        self.check_dtr.pack(side='left', padx=(0, 20))
        
        self.check_rts = ttk.Checkbutton(flow_frame, text="RTS", variable=self.var_rts)
        self.check_rts.pack(side='left')
        
        # Botones de acción
        btn_frame = tk.Frame(frame, bg=COLORES['fondo_panel'])
        btn_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Botón para detectar puertos
        self.btn_detectar = WidgetsPersonalizados.crear_boton_moderno(
            btn_frame, "🔍 Detectar Puertos", self.detectar_puertos)
        self.btn_detectar.pack(side='left', padx=(0, 10))
        
        # Botón para aplicar configuración
        self.btn_aplicar = WidgetsPersonalizados.crear_boton_moderno(
            btn_frame, "✅ Aplicar Configuración", self.aplicar_configuracion,
            estilo='Exito.TButton')
        self.btn_aplicar.pack(side='left')
        
        # Cargar configuración actual
        self.cargar_configuracion_actual()
    
    def crear_panel_monitoreo(self, parent):
        """Crea el panel de monitoreo de peso"""
        # Frame con borde y título
        frame = EstilosModernos.crear_panel_moderno(
            parent, "Monitoreo de Peso")
        frame.pack(fill='x', pady=(0, 15))
        
        # Frame para contenido
        monitor_frame = tk.Frame(frame, bg=COLORES['fondo_panel'])
        monitor_frame.pack(fill='x', padx=15, pady=15)
        
        # Peso actual (grande)
        self.lbl_peso_titulo = tk.Label(monitor_frame, 
                                      text="Peso Actual:",
                                      font=FUENTES['subtitulo'],
                                      bg=COLORES['fondo_panel'],
                                      fg=COLORES['texto_principal'])
        self.lbl_peso_titulo.pack(pady=(0, 5))
        
        self.lbl_peso = tk.Label(monitor_frame, 
                               text="0.00 kg",
                               font=FUENTES['extra_grande'],
                               bg=COLORES['fondo_panel'],
                               fg=COLORES['primario'])
        self.lbl_peso.pack(pady=(0, 10))
        
        # Estado de conexión
        estado_frame = tk.Frame(monitor_frame, bg=COLORES['fondo_panel'])
        estado_frame.pack(fill='x')
        
        self.indicador_conexion = EstilosModernos.crear_indicador_estado(
            estado_frame, "Conexión: Desconectado", COLORES['inactivo'])
        self.indicador_conexion.pack(side='left', padx=(0, 15))
        
        self.lbl_ultimo_error = tk.Label(estado_frame, 
                                       text="",
                                       font=FUENTES['pequena'],
                                       bg=COLORES['fondo_panel'],
                                       fg=COLORES['peligro'])
        self.lbl_ultimo_error.pack(side='left')
    
    def crear_panel_datos_recibidos(self, parent):
        """Crea el panel de datos recibidos"""
        # Frame con borde y título
        frame = EstilosModernos.crear_panel_moderno(
            parent, "Datos Recibidos")
        frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Frame para contenido
        datos_frame = tk.Frame(frame, bg=COLORES['fondo_panel'])
        datos_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Texto con scroll
        self.txt_datos = tk.Text(datos_frame, 
                               font=FUENTES['monospace'],
                               bg=COLORES['fondo_entrada'],
                               fg=COLORES['texto_principal'],
                               height=10)
        self.txt_datos.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(datos_frame, command=self.txt_datos.yview)
        scrollbar.pack(side='right', fill='y')
        self.txt_datos.config(yscrollcommand=scrollbar.set)
        
        # Hacer el texto de solo lectura
        self.txt_datos.config(state='disabled')
    
    def crear_botones_inferiores(self, parent):
        """Crea los botones inferiores"""
        btn_frame = tk.Frame(parent, bg=COLORES['fondo_principal'])
        btn_frame.pack(fill='x')
        
        # Botón para limpiar datos
        self.btn_limpiar = WidgetsPersonalizados.crear_boton_moderno(
            btn_frame, "🧹 Limpiar Datos", self.limpiar_datos)
        self.btn_limpiar.pack(side='left', padx=(0, 10))
        
        # Botón para cerrar
        self.btn_cerrar = WidgetsPersonalizados.crear_boton_moderno(
            btn_frame, "✖️ Cerrar", self.cerrar_ventana)
        self.btn_cerrar.pack(side='right')
    
    def cargar_configuracion_actual(self):
        """Carga la configuración actual de la balanza"""
        # Cargar puertos disponibles
        self.detectar_puertos()
        
        # Cargar configuración actual
        estado = self.balanza.obtener_estado()
        
        # Seleccionar puerto actual
        if estado['puerto'] in self.combo_puertos['values']:
            self.combo_puertos.set(estado['puerto'])
        
        # Seleccionar baudrate actual
        self.combo_baudrate.set(str(estado['baudrate']))
        
        # Seleccionar protocolo actual
        if estado['protocolo'] in self.combo_protocolo['values']:
            self.combo_protocolo.set(estado['protocolo'])
        else:
            self.combo_protocolo.set("CONTINUO")
        
        # Configurar timeout
        self.spin_timeout.delete(0, 'end')
        self.spin_timeout.insert(0, str(self.balanza.timeout))
        
        # Configurar DTR y RTS
        self.var_dtr.set(estado['dtr'])
        self.var_rts.set(estado['rts'])
    
    def detectar_puertos(self):
        """Detecta los puertos disponibles"""
        puertos = self.balanza.obtener_puertos_disponibles()
        
        # Formatear puertos para mostrar
        puertos_mostrar = []
        for p in puertos:
            puertos_mostrar.append(p['puerto'])
        
        # Si no hay puertos, mostrar mensaje
        if not puertos_mostrar:
            puertos_mostrar = ["No hay puertos disponibles"]
        
        # Actualizar combobox
        self.combo_puertos['values'] = puertos_mostrar
        
        # Seleccionar el puerto actual si está disponible
        puerto_actual = self.balanza.puerto
        if puerto_actual in puertos_mostrar:
            self.combo_puertos.set(puerto_actual)
        elif puertos_mostrar:
            self.combo_puertos.set(puertos_mostrar[0])
    
    def aplicar_configuracion(self):
        """Aplica la configuración seleccionada"""
        try:
            # Obtener valores
            puerto = self.combo_puertos.get()
            baudrate = int(self.combo_baudrate.get())
            protocolo = self.combo_protocolo.get()
            timeout = float(self.spin_timeout.get())
            dtr = self.var_dtr.get()
            rts = self.var_rts.get()
            
            # Validar puerto
            if puerto == "No hay puertos disponibles":
                messagebox.showerror("Error", "No hay puertos disponibles")
                return
            
            # Aplicar configuración
            if self.balanza.cambiar_configuracion(
                puerto=puerto, baudrate=baudrate, protocolo=protocolo,
                timeout=timeout, activar_dtr=dtr, activar_rts=rts):
                
                messagebox.showinfo("Éxito", "Configuración aplicada correctamente")
                
                # Actualizar estado
                self.actualizar_estado_conexion()
            else:
                messagebox.showerror("Error", "No se pudo aplicar la configuración")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar configuración: {str(e)}")
    
    def iniciar_monitoreo(self):
        """Inicia el monitoreo de la balanza"""
        self.monitoreo_activo = True
        self.thread_monitoreo = threading.Thread(target=self.monitorear_balanza)
        self.thread_monitoreo.daemon = True
        self.thread_monitoreo.start()
    
    def monitorear_balanza(self):
        """Monitorea la balanza en un hilo separado"""
        while self.monitoreo_activo:
            try:
                # Obtener peso
                peso = self.balanza.obtener_peso()
                
                # Actualizar interfaz
                self.ventana.after(0, self.actualizar_peso, peso)
                
                # Actualizar estado de conexión
                self.ventana.after(0, self.actualizar_estado_conexion)
                
                # Actualizar datos recibidos
                datos = self.balanza.obtener_datos_recibidos()
                self.ventana.after(0, self.actualizar_datos_recibidos, datos)
                
            except Exception as e:
                print(f"Error en monitoreo: {e}")
            
            # Esperar un poco
            time.sleep(0.5)
    
    def actualizar_peso(self, peso):
        """Actualiza el peso mostrado"""
        self.lbl_peso.config(text=f"{peso:.2f} kg")
    
    def actualizar_estado_conexion(self):
        """Actualiza el estado de la conexión"""
        estado = self.balanza.obtener_estado()
        
        if estado['conectada']:
            # Actualizar indicador
            for widget in self.indicador_conexion.winfo_children():
                if isinstance(widget, tk.Canvas):
                    widget.delete("all")
                    widget.create_oval(2, 2, 10, 10, fill=COLORES['activo'], outline=COLORES['activo'])
                elif isinstance(widget, tk.Label):
                    widget.configure(text=f"Conexión: {estado['puerto']} @ {estado['baudrate']} bps")
        else:
            # Actualizar indicador
            for widget in self.indicador_conexion.winfo_children():
                if isinstance(widget, tk.Canvas):
                    widget.delete("all")
                    widget.create_oval(2, 2, 10, 10, fill=COLORES['peligro'], outline=COLORES['peligro'])
                elif isinstance(widget, tk.Label):
                    widget.configure(text="Conexión: Desconectado")
        
        # Actualizar error
        if estado['ultimo_error']:
            self.lbl_ultimo_error.config(text=f"Error: {estado['ultimo_error']}")
        else:
            self.lbl_ultimo_error.config(text="")
    
    def actualizar_datos_recibidos(self, datos):
        """Actualiza los datos recibidos en el texto"""
        # Habilitar edición
        self.txt_datos.config(state='normal')
        
        # Limpiar texto
        self.txt_datos.delete(1.0, tk.END)
        
        # Agregar datos
        for dato in datos:
            self.txt_datos.insert(tk.END, dato + "\n")
        
        # Scroll al final
        self.txt_datos.see(tk.END)
        
        # Deshabilitar edición
        self.txt_datos.config(state='disabled')
    
    def limpiar_datos(self):
        """Limpia los datos recibidos"""
        self.balanza.limpiar_datos_recibidos()
        self.txt_datos.config(state='normal')
        self.txt_datos.delete(1.0, tk.END)
        self.txt_datos.config(state='disabled')
    
    def cerrar_ventana(self):
        """Cierra la ventana"""
        # Detener monitoreo
        self.monitoreo_activo = False
        if self.thread_monitoreo:
            self.thread_monitoreo.join(timeout=1.0)
        
        # Cerrar ventana
        self.ventana.destroy()
