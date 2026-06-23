import os
import typing as t

import gradio as gr

from openai import AsyncOpenAI


SGLANG_BASE_URL = os.environ.get("SGLANG_BASE_URL", "http://localhost:6666/v1")
SGLANG_MODEL = os.environ.get("SGLANG_MODEL", "Qwen/Qwen3-Next-80B-A3B-Instruct")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "EMPTY")
GRADIO_PORT = int(os.environ.get("GRADIO_PORT", "7860"))


def _build_messages(
    user_message: str,
    history: list[dict[str, str]] | None,
    system_prompt: str | None,
) -> list[dict[str, str]]:
    """Конвертация истории gr.Chatbot в формат OpenAI Chat API."""
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    if history:
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_message})
    return messages


client = AsyncOpenAI(base_url=SGLANG_BASE_URL, api_key=OPENAI_API_KEY or "EMPTY_KEY")


async def generate_response(
    user_message: str,
    history: list[dict[str, str]] | None,
    temperature: float,
    top_p: float,
    max_tokens: int | float | None,
    system_prompt: str,
):
    """Генерация ответа с потоковой выдачей через OpenAI-совместимый SGLang.

    Функция-генератор для gr.ChatInterface. Возвращает инкрементальный текст.
    """
    try:
        messages = _build_messages(
            user_message=user_message,
            history=history,
            system_prompt=system_prompt,
        )

        # Безопасная обработка max_tokens
        max_new_tokens: int | None = None
        if isinstance(max_tokens, (int, float)) and max_tokens > 0:
            max_new_tokens = int(max_tokens)

        create_kwargs: dict[str, t.Any] = {
            "model": SGLANG_MODEL,
            "messages": messages,
            "temperature": float(temperature),
            "top_p": float(top_p),
            "max_tokens": max_new_tokens,
            "stream": True,
        }

        stream = await client.chat.completions.create(**create_kwargs)

        accumulated_text = ""
        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            content_piece = getattr(delta, "content", None)
            if content_piece:
                accumulated_text += content_piece
                yield accumulated_text

        if not accumulated_text:
            yield ""

    except Exception as e:  # Ошибку отображаем пользователю
        yield f"Ошибка: {e}"


def build_demo() -> gr.Blocks:
    """Собирает интерфейс Gradio ChatInterface с дополнительными входами."""

    with gr.Blocks(title="SGLang Chat (Gradio)") as demo:
        gr.Markdown("### Qwen3-Next -- локальный инференс через SGLang")

        gr.ChatInterface(
            fn=generate_response,
            type="messages",
            submit_btn="Отправить",
            additional_inputs=[
                gr.Slider(
                    minimum=0.0,
                    maximum=2.0,
                    value=0.7,
                    step=0.01,
                    label="temperature",
                ),
                gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.8,
                    step=0.01,
                    label="top_p",
                ),
                gr.Slider(
                    minimum=1,
                    maximum=64000,
                    value=2048,
                    step=1,
                    label="max_tokens",
                ),
                gr.Textbox(
                    label="system prompt",
                    placeholder="Вы можете задать стиль и поведение ассистента...",
                    lines=3,
                ),
            ],
        )

    return demo


def main() -> None:
    """Точка входа запуска демо с очередью для потоковой выдачи."""
    demo = build_demo()
    demo.queue()
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=GRADIO_PORT,
        debug=True,
    )


if __name__ == "__main__":
    main()
