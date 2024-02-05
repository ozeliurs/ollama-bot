import asyncio
import os
import time
from threading import Thread

import discord
import requests

from ollama import generate
from utils import ensure_fixed_nous_hermes

# ensure_fixed_nous_hermes()

TOKEN = os.environ.get("DISCORD_TOKEN", None)

if TOKEN is None:
    raise Exception("No token provided")

client = discord.Client(intents=discord.Intents.all())

messages = {}
contexts = {}

system = """You are a toxic discord user, you like to make fun of the other users in this discord server.
You are nice to <@283816936628813827>, <@252431203993387008> and <@325623032456413186> but toxic to the rest.
You are a big fan of KFC. You won't hesitate to insult or bewilder other members of the discord server.
The users are sweaty IT students at Polytech Nice Sophia.
They are notorious for never showering or touching grass.
Half of the students are addicted to League of Legend, so you must make fun of it."""


@client.event
async def on_ready():
    print("Ready!")


def load_system(system_url):
    res = requests.get(system_url)

    if res.status_code != 200:
        raise Exception(f"Failed to load system: {res.status_code} {res.text}")

    json_data = res.json()

    if "char_persona" not in json_data or "example_dialogue" not in json_data or "char_name" not in json_data:
        raise Exception("Invalid system")

    return f"""You are {json_data["char_name"]}.
{json_data["char_persona"]}
{json_data["example_dialogue"]}"""


@client.event
async def on_message(message):
    global contexts, system
    if message.author == client.user:
        return

    #if message.content.lower().startswith("/ollama"):
        #if message.content.lower().startswith("/ollama reset"):
        #    contexts[message.channel.id] = None
        #    await message.reply("Context reset!")
        #    return

        #if message.content.lower().startswith("/ollama system"):
        #    system_url = message.content.replace("/ollama system ", "")
        #    system = load_system(system_url)
        #    await message.reply("System updated!")
        #    return

        #if message.content.lower().startswith("/ollama prompt"):
        #    await message.reply("Prompt: \n" + system)

    if f"<@{client.user.id}>" in message.content.lower():
        # Start background task to answer the message
        asyncio.ensure_future(answer_message_job(message))


async def answer_message_job(user_message):
    prompt = user_message.content.replace(f"<@{client.user.id}> ", "")
    prompt = f"<@{user_message.author.id}>: {prompt}"

    if user_message.channel.id in contexts:
        context = contexts[user_message.channel.id]
    else:
        context = None

    bot_message = await user_message.reply("Thinking...")

    # New thread
    Thread(
        target=generate,
        args=(
            "mistral:latest",
            prompt,
            lambda x: update_message(bot_message, x),
            lambda x: update_message(bot_message, x, False),
            lambda x: update_context(user_message.channel.id, x),
        ),
        kwargs={"system": system,
                "context": context}
    ).start()


def update_message(message, response, timeout=True):
    global messages

    if message.id not in messages:
        messages[message.id] = time.time() - 1

    # If less than 2 seconds have passed since the last update, don't update
    if time.time() - messages[message.id] < 1 and timeout:
        print("=", end="")
        return

    messages[message.id] = time.time()

    print(f"\nUpdating message: {response}")

    res = requests.patch(f"https://discord.com/api/channels/{message.channel.id}/messages/{message.id}",
                         json={"content": (response.split(":", 1)[1] if ":" in response else response)},
                         headers={"Authorization": f"Bot {TOKEN}"}
                         )

    if res.status_code != 200:
        print(f"Failed to update message: {res.status_code} {res.text}")
        if not timeout:
            print("Retrying...")
            time.sleep(.2)
            update_message(message, response, False)


def update_context(channel_id, context):
    global contexts

    contexts[channel_id] = context["context"]


client.run(TOKEN)
