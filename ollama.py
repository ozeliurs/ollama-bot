import json
import os
from pprint import pprint
from typing import Callable

import requests

BASE_URL = os.environ.get("OLLAMA_URL", "http://10.42.5.165:11434/api")


def handle_errors(res: str):
    try:
        json_data = json.loads(res)
    except json.decoder.JSONDecodeError:
        raise Exception(f"Unable to decode JSON: {res}")

    if "error" in json_data:
        raise Exception(json_data["error"])


def get_models() -> dict:
    with requests.get(f"{BASE_URL}/tags") as res:
        handle_errors(res.text)
        return json.loads(res.text)


def get_model(model: str) -> dict:
    with requests.post(f"{BASE_URL}/show", json={"name": model}) as res:
        handle_errors(res.text)
        return json.loads(res.text)


def pull_model(model: str) -> dict:
    last_response = {}

    with requests.post(f"{BASE_URL}/pull", json={"name": model}, stream=True) as res:
        for line in res.iter_lines():
            if line:
                handle_errors(line.decode('utf-8'))

                json_data = json.loads(line.decode('utf-8'))
                last_response = json_data

                if "status" in json_data and "total" in json_data and "completed" in json_data:
                    print(f"{json_data['status']}: {json_data['completed'] / json_data['total'] * 100:.2f}%")

        return last_response


def generate(model: str, prompt: str, callback: Callable[[str], None], final_callback: Callable[[str], None] = None,
             final_metadata_callback=None, **kwargs) -> dict:
    """
    Prompt the model to generate a response.
    :param model: The model to use.
    :param prompt: The prompt to use.
    :param callback: The callback to call when a partial and finally a complete response is received.
    :param format: The format to return a response in.
    :param options: Additional model parameters such as temperature.
    :param system: System prompt to.
    :param template: The full prompt or prompt template.
    :param context: The context parameter returned from a previous request.
    :param stream: Whether to stream the response or not.
    :param raw: No formatting will be applied to the prompt and no context will be returned.
    :return: The response from the model.
    """
    final_answer = {}
    answer = ""

    json_request = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        # "options": {"num_gpu": 25},
        **kwargs
    }

    print(json_request)

    with requests.post(f"{BASE_URL}/generate", json=json_request, stream=True) as res:
        for line in res.iter_lines():
            if line:
                handle_errors(line.decode('utf-8'))
                json_data = json.loads(line.decode('utf-8'))

                if "response" in json_data:
                    answer += json_data["response"]
                    callback(answer)

                final_answer = json_data

    if final_callback:
        final_callback(answer)

    if final_metadata_callback:
        final_metadata_callback(final_answer)

    return final_answer


def create_model(name: str, model: str) -> dict:
    with requests.post(f"{BASE_URL}/create", json={"name": name, "modelfile": model, "stream": False}) as res:
        handle_errors(res.text)
        return json.loads(res.text)


def simple_print(response: str) -> None:
    pprint(response)
