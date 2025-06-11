#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detector Automático de Balanza - Sistema de Pesaje de Fardos
Programa de consola para detectar automáticamente la configuración ideal de cualquier balanza

Autor: Sistema de Pesaje
Fecha: 2024
"""

import serial
import serial.tools.list_ports
import time
import re
import json
import os
from datetime import datetime


class DetectorBalanza:
    """Detector automático de configuración de balanza"""

    def __init__(self):
        self.configuraciones_detectadas = []
        self.mejor_configuracion = None

        # Configuraciones a probar
        self.puertos_disponibles = []
        self.baudrates = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
        self.protocolos = {
            'CONTINUO': {'comando': b'', 'descripcion': 'Lectura continua (sin comando)'},
            'ESTANDAR': {'comando': b'P\r\n', 'descripcion': 'Comando P estándar'},
            'TOLEDO': {'comando': b'W\r\n', 'descripcion': 'Protocolo Toledo'},
            'AND': {'comando': b'Q\r\n', 'descripcion': 'Protocolo AND'},
            'OHAUS': {'comando': b'IP\r\n', 'descripcion': 'Protocolo Ohaus'},
            'METTLER': {'comando': b'S\r\n', 'descripcion': 'Protocolo Mettler'},
            'CAS': {'comando': b'R\r\n', 'descripcion': 'Protocolo CAS'},
            'DIBAL': {'comando': b'P\r', 'descripcion': 'Protocolo Dibal'},
            'DIGI': {'comando': b'W', 'descripcion': 'Protocolo Digi'},
            'GAMA': {'comando': b'\r\n', 'descripcion': 'Protocolo GAMA'}
        }

        self.configuraciones_dtr_rts = [
            {'dtr': True, 'rts': True, 'descripcion': 'DTR y RTS activados'},
            {'dtr': True, 'rts': False, 'descripcion': 'Solo DTR activado'},
            {'dtr': False, 'rts': True, 'descripcion': 'Solo RTS activado'},
            {'dtr': False, 'rts': False, 'descripcion': 'DTR y RTS desactivados'}
        ]

    def mostrar_banner(self):
        """Muestra el banner del programa"""
        print("=" * 80)
        print("🔍 DETECTOR AUTOMÁTICO DE BALANZA")
        print("   Sistema de Pesaje de Fardos v2.0")
        print("=" * 80)
        print()
        print("Este programa detectará automáticamente la configuración")
        print("ideal para su balanza y generará el archivo de configuración.")
        print()

    def detectar_puertos(self):
        """Detecta todos los puertos COM disponibles"""
        print("🔌 Detectando puertos COM disponibles...")

        try:
            puertos = list(serial.tools.list_ports.comports())
            self.puertos_disponibles = []

            for puerto in puertos:
                self.puertos_disponibles.append({
                    'puerto': puerto.device,
                    'descripcion': puerto.description,
                    'fabricante': puerto.manufacturer or 'Desconocido'
                })

            if self.puertos_disponibles:
                print(
                    f"✅ Encontrados {len(self.puertos_disponibles)} puertos:")
                for i, puerto in enumerate(self.puertos_disponibles, 1):
                    print(
                        f"   {i}. {puerto['puerto']} - {puerto['descripcion']}")
                    print(f"      Fabricante: {puerto['fabricante']}")
            else:
                print("❌ No se encontraron puertos COM disponibles")
                return False

            return True

        except Exception as e:
            print(f"❌ Error al detectar puertos: {e}")
            return False

    def probar_configuracion(self, puerto, baudrate, protocolo, dtr_rts):
        """Prueba una configuración específica"""
        try:
            # Crear conexión
            with serial.Serial(
                port=puerto,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=2,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False
            ) as ser:

                # Configurar DTR y RTS
                ser.setDTR(dtr_rts['dtr'])
                ser.setRTS(dtr_rts['rts'])

                # Limpiar buffers
                ser.reset_input_buffer()
                ser.reset_output_buffer()

                # Esperar un momento para estabilizar
                time.sleep(0.5)

                # Probar protocolo
                resultado = self.probar_protocolo(ser, protocolo)

                if resultado['exito']:
                    configuracion = {
                        'puerto': puerto,
                        'baudrate': baudrate,
                        'protocolo': protocolo,
                        'dtr': dtr_rts['dtr'],
                        'rts': dtr_rts['rts'],
                        'peso_detectado': resultado['peso'],
                        'respuesta_cruda': resultado['respuesta_cruda'],
                        'calidad': resultado['calidad'],
                        'timestamp': datetime.now().isoformat()
                    }

                    self.configuraciones_detectadas.append(configuracion)
                    return configuracion

                return None

        except Exception as e:
            return None

    def probar_protocolo(self, conexion, protocolo):
        """Prueba un protocolo específico"""
        try:
            comando = self.protocolos[protocolo]['comando']

            if protocolo == 'CONTINUO':
                # Para protocolo continuo, solo escuchar
                return self.escuchar_datos_continuos(conexion)
            else:
                # Para otros protocolos, enviar comando
                return self.enviar_comando_y_leer(conexion, comando, protocolo)

        except Exception as e:
            return {'exito': False, 'error': str(e)}

    def escuchar_datos_continuos(self, conexion):
        """Escucha datos de balanzas que envían continuamente - MEJORADO"""
        buffer = ""
        datos_recibidos = []
        tiempo_inicio = time.time()

        print("🔍 Escuchando datos continuos...")

        while time.time() - tiempo_inicio < 4:  # Escuchar por 4 segundos
            if conexion.in_waiting:
                try:
                    byte = conexion.read().decode('ascii', errors='ignore')

                    if byte in ['\r', '\n']:
                        if buffer.strip():
                            linea = buffer.strip()
                            datos_recibidos.append(linea)
                            print(f"📡 Recibido: '{linea}'")

                            # Si tenemos suficientes muestras, analizar
                            if len(datos_recibidos) >= 3:
                                break
                        buffer = ""
                    else:
                        buffer += byte

                except Exception as e:
                    print(f"⚠️ Error leyendo byte: {e}")
                    continue
            else:
                time.sleep(0.01)

        if datos_recibidos:
            print(f"📊 Analizando {len(datos_recibidos)} líneas recibidas...")

            # Analizar todos los datos
            pesos_detectados = []
            for dato in datos_recibidos:
                peso = self._extraer_peso_de_cadena(dato)
                if peso >= 0:  # Incluir peso 0 como válido
                    pesos_detectados.append(peso)

            if pesos_detectados:
                # Calcular estadísticas
                peso_promedio = sum(pesos_detectados) / len(pesos_detectados)
                peso_min = min(pesos_detectados)
                peso_max = max(pesos_detectados)

                print(f"✅ Pesos detectados: {pesos_detectados}")
                print(
                    f"📈 Promedio: {peso_promedio:.2f}, Min: {peso_min:.2f}, Max: {peso_max:.2f}")

                calidad = self.calcular_calidad_lectura(
                    pesos_detectados, datos_recibidos)

                return {
                    'exito': True,
                    'peso': peso_promedio,
                    'respuesta_cruda': datos_recibidos,
                    'calidad': calidad,
                    'estadisticas': {
                        'promedio': peso_promedio,
                        'minimo': peso_min,
                        'maximo': peso_max,
                        'variacion': peso_max - peso_min
                    }
                }

        print("❌ No se recibieron datos válidos")
        return {'exito': False}

    def enviar_comando_y_leer(self, conexion, comando, protocolo):
        """Envía comando y lee respuesta"""
        try:
            # Enviar comando
            conexion.write(comando)
            time.sleep(0.5)

            # Leer respuesta
            respuestas = []
            for _ in range(3):  # Intentar 3 veces
                respuesta = conexion.readline().decode('ascii', errors='ignore').strip()
                if respuesta:
                    respuestas.append(respuesta)
                time.sleep(0.2)

            if respuestas:
                # Analizar respuestas
                pesos_detectados = []
                for respuesta in respuestas:
                    peso = self.extraer_peso_de_cadena(respuesta)
                    if peso > 0:
                        pesos_detectados.append(peso)

                if pesos_detectados:
                    peso_promedio = sum(pesos_detectados) / \
                        len(pesos_detectados)
                    calidad = self.calcular_calidad_lectura(
                        pesos_detectados, respuestas)

                    return {
                        'exito': True,
                        'peso': peso_promedio,
                        'respuesta_cruda': respuestas,
                        'calidad': calidad
                    }

            return {'exito': False}

        except Exception as e:
            return {'exito': False, 'error': str(e)}

    def extraer_peso_de_cadena(self, cadena):
        """Extrae el peso de una cadena"""
        try:
            # Buscar números con punto decimal
            patron_decimal = r'[-+]?\s*\d+\.\d+'
            match = re.search(patron_decimal, cadena)
            if match:
                return float(match.group().replace(' ', ''))

            # Buscar números enteros
            patron_entero = r'[-+]?\s*\d+'
            match = re.search(patron_entero, cadena)
            if match:
                return float(match.group().replace(' ', ''))

            return 0.0

        except:
            return 0.0

    def _extraer_peso_de_cadena(self, cadena):
        """Extrae el peso de una cadena - MEJORADO para todas las balanzas"""
        try:
            print(f"🔍 Analizando: '{cadena}' (len: {len(cadena)})")

            # Limpiar la cadena
            cadena_limpia = cadena.strip()

            # Patrones específicos para diferentes balanzas

            # 1. Balanza GAMA - Formato: ST,GS,+000000
            if "ST,GS," in cadena_limpia:
                match = re.search(r'ST,GS,([+-]?\d+)', cadena_limpia)
                if match:
                    numero = int(match.group(1))
                    # Convertir según el formato de tu balanza
                    peso = numero / 100.0  # Ajustar divisor según necesidad
                    print(f"✅ GAMA detectado: {numero} -> {peso:.2f} kg")
                    return peso

            # 2. Detectar mensajes de peso cero
            patrones_cero = ["000000", "0000000", "+000000",
                             "+0000000", "no weight", "sin peso"]
            if any(patron in cadena_limpia.lower() for patron in patrones_cero):
                print("🔄 Peso cero detectado")
                return 0.0

            # 3. Formato con unidades explícitas (ej: "25.34 kg", "1234 g")
            patron_con_unidad = r'([-+]?\s*\d+\.?\d*)\s*(kg|g|lb)'
            match = re.search(patron_con_unidad, cadena_limpia.lower())
            if match:
                numero = float(match.group(1).replace(' ', ''))
                unidad = match.group(2)
                if unidad == 'g':
                    numero = numero / 1000.0  # Convertir gramos a kg
                elif unidad == 'lb':
                    numero = numero * 0.453592  # Convertir libras a kg
                print(f"✅ Con unidad {unidad}: {numero:.2f} kg")
                return numero

            # 4. Números con punto decimal
            patron_decimal = r'[-+]?\s*\d+\.\d+'
            match = re.search(patron_decimal, cadena_limpia)
            if match:
                numero_str = match.group().replace(' ', '')
                peso = float(numero_str)
                print(f"✅ Decimal: '{numero_str}' -> {peso:.2f} kg")
                return peso

            # 5. Números enteros grandes (probablemente en gramos)
            patron_entero_grande = r'[-+]?\s*\d{4,}'
            match = re.search(patron_entero_grande, cadena_limpia)
            if match:
                numero_str = match.group().replace(' ', '')
                numero = float(numero_str)
                if numero > 1000:
                    peso = numero / 1000.0  # Asumir gramos
                    print(
                        f"✅ Entero grande (g->kg): '{numero_str}' -> {peso:.2f} kg")
                    return peso
                else:
                    print(
                        f"✅ Entero grande: '{numero_str}' -> {numero:.2f} kg")
                    return numero

            # 6. Cualquier número
            patron_numero = r'[-+]?\s*\d+'
            match = re.search(patron_numero, cadena_limpia)
            if match:
                numero_str = match.group().replace(' ', '')
                peso = float(numero_str)
                print(f"✅ Número: '{numero_str}' -> {peso:.2f} kg")
                return peso

            print(f"❌ No se extrajo peso de: '{cadena}'")
            return 0.0

        except Exception as e:
            print(f"⚠️ Error extrayendo peso: {e}")
            return 0.0

    def calcular_calidad_lectura(self, pesos, respuestas_crudas):
        """Calcula la calidad de la lectura - MEJORADO"""
        if not pesos:
            return 0

        # Factor 1: Consistencia de datos
        consistencia = 0
        if len(pesos) > 1:
            variacion = max(pesos) - min(pesos)
            if variacion == 0:  # Perfectamente consistente
                consistencia = 100
            elif variacion < 0.1:  # Muy consistente
                consistencia = 95
            elif variacion < 0.5:  # Bastante consistente
                consistencia = 85
            elif variacion < 1.0:  # Moderadamente consistente
                consistencia = 70
            elif variacion < 5.0:  # Poco consistente
                consistencia = 50
            else:
                consistencia = 20
        else:
            consistencia = 60  # Una sola lectura

        # Factor 2: Velocidad de respuesta
        velocidad = min(100, len(respuestas_crudas) * 15)

        # Factor 3: Calidad del formato de datos
        formato = 0
        datos_numericos = 0
        for respuesta in respuestas_crudas:
            if any(char.isdigit() for char in respuesta):
                datos_numericos += 1
            if '.' in respuesta:  # Datos decimales son mejores
                formato += 10
            if len(respuesta) > 5:  # Respuestas más largas suelen ser más informativas
                formato += 5

        if datos_numericos > 0:
            formato += (datos_numericos / len(respuestas_crudas)) * 50
        formato = min(100, formato)

        # Factor 4: Estabilidad (pesos no todos cero)
        estabilidad = 0
        pesos_no_cero = [p for p in pesos if p > 0]
        if pesos_no_cero:
            estabilidad = min(100, (len(pesos_no_cero) / len(pesos)) * 100)
        else:
            estabilidad = 30  # Penalizar si todos son cero, pero no eliminar

        # Calidad total (promedio ponderado)
        calidad_total = (
            consistencia * 0.35 +  # 35% consistencia
            velocidad * 0.25 +     # 25% velocidad
            formato * 0.25 +       # 25% formato
            estabilidad * 0.15     # 15% estabilidad
        )

        return round(calidad_total)

    def ejecutar_deteccion_completa(self):
        """Ejecuta la detección completa"""
        print("🔍 Iniciando detección automática de balanza...")
        print()

        total_pruebas = len(self.puertos_disponibles) * len(self.baudrates) * \
            len(self.protocolos) * len(self.configuraciones_dtr_rts)
        prueba_actual = 0

        for puerto_info in self.puertos_disponibles:
            puerto = puerto_info['puerto']
            print(f"📡 Probando puerto {puerto}...")

            for baudrate in self.baudrates:
                for protocolo in self.protocolos:
                    for dtr_rts in self.configuraciones_dtr_rts:
                        prueba_actual += 1
                        progreso = (prueba_actual / total_pruebas) * 100

                        print(
                            f"\r   Progreso: {progreso:.1f}% - {baudrate} bps, {protocolo}, {dtr_rts['descripcion']}", end='', flush=True)

                        config = self.probar_configuracion(
                            puerto, baudrate, protocolo, dtr_rts)
                        if config:
                            print(f"\n   ✅ Configuración válida encontrada!")
                            print(
                                f"      Peso detectado: {config['peso_detectado']:.2f} kg")
                            print(f"      Calidad: {config['calidad']}%")

            print()  # Nueva línea después de cada puerto

        print(
            f"\n🎯 Detección completada. Encontradas {len(self.configuraciones_detectadas)} configuraciones válidas.")

    def seleccionar_mejor_configuracion(self):
        """Selecciona la mejor configuración basada en calidad"""
        if not self.configuraciones_detectadas:
            return None

        # Ordenar por calidad (descendente)
        self.configuraciones_detectadas.sort(
            key=lambda x: x['calidad'], reverse=True)
        self.mejor_configuracion = self.configuraciones_detectadas[0]

        return self.mejor_configuracion

    def mostrar_resultados(self):
        """Muestra los resultados de la detección"""
        if not self.configuraciones_detectadas:
            print("❌ No se encontraron configuraciones válidas.")
            print("\nPosibles causas:")
            print("• La balanza no está conectada o encendida")
            print("• Cable de comunicación defectuoso")
            print("• Balanza con protocolo no estándar")
            print("• Problemas de permisos en puertos COM")
            return

        print("\n" + "=" * 60)
        print("📊 RESULTADOS DE LA DETECCIÓN")
        print("=" * 60)

        print(
            f"\n🎯 MEJOR CONFIGURACIÓN (Calidad: {self.mejor_configuracion['calidad']}%):")
        print(f"   Puerto: {self.mejor_configuracion['puerto']}")
        print(f"   Baudrate: {self.mejor_configuracion['baudrate']} bps")
        print(f"   Protocolo: {self.mejor_configuracion['protocolo']}")
        print(f"   DTR: {self.mejor_configuracion['dtr']}")
        print(f"   RTS: {self.mejor_configuracion['rts']}")
        print(
            f"   Peso detectado: {self.mejor_configuracion['peso_detectado']:.2f} kg")

        if len(self.configuraciones_detectadas) > 1:
            print(
                f"\n📋 OTRAS CONFIGURACIONES VÁLIDAS ({len(self.configuraciones_detectadas)-1}):")
            for i, config in enumerate(self.configuraciones_detectadas[1:], 2):
                print(
                    f"   {i}. {config['puerto']} - {config['baudrate']} bps - {config['protocolo']} (Calidad: {config['calidad']}%)")

    def exportar_configuracion(self):
        """Exporta la configuración al archivo del sistema"""
        if not self.mejor_configuracion:
            print("❌ No hay configuración para exportar")
            return False

        try:
            # Crear configuración para el sistema principal
            config_sistema = {
                'BALANZA_CONFIG': {
                    'puerto_serie': self.mejor_configuracion['puerto'],
                    'baudrate': self.mejor_configuracion['baudrate'],
                    'timeout': 1,
                    'protocolo': self.mejor_configuracion['protocolo'],
                    'activar_dtr': self.mejor_configuracion['dtr'],
                    'activar_rts': self.mejor_configuracion['rts']
                },
                'DETECCION_INFO': {
                    'fecha_deteccion': self.mejor_configuracion['timestamp'],
                    'peso_detectado': self.mejor_configuracion['peso_detectado'],
                    'calidad': self.mejor_configuracion['calidad'],
                    # Solo primeras 3 respuestas
                    'respuesta_cruda': self.mejor_configuracion['respuesta_cruda'][:3]
                }
            }

            # Guardar en archivo JSON
            with open('balanza_config_detectada.json', 'w', encoding='utf-8') as f:
                json.dump(config_sistema, f, indent=4, ensure_ascii=False)

            # Generar archivo Python para importar
            config_python = f'''# Configuración de balanza detectada automáticamente
# Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# Calidad de detección: {self.mejor_configuracion['calidad']}%

BALANZA_CONFIG = {{
    'puerto_serie': '{self.mejor_configuracion['puerto']}',
    'baudrate': {self.mejor_configuracion['baudrate']},
    'timeout': 1,
    'protocolo': '{self.mejor_configuracion['protocolo']}',
    'activar_dtr': {self.mejor_configuracion['dtr']},
    'activar_rts': {self.mejor_configuracion['rts']},
}}

# Información de detección
DETECCION_INFO = {{
    'fecha_deteccion': '{self.mejor_configuracion['timestamp']}',
    'peso_detectado': {self.mejor_configuracion['peso_detectado']},
    'calidad': {self.mejor_configuracion['calidad']},
}}
'''

            with open('balanza_config_detectada.py', 'w', encoding='utf-8') as f:
                f.write(config_python)

            print("\n✅ Configuración exportada exitosamente:")
            print("   📄 balanza_config_detectada.json")
            print("   🐍 balanza_config_detectada.py")
            print("\nPara usar esta configuración en su sistema:")
            print("1. Copie el contenido de balanza_config_detectada.py")
            print("2. Reemplace BALANZA_CONFIG en config/configuracion.py")
            print("3. Reinicie el sistema principal")

            return True

        except Exception as e:
            print(f"❌ Error al exportar configuración: {e}")
            return False

    def menu_interactivo(self):
        """Menú interactivo para el usuario"""
        while True:
            print("\n" + "=" * 50)
            print("🔧 MENÚ DE OPCIONES")
            print("=" * 50)
            print("1. 🔍 Ejecutar detección automática")
            print("2. 📊 Mostrar resultados")
            print("3. 💾 Exportar configuración")
            print("4. 🔄 Probar configuración actual")
            print("5. ❌ Salir")
            print()

            try:
                opcion = input("Seleccione una opción (1-5): ").strip()

                if opcion == '1':
                    if self.puertos_disponibles:
                        self.ejecutar_deteccion_completa()
                        if self.configuraciones_detectadas:
                            self.seleccionar_mejor_configuracion()
                            self.mostrar_resultados()
                    else:
                        print("❌ No hay puertos disponibles para probar")

                elif opcion == '2':
                    self.mostrar_resultados()

                elif opcion == '3':
                    if self.mejor_configuracion:
                        self.exportar_configuracion()
                    else:
                        print("❌ Primero debe ejecutar la detección")

                elif opcion == '4':
                    self.probar_configuracion_actual()

                elif opcion == '5':
                    print("👋 ¡Hasta luego!")
                    break

                else:
                    print("❌ Opción no válida")

            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def probar_configuracion_actual(self):
        """Prueba la configuración actual del sistema"""
        try:
            # Intentar cargar configuración actual
            if os.path.exists('config/configuracion.py'):
                import sys
                sys.path.append('.')
                from config.configuracion import BALANZA_CONFIG

                print("🔧 Probando configuración actual del sistema...")
                print(f"   Puerto: {BALANZA_CONFIG['puerto_serie']}")
                print(f"   Baudrate: {BALANZA_CONFIG['baudrate']}")

                # Crear configuración para probar
                dtr_rts = {
                    'dtr': BALANZA_CONFIG.get('activar_dtr', True),
                    'rts': BALANZA_CONFIG.get('activar_rts', True)
                }

                config = self.probar_configuracion(
                    BALANZA_CONFIG['puerto_serie'],
                    BALANZA_CONFIG['baudrate'],
                    BALANZA_CONFIG.get('protocolo', 'CONTINUO'),
                    dtr_rts
                )

                if config:
                    print(f"✅ Configuración actual funciona correctamente")
                    print(
                        f"   Peso detectado: {config['peso_detectado']:.2f} kg")
                    print(f"   Calidad: {config['calidad']}%")
                else:
                    print("❌ La configuración actual no funciona")
                    print(
                        "   Ejecute la detección automática para encontrar una configuración válida")
            else:
                print("❌ No se encontró archivo de configuración")

        except Exception as e:
            print(f"❌ Error al probar configuración actual: {e}")

    def ejecutar(self):
        """Ejecuta el programa principal"""
        self.mostrar_banner()

        if not self.detectar_puertos():
            input("\nPresione Enter para salir...")
            return

        self.menu_interactivo()


def main():
    """Función principal"""
    try:
        detector = DetectorBalanza()
        detector.ejecutar()
    except KeyboardInterrupt:
        print("\n👋 Programa interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        input("Presione Enter para salir...")


if __name__ == "__main__":
    main()
