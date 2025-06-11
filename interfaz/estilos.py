import tkinter as tk
from tkinter import ttk
from config.configuracion import COLORES, FUENTES, DIMENSIONES

class EstilosModernos:
    """Clase para aplicar estilos modernos a los widgets de tkinter"""
    
    @staticmethod
    def configurar_estilos():
        """Configura los estilos ttk para toda la aplicación"""
        style = ttk.Style()
        
        # Configurar tema base
        style.theme_use('clam')
        
        # === ESTILOS PARA BOTONES ===
        style.configure('Moderno.TButton',
                       background=COLORES['primario'],
                       foreground=COLORES['texto_blanco'],
                       font=FUENTES['normal'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        style.map('Moderno.TButton',
                 background=[('active', COLORES['secundario']),
                           ('pressed', COLORES['acento'])])
        
        # Botón de éxito
        style.configure('Exito.TButton',
                       background=COLORES['exito'],
                       foreground=COLORES['texto_blanco'],
                       font=FUENTES['normal'],
                       borderwidth=0,
                       padding=(15, 8))
        
        # Botón de peligro
        style.configure('Peligro.TButton',
                       background=COLORES['peligro'],
                       foreground=COLORES['texto_blanco'],
                       font=FUENTES['normal'],
                       borderwidth=0,
                       padding=(10, 6))

        # Botón para barra de estado (más pequeño)
        style.configure('BarraEstado.TButton',
                       background=COLORES['primario'],
                       foreground=COLORES['texto_blanco'],
                       font=FUENTES['pequena'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(8, 4))

        style.map('BarraEstado.TButton',
                 background=[('active', COLORES['secundario']),
                           ('pressed', COLORES['acento'])])
        
        # === ESTILOS PARA CAMPOS DE ENTRADA ===
        style.configure('Moderno.TEntry',
                       fieldbackground=COLORES['fondo_entrada'],
                       borderwidth=2,
                       relief='solid',
                       bordercolor=COLORES['borde_principal'],
                       font=FUENTES['normal'],
                       padding=(10, 8))
        
        style.map('Moderno.TEntry',
                 bordercolor=[('focus', COLORES['borde_activo'])])
        
        # === ESTILOS PARA LABELS ===
        style.configure('Titulo.TLabel',
                       background=COLORES['fondo_principal'],
                       foreground=COLORES['texto_principal'],
                       font=FUENTES['titulo'])
        
        style.configure('Subtitulo.TLabel',
                       background=COLORES['fondo_principal'],
                       foreground=COLORES['texto_principal'],
                       font=FUENTES['subtitulo'])
        
        style.configure('Normal.TLabel',
                       background=COLORES['fondo_principal'],
                       foreground=COLORES['texto_principal'],
                       font=FUENTES['normal'])
        
        style.configure('Estadistica.TLabel',
                       background=COLORES['fondo_panel'],
                       foreground=COLORES['primario'],
                       font=FUENTES['grande'])
        
        # === ESTILOS PARA FRAMES ===
        style.configure('Panel.TFrame',
                       background=COLORES['fondo_panel'],
                       relief='solid',
                       borderwidth=1,
                       bordercolor=COLORES['borde_principal'])
        
        # === ESTILOS PARA TREEVIEW ===
        style.configure('Moderno.Treeview',
                       background=COLORES['fondo_panel'],
                       foreground=COLORES['texto_principal'],
                       font=FUENTES['normal'],
                       fieldbackground=COLORES['fondo_panel'],
                       borderwidth=0,
                       rowheight=DIMENSIONES['altura_fila_tabla'])
        
        style.configure('Moderno.Treeview.Heading',
                       background=COLORES['primario'],
                       foreground=COLORES['texto_blanco'],
                       font=FUENTES['subtitulo'],
                       relief='flat')
        
        style.map('Moderno.Treeview',
                 background=[('selected', COLORES['fondo_seleccion'])])
        
        # === ESTILOS PARA SCROLLBAR ===
        style.configure('Moderno.Vertical.TScrollbar',
                       background=COLORES['borde_principal'],
                       troughcolor=COLORES['fondo_principal'],
                       borderwidth=0,
                       arrowcolor=COLORES['primario'])

    @staticmethod
    def crear_frame_con_sombra(parent, **kwargs):
        """Crea un frame con efecto de sombra"""
        # Frame contenedor para la sombra
        shadow_frame = tk.Frame(parent, bg=COLORES['sombra'], **kwargs)
        
        # Frame principal
        main_frame = tk.Frame(shadow_frame, 
                             bg=COLORES['fondo_panel'],
                             relief='flat',
                             bd=0)
        main_frame.pack(padx=2, pady=2, fill='both', expand=True)
        
        return shadow_frame, main_frame

    @staticmethod
    def crear_separador_horizontal(parent):
        """Crea un separador horizontal elegante"""
        separator = tk.Frame(parent, 
                           height=1, 
                           bg=COLORES['borde_principal'])
        return separator

    @staticmethod
    def crear_indicador_estado(parent, texto, color):
        """Crea un indicador de estado con color"""
        frame = tk.Frame(parent, bg=COLORES['fondo_panel'])
        
        # Círculo indicador
        canvas = tk.Canvas(frame, width=12, height=12, 
                          bg=COLORES['fondo_panel'], 
                          highlightthickness=0)
        canvas.create_oval(2, 2, 10, 10, fill=color, outline=color)
        canvas.pack(side='left', padx=(0, 5))
        
        # Texto
        label = tk.Label(frame, text=texto, 
                        bg=COLORES['fondo_panel'],
                        fg=COLORES['texto_secundario'],
                        font=FUENTES['pequena'])
        label.pack(side='left')
        
        return frame

class WidgetsPersonalizados:
    """Widgets personalizados con mejor apariencia"""
    
    @staticmethod
    def crear_boton_moderno(parent, texto, comando, estilo='Moderno.TButton', **kwargs):
        """Crea un botón con estilo moderno"""
        boton = ttk.Button(parent, text=texto, command=comando, style=estilo, **kwargs)
        return boton
    
    @staticmethod
    def crear_entrada_moderna(parent, **kwargs):
        """Crea un campo de entrada con estilo moderno"""
        entrada = ttk.Entry(parent, style='Moderno.TEntry', **kwargs)
        return entrada
    
    @staticmethod
    def crear_tabla_moderna(parent, columnas, **kwargs):
        """Crea una tabla con estilo moderno"""
        # Frame contenedor
        frame = tk.Frame(parent, bg=COLORES['fondo_panel'])
        
        # Treeview
        tabla = ttk.Treeview(frame, columns=columnas, show='headings', 
                           style='Moderno.Treeview', **kwargs)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tabla.yview,
                                style='Moderno.Vertical.TScrollbar')
        tabla.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        tabla.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        return frame, tabla
    
    @staticmethod
    def crear_tarjeta_estadistica(parent, titulo, valor, icono=None):
        """Crea una tarjeta para mostrar estadísticas"""
        # Frame principal con sombra
        shadow_frame, main_frame = EstilosModernos.crear_frame_con_sombra(parent)
        
        # Contenido
        content_frame = tk.Frame(main_frame, bg=COLORES['fondo_panel'])
        content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Título
        titulo_label = tk.Label(content_frame, text=titulo,
                              bg=COLORES['fondo_panel'],
                              fg=COLORES['texto_secundario'],
                              font=FUENTES['normal'])
        titulo_label.pack(anchor='w')
        
        # Valor
        valor_label = tk.Label(content_frame, text=str(valor),
                             bg=COLORES['fondo_panel'],
                             fg=COLORES['primario'],
                             font=FUENTES['normal'])
        valor_label.pack(anchor='w', pady=(5, 0))
        
        return shadow_frame, valor_label
