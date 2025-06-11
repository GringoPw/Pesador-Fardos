import tkinter as tk
from tkinter import ttk
import webbrowser
from interfaz.estilos import EstilosModernos, WidgetsPersonalizados
from config.configuracion import COLORES, FUENTES, DIMENSIONES

class VentanaAcercaDe:
    """Ventana para mostrar información de contacto y acerca del sistema"""
    
    def __init__(self, parent):
        self.parent = parent
        
        self.ventana = tk.Toplevel(parent)
        self.configurar_ventana()
        self.crear_interfaz()
    
    def configurar_ventana(self):
        """Configura la ventana de acerca de"""
        self.ventana.title("Acerca del Sistema")
        self.ventana.geometry("600x500")
        self.ventana.configure(bg=COLORES['fondo_principal'])
        self.ventana.resizable(False, False)
        self.ventana.transient(self.parent)
        self.ventana.grab_set()
        
        # Centrar ventana
        self.ventana.update_idletasks()
        x = (self.ventana.winfo_screenwidth() // 2) - 300
        y = (self.ventana.winfo_screenheight() // 2) - 250
        self.ventana.geometry(f"+{x}+{y}")
    
    def crear_interfaz(self):
        """Crea la interfaz de la ventana"""
        # === TÍTULO ===
        titulo_frame = tk.Frame(self.ventana, bg=COLORES['primario'], height=60)
        titulo_frame.pack(fill='x')
        titulo_frame.pack_propagate(False)
        
        tk.Label(titulo_frame, text="📞 Información de Contacto",
                bg=COLORES['primario'],
                fg=COLORES['texto_blanco'],
                font=FUENTES['titulo']).pack(expand=True)
        
        # === CONTENIDO PRINCIPAL ===
        contenido_frame = tk.Frame(self.ventana, bg=COLORES['fondo_principal'])
        contenido_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # === INFORMACIÓN DEL DESARROLLADOR ===
        self.crear_seccion_desarrollador(contenido_frame)
        
        # === INFORMACIÓN DEL SISTEMA ===
        self.crear_seccion_sistema(contenido_frame)
        
        # === BOTÓN CERRAR ===
        btn_cerrar = WidgetsPersonalizados.crear_boton_moderno(
            self.ventana, "Cerrar", self.cerrar_ventana)
        btn_cerrar.pack(pady=15)
    
    def crear_seccion_desarrollador(self, parent):
        """Crea la sección con información del desarrollador"""
        # Frame con sombra
        shadow_frame, dev_frame = EstilosModernos.crear_frame_con_sombra(parent)
        shadow_frame.pack(fill='x', pady=(0, 15))
        
        # Contenido
        contenido = tk.Frame(dev_frame, bg=COLORES['fondo_panel'])
        contenido.pack(fill='x', padx=15, pady=15)
        
        # Título
        tk.Label(contenido, text="Desarrollador",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(anchor='w', pady=(0, 10))
        
        # Información de contacto
        info_frame = tk.Frame(contenido, bg=COLORES['fondo_panel'])
        info_frame.pack(fill='x')
        
        # Nombre
        self.crear_campo_info(info_frame, "Nombre:", "Ing. Espindola P. Joaquin")
        
        # Teléfono
        self.crear_campo_info(info_frame, "Teléfono:", "+54 3735 416373")
        
        # Email
        email = "joaquin.paw@gmail.com"
        email_frame = tk.Frame(info_frame, bg=COLORES['fondo_panel'])
        email_frame.pack(fill='x', pady=5)
        
        tk.Label(email_frame, text="Email:",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_secundario'],
                font=FUENTES['normal']).pack(side='left', padx=(0, 10))
        
        email_btn = tk.Label(email_frame, text=email,
                           bg=COLORES['fondo_panel'],
                           fg=COLORES['primario'],
                           font=FUENTES['normal'],
                           cursor="hand2")
        email_btn.pack(side='left')
        email_btn.bind("<Button-1>", lambda e: webbrowser.open(f"mailto:{email}"))
        
        # Web
        web = "www.github.com/GringoPw"
        web_frame = tk.Frame(info_frame, bg=COLORES['fondo_panel'])
        web_frame.pack(fill='x', pady=5)
        
        tk.Label(web_frame, text="Web:",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_secundario'],
                font=FUENTES['normal']).pack(side='left', padx=(0, 10))
        
        web_btn = tk.Label(web_frame, text=web,
                         bg=COLORES['fondo_panel'],
                         fg=COLORES['primario'],
                         font=FUENTES['normal'],
                         cursor="hand2")
        web_btn.pack(side='left')
        web_btn.bind("<Button-1>", lambda e: webbrowser.open(f"https://{web}"))
    
    def crear_seccion_sistema(self, parent):
        """Crea la sección con información del sistema"""
        # Frame con sombra
        shadow_frame, sys_frame = EstilosModernos.crear_frame_con_sombra(parent)
        shadow_frame.pack(fill='x')
        
        # Contenido
        contenido = tk.Frame(sys_frame, bg=COLORES['fondo_panel'])
        contenido.pack(fill='x', padx=15, pady=15)
        
        # Título
        tk.Label(contenido, text="Información del Sistema",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(anchor='w', pady=(0, 10))
        
        # Información del sistema
        info_frame = tk.Frame(contenido, bg=COLORES['fondo_panel'])
        info_frame.pack(fill='x')
        
        # Versión
        self.crear_campo_info(info_frame, "Versión:", "1.7")
        
        # Fecha de actualización
        self.crear_campo_info(info_frame, "Última actualización:", "Junio 2025")
        
        # Licencia
        self.crear_campo_info(info_frame, "Licencia:", "Uso exclusivo para Marfra S.A")
        
        # Soporte
        soporte_frame = tk.Frame(info_frame, bg=COLORES['fondo_panel'])
        soporte_frame.pack(fill='x', pady=5)
        
        tk.Label(soporte_frame, text="Soporte técnico:",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_secundario'],
                font=FUENTES['normal']).pack(anchor='w')
        
        tk.Label(soporte_frame, text="Para soporte técnico, contacte al desarrollador\n"
                                   "Horario de atención: Lunes a Viernes de 9:00 a 18:00",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['normal'],
                justify='left').pack(anchor='w', padx=(20, 0))
    
    def crear_campo_info(self, parent, titulo, valor):
        """Crea un campo de información"""
        frame = tk.Frame(parent, bg=COLORES['fondo_panel'])
        frame.pack(fill='x', pady=5)
        
        tk.Label(frame, text=titulo,
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_secundario'],
                font=FUENTES['normal']).pack(side='left', padx=(0, 10))
        
        tk.Label(frame, text=valor,
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['normal']).pack(side='left')
    
    def cerrar_ventana(self):
        """Cierra la ventana"""
        self.ventana.destroy()
