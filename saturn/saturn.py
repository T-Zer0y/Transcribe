"""Saturn - conversor de mídia com GUI (ASF <-> MP4, MP4 -> MP3).

Depende do binário `ffmpeg` disponível no PATH do sistema.
"""

import subprocess
import threading

import PySimpleGUI as sg


def _rodar_ffmpeg(comando, janela):
    try:
        processo = subprocess.Popen(
            comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        _, err = processo.communicate()
        if processo.returncode != 0:
            raise RuntimeError(err.decode("utf-8", errors="replace"))
        janela.write_event_value("-CONCLUSAO-", None)
    except Exception as e:
        janela.write_event_value("-ERRO-", str(e))


def converter_asf_para_mp4(arquivo_asf, arquivo_mp4, janela):
    comando = f'ffmpeg -i "{arquivo_asf}" -vcodec libx264 -acodec aac "{arquivo_mp4}"'
    _rodar_ffmpeg(comando, janela)


def converter_mp4_para_asf(arquivo_mp4, arquivo_asf, janela):
    comando = f'ffmpeg -i "{arquivo_mp4}" -vcodec wmv2 -acodec wmav2 "{arquivo_asf}"'
    _rodar_ffmpeg(comando, janela)


def converter_mp4_para_mp3(arquivo_mp4, arquivo_mp3, janela):
    comando = f'ffmpeg -i "{arquivo_mp4}" -vn -acodec libmp3lame "{arquivo_mp3}"'
    _rodar_ffmpeg(comando, janela)


layout = [
    [sg.Text("Selecione o arquivo de entrada")],
    [
        sg.In(),
        sg.FileBrowse(
            button_text="Selecionar",
            file_types=(("Arquivos ASF", "*.asf"), ("Arquivos MP4", "*.mp4")),
        ),
    ],
    [sg.Text("Salvar como arquivo de saída")],
    [
        sg.In(),
        sg.SaveAs(
            button_text="Salvar Como",
            file_types=(
                ("Arquivos ASF", "*.asf"),
                ("Arquivos MP4", "*.mp4"),
                ("Arquivos MP3", "*.mp3"),
            ),
        ),
    ],
    [sg.Button("Iniciar Conversão", key="Converter")],
    [sg.Text("", size=(15, 1), key="status")],
]

janela = sg.Window("Saturn", layout, margins=(100, 50))

while True:
    evento, valores = janela.read(timeout=100)
    if evento == sg.WINDOW_CLOSED:
        break
    if evento == "Converter":
        arquivo_entrada = valores[0]
        arquivo_saida = valores[1]
        janela["status"].update(value="Em progresso...")

        if arquivo_entrada.endswith(".asf") and arquivo_saida.endswith(".mp4"):
            alvo = converter_asf_para_mp4
        elif arquivo_entrada.endswith(".mp4") and arquivo_saida.endswith(".asf"):
            alvo = converter_mp4_para_asf
        elif arquivo_entrada.endswith(".mp4") and arquivo_saida.endswith(".mp3"):
            alvo = converter_mp4_para_mp3
        else:
            janela["status"].update(value="Combinação de formatos não suportada")
            continue

        threading.Thread(
            target=alvo, args=(arquivo_entrada, arquivo_saida, janela), daemon=True
        ).start()

    if evento == "-CONCLUSAO-":
        janela["status"].update(value="Conversão concluída!")
        sg.popup("Conversão Concluída!", "Seu arquivo foi convertido com sucesso.")
    elif evento == "-ERRO-":
        janela["status"].update(value="Erro na conversão")
        sg.popup("Erro na Conversão", f"Ocorreu um erro durante a conversão: {valores['-ERRO-']}")

janela.close()
