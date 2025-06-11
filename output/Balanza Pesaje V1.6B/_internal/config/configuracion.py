# Configuración del Sistema de Pesaje de Fardos
# Aquí puedes modificar fácilmente todos los parámetros del sistema

# === CONFIGURACIÓN DE CAMPOS ===
CAMPOS_CONFIG = {
    'tara_por_fardo': 2.0,  # kg de tara por cada fardo
    'precision_decimal': 2,  # decimales para mostrar pesos
    'numero_fardo_inicial': 1,  # número inicial de fardos
}

# === CONFIGURACIÓN DE BALANZA GAMA ===
BALANZA_CONFIG = {
    'puerto_serie': 'COM1',   # Puerto serie de la balanza
    'baudrate': 9600,         # Velocidad de comunicación
    'timeout': 1,             # Timeout en segundos
    'activar_dtr': True,      # Activar DTR para la balanza
    'activar_rts': True,      # Activar RTS para la balanza
}

# === CONFIGURACIÓN VISUAL MEJORADA ===
COLORES = {
    # Colores principales
    'primario': '#2E86AB',      # Azul principal
    'secundario': '#A23B72',    # Rosa/magenta
    'acento': '#F18F01',        # Naranja
    'exito': '#C73E1D',         # Rojo para éxito/completado
    
    # Fondos
    'fondo_principal': '#F8F9FA',
    'fondo_panel': '#FFFFFF',
    'fondo_entrada': '#FFFFFF',
    'fondo_hover': '#E3F2FD',
    'fondo_seleccion': '#BBDEFB',
    
    # Textos
    'texto_principal': '#212529',
    'texto_secundario': '#6C757D',
    'texto_blanco': '#FFFFFF',
    'texto_exito': '#155724',
    'texto_error': '#721C24',
    
    # Bordes y separadores
    'borde_principal': '#DEE2E6',
    'borde_activo': '#2E86AB',
    'sombra': '#DDDDDD',
    
    # Estados
    'activo': '#28A745',
    'inactivo': '#6C757D',
    'peligro': '#DC3545',
    'advertencia': '#FFC107',
}

FUENTES = {
    'titulo': ('Segoe UI', 16, 'bold'),
    'subtitulo': ('Segoe UI', 12, 'bold'),
    'normal': ('Segoe UI', 10),
    'pequena': ('Segoe UI', 9),
    'monospace': ('Consolas', 10),
    'grande': ('Segoe UI', 14),
    'extra_grande': ('Segoe UI', 18, 'bold'),
}

DIMENSIONES = {
    'ventana_ancho': 1200,
    'ventana_alto': 700,
    'panel_fardos_ancho': 500,
    'panel_stats_ancho': 350,
    'altura_fila_tabla': 20,
    'padding_general': 15,
    'padding_pequeno': 8,
    'radio_borde': 8,
}

# === CONFIGURACIÓN DE EXPORTACIÓN ===
EXPORTACION_CONFIG = {
    'carpeta_destino': 'exportaciones',
    'formato_fecha': '%Y%m%d_%H%M%S',
    'separador_csv': ';',
    'encoding': 'utf-8-sig',  # Para compatibilidad con Excel
}

# === MENSAJES DEL SISTEMA ===
MENSAJES = {
    'ticket_creado': 'Ticket creado exitosamente',
    'fardo_agregado': 'Fardo agregado correctamente',
    'exportacion_exitosa': 'Archivo exportado correctamente',
    'error_conexion_balanza': 'Error al conectar con la balanza',
    'error_exportacion': 'Error al exportar archivo',
    'confirmacion_eliminar': '¿Está seguro de eliminar este fardo?',
    'sin_datos': 'No hay datos para exportar',
}

# === CONFIGURACIÓN DE VALIDACIONES ===
VALIDACIONES = {
    'ticket_min_length': 1,
    'ticket_max_length': 20,
    'peso_minimo': 0.1,
    'peso_maximo': 100000000.0,
    'numero_fardo_maximo': 10000000,
}
