import asyncio
import functools
import logging.handlers
import os
import threading
from typing import Dict, Optional, Type

import discord
from dotenv import load_dotenv
from langchain_core.messages import AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import _convert_delta_to_message_chunk
from langsmith.schemas import UsageMetadata
from pydantic import SecretStr

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
logging.getLogger("discord.http").setLevel(logging.INFO)
# log to stdout
handler = logging.StreamHandler()
dt_fmt = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


class CustomChatOpenAI(ChatOpenAI):
    def _convert_chunk_to_generation_chunk(
        self,
        chunk: dict,
        default_chunk_class: Type,
        base_generation_info: Optional[Dict],
    ) -> Optional[ChatGenerationChunk]:
        if chunk.get("type") == "content.delta":  # from beta.chat.completions.stream
            return None
        choices = (
            chunk.get("choices", [])
            # from beta.chat.completions.stream
            or chunk.get("chunk", {}).get("choices", [])
        )

        usage_metadata: Optional[UsageMetadata] = None
        if len(choices) == 0:
            # logprobs is implicitly None
            generation_chunk = ChatGenerationChunk(
                message=default_chunk_class(content="", usage_metadata=usage_metadata)
            )
            return generation_chunk

        choice = choices[0]
        if choice["delta"] is None:
            return None

        message_chunk = _convert_delta_to_message_chunk(
            choice["delta"], default_chunk_class
        )
        generation_info = {**base_generation_info} if base_generation_info else {}

        if finish_reason := choice.get("finish_reason"):
            generation_info["finish_reason"] = finish_reason
            if model_name := chunk.get("model"):
                generation_info["model_name"] = model_name
            if system_fingerprint := chunk.get("system_fingerprint"):
                generation_info["system_fingerprint"] = system_fingerprint

        logprobs = choice.get("logprobs")
        if logprobs:
            generation_info["logprobs"] = logprobs

        if usage_metadata and isinstance(message_chunk, AIMessageChunk):
            message_chunk.usage_metadata = usage_metadata

        generation_chunk = ChatGenerationChunk(
            message=message_chunk, generation_info=generation_info or None
        )
        return generation_chunk


openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

if not openai_model:
    raise ValueError("OPENAI_MODEL environment variable is not set")

openai = CustomChatOpenAI(
    api_key=SecretStr(openai_api_key),
    base_url=os.getenv("OPENAI_BASE_URL"),
    model=openai_model,
)


def debounce(wait_time):
    """
    Decorator that will debounce a function so that it is called after wait_time seconds.
    If it is called multiple times, it will wait for the last call to be debounced and run only this one.
    Supports both synchronous and asynchronous functions.
    """

    def decorator(function):
        if asyncio.iscoroutinefunction(function):
            # Async version
            @functools.wraps(function)
            async def async_debounced(*args, **kwargs):
                if async_debounced._task is not None:
                    async_debounced._task.cancel()

                async def call_function():
                    await asyncio.sleep(wait_time)
                    async_debounced._task = None
                    return await function(*args, **kwargs)

                async_debounced._task = asyncio.create_task(call_function())

            async_debounced._task = None
            return async_debounced
        else:
            # Sync version
            @functools.wraps(function)
            def sync_debounced(*args, **kwargs):
                def call_function():
                    sync_debounced._timer = None
                    return function(*args, **kwargs)

                if sync_debounced._timer is not None:
                    sync_debounced._timer.cancel()

                sync_debounced._timer = threading.Timer(wait_time, call_function)
                sync_debounced._timer.start()

            sync_debounced._timer = None
            return sync_debounced

    return decorator


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


def get_full_message(stream):
    full_message = ""
    for message in stream:
        if "content" in message.__dict__:
            full_message += message.content
        yield full_message


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!chat"):
        response = get_full_message(openai.stream(message.content[6:]))
        # send Thinking... message
        message = await message.channel.send("Thinking...")

        @debounce(0.3)
        async def message_edit(content):
            return await message.edit(content=content)

        for full_message in response:
            await message_edit(full_message)


if TOKEN is None:
    raise ValueError("DISCORD_TOKEN environment variable is not set")

client.run(TOKEN, log_handler=None)
