import sounddevice as sd
import pyttsx3

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
    print("=== VOZES DISPONÍVEIS ===")
    vozes = engine.getProperty('voices')
    for i, voz in enumerate(vozes):
        print(f"{i}: {voz.name} | ID: {voz.id}")
    print("==========================\n")
    return vozes


def falar_com_voz(frase, nome_voz_parcial=None):
    engine = pyttsx3.init()
    vozes = listar_vozes(engine)

    if nome_voz_parcial:
        encontrada = False
        for voz in vozes:
            if nome_voz_parcial.lower() in voz.name.lower():
                engine.setProperty('voice', voz.id)
                encontrada = True
                print(f"✅ Usando a voz: {voz.name}\n")
                break
        if not encontrada:
            print("⚠️ Voz não encontrada. Usando voz padrão.\n")

    engine.say(frase)
    engine.runAndWait()


def main():
    # Etapa 1: Listar dispositivos
    listar_dispositivos_audio()

    # Usar a voz 171

    # Listar as frases em especifico

    # Etapa 2: Frase a ser falada
    frase = input("Digite a frase que você quer que o sistema fale: ")

    # Etapa 3: Nome (ou parte do nome) da voz desejada
    nome_voz = input("Digite parte do nome da voz desejada (ou deixe vazio para usar a padrão): ")

    # Etapa 4: Falar
    falar_com_voz(frase, nome_voz)

if __name__ == "__main__":
    main()
