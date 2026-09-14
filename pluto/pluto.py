"""Pluto - transcrição rápida de áudio via Whisper (linha de comando).

Uso: python pluto.py caminho/para/audio.m4a
"""

import sys

import whisper


def main():
    if len(sys.argv) != 2:
        print("Uso: python pluto.py <arquivo de áudio>")
        raise SystemExit(1)

    modelo = whisper.load_model("base")
    resultado = modelo.transcribe(sys.argv[1])
    print(resultado["text"])


if __name__ == "__main__":
    main()
