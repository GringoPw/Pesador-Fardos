# leer_balanza.py
import serial

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

buffer = ""

try:
    while True:
        if ser.in_waiting:
            byte = ser.read().decode('ascii', errors='ignore')
            if byte in ['\r', '\n']:  # Detectar fin de línea
                if buffer.strip():
                    print("Peso recibido:", buffer.strip())
                buffer = ""
            else:
                buffer += byte

except KeyboardInterrupt:
    print("Finalizado por el usuario.")
finally:
    ser.close()
