
import serial
import time

# Windows PC 使用 COM3
arduino = serial.Serial(
    port="COM4",
    baudrate=9600,
    timeout=1
)

# 等待 Arduino UNO 重啟
time.sleep(2)

print("Connected to Arduino UNO")

try:
    while True:
        frequency = int(input(
            "Enter FREQUENCY (1-1000): "
        ))

        if 1 <= frequency <= 1000:
            arduino.write(
                f"{frequency}\n".encode("utf-8")
            )
            print(f"Sent FREQUENCY = {frequency}")
        else:
            print("Please enter 1-1000")

except (KeyboardInterrupt, EOFError):
    print("\nProgram stopped")

finally:
    arduino.close()
