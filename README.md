# Video Transcriber

Транскрибация видео с YouTube, VK Video или локальных файлов в текст с помощью
[faster-whisper](https://github.com/SYSTRAN/faster-whisper) и [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- `ffmpeg` в `PATH` — нужен `yt-dlp` для некоторых форматов и кодеков.

## Установка

```bash
uv sync