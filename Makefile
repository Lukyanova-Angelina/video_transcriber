# --- Переменные (можно переопределять снаружи) ---
OUT      ?= transcription.txt
MODEL    ?= large-v3-turbo
SRC_LANG ?=

.PHONY: help install lint format check run clean

help:
	@echo "📖 Доступные команды:"
	@echo ""
	@echo "  make install                             — установить зависимости (uv sync)"
	@echo "  make run                                 — запустить скрипт (интерактивно)"
	@echo "  make transcribe URL=<ссылка>             — транскрибация по ссылке"
	@echo "  make transcribe FILE=<путь>              — транскрибация локального файла"
	@echo "  make lint                                — проверка ruff"
	@echo "  make format                              — автоформат ruff"
	@echo "  make check                               — lint + format --check (как в CI)"
	@echo "  make clean                               — удалить .venv и __pycache__"
	@echo ""
	@echo "Параметры (добавьте к любой команде):"
	@echo "  OUT=$(OUT)   MODEL=$(MODEL)   SRC_LANG=<ru/en/…>"

install:
	uv sync

lint:
	uv run ruff check .

format:
	uv run ruff format .

check:
	uv run ruff check .
	uv run ruff format --check .

run:
	uv run main.py -o "$(OUT)" -m "$(MODEL)" $(if $(SRC_LANG),-l $(SRC_LANG))

transcribe:
ifdef URL
	uv run main.py "$(URL)" -o "$(OUT)" -m "$(MODEL)" $(if $(SRC_LANG),-l $(SRC_LANG))
else ifdef FILE
	uv run main.py "$(FILE)" -o "$(OUT)" -m "$(MODEL)" $(if $(SRC_LANG),-l $(SRC_LANG))
else
	@echo "❌ Укажите URL=<ссылка> или FILE=<путь>"
	@echo "   Пример: make transcribe URL=\"https://youtu.be/xxx\" OUT=lecture.txt SRC_LANG=ru"
	@exit 1
endif

clean:
	rm -rf .venv __pycache__ .ruff_cache