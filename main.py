#!/usr/bin/env python3
"""Транскрибация видео/аудио в текст с помощью faster-whisper."""

import argparse
import tempfile
from pathlib import Path

import yt_dlp
from faster_whisper import BatchedInferencePipeline, WhisperModel
import os
import site
from pathlib import Path

# Добавляем пути к CUDA-библиотекам, установленным через pip (nvidia-*-cu12)
for sp in site.getsitepackages():
    nvidia_dir = Path(sp) / "nvidia"
    if nvidia_dir.exists():
        for lib_dir in nvidia_dir.glob("*/lib"):
            os.environ["LD_LIBRARY_PATH"] = (
                str(lib_dir) + ":" + os.environ.get("LD_LIBRARY_PATH", "")
            )

def download_audio(url: str) -> str:
    """Скачивает аудио по URL (YouTube, VK и др.) во временную папку."""
    temp_dir = tempfile.mkdtemp(prefix="whisper_dl_")
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "outtmpl": f"{temp_dir}/%(title)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "fixup": "never", 
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    print(f"⬇️  Аудио скачано: {filename}")
    return filename


def transcribe(
    media_path: str,
    model_size: str = "large-v3-turbo",
    language: str | None = None,
    output: str = "transcription.txt",
) -> None:
    """Транскрибирует медиафайл и сохраняет результат в текстовый файл."""
    print(f"🧠 Загрузка модели {model_size} (device=auto)...")
    model = WhisperModel(model_size, device="auto", compute_type="auto")
    batched_model = BatchedInferencePipeline(model=model)

    print("✍️  Транскрибация...")
    segments, _info = batched_model.transcribe(
        media_path,
        language=language,
        batch_size=8,
        vad_filter=True,
    )

    out_path = Path(output)
    with out_path.open("w", encoding="utf-8") as f:
        for segment in segments:
            line = f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n"
            f.write(line)
            print(line, end="")

    print(f"\n✅ Готово. Текст сохранён в {out_path}")


def prompt_source() -> str:
    """Интерактивно спрашивает источник, если он не передан аргументом."""
    print("📥 Что транскрибируем?")
    print("   • Вставьте ссылку (YouTube / VK / другой сайт)")
    print("   • Или путь к локальному видео/аудио файлу")
    while True:
        source = input("→ ").strip().strip('"').strip("'")
        if source:
            return source
        print("⚠️  Пустой ввод, попробуйте снова.")


def normalize_language(raw: str | None) -> str | None:
    """Приводит локаль (ru_RU.UTF-8) к коду языка (ru). Возвращает None для пустого значения."""
    if not raw:
        return None
    # Отрезаем кодировку и региональную часть: ru_RU.UTF-8 -> ru_RU -> ru
    code = raw.split(".")[0].split("_")[0].split("-")[0].strip().lower()
    return code or None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Транскрибация видео/аудио в текст (faster-whisper)"
    )
    parser.add_argument(
        "source",
        nargs="?",
        help="URL (YouTube/VK) или путь к локальному файлу. "
        "Если не указан — будет интерактивный ввод.",
    )
    parser.add_argument(
        "-o", "--output", default="transcription.txt", help="Итоговый текстовый файл"
    )
    parser.add_argument(
        "-m",
        "--model",
        default="large-v3-turbo",
        help="Размер модели Whisper (tiny, base, small, medium, large-v3, large-v3-turbo)",
    )
    parser.add_argument(
        "-l", "--language", default=None,
        help="Код языка: ru, en, de и т.д. (локаль ru_RU.UTF-8 тоже принимается)"
    )
    args = parser.parse_args()

    if not args.source:
        args.source = prompt_source()

    language = normalize_language(args.language)

    if args.source.startswith(("http://", "https://")):
        media_path = download_audio(args.source)
    else:
        media_path = args.source

    transcribe(
        media_path,
        model_size=args.model,
        language=language,
        output=args.output,
    )

if __name__ == "__main__":
    main()
