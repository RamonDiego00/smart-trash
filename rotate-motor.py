import pigpio
import time

# Inicializa a interface com o pigpio
pi = pigpio.pi()

if not pi.connected:
    exit("Não foi possível conectar ao pigpiod")

SERVO_PIN = 13  # GPIO13 (pino 21 físico)

# Função para mover o servo para um ângulo específico
def set_servo_angle(angle):
    # Converte ângulo para largura de pulso (em microssegundos)
    pulse_width = 500 + (angle / 180.0) * 2000
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)

# Loop de teste: 0° -> 90° -> 180°
try:
    while True:
        set_servo_angle(0)
        print("Movendo para 0°")
        time.sleep(1)

        set_servo_angle(90)
        print("Movendo para 90°")
        time.sleep(1)

        set_servo_angle(180)
        print("Movendo para 180°")
        time.sleep(1)

except KeyboardInterrupt:
    print("Encerrando...")

finally:
    # Desliga o sinal PWM do servo
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()
