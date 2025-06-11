import tkinter as tk
from tkinter import ttk
from interfaz.estilos import EstilosModernos, WidgetsPersonalizados
from config.configuracion import COLORES, FUENTES, DIMENSIONES

class PanelEstadisticas:
    def __init__(self, parent, gestor):
        self.parent = parent
        self.gestor = gestor
        self.ticket_actual = None
        
        # Variables para datos adicionales
        self.entry_kg_bruto_romaneo = None
        self.entry_agregado = None
        self.entry_resto = None
        self.text_observaciones = None
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz del panel de estadísticas"""
        # === TÍTULO DEL PANEL ===
        titulo_frame = tk.Frame(self.parent, bg=COLORES['fondo_principal'])
        titulo_frame.pack(fill='x', pady=(0, 10))
        
        titulo_label = tk.Label(titulo_frame, text="📊 Estadísticas del Ticket",
                              bg=COLORES['fondo_principal'],
                              fg=COLORES['texto_principal'],
                              font=FUENTES['titulo'])
        titulo_label.pack(anchor='w')
        
        # === ESTADÍSTICAS PRINCIPALES ===
        self.crear_estadisticas_principales()
        
        # === DATOS ADICIONALES ===
        self.crear_datos_adicionales()
        
        # === CÁLCULO DE RINDE ===
        self.crear_calculo_rinde()
        
        # === OBSERVACIONES ===
        self.crear_observaciones()
    
    def crear_estadisticas_principales(self):
        """Crea las estadísticas principales"""
        # Frame con sombra
        shadow_frame, stats_frame = EstilosModernos.crear_frame_con_sombra(self.parent)
        shadow_frame.pack(fill='x', pady=(0, 10))
        
        # Contenido
        contenido = tk.Frame(stats_frame, bg=COLORES['fondo_panel'])
        contenido.pack(fill='x', padx=15, pady=15)
        
        # Título
        tk.Label(contenido, text="Estadísticas Principales",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(anchor='w', pady=(0, 10))
        
        # Grid para estadísticas
        stats_grid = tk.Frame(contenido, bg=COLORES['fondo_panel'])
        stats_grid.pack(fill='x')
        
        # Configurar grid
        for i in range(2):
            stats_grid.grid_columnconfigure(i, weight=1)
        
        # Cantidad de fardos
        self.crear_stat_item(stats_grid, "Cantidad de Fardos:", "0", 0, 0)
        self.label_cantidad_fardos = self.labels_stats["Cantidad de Fardos:"]
        
        # Bruto Fardos
        self.crear_stat_item(stats_grid, "Bruto Fardos:", "0.00 kg", 0, 1)
        self.label_bruto_fardos = self.labels_stats["Bruto Fardos:"]
        
        # Tara fardos
        self.crear_stat_item(stats_grid, "Tara Fardos:", "0.00 kg", 1, 0)
        self.label_tara_fardos = self.labels_stats["Tara Fardos:"]
        
        # Peso promedio
        self.crear_stat_item(stats_grid, "Peso Promedio:", "0.00 kg", 1, 1)
        self.label_peso_promedio = self.labels_stats["Peso Promedio:"]
    
    def crear_stat_item(self, parent, titulo, valor, row, col):
        """Crea un elemento de estadística"""
        if not hasattr(self, 'labels_stats'):
            self.labels_stats = {}
        
        frame = tk.Frame(parent, bg=COLORES['fondo_panel'])
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Título
        tk.Label(frame, text=titulo,
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_secundario'],
                font=FUENTES['normal']).pack(anchor='w')
        
        # Valor
        label_valor = tk.Label(frame, text=valor,
                             bg=COLORES['fondo_panel'],
                             fg=COLORES['primario'],
                             font=FUENTES['grande'])
        label_valor.pack(anchor='w')
        
        self.labels_stats[titulo] = label_valor
    
    def crear_datos_adicionales(self):
        """Crea la sección de datos adicionales"""
        # Frame con sombra
        shadow_frame, datos_frame = EstilosModernos.crear_frame_con_sombra(self.parent)
        shadow_frame.pack(fill='x', pady=(0, 10))
        
        # Contenido del frame
        contenido = tk.Frame(datos_frame, bg=COLORES['fondo_panel'])
        contenido.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Título
        tk.Label(contenido, text="Datos Adicionales",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(anchor='w', pady=(0, 10))
        
        # Grid para los campos
        campos_grid = tk.Frame(contenido, bg=COLORES['fondo_panel'])
        campos_grid.pack(fill='x')
        
        # Configurar grid
        for i in range(2):
            campos_grid.grid_columnconfigure(i, weight=1)
        
        # Kg Bruto Romaneo
        self.crear_campo_entrada(campos_grid, "Kg Bruto Romaneo:", 0, 0, 'kg_bruto_romaneo')
        
        # Agregado
        self.crear_campo_entrada(campos_grid, "Agregado:", 0, 1, 'agregado', valor_defecto="0")
        
        # Resto
        self.crear_campo_entrada(campos_grid, "Resto:", 1, 0, 'resto', valor_defecto="0")
    
    def crear_campo_entrada(self, parent, titulo, row, col, nombre_campo, valor_defecto=""):
        """Crea un campo de entrada"""
        frame = tk.Frame(parent, bg=COLORES['fondo_panel'])
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Título
        tk.Label(frame, text=titulo,
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['normal']).pack(anchor='w')
        
        # Campo de entrada
        entry = WidgetsPersonalizados.crear_entrada_moderna(frame, width=15)
        entry.pack(anchor='w', pady=(5, 0))
        entry.insert(0, valor_defecto)
        
        # Bind para actualizar cálculos automáticamente
        entry.bind('<KeyRelease>', self.actualizar_calculos)
        entry.bind('<FocusOut>', self.actualizar_calculos)
        
        # Asignar a la variable correspondiente
        if nombre_campo == 'kg_bruto_romaneo':
            self.entry_kg_bruto_romaneo = entry
        elif nombre_campo == 'agregado':
            self.entry_agregado = entry
        elif nombre_campo == 'resto':
            self.entry_resto = entry
    
    def crear_calculo_rinde(self):
        """Crea la sección de cálculo de rinde"""
        # Frame con sombra
        shadow_frame, rinde_frame = EstilosModernos.crear_frame_con_sombra(self.parent)
        shadow_frame.pack(fill='x', pady=(0, 10))
        
        # Contenido
        contenido = tk.Frame(rinde_frame, bg=COLORES['fondo_panel'])
        contenido.pack(fill='x', padx=15, pady=15)
        
        # Título
        tk.Label(contenido, text="Cálculo de Rinde",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(anchor='w', pady=(0, 10))
        
        # Fórmula explicativa
        formula_frame = tk.Frame(contenido, bg=COLORES['fondo_panel'])
        formula_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(formula_frame, text="Fórmula: (Bruto Fardos + Resto - Agregado - Tara Fardos) / Kg Bruto Romaneo × 100",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_secundario'],
                font=FUENTES['pequena']).pack(anchor='w')
        
        # Resultado del rinde
        self.label_rinde = tk.Label(contenido, text="Rinde: -- %",
                                  bg=COLORES['fondo_panel'],
                                  fg=COLORES['exito'],
                                  font=FUENTES['extra_grande'])
        self.label_rinde.pack(anchor='w')
        
        # Desglose del cálculo
        self.label_desglose = tk.Label(contenido, text="",
                                     bg=COLORES['fondo_panel'],
                                     fg=COLORES['texto_secundario'],
                                     font=FUENTES['pequena'],
                                     justify='left')
        self.label_desglose.pack(anchor='w', pady=(5, 0))
    
    def crear_observaciones(self):
        """Crea la sección de observaciones"""
        # Frame con sombra
        shadow_frame, obs_frame = EstilosModernos.crear_frame_con_sombra(self.parent)
        shadow_frame.pack(fill='both', expand=True)
        
        # Contenido del frame
        contenido = tk.Frame(obs_frame, bg=COLORES['fondo_panel'])
        contenido.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Título
        tk.Label(contenido, text="Observaciones",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(anchor='w', pady=(0, 10))
        
        # Text widget con scrollbar
        text_container = tk.Frame(contenido, bg=COLORES['fondo_panel'])
        text_container.pack(fill='both', expand=True)
        
        self.text_observaciones = tk.Text(text_container, height=4,
                                        bg=COLORES['fondo_entrada'],
                                        fg=COLORES['texto_principal'],
                                        font=FUENTES['normal'],
                                        wrap=tk.WORD,
                                        relief='solid',
                                        borderwidth=1)
        self.text_observaciones.pack(side='left', fill='both', expand=True)
        
        # Scrollbar para observaciones
        scroll_obs = ttk.Scrollbar(text_container, orient='vertical',
                                  command=self.text_observaciones.yview)
        scroll_obs.pack(side='right', fill='y')
        self.text_observaciones.configure(yscrollcommand=scroll_obs.set)
    
    def actualizar_calculos(self, event=None):
        """Actualiza todos los cálculos automáticamente"""
        if not self.ticket_actual:
            return
        
        try:
            # Obtener valores
            bruto_fardos = self.ticket_actual.obtener_peso_total()
            cantidad_fardos = self.ticket_actual.obtener_cantidad_fardos()
            tara_fardos = cantidad_fardos * 2.0  # 2 kg por fardo
            
            # Obtener valores de los campos
            kg_bruto_romaneo = self.obtener_valor_numerico(self.entry_kg_bruto_romaneo)
            agregado = self.obtener_valor_numerico(self.entry_agregado)
            resto = self.obtener_valor_numerico(self.entry_resto)
            
            # Calcular rinde si hay kg bruto romaneo
            if kg_bruto_romaneo > 0:
                numerador = bruto_fardos + resto - agregado - tara_fardos
                rinde = (numerador / kg_bruto_romaneo) * 100
                
                self.label_rinde.configure(text=f"Rinde: {rinde:.2f} %")
                
                # Mostrar desglose
                desglose = (f"Cálculo: ({bruto_fardos:.2f} + {resto:.2f} - {agregado:.2f} - {tara_fardos:.2f}) / {kg_bruto_romaneo:.2f} × 100\n"
                           f"= {numerador:.2f} / {kg_bruto_romaneo:.2f} × 100 = {rinde:.2f}%")
                self.label_desglose.configure(text=desglose)
            else:
                self.label_rinde.configure(text="Rinde: -- %")
                self.label_desglose.configure(text="Ingrese Kg Bruto Romaneo para calcular")
                
        except Exception as e:
            print(f"Error en cálculos: {e}")
    
    def obtener_valor_numerico(self, entry):
        """Obtiene un valor numérico de un campo de entrada"""
        try:
            valor = entry.get().strip().replace(',', '.')
            return float(valor) if valor else 0.0
        except (ValueError, AttributeError):
            return 0.0
    
    def actualizar_datos(self, ticket):
        """Actualiza los datos mostrados"""
        if not ticket:
            self.limpiar_datos()
            return
        
        self.ticket_actual = ticket
        
        # Estadísticas principales
        cantidad_fardos = ticket.obtener_cantidad_fardos()
        bruto_fardos = ticket.obtener_peso_total()
        tara_fardos = cantidad_fardos * 2.0  # 2 kg por fardo
        peso_promedio = bruto_fardos / cantidad_fardos if cantidad_fardos > 0 else 0
        
        self.label_cantidad_fardos.configure(text=str(cantidad_fardos))
        self.label_bruto_fardos.configure(text=f"{bruto_fardos:.2f} kg")
        self.label_tara_fardos.configure(text=f"{tara_fardos:.2f} kg")
        self.label_peso_promedio.configure(text=f"{peso_promedio:.2f} kg")
        
        # Actualizar cálculos
        self.actualizar_calculos()
    
    def limpiar_datos(self):
        """Limpia todos los datos mostrados"""
        self.ticket_actual = None
        
        # Limpiar estadísticas
        self.label_cantidad_fardos.configure(text="0")
        self.label_bruto_fardos.configure(text="0.00 kg")
        self.label_tara_fardos.configure(text="0.00 kg")
        self.label_peso_promedio.configure(text="0.00 kg")
        
        # Limpiar campos adicionales
        if self.entry_kg_bruto_romaneo:
            self.entry_kg_bruto_romaneo.delete(0, tk.END)
        if self.entry_agregado:
            self.entry_agregado.delete(0, tk.END)
            self.entry_agregado.insert(0, "0")
        if self.entry_resto:
            self.entry_resto.delete(0, tk.END)
            self.entry_resto.insert(0, "0")
        if self.text_observaciones:
            self.text_observaciones.delete(1.0, tk.END)
        
        # Limpiar rinde
        self.label_rinde.configure(text="Rinde: -- %")
        self.label_desglose.configure(text="")
    
    def obtener_datos_adicionales(self):
        """Obtiene los datos adicionales ingresados"""
        datos = {}
        
        if self.entry_kg_bruto_romaneo:
            datos['kg_bruto_romaneo'] = self.entry_kg_bruto_romaneo.get().strip()
        
        if self.entry_agregado:
            datos['agregado'] = self.entry_agregado.get().strip()
        
        if self.entry_resto:
            datos['resto'] = self.entry_resto.get().strip()
        
        if self.text_observaciones:
            datos['observaciones'] = self.text_observaciones.get(1.0, tk.END).strip()
        
        return datos
    
    def cargar_datos_adicionales(self, ticket):
        """Carga los datos adicionales de un ticket"""
        if not ticket:
            return
        
        # Cargar kg bruto romaneo
        if hasattr(ticket, 'kg_bruto_romaneo') and ticket.kg_bruto_romaneo is not None:
            if self.entry_kg_bruto_romaneo:
                self.entry_kg_bruto_romaneo.delete(0, tk.END)
                self.entry_kg_bruto_romaneo.insert(0, str(ticket.kg_bruto_romaneo))
        
        # Cargar agregado
        if hasattr(ticket, 'agregado') and ticket.agregado is not None:
            if self.entry_agregado:
                self.entry_agregado.delete(0, tk.END)
                self.entry_agregado.insert(0, str(ticket.agregado))
        
        # Cargar resto
        if hasattr(ticket, 'resto') and ticket.resto is not None:
            if self.entry_resto:
                self.entry_resto.delete(0, tk.END)
                self.entry_resto.insert(0, str(ticket.resto))
        
        # Cargar observaciones
        if hasattr(ticket, 'observaciones') and ticket.observaciones:
            if self.text_observaciones:
                self.text_observaciones.delete(1.0, tk.END)
                self.text_observaciones.insert(1.0, ticket.observaciones)
        
        # Actualizar cálculos después de cargar
        self.actualizar_calculos()
