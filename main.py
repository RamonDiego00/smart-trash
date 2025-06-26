import cv2
import numpy as np

# Inicializa a câmera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erro: Câmera não acessível.")
    exit()

print("Câmera ativa. Pressione 'q' para sair.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro: Frame não capturado.")
        break

    # Converte o frame para HSV (melhor para detecção de cores)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # --- DETECÇÃO DO CELULAR (supondo que seja um retângulo escuro/preto) ---
    # Define faixa de cor preta/escura (ajuste conforme necessário)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])
    mask_phone = cv2.inRange(hsv, lower_black, upper_black)

    # Encontra contornos na máscara
    contours, _ = cv2.findContours(mask_phone, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtra contornos grandes (celular tende a ser maior que ruídos)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 5000:  # Ajuste este valor conforme a distância da câmera
            # Aproxima o contorno para um polígono
            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
            if len(approx) == 4:  # Se for um quadrilátero (celular retangular)
                cv2.drawContours(frame, [approx], 0, (0, 255, 0), 3)
                cv2.putText(frame, "CELULAR", (approx.ravel()[0], approx.ravel()[1]), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # --- DETECÇÃO DO CABO (supondo que seja fino e longo) ---
    # Define faixa de cor (ex: cabos pretos ou coloridos - ajuste HSV!)
    lower_cable = np.array([0, 0, 0])  # Exemplo: preto
    upper_cable = np.array([180, 255, 100])
    mask_cable = cv2.inRange(hsv, lower_cable, upper_cable)

    # Operações morfológicas para remover ruídos
    kernel = np.ones((5, 5), np.uint8)
    mask_cable = cv2.morphologyEx(mask_cable, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask_cable, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 1000 < area < 5000:  # Cabos são menores que celulares
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            if aspect_ratio > 4 or aspect_ratio < 0.25:  # Formato alongado
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, "CABO", (x, y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Exibe o frame resultante
    cv2.imshow('Detector de E-Lixo', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()