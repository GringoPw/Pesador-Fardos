import os
from datetime import datetime
from typing import List, Optional
from funciones.modelos import Ticket, Fardo
from funciones.simulador_balanza import ConexionBalanza
from funciones.exportador import Exportador
from config.configuracion import CAMPOS_CONFIG, VALIDACIONES

class GestorFardos:
    """Clase principal para gestionar los fardos y tickets"""
    
    def __init__(self):
        self.balanza = ConexionBalanza()
        self.exportador = Exportador()
        self.tickets: List[Ticket] = []
        self.tara_por_fardo = CAMPOS_CONFIG['tara_por_fardo']
        self.precision_decimal = CAMPOS_CONFIG['precision_decimal']
    
    def crear_ticket(self, numero_ticket: str) -> Ticket:
        """Crea un nuevo ticket"""
        # Validar número de ticket
        if not numero_ticket:
            raise ValueError("El número de ticket no puede estar vacío")
        
        if len(numero_ticket) < VALIDACIONES['ticket_min_length']:
            raise ValueError(f"El número de ticket debe tener al menos {VALIDACIONES['ticket_min_length']} caracteres")
        
        if len(numero_ticket) > VALIDACIONES['ticket_max_length']:
            raise ValueError(f"El número de ticket no puede exceder {VALIDACIONES['ticket_max_length']} caracteres")
        
        # Verificar que no exista un ticket con el mismo número
        for ticket in self.tickets:
            if ticket.numero == numero_ticket:
                raise ValueError(f"Ya existe un ticket con el número {numero_ticket}")
        
        # Crear y agregar el ticket
        nuevo_ticket = Ticket(numero_ticket)
        self.tickets.append(nuevo_ticket)
        
        print(f"✅ Ticket {numero_ticket} creado exitosamente")
        return nuevo_ticket
    
    def obtener_peso_balanza(self) -> float:
        """Obtiene el peso actual de la balanza"""
        peso = self.balanza.obtener_peso()
        return round(peso, self.precision_decimal)
    
    def obtener_hora_actual(self) -> datetime:
        """Obtiene la hora actual"""
        return datetime.now()
    
    def agregar_fardo(self, ticket: Ticket, numero_fardo: int, peso: float) -> Fardo:
        """Agrega un fardo al ticket"""
        # Validar peso
        if peso < VALIDACIONES['peso_minimo']:
            raise ValueError(f"El peso debe ser mayor a {VALIDACIONES['peso_minimo']} kg")
        
        if peso > VALIDACIONES['peso_maximo']:
            raise ValueError(f"El peso no puede exceder {VALIDACIONES['peso_maximo']} kg")
        
        # Validar número de fardo
        if numero_fardo < 1 or numero_fardo > VALIDACIONES['numero_fardo_maximo']:
            raise ValueError(f"El número de fardo debe estar entre 1 y {VALIDACIONES['numero_fardo_maximo']}")
        
        # Crear y agregar el fardo
        nuevo_fardo = Fardo(numero_fardo, peso)
        ticket.agregar_fardo(nuevo_fardo)
        
        return nuevo_fardo
    
    def eliminar_fardo(self, ticket: Ticket, numero_fardo: int) -> None:
        """Elimina un fardo del ticket"""
        ticket.eliminar_fardo(numero_fardo)
    
    def calcular_tara_total(self, ticket: Ticket) -> float:
        """Calcula la tara total para un ticket"""
        return ticket.obtener_cantidad_fardos() * self.tara_por_fardo
    
    def exportar_csv(self, ticket: Ticket) -> str:
        """Exporta el ticket a un archivo CSV"""
        return self.exportador.exportar_ticket_csv(ticket)
    
    def exportar_pdf(self, ticket: Ticket) -> str:
        """Exporta el ticket a un archivo PDF"""
        return self.exportador.exportar_ticket_pdf(ticket)
    
    def cerrar(self):
        """Cierra las conexiones y libera recursos"""
        self.balanza.cerrar()
