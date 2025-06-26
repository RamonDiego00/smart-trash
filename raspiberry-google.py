import numpy as np
import tflite_runtime.interpreter as tflite
from picamera import PiCamera
import time
import cv2

# Carrega o modelo e labels
interpreter = tflite.Interpreter(model_path="modelo.tflite")
interpreter.allocate_tensors()

with open("labels.txt", "r") as f:
    labels = [line.strip() for line in f.readlines()]

# Configuração da câmera
camera = PiCamera()
camera.resolution = (224, 224)  # Verifique o tamanho de entrada do seu modelo
raw_capture = np.empty((224, 224, 3), dtype=np.uint8)

# Detalhes de entrada/saída do modelo
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

try:
    while True:
        # Captura imagem
        camera.capture(raw_capture, format="bgr")
        
        # Pré-processamento (normalização para int8)
        input_data = np.expand_dims(raw_capture, axis=0).astype(np.float32)
        input_data = (input_data / 127.5) - 1  # Normalização para modelos quantizados
        
        # Inferência
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        
        # Resultado
        class_id = np.argmax(output_data[0])
        confidence = float(output_data[0][class_id])
        label = labels[class_id]
        
        print(f"Objeto: {label} - Confiança: {confidence*100:.1f}%")
        
        # Mostra imagem (opcional)
        cv2.imshow("Classificação", raw_capture)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
finally:
    camera.close()
    cv2.destroyAllWindows()