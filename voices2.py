from gtts import gTTS
import os
import platform
import tempfile
import time

def falar_texto_google(texto, idioma='pt-br'):
    # Gerar áudio
    tts = gTTS(text=texto, lang=idioma)

    # Criar arquivo temporário para o áudio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        caminho_audio = fp.name
    tts.save(caminho_audio)

    # Reproduzir o áudio conforme o sistema operacional
    sistema = platform.system()
    if sistema == "Windows":
        os.system(f'start {caminho_audio}')
    elif sistema == "Darwin":  # macOS
        os.system(f'afplay {caminho_audio}')
    else:  # Linux
        os.system(f'mpg123 {caminho_audio}')  # mpg123 precisa estar instalado

    # Espera suficiente para a fala terminar (ou pode ser estimado com duração do áudio)
    time.sleep(6)

    # Remover arquivo temporário após a execução
    try:
        os.remove(caminho_audio)
    except Exception as e:
        print(f"Não foi possível remover o arquivo temporário: {e}")

def main():
    frase = "Coloque o lixo na plataforma. E aguarde... 5 segundos."
    print("🔊 Reproduzindo a mensagem com voz natural...")
    falar_texto_google(frase)

if __name__ == "__main__":
    main()
