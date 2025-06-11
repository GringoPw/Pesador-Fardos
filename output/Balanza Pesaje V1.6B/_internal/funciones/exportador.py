import os
import csv
from datetime import datetime
from typing import List
from config.configuracion import EXPORTACION_CONFIG

class Exportador:
    """Clase para exportar datos a diferentes formatos"""
    
    def __init__(self):
        self.carpeta_destino = EXPORTACION_CONFIG['carpeta_destino']
        self.formato_fecha = EXPORTACION_CONFIG['formato_fecha']
        self.separador_csv = EXPORTACION_CONFIG['separador_csv']
        self.encoding = EXPORTACION_CONFIG['encoding']
        
        # Crear carpeta de exportaciones si no existe
        if not os.path.exists(self.carpeta_destino):
            os.makedirs(self.carpeta_destino)
    
    def _generar_nombre_archivo(self, ticket_numero: str, extension: str) -> str:
        """Genera un nombre de archivo único con timestamp"""
        timestamp = datetime.now().strftime(self.formato_fecha)
        return f"{self.carpeta_destino}/Ticket_{ticket_numero}_{timestamp}.{extension}"
    
    def exportar_ticket_csv(self, ticket) -> str:
        """Exporta un ticket a formato CSV"""
        nombre_archivo = self._generar_nombre_archivo(ticket.numero, "csv")
        
        try:
            with open(nombre_archivo, 'w', newline='', encoding=self.encoding) as archivo:
                writer = csv.writer(archivo, delimiter=self.separador_csv)
                
                # Encabezado
                writer.writerow(['Ticket', 'Fecha', 'Hora', 'Total Fardos', 'Peso Total (kg)'])
                writer.writerow([
                    ticket.numero,
                    ticket.fecha_creacion.strftime('%d/%m/%Y'),
                    ticket.fecha_creacion.strftime('%H:%M:%S'),
                    ticket.obtener_cantidad_fardos(),
                    f"{ticket.obtener_peso_total():.2f}"
                ])
                
                # Línea en blanco
                writer.writerow([])
                
                # Detalle de fardos
                writer.writerow(['N° Fardo', 'Peso (kg)', 'Hora'])
                for fardo in ticket.fardos:
                    writer.writerow([
                        fardo.numero,
                        f"{fardo.peso:.2f}",
                        fardo.hora_pesaje.strftime('%H:%M:%S')
                    ])
            
            print(f"Archivo CSV exportado: {nombre_archivo}")
            return nombre_archivo
            
        except Exception as e:
            print(f"Error al exportar CSV: {str(e)}")
            raise
    
    def exportar_ticket_pdf(self, ticket) -> str:
        """Exporta un ticket a formato PDF"""
        nombre_archivo = self._generar_nombre_archivo(ticket.numero, "pdf")
        
        try:
            # Importar reportlab solo cuando sea necesario
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            # Crear documento
            doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            elementos = []
            
            # Estilos
            estilos = getSampleStyleSheet()
            titulo_estilo = estilos['Heading1']
            subtitulo_estilo = estilos['Heading2']
            normal_estilo = estilos['Normal']
            
            # Título
            elementos.append(Paragraph(f"Ticket de Pesaje #{ticket.numero}", titulo_estilo))
            elementos.append(Spacer(1, 12))
            
            # Información general
            fecha_str = ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M:%S')
            elementos.append(Paragraph(f"Fecha: {fecha_str}", normal_estilo))
            elementos.append(Paragraph(f"Total Fardos: {ticket.obtener_cantidad_fardos()}", normal_estilo))
            elementos.append(Paragraph(f"Peso Total: {ticket.obtener_peso_total():.2f} kg", normal_estilo))
            elementos.append(Spacer(1, 12))
            
            # Tabla de fardos
            elementos.append(Paragraph("Detalle de Fardos", subtitulo_estilo))
            elementos.append(Spacer(1, 6))
            
            # Datos para la tabla
            datos = [['N° Fardo', 'Peso (kg)', 'Hora']]
            for fardo in ticket.fardos:
                datos.append([
                    str(fardo.numero),
                    f"{fardo.peso:.2f}",
                    fardo.hora_pesaje.strftime('%H:%M:%S')
                ])
            
            # Crear tabla
            tabla = Table(datos)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elementos.append(tabla)
            
            # Generar PDF
            doc.build(elementos)
            
            print(f"Archivo PDF exportado: {nombre_archivo}")
            return nombre_archivo
            
        except ImportError:
            print("Error: No se pudo importar reportlab. Instale con: pip install reportlab")
            raise
        except Exception as e:
            print(f"Error al exportar PDF: {str(e)}")
            raise
