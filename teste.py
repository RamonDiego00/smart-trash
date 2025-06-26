import cv2
import numpy as np
import os

# Inicializa o detector ORB
orb = cv2.ORB_create(nfeatures=1000)

# Função para carregar múltiplas imagens de referência e extrair descritores
def load_reference_images(folder_path):
    descriptors_list = []
    kp_list = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img_path = os.path.join(folder_path, filename)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            kp, des = orb.detectAndCompute(img, None)
            
            if des is not None:
                kp_list.append(kp)
                descriptors_list.append(des)
    
    # Concatena todos os descritores em um único array
    if descriptors_list:
        descriptors_combined = np.vstack(descriptors_list)
        return kp_list, descriptors_combined
    else:
        return None, None

# Carrega todas as imagens de referência (ajuste os caminhos das pastas!)
kp_celular, des_celular = load_reference_images("images-cellphone/")
kp_cabo, des_cabo = load_reference_images("images-cables/")

if des_celular is None or des_cabo is None:
    print("Erro: Nenhuma imagem de referência válida encontrada. Verifique as pastas.")
    exit()

# Inicializa a câmera e o matcher
cap = cv2.VideoCapture(0)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

print("Câmera ativa. Pressione 'q' para sair.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Erro: Frame não capturado.")
        break

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    kp_frame, des_frame = orb.detectAndCompute(gray_frame, None)

    # Função para detectar objetos com base nos descritores combinados
    def detect_object(ref_name, kp_ref_list, des_ref, frame, kp_frame, des_frame, threshold=15):
        if des_ref is not None and des_frame is not None:
            matches = bf.match(des_ref, des_frame)
            matches = sorted(matches, key=lambda x: x.distance)
            
            if len(matches) > threshold:
                # Usa o primeiro keypoint da lista como referência para desenho
                src_pts = np.float32([kp_ref_list[0][matches[0].queryIdx].pt]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp_frame[matches[0].trainIdx].pt]).reshape(-1, 1, 2)
                
                # Desenha um círculo no ponto correspondente
                for m in matches[:50]:  # Limita a quantidade para melhor visualização
                    dst_pos = tuple(map(int, kp_frame[m.trainIdx].pt))
                    cv2.circle(frame, dst_pos, 3, (0, 255, 0), -1)
                
                cv2.putText(frame, ref_name, (int(dst_pts[0][0][0]), int(dst_pts[0][0][1])),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return frame

    # Detecta celular e cabo
    if des_celular is not None:
        frame = detect_object("CELULAR", kp_celular, des_celular, frame, kp_frame, des_frame)
    if des_cabo is not None:
        frame = detect_object("CABO", kp_cabo, des_cabo, frame, kp_frame, des_frame)

    cv2.imshow('Detector de E-Lixo (Multiplas Referencias)', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()