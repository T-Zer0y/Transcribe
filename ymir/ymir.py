"""Ymir - transcrição offline de vídeo/áudio com timestamps, via Vosk.

Depende do binário `ffmpeg` no PATH e de um modelo Vosk baixado localmente
(veja o README na raiz do repositório).
"""

import json
import os
import subprocess
import uuid
import wave

import PySimpleGUI as sg
import threading
from vosk import KaldiRecognizer, Model, SetLogLevel

SetLogLevel(0)

CAMINHO_MODELO = os.environ.get("YMIR_MODELO", "Modelos/Pt/vosk-model-small-pt-0.3")


def transcrever_audio(arquivo_video, arquivo_saida, janela):
    try:
        # Extrai e normaliza o áudio (mono, 16kHz) para o formato esperado pelo Vosk
        arquivo_audio = f"{uuid.uuid4()}.wav"
        comando = (
            f'ffmpeg -i "{arquivo_video}" -ac 1 -ar 16000 -af "volume=1.5" '
            f'"{arquivo_audio}" -y'
        )
        processo = subprocess.Popen(
            comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        _, err = processo.communicate()
        if processo.returncode != 0:
            raise RuntimeError(f"Erro ao extrair áudio: {err.decode('utf-8', errors='replace')}")

        if not os.path.exists(CAMINHO_MODELO):
            raise FileNotFoundError(
                f"O caminho do modelo '{CAMINHO_MODELO}' não existe. Baixe e extraia o "
                "modelo em https://alphacephei.com/vosk/models."
            )

        modelo = Model(CAMINHO_MODELO)
        wf = wave.open(arquivo_audio, "rb")
        rec = KaldiRecognizer(modelo, wf.getframerate())
        rec.SetWords(True)

        transcricao = []
        while True:
            dados = wf.readframes(4000)
            if len(dados) == 0:
                break
            if rec.AcceptWaveform(dados):
                resultado = json.loads(rec.Result())
                transcricao.append(resultado)
                janela.write_event_value("-TRANSCRICAO-PARCIAL-", resultado)

        resultado_final = json.loads(rec.FinalResult())
        transcricao.append(resultado_final)
        janela.write_event_value("-TRANSCRICAO-PARCIAL-", resultado_final)

        wf.close()
        os.remove(arquivo_audio)

        # Achata os segmentos em uma lista de palavras com timestamp
        texto_transcricao = [
            f"[{p['start']:.2f} - {p['end']:.2f}] {p['word']}"
            for segmento in transcricao
            if "result" in segmento
            for p in segmento["result"]
        ]

        with open(arquivo_saida, "w", encoding="utf-8") as f:
            f.write("\n".join(texto_transcricao))

        janela.write_event_value("-CONCLUSAO-", "\n".join(texto_transcricao))
    except Exception as e:
        janela.write_event_value("-ERRO-", str(e))


layout = [
    [sg.Text("Selecione o arquivo de vídeo (ASF ou MP4)")],
    [
        sg.In(),
        sg.FileBrowse(
            button_text="Selecionar",
            file_types=(("Arquivos ASF", "*.asf"), ("Arquivos MP4", "*.mp4")),
        ),
    ],
    [sg.Text("Salvar transcrição como")],
    [sg.In(), sg.SaveAs(button_text="Salvar Como", file_types=(("Arquivos TXT", "*.txt"),))],
    [sg.Button("Iniciar Transcrição", key="Transcrever")],
    [sg.Text("", size=(40, 1), key="status")],
    [sg.Multiline(size=(60, 20), key="transcription", disabled=True)],
]

janela = sg.Window("Ymir", layout, margins=(100, 50))

while True:
    evento, valores = janela.read(timeout=100)
    if evento == sg.WINDOW_CLOSED:
        break
    if evento == "Transcrever":
        arquivo_video = valores[0]
        arquivo_saida = valores[1]
        janela["status"].update(value="Transcrição em progresso...")
        janela["transcription"].update(value="")
        threading.Thread(
            target=transcrever_audio, args=(arquivo_video, arquivo_saida, janela), daemon=True
        ).start()

    if evento == "-TRANSCRICAO-PARCIAL-":
        parcial = valores[evento]
        if "result" in parcial:
            texto = "\n".join(
                f"[{p['start']:.2f} - {p['end']:.2f}] {p['word']}" for p in parcial["result"]
            )
            janela["transcription"].update(janela["transcription"].get() + "\n" + texto)
    elif evento == "-CONCLUSAO-":
        janela["status"].update(value="Transcrição concluída!")
        janela["transcription"].update(value=valores[evento])
        sg.popup("Transcrição Concluída!", "A transcrição do seu arquivo foi concluída com sucesso.")
    elif evento == "-ERRO-":
        janela["status"].update(value="Erro na transcrição")
        sg.popup("Erro na Transcrição", f"Ocorreu um erro durante a transcrição: {valores['-ERRO-']}")

janela.close()
