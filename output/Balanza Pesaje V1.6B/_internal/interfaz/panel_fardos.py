import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING
from interfaz.estilos import EstilosModernos, WidgetsPersonalizados
from config.configuracion import COLORES, FUENTES, DIMENSIONES, MENSAJES

class PanelFardos:
    def __init__(self, parent, gestor, ventana_principal):
        self.parent = parent
        self.gestor = gestor
        self.ventana_principal = ventana_principal
        self.modo_pesaje_activo = False
        self.primer_fardo_ingresado = False
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        """Crea la interfaz del panel de fardos"""
        # === TÍTULO DEL PANEL ===
        titulo_frame = tk.Frame(self.parent, bg=COLORES['fondo_principal'])
        titulo_frame.pack(fill='x', pady=(0, 15))
        
        titulo_label = tk.Label(titulo_frame, text="📦 Lista de Fardos",
                              bg=COLORES['fondo_principal'],
                              fg=COLORES['texto_principal'],
                              font=FUENTES['titulo'])
        titulo_label.pack(side='left')
        
        # === CONTROLES DE FARDO ===
        self.crear_controles_fardo()
        
        # === TABLA DE FARDOS ===
        self.crear_tabla_fardos()
        
        # === BOTONES DE ACCIÓN ===
        self.crear_botones_accion()
    
    def crear_controles_fardo(self):
        """Crea los controles para ingresar fardos"""
        # Frame principal con sombra
        shadow_frame, self.controles_frame = EstilosModernos.crear_frame_con_sombra(self.parent)
        shadow_frame.pack(fill='x', pady=(0, 15))
        
        # Contenido del frame
        contenido = tk.Frame(self.controles_frame, bg=COLORES['fondo_panel'])
        contenido.pack(fill='x', padx=20, pady=15)
        
        # Título de la sección
        tk.Label(contenido, text="Nuevo Fardo",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(anchor='w', pady=(0, 10))
        
        # Frame para controles en línea
        controles_linea = tk.Frame(contenido, bg=COLORES['fondo_panel'])
        controles_linea.pack(fill='x')
        
        # Número de fardo
        tk.Label(controles_linea, text="N° Fardo:",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['normal']).pack(side='left')
        
        self.entry_numero_fardo = WidgetsPersonalizados.crear_entrada_moderna(
            controles_linea, width=8, state='disabled')
        self.entry_numero_fardo.pack(side='left', padx=(10, 20))
        self.entry_numero_fardo.bind('<KeyRelease>', self.validar_numero_fardo)
        
        # Peso actual
        tk.Label(controles_linea, text="Peso:",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['normal']).pack(side='left')
        
        self.label_peso_actual = tk.Label(controles_linea, text="0.00 kg",
                                        bg=COLORES['fondo_panel'],
                                        fg=COLORES['primario'],
                                        font=FUENTES['grande'])
        self.label_peso_actual.pack(side='left', padx=(10, 20))
        
        # Frame para botones de pesaje
        botones_pesaje = tk.Frame(controles_linea, bg=COLORES['fondo_panel'])
        botones_pesaje.pack(side='right')
        
        # Botón pesar
        self.btn_pesar = WidgetsPersonalizados.crear_boton_moderno(
            botones_pesaje, "⚖️ Pesar", self.procesar_fardo, 
            'Exito.TButton', state='disabled')
        self.btn_pesar.pack(side='left', padx=(0, 5))
        
        # Botón repesar
        self.btn_repesar = WidgetsPersonalizados.crear_boton_moderno(
            botones_pesaje, "🔄 Repesar", self.repesar_fardo, 
            'Moderno.TButton', state='disabled')
        self.btn_repesar.pack(side='left')
        
        # Indicador de estado
        self.estado_frame = tk.Frame(contenido, bg=COLORES['fondo_panel'])
        self.estado_frame.pack(fill='x', pady=(10, 0))
        
        self.indicador_estado = tk.Label(self.estado_frame, 
                                       text="⏸️ Esperando ticket...",
                                       bg=COLORES['fondo_panel'],
                                       fg=COLORES['texto_secundario'],
                                       font=FUENTES['normal'])
        self.indicador_estado.pack(side='left')
    
    def crear_tabla_fardos(self):
        """Crea la tabla para mostrar los fardos"""
        # Frame con sombra para la tabla
        shadow_frame, tabla_frame = EstilosModernos.crear_frame_con_sombra(self.parent)
        shadow_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Título de la tabla
        titulo_tabla = tk.Frame(tabla_frame, bg=COLORES['fondo_panel'])
        titulo_tabla.pack(fill='x', padx=15, pady=(15, 10))
        
        tk.Label(titulo_tabla, text="Fardos Registrados",
                bg=COLORES['fondo_panel'],
                fg=COLORES['texto_principal'],
                font=FUENTES['subtitulo']).pack(side='left')
        
        # Contador de fardos
        self.label_contador = tk.Label(titulo_tabla, text="(0 fardos)",
                                     bg=COLORES['fondo_panel'],
                                     fg=COLORES['texto_secundario'],
                                     font=FUENTES['normal'])
        self.label_contador.pack(side='right')
        
        # Contenedor de la tabla
        tabla_container = tk.Frame(tabla_frame, bg=COLORES['fondo_panel'])
        tabla_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Crear tabla moderna
        columnas = ('numero', 'peso', 'hora')
        self.tabla_frame, self.tabla = WidgetsPersonalizados.crear_tabla_moderna(
            tabla_container, columnas)
        self.tabla_frame.pack(fill='both', expand=True)
        
        # Configurar columnas
        self.tabla.heading('numero', text='N° Fardo')
        self.tabla.heading('peso', text='Peso (kg)')
        self.tabla.heading('hora', text='Hora')
        
        self.tabla.column('numero', width=80, anchor='center')
        self.tabla.column('peso', width=100, anchor='center')
        self.tabla.column('hora', width=120, anchor='center')
        
        # Eventos de la tabla
        self.tabla.bind('<Double-1>', self.ver_detalle_fardo)
        self.tabla.bind('<Button-3>', self.mostrar_menu_contextual)
        self.tabla.bind('<<TreeviewSelect>>', self.on_seleccionar_fardo)
    
    def crear_botones_accion(self):
        """Crea los botones de acción con diseño responsive"""
        # Frame principal para botones
        botones_main_frame = tk.Frame(self.parent, bg=COLORES['fondo_principal'])
        botones_main_frame.pack(fill='x', pady=(0, 10))
        
        # Botones de gestión (izquierda)
        botones_izq_frame = tk.Frame(botones_main_frame, bg=COLORES['fondo_principal'])
        botones_izq_frame.pack(side='left')
        
        # Botón eliminar fardo
        self.btn_eliminar = WidgetsPersonalizados.crear_boton_moderno(
            botones_izq_frame, "🗑️ Eliminar", self.eliminar_fardo_seleccionado,
            'Peligro.TButton', state='disabled')
        self.btn_eliminar.pack(side='left', padx=(0, 10))
        
        # Botón nuevo ticket
        self.btn_nuevo_ticket = WidgetsPersonalizados.crear_boton_moderno(
            botones_izq_frame, "📋 Nuevo Ticket", self.ventana_principal.reiniciar_ticket,
            state='disabled')
        self.btn_nuevo_ticket.pack(side='left')
        
        # Botones de exportación (derecha)
        botones_der_frame = tk.Frame(botones_main_frame, bg=COLORES['fondo_principal'])
        botones_der_frame.pack(side='right')
        
        self.btn_export_csv = WidgetsPersonalizados.crear_boton_moderno(
            botones_der_frame, "📊 CSV", self.exportar_csv, state='disabled')
        self.btn_export_csv.pack(side='left', padx=(0, 10))
        
        self.btn_export_pdf = WidgetsPersonalizados.crear_boton_moderno(
            botones_der_frame, "📄 PDF", self.exportar_pdf, state='disabled')
        self.btn_export_pdf.pack(side='left')
    
    def validar_numero_fardo(self, event=None):
        """Valida el número de fardo ingresado"""
        try:
            numero = self.entry_numero_fardo.get().strip()
            if numero and int(numero) > 0:
                self.btn_pesar.configure(state='normal')
            else:
                self.btn_pesar.configure(state='disabled')
        except ValueError:
            self.btn_pesar.configure(state='disabled')
    
    def on_seleccionar_fardo(self, event):
        """Maneja la selección de un fardo en la tabla"""
        seleccion = self.tabla.selection()
        if seleccion and self.modo_pesaje_activo:
            self.btn_eliminar.configure(state='normal')
            self.btn_repesar.configure(state='normal')
            
            # Cargar datos del fardo seleccionado para repesar
            item = seleccion[0]
            numero_fardo = self.tabla.item(item)['values'][0]
            self.entry_numero_fardo.configure(state='normal')
            self.entry_numero_fardo.delete(0, tk.END)
            self.entry_numero_fardo.insert(0, str(numero_fardo))
        else:
            self.btn_eliminar.configure(state='disabled')
            self.btn_repesar.configure(state='disabled')
    
    def activar_modo_pesaje(self):
        """Activa el modo de pesaje"""
        self.modo_pesaje_activo = True
        self.primer_fardo_ingresado = False
        
        # Habilitar controles
        self.entry_numero_fardo.configure(state='normal')
        self.btn_nuevo_ticket.configure(state='normal')
        self.btn_export_csv.configure(state='normal')
        self.btn_export_pdf.configure(state='normal')
        
        # Configurar primer fardo (editable)
        self.entry_numero_fardo.delete(0, tk.END)
        self.entry_numero_fardo.insert(0, "1")
        self.entry_numero_fardo.focus()
        
        self.indicador_estado.configure(text="✏️ Ingrese el número del primer fardo",
                                      fg=COLORES['primario'])
        
        # Simular peso inicial
        self.actualizar_peso_actual()
    
    def desactivar_modo_pesaje(self):
        """Desactiva el modo de pesaje"""
        self.modo_pesaje_activo = False
        self.primer_fardo_ingresado = False
        
        # Deshabilitar controles
        self.entry_numero_fardo.configure(state='disabled')
        self.btn_pesar.configure(state='disabled')
        self.btn_repesar.configure(state='disabled')
        self.btn_eliminar.configure(state='disabled')
        self.btn_nuevo_ticket.configure(state='disabled')
        self.btn_export_csv.configure(state='disabled')
        self.btn_export_pdf.configure(state='disabled')
        
        self.entry_numero_fardo.delete(0, tk.END)
        self.label_peso_actual.configure(text="0.00 kg")
        self.indicador_estado.configure(text="⏸️ Esperando ticket...",
                                      fg=COLORES['texto_secundario'])
        
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        self.label_contador.configure(text="(0 fardos)")
    
    def actualizar_peso_actual(self):
        """Actualiza el peso actual de la balanza"""
        if self.modo_pesaje_activo:
            print("🔄 Actualizando peso en interfaz...")
            try:
                peso = self.gestor.obtener_peso_balanza()
                print(f"📊 Peso recibido en interfaz: {peso} kg")
                self.label_peso_actual.configure(text=f"{peso:.2f} kg")
            except Exception as e:
                print(f"❌ Error al actualizar peso en interfaz: {e}")
                self.label_peso_actual.configure(text="Error")
            
            # Actualizar cada 1 segundo (cambiado de 500ms)
            self.parent.after(1000, self.actualizar_peso_actual)
    
    def procesar_fardo(self):
        """Procesa un nuevo fardo"""
        if not self.ventana_principal.ticket_actual:
            return
        
        try:
            peso = self.gestor.obtener_peso_balanza()
            numero_fardo = int(self.entry_numero_fardo.get())
            
            # Verificar peso cero y confirmar
            if peso == 0.0:
                if not messagebox.askyesno("Confirmar Peso Cero", 
                                         f"El peso detectado es 0.00 kg.\n"
                                         f"¿Desea registrar el fardo #{numero_fardo} con peso cero?"):
                    return
            
            # Verificar si ya existe un fardo con este número
            fardo_existente = None
            for fardo in self.ventana_principal.ticket_actual.fardos:
                if fardo.numero == numero_fardo:
                    fardo_existente = fardo
                    break
            
            if fardo_existente:
                # Confirmar repesaje
                if messagebox.askyesno("Confirmar Repesaje", 
                                     f"¿Desea repesar el fardo #{numero_fardo}?\n"
                                     f"Peso anterior: {fardo_existente.peso:.2f} kg\n"
                                     f"Peso actual: {peso:.2f} kg"):
                    self.repesar_fardo_existente(numero_fardo, peso)
                return
            
            # Agregar nuevo fardo
            fardo = self.gestor.agregar_fardo(self.ventana_principal.ticket_actual, 
                                            numero_fardo, peso)
            
            # Agregar a la tabla
            self.tabla.insert('', 'end', values=(
                fardo.numero,
                f"{fardo.peso:.2f}",
                fardo.hora_pesaje.strftime("%H:%M:%S")
            ))
            
            # Actualizar contador
            total_fardos = len(self.ventana_principal.ticket_actual.fardos)
            self.label_contador.configure(text=f"({total_fardos} fardos)")
            
            # Preparar siguiente fardo
            if not self.primer_fardo_ingresado:
                self.primer_fardo_ingresado = True
                self.indicador_estado.configure(text="✅ Listo para pesar fardos",
                                              fg=COLORES['exito'])
            
            # Incrementar número automáticamente después del primer fardo
            siguiente_numero = numero_fardo + 1
            self.entry_numero_fardo.delete(0, tk.END)
            self.entry_numero_fardo.insert(0, str(siguiente_numero))
            
            # Actualizar estadísticas
            self.ventana_principal.panel_estadisticas.actualizar_datos(
                self.ventana_principal.ticket_actual)
            
            # Actualizar estado
            self.ventana_principal.actualizar_estado(MENSAJES['fardo_agregado'])
            
            # Agregar guardado automático
            self.guardar_automatico()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar fardo: {str(e)}")
    
    def repesar_fardo(self):
        """Repesa el fardo seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un fardo para repesar")
            return
        
        try:
            item = seleccion[0]
            numero_fardo = int(self.tabla.item(item)['values'][0])
            peso_nuevo = self.gestor.obtener_peso_balanza()
            
            # Verificar peso cero y confirmar
            if peso_nuevo == 0.0:
                if not messagebox.askyesno("Confirmar Peso Cero", 
                                         f"El peso detectado es 0.00 kg.\n"
                                         f"¿Desea repesar el fardo #{numero_fardo} con peso cero?"):
                    return
            
            # Obtener peso anterior
            fardo_existente = None
            for fardo in self.ventana_principal.ticket_actual.fardos:
                if fardo.numero == numero_fardo:
                    fardo_existente = fardo
                    break
            
            if fardo_existente:
                if messagebox.askyesno("Confirmar Repesaje", 
                                     f"¿Confirma repesar el fardo #{numero_fardo}?\n"
                                     f"Peso anterior: {fardo_existente.peso:.2f} kg\n"
                                     f"Peso nuevo: {peso_nuevo:.2f} kg"):
                    self.repesar_fardo_existente(numero_fardo, peso_nuevo)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al repesar fardo: {str(e)}")
    
    def repesar_fardo_existente(self, numero_fardo, peso_nuevo):
        """Actualiza el peso de un fardo existente"""
        # Actualizar en el modelo
        for fardo in self.ventana_principal.ticket_actual.fardos:
            if fardo.numero == numero_fardo:
                fardo.peso = peso_nuevo
                fardo.hora_pesaje = self.gestor.obtener_hora_actual()
                break
        
        # Actualizar en la tabla
        for item in self.tabla.get_children():
            if int(self.tabla.item(item)['values'][0]) == numero_fardo:
                self.tabla.item(item, values=(
                    numero_fardo,
                    f"{peso_nuevo:.2f}",
                    fardo.hora_pesaje.strftime("%H:%M:%S")
                ))
                break
        
        # Actualizar estadísticas
        self.ventana_principal.panel_estadisticas.actualizar_datos(
            self.ventana_principal.ticket_actual)
        
        self.ventana_principal.actualizar_estado("Fardo repesado correctamente")

        # Agregar:
        self.guardar_automatico()
    
    def eliminar_fardo_seleccionado(self):
        """Elimina el fardo seleccionado"""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un fardo para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", MENSAJES['confirmacion_eliminar']):
            item = seleccion[0]
            numero_fardo = int(self.tabla.item(item)['values'][0])
            
            # Eliminar del gestor
            self.gestor.eliminar_fardo(self.ventana_principal.ticket_actual, numero_fardo)
            
            # Eliminar de la tabla
            self.tabla.delete(item)
            
            # Actualizar contador
            total_fardos = len(self.ventana_principal.ticket_actual.fardos)
            self.label_contador.configure(text=f"({total_fardos} fardos)")
            
            # Actualizar estadísticas
            self.ventana_principal.panel_estadisticas.actualizar_datos(
                self.ventana_principal.ticket_actual)
    
    def ver_detalle_fardo(self, event):
        """Muestra el detalle de un fardo"""
        seleccion = self.tabla.selection()
        if seleccion:
            item = seleccion[0]
            valores = self.tabla.item(item)['values']
            messagebox.showinfo("Detalle del Fardo", 
                              f"Número: {valores[0]}\n"
                              f"Peso: {valores[1]} kg\n"
                              f"Hora: {valores[2]}")
    
    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual"""
        # Crear menú contextual
        menu = tk.Menu(self.parent, tearoff=0)
        
        seleccion = self.tabla.selection()
        if seleccion and self.modo_pesaje_activo:
            menu.add_command(label="🔄 Repesar", command=self.repesar_fardo)
            menu.add_command(label="🗑️ Eliminar", command=self.eliminar_fardo_seleccionado)
            menu.add_separator()
            menu.add_command(label="ℹ️ Ver Detalle", command=lambda: self.ver_detalle_fardo(None))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def exportar_csv(self):
        """Exporta los datos a CSV"""
        if not self.ventana_principal.ticket_actual:
            messagebox.showwarning("Advertencia", MENSAJES['sin_datos'])
            return
        
        try:
            archivo = self.gestor.exportar_csv(self.ventana_principal.ticket_actual)
            messagebox.showinfo("Éxito", f"Archivo exportado: {archivo}")
            self.ventana_principal.actualizar_estado(MENSAJES['exportacion_exitosa'])
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def exportar_pdf(self):
        """Exporta los datos a PDF"""
        if not self.ventana_principal.ticket_actual:
            messagebox.showwarning("Advertencia", MENSAJES['sin_datos'])
            return
        
        try:
            archivo = self.gestor.exportar_pdf(self.ventana_principal.ticket_actual)
            messagebox.showinfo("Éxito", f"Archivo exportado: {archivo}")
            self.ventana_principal.actualizar_estado(MENSAJES['exportacion_exitosa'])
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def cargar_fardos_desde_ticket(self, ticket):
        """Carga los fardos desde un ticket guardado"""
        # Limpiar tabla actual
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Cargar fardos en la tabla
        for fardo in ticket.fardos:
            self.tabla.insert('', 'end', values=(
                fardo.numero,
                f"{fardo.peso:.2f}",
                fardo.hora_pesaje.strftime("%H:%M:%S")
            ))
        
        # Actualizar contador
        total_fardos = len(ticket.fardos)
        self.label_contador.configure(text=f"({total_fardos} fardos)")
        
        # Configurar siguiente número de fardo
        if ticket.fardos:
            max_numero = max(fardo.numero for fardo in ticket.fardos)
            self.entry_numero_fardo.delete(0, tk.END)
            self.entry_numero_fardo.insert(0, str(max_numero + 1))
            self.primer_fardo_ingresado = True
            self.indicador_estado.configure(text="✅ Ticket cargado - Listo para continuar",
                                          fg=COLORES['exito'])
        else:
            self.entry_numero_fardo.delete(0, tk.END)
            self.entry_numero_fardo.insert(0, "1")
            self.primer_fardo_ingresado = False
            self.indicador_estado.configure(text="✏️ Ingrese el número del primer fardo",
                                          fg=COLORES['primario'])

    def guardar_automatico(self):
        """Guarda automáticamente el ticket después de cada fardo"""
        if self.ventana_principal.ticket_actual:
            try:
                # Obtener datos adicionales
                datos_adicionales = None
                if self.ventana_principal.panel_estadisticas:
                    datos_adicionales = self.ventana_principal.panel_estadisticas.obtener_datos_adicionales()
            
                # Guardar en base de datos
                if self.ventana_principal.bd.guardar_ticket(self.ventana_principal.ticket_actual, datos_adicionales):
                    self.ventana_principal.ticket_guardado = True
                    # Actualizar botón guardar para mostrar que está guardado
                    self.ventana_principal.btn_guardar.configure(text="✅ Auto-guardado")
                    self.ventana_principal.root.after(2000, 
                        lambda: self.ventana_principal.btn_guardar.configure(text="💾 Guardar"))
                
                    print(f"✅ Auto-guardado: Ticket {self.ventana_principal.ticket_actual.numero}")
            
            except Exception as e:
                print(f"⚠️ Error en auto-guardado: {str(e)}")
                # No mostrar error al usuario para no interrumpir el flujo
