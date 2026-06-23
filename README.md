# sglang-serve

Сервинг LLM через [SGLang](https://lmsysorg.mintlify.app/docs/get-started/install).

## Что внутри

- **Dockerfile** — тянет готовый образ `lmsysorg/sglang:v0.5.13.post1-cu130` с Docker Hub, ставит `screen` и зависимости из `pyproject.toml`.
- **Makefile** — `build` (собрать образ) и `run` (поднять контейнер с GPU и зайти в bash).
- **gradio_app.py** — простой чат-UI поверх OpenAI-совместимого эндпоинта SGLang.

## Использование

```bash
make build
make run
```

`make run` бросает в bash внутри контейнера (GPU проброшены, порты `6666`/`7860`,
кэш HF и репо смонтированы). Дальше всё руками — например в `screen`:

```bash
python3 -m sglang.launch_server \
  --model-path Qwen/Qwen3-Next-80B-A3B-Instruct \
  --tp 2 \
  --attention-backend flashinfer \
  --host 0.0.0.0 --port 6666

python3 src/gradio_app.py
```

Команда сервинга — из
[cookbook Qwen3-Next](https://lmsysorg.mintlify.app/cookbook/autoregressive/Qwen/Qwen3-Next).
