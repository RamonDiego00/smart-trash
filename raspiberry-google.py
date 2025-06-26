import numpy as np
import tflite_runtime.interpreter as tflite
from picamera2 import Picamera2
import cv2

def main():
    # Carrega o modelo e labels
    interpreter = tflite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()
    
    with open("labels.txt", "r") as f:
        labels = [line.strip() for line in f.readlines()]

    # Configuração da câmera com Picamera2
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"size": (224, 224), "format": "BGR888"})
    picam2.configure(config)
    picam2.start()

    # Detalhes de entrada/saída do modelo
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    try:
        while True:
            # Captura imagem com Picamera2
            image = picam2.capture_array()
            
            # Pré-processamento (normalização para int8)
            input_data = np.expand_dims(image, axis=0).astype(np.float32)
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
            
            # Mostra imagem com resultado (opcional)
            cv2.putText(image, f"{label} ({confidence*100:.1f}%)", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (0, 255, 0), 2)
            cv2.imshow("Classificação", image)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()