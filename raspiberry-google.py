import numpy as np
import tflite_runtime.interpreter as tflite
from picamera2 import Picamera2
import cv2
import time
import pigpio

# ================== CONFIGURAÇÕES ==================
CONFIDENCE_THRESHOLD = 150.0
STABLE_TIME_REQUIRED = 1.5
SERVO_GPIO = 13  # GPIO físico 33
PULSE_LEFT = 1000   # µs ≈ -30°
PULSE_CENTER = 1500 # µs ≈ 0°
PULSE_RIGHT = 2000  # µs ≈ +30°
LABEL_LEFT = "2 Pilhas"
LABEL_RIGHT = "0 Fontes"
# ===================================================

def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Erro: não foi possível conectar ao pigpio.")
        return

    pi.set_servo_pulsewidth(SERVO_GPIO, PULSE_CENTER)

    interpreter = tflite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()
    with open("labels.txt", "r") as f:
        labels = [line.strip() for line in f.readlines()]

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (224, 224), "format": "BGR888"})
    picam2.configure(config)
    picam2.start()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_dtype = input_details[0]['dtype']

    # Controle de detecção e tempo
    last_detected_label = None
    detection_start_time = None
    ultima_acao_time = time.time()
    estado_atual = "CENTRO"

    try:
        while True:
            image = picam2.capture_array()

            # Prepara imagem
            if input_dtype == np.uint8:
                input_data = np.expand_dims(image, axis=0)
            else:
                input_data = np.expand_dims(image.astype(np.float32), axis=0)
                input_data = (input_data / 127.5) - 1

            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details[0]['index'])

            class_id = np.argmax(output_data[0])
            confidence = float(output_data[0][class_id])
            label = labels[class_id]

            print(f"Detectado: {label} ({confidence*100:.1f}%)")

            # Exibe texto na imagem
            cv2.putText(image, f"{label} ({confidence*100:.1f}%)", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Classificador", image)

            agora = time.time()

            print(agora)
            print(label)
            print(LABEL_LEFT, LABEL_RIGHT)
            print(confidence)
            print(CONFIDENCE_THRESHOLD)


            if confidence > CONFIDENCE_THRESHOLD and label in [LABEL_LEFT, LABEL_RIGHT]:
                print("Passou pela confian'ca")
                if label == last_detected_label:
                    if detection_start_time and (agora - detection_start_time) >= STABLE_TIME_REQUIRED:
                        print("Passou pelo tempo de duracao")
                        if label == LABEL_LEFT and estado_atual != "ESQUERDA":
                            print("Inclina para ESQUERDA")
                            pi.set_servo_pulsewidth(SERVO_GPIO, PULSE_LEFT)
                            estado_atual = "ESQUERDA"
                            ultima_acao_time = agora
                        elif label == LABEL_RIGHT and estado_atual != "DIREITA":
                            print("Inclina para DIREITA")
                            pi.set_servo_pulsewidth(SERVO_GPIO, PULSE_RIGHT)
                            estado_atual = "DIREITA"
                            ultima_acao_time = agora
                else:
                    last_detected_label = label
                    detection_start_time = agora
            else:
                last_detected_label = None
                detection_start_time = None

            # Voltar para centro se sem detecção por mais de 3s
            if agora - ultima_acao_time > 10 and estado_atual != "CENTRO":
                print("Retornando ao CENTRO")
                # Colocar um anuncio por voz via bluetooth                                                                            
                pi.set_servo_pulsewidth(SERVO_GPIO, PULSE_CENTER)
                estado_atual = "CENTRO"
                ultima_acao_time = agora

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        pi.set_servo_pulsewidth(SERVO_GPIO, 0)
        pi.stop()
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
