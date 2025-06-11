# Sistema de Pesaje de Fardos v2.0

Nace de la necesidad de automatizar los procesos de pesaje de la empresa.

Sistema completo para el pesaje, registro y gestión de fardos con interfaz gráfica moderna, base de datos local y capacidad de exportación.

## Descripción

El Sistema de Pesaje de Fardos es una aplicación de escritorio desarrollada en Python que permite gestionar el proceso de pesaje de fardos, registrando la información en tickets y almacenándola en una base de datos local. El sistema ofrece una interfaz gráfica moderna e intuitiva, con capacidad para trabajar con balanzas reales o en modo simulación.

### Características principales

- **Interfaz gráfica moderna**: Diseño intuitivo y responsive con temas de colores personalizados
- **Gestión de tickets**: Creación, edición y eliminación de tickets de pesaje
- **Registro de fardos**: Captura de peso de fardos individuales con número y hora de pesaje
- **Estadísticas en tiempo real**: Visualización de datos como cantidad de fardos, peso total, tara y promedio
- **Historial completo**: Acceso al historial de tickets guardados con búsqueda y filtrado
- **Exportación de datos**: Generación de reportes en formatos CSV y PDF
- **Base de datos local**: Almacenamiento persistente de todos los datos en SQLite
- **Modo simulación**: Capacidad de funcionar sin balanza física, generando pesos aleatorios
- **Configuración en red**: Posibilidad de compartir la base de datos entre múltiples computadoras

## Requisitos del sistema

- **Sistema operativo**: Windows 7+
- **Python**: Versión 3.6 o superior
- **Dependencias**: Ver archivo `requirements.txt`
- **Espacio en disco**: Mínimo 50MB para la instalación básica
- **Memoria RAM**: Mínimo 2GB recomendado

## Instalación

1. Clonar o descargar este repositorio
2. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```
   O ejecutar el script de instalación:
   ```
   python instalar_dependencias.py
   ```
3. Ejecutar la aplicación:
   ```
   python main.py
   ```

## Estructura del proyecto

```
Pesador-Fardos/
├── config/                  # Configuraciones del sistema
│   └── configuracion.py     # Parámetros de configuración (colores, fuentes, etc.)
├── exportaciones/           # Carpeta donde se guardan los archivos exportados
├── funciones/               # Lógica de negocio
│   ├── base_datos.py        # Gestión de la base de datos SQLite
│   ├── conexion_internet.py # Verificador de conexión a internet
│   ├── exportador.py        # Funciones para exportar a CSV y PDF
│   ├── gestor_fardos.py     # Lógica principal para gestión de fardos
│   ├── modelos.py           # Modelos de datos (Ticket, Fardo)
│   └── simulador_balanza.py # Simulador de balanza para pruebas
├── interfaz/                # Componentes de la interfaz gráfica
│   ├── estilos.py           # Estilos y widgets personalizados
│   ├── panel_estadisticas.py # Panel de estadísticas
│   ├── panel_fardos.py      # Panel de gestión de fardos
│   ├── ventana_historial.py # Ventana de historial de tickets
│   └── ventana_principal.py # Ventana principal de la aplicación
├── configurar_red.py        # Utilidad para configurar el sistema en red
├── instalar_dependencias.py # Script para instalar dependencias
├── main.py                  # Punto de entrada principal
├── pesaje_fardos.db         # Base de datos SQLite
├── probar_dependencias.py   # Verificador de dependencias
├── requirements.txt         # Lista de dependencias
└── visor_tickets.py         # Visor de tickets para estaciones secundarias
```

## Guía de uso

### Inicio rápido

1. **Crear un nuevo ticket**:
   - Ingrese un número de ticket en el campo correspondiente
   - Haga clic en "Crear Ticket" o presione Enter

2. **Registrar fardos**:
   - El sistema asignará automáticamente el número del primer fardo (1)
   - Haga clic en "Pesar" para registrar el peso actual
   - El sistema incrementará automáticamente el número para el siguiente fardo

3. **Guardar el ticket**:
   - Haga clic en el botón "Guardar" en la barra inferior
   - Opcionalmente, puede ingresar el peso bruto y observaciones antes de guardar

4. **Exportar datos**:
   - Utilice los botones "CSV" o "PDF" para exportar el ticket actual
   - Los archivos se guardarán en la carpeta "exportaciones"

5. **Consultar historial**:
   - Haga clic en "Historial" para ver todos los tickets guardados
   - Puede cargar o eliminar tickets desde esta ventana

### Atajos de teclado

- **Enter**: Crear ticket (cuando el foco está en el campo de número de ticket) o pesar fardo
- **Ctrl+S**: Guardar ticket actual
- **Ctrl+H**: Abrir ventana de historial

## Configuración en red

El sistema puede configurarse para funcionar en red, permitiendo que múltiples computadoras accedan a la misma base de datos.

### Configuración del servidor (PC principal)

1. Crear una carpeta compartida en la red
2. Copiar el archivo `pesaje_fardos.db` a la carpeta compartida
3. Ejecutar `python configurar_red.py` y seguir las instrucciones para configurar la ruta de la base de datos

### Configuración del cliente (PC secundaria)

1. Instalar Python y las dependencias necesarias
2. Copiar los archivos del sistema a la PC cliente
3. Ejecutar `python configurar_red.py` para configurar la ruta a la base de datos compartida
4. Usar `python visor_tickets.py` para ejecutar el visor de tickets (modo solo lectura)

## Solución de problemas

### Problemas comunes

1. **Error de dependencias faltantes**:
   - Ejecute `python instalar_dependencias.py` para instalar todas las dependencias necesarias

2. **Error de conexión a la base de datos**:
   - Verifique que el archivo `pesaje_fardos.db` existe y no está dañado
   - Asegúrese de tener permisos de escritura en la carpeta donde se encuentra la base de datos

3. **Error de conexión en red**:
   - Verifique que la carpeta compartida es accesible desde la PC cliente
   - Compruebe los permisos de lectura/escritura en la carpeta compartida

## Desarrollo y contribuciones

El sistema está desarrollado en Python utilizando Tkinter para la interfaz gráfica y SQLite para la base de datos. Se ha diseñado con una arquitectura modular para facilitar el mantenimiento y la extensión.

### Tecnologías utilizadas

- **Python**: Lenguaje de programación principal
- **Tkinter**: Biblioteca para la interfaz gráfica
- **SQLite**: Motor de base de datos
- **ReportLab**: Generación de archivos PDF
- **PySerial**: Comunicación con balanzas (modo real)

## Licencia

Este software es propiedad de su autor y está protegido por las leyes de derechos de autor. Su uso, modificación y distribución están sujetos a los términos acordados con el autor.

## Contacto

Para soporte técnico o consultas, contacte al desarrollador:

- **Correo**: [joaquin.paw@gmail.com](mailto:joaquin.paw@gmail.com)
- **Teléfono**: +54 3735 416373