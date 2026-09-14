# Transcribe

Três utilitários independentes de linha de comando/GUI para conversão de
mídia e transcrição de áudio e vídeo, escritos em Python.

## Ferramentas

### Saturn

Conversor de mídia com interface gráfica (PySimpleGUI). Converte entre
ASF e MP4, e extrai trilhas de áudio de MP4 para MP3.

```sh
python saturn/saturn.py
```

### Ymir

Transcrição offline de vídeo/áudio para texto, com timestamp por palavra,
usando [Vosk](https://alphacephei.com/vosk/). Interface gráfica, roda
inteiramente local (sem enviar áudio para nenhum serviço externo).

```sh
python ymir/ymir.py
```

Requer um modelo Vosk baixado localmente. Por padrão o script procura em
`Modelos/Pt/vosk-model-small-pt-0.3` (relativo ao diretório de trabalho);
o caminho pode ser sobrescrito com a variável de ambiente `YMIR_MODELO`.
Baixe um modelo em https://alphacephei.com/vosk/models.

### Pluto

Transcrição rápida via linha de comando usando
[Whisper](https://github.com/openai/whisper).

```sh
python pluto/pluto.py caminho/para/audio.m4a
```

## Requisitos

- Python 3.9+
- [`ffmpeg`](https://ffmpeg.org/) disponível no `PATH` (usado por Saturn e Ymir)
- `pip install -r requirements.txt`

## Histórico

Os três utilitários passaram por algumas gerações antes de chegar à forma
atual:

- **Saturn** começou como um script baseado em `moviepy` fazendo apenas
  ASF → MP4. Passou a usar chamadas diretas ao `ffmpeg` (mais rápido e
  com menos dependências), ganhou conversão nos dois sentidos e, por
  fim, exportação para MP3 com tratamento de erros.
- **Ymir** começou transcrevendo o áudio inteiro em memória e imprimindo
  o resultado bruto. Ganhou, em iterações sucessivas: timestamps por
  palavra, normalização do áudio antes do reconhecimento (mono, 16kHz,
  ganho), atualização parcial da transcrição em tempo real na interface
  e tratamento de erros mais claro.
- **Pluto** é o mais simples dos três: um script único usando Whisper
  para transcrição rápida via linha de comando.

Versões intermediárias e artefatos de build/modelos vendorizados foram
removidos do repositório para manter o histórico limpo.
