import sounddevice as sd
import pyttsx3
import time

def listar_dispositivos_audio():
    print("=== DISPOSITIVOS DE ÁUDIO DETECTADOS ===")
    dispositivos = sd.query_devices()
    for i, d in enumerate(dispositivos):
        tipo = []
        if d['max_input_channels'] > 0:
            tipo.append("Entrada")
        if d['max_output_channels'] > 0:
            tipo.append("Saída")
        print(f"{i}: {d['name']} ({' e '.join(tipo)})")
    print("========================================\n")


def listar_vozes(engine):
    vozes = engine.getProperty('voices')
    print("=== VOZES DISPONÍVEIS ===")
    for i, voz in enumerate(vozes):
        print(f"{i}: {voz.name} | ID: {voz.id}")
    print("==========================\n")
    return vozes


def falar_com_voz(frase):
    engine = pyttsx3.init()
    vozes = listar_vozes(engine)

    # Tentar selecionar voz em português do Brasil
    voz_selecionada = None
    for voz in vozes:
        if 'brazil' in voz.name.lower() or 'pt' in voz.id.lower():
            voz_selecionada = voz
            break

    if voz_selecionada:
        engine.setProperty('voice', 115)
        print(f"✅ Usando a voz: {voz_selecionada.name}\n")
    else:
        print("⚠️ Voz em português do Brasil não encontrada. Usando padrão.\n")

    engine.setProperty('rate', 130)  # velocidade mais lenta

    frases = frase.strip().split('.')
    for f in frases:
        f = f.strip()
        if f:
            engine.say(f)
            engine.runAndWait()
            time.sleep(0.6)  # pequena pausa entre frases


def main():
    listar_dispositivos_audio()

    # Frase fixa
    frase = "Coloque o lixo na plataforma. E aguarde 5 segundos."

    falar_com_voz(frase)

if __name__ == "__main__":
    main()
