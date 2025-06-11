# leer_balanza_cambios.py
import serial
import re

ser = serial.Serial(
    port='COM1',
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1,
    xonxoff=False,      # Soft handshake OFF
    rtscts=False,       # RTS/CTS OFF (hardware handshake OFF)
    dsrdtr=False        # DSR/DTR OFF (si querés activarlo, poné True)
)

# Activar DTR y RTS manualmente
ser.setDTR(True)
ser.setRTS(True)

print("Esperando datos de la balanza en COM1...")
print("Solo se mostrarán los cambios de peso...\n")

buffer = ""
peso_anterior = None

def extraer_peso(texto):
    """Extrae el valor numérico del peso del texto recibido"""
    # Buscar números con posibles decimales
    match = re.search(r'[-+]?\d*\.?\d+', texto)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None

try:
    while True:
        if ser.in_waiting:
            byte = ser.read().decode('ascii', errors='ignore')
            if byte in ['\r', '\n']:  # Detectar fin de línea
                if buffer.strip():
                    peso_actual = extraer_peso(buffer.strip())
                    
                    # Solo mostrar si el peso cambió
                    if peso_actual is not None and peso_actual != peso_anterior:
                        print(f"Peso: {peso_actual} kg")
                        peso_anterior = peso_actual
                        
                buffer = ""
            else:
                buffer += byte

except KeyboardInterrupt:
    print("\nFinalizado por el usuario.")
finally:
    ser.close()