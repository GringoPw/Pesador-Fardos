import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Tuple
from funciones.modelos import Ticket, Fardo

class BaseDatos:
    """Clase para manejar la base de datos SQLite"""
    
    def __init__(self, nombre_db: str = "pesaje_fardos.db"):
        self.nombre_db = nombre_db
        self.ruta_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), nombre_db)
        self.inicializar_db()
    
    def inicializar_db(self):
        """Inicializa la base de datos y crea las tablas si no existen"""
        try:
            with sqlite3.connect(self.ruta_db) as conn:
                cursor = conn.cursor()
                
                # Tabla de tickets
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        numero TEXT UNIQUE NOT NULL,
                        fecha_creacion TIMESTAMP NOT NULL,
                        kg_bruto_romaneo REAL,
                        agregado REAL DEFAULT 0,
                        resto REAL DEFAULT 0,
                        observaciones TEXT,
                        estado TEXT DEFAULT 'ACTIVO',
                        fecha_guardado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Tabla de fardos
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS fardos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id INTEGER NOT NULL,
                        numero INTEGER NOT NULL,
                        peso REAL NOT NULL,
                        hora_pesaje TIMESTAMP NOT NULL,
                        FOREIGN KEY (ticket_id) REFERENCES tickets (id),
                        UNIQUE(ticket_id, numero)
                    )
                ''')
                
                # Verificar si necesitamos agregar las nuevas columnas
                cursor.execute("PRAGMA table_info(tickets)")
                columnas_existentes = [columna[1] for columna in cursor.fetchall()]
                
                # Agregar nuevas columnas si no existen
                if 'kg_bruto_romaneo' not in columnas_existentes:
                    cursor.execute('ALTER TABLE tickets ADD COLUMN kg_bruto_romaneo REAL')
                    print("✅ Columna kg_bruto_romaneo agregada")
                
                if 'agregado' not in columnas_existentes:
                    cursor.execute('ALTER TABLE tickets ADD COLUMN agregado REAL DEFAULT 0')
                    print("✅ Columna agregado agregada")
                
                if 'resto' not in columnas_existentes:
                    cursor.execute('ALTER TABLE tickets ADD COLUMN resto REAL DEFAULT 0')
                    print("✅ Columna resto agregada")
                
                # Índices para mejor rendimiento
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_numero ON tickets(numero)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_fecha ON tickets(fecha_creacion)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_fardos_ticket ON fardos(ticket_id)')
                
                conn.commit()
                print("✅ Base de datos inicializada correctamente")
                
        except Exception as e:
            print(f"❌ Error al inicializar base de datos: {str(e)}")
            raise
    
    def guardar_ticket(self, ticket: Ticket, datos_adicionales: dict = None) -> bool:
        """Guarda un ticket completo en la base de datos"""
        try:
            with sqlite3.connect(self.ruta_db) as conn:
                cursor = conn.cursor()
                
                # Preparar datos adicionales
                kg_bruto_romaneo = None
                agregado = 0.0
                resto = 0.0
                observaciones = ""
                
                if datos_adicionales:
                    # Kg Bruto Romaneo
                    kg_bruto_str = datos_adicionales.get('kg_bruto_romaneo', '').strip()
                    if kg_bruto_str:
                        try:
                            kg_bruto_romaneo = float(kg_bruto_str.replace(',', '.'))
                        except ValueError:
                            kg_bruto_romaneo = None
                    
                    # Agregado
                    agregado_str = datos_adicionales.get('agregado', '0').strip()
                    try:
                        agregado = float(agregado_str.replace(',', '.'))
                    except ValueError:
                        agregado = 0.0
                    
                    # Resto
                    resto_str = datos_adicionales.get('resto', '0').strip()
                    try:
                        resto = float(resto_str.replace(',', '.'))
                    except ValueError:
                        resto = 0.0
                    
                    # Observaciones
                    observaciones = datos_adicionales.get('observaciones', '').strip()
                
                # Verificar si el ticket ya existe
                cursor.execute('SELECT id FROM tickets WHERE numero = ?', (ticket.numero,))
                ticket_existente = cursor.fetchone()
                
                if ticket_existente:
                    # Actualizar ticket existente
                    ticket_id = ticket_existente[0]
                    cursor.execute('''
                        UPDATE tickets 
                        SET kg_bruto_romaneo = ?, agregado = ?, resto = ?, 
                            observaciones = ?, fecha_guardado = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (kg_bruto_romaneo, agregado, resto, observaciones, ticket_id))
                    
                    # Eliminar fardos existentes para reemplazarlos
                    cursor.execute('DELETE FROM fardos WHERE ticket_id = ?', (ticket_id,))
                else:
                    # Insertar nuevo ticket
                    cursor.execute('''
                        INSERT INTO tickets (numero, fecha_creacion, kg_bruto_romaneo, 
                                           agregado, resto, observaciones)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (ticket.numero, ticket.fecha_creacion, kg_bruto_romaneo, 
                          agregado, resto, observaciones))
                    ticket_id = cursor.lastrowid
                
                # Insertar fardos
                for fardo in ticket.fardos:
                    cursor.execute('''
                        INSERT INTO fardos (ticket_id, numero, peso, hora_pesaje)
                        VALUES (?, ?, ?, ?)
                    ''', (ticket_id, fardo.numero, fardo.peso, fardo.hora_pesaje))
                
                conn.commit()
                print(f"✅ Ticket {ticket.numero} guardado correctamente")
                return True
                
        except Exception as e:
            print(f"❌ Error al guardar ticket: {str(e)}")
            return False
    
    def obtener_historial_tickets(self) -> List[Tuple]:
        """Obtiene el historial de todos los tickets"""
        try:
            with sqlite3.connect(self.ruta_db) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT t.numero, t.fecha_creacion, COUNT(f.id) as cantidad_fardos,
                           COALESCE(SUM(f.peso), 0) as peso_total, t.fecha_guardado
                    FROM tickets t
                    LEFT JOIN fardos f ON t.id = f.ticket_id
                    WHERE t.estado = 'ACTIVO'
                    GROUP BY t.id, t.numero, t.fecha_creacion, t.fecha_guardado
                    ORDER BY t.fecha_guardado DESC
                ''')
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error al obtener historial: {str(e)}")
            return []
    
    def cargar_ticket(self, numero_ticket: str) -> Optional[Ticket]:
        """Carga un ticket completo desde la base de datos"""
        try:
            with sqlite3.connect(self.ruta_db) as conn:
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
                
                # Asignar datos adicionales
                ticket.kg_bruto_romaneo = ticket_data[2]
                ticket.agregado = ticket_data[3] if ticket_data[3] is not None else 0.0
                ticket.resto = ticket_data[4] if ticket_data[4] is not None else 0.0
                ticket.observaciones = ticket_data[5] or ""
                
                # Obtener fardos del ticket
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
                
                print(f"✅ Ticket {numero_ticket} cargado correctamente con {len(ticket.fardos)} fardos")
                return ticket
                
        except Exception as e:
            print(f"❌ Error al cargar ticket: {str(e)}")
            return None
    
    def eliminar_ticket(self, numero_ticket: str) -> bool:
        """Marca un ticket como eliminado (soft delete)"""
        try:
            with sqlite3.connect(self.ruta_db) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tickets 
                    SET estado = 'ELIMINADO', fecha_guardado = CURRENT_TIMESTAMP
                    WHERE numero = ?
                ''', (numero_ticket,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Error al eliminar ticket: {str(e)}")
            return False
    
    def obtener_estadisticas_generales(self) -> dict:
        """Obtiene estadísticas generales de la base de datos"""
        try:
            with sqlite3.connect(self.ruta_db) as conn:
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
            print(f"❌ Error al obtener estadísticas: {str(e)}")
            return {'total_tickets': 0, 'total_fardos': 0, 'peso_total': 0}
