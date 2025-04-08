import os
import json
from typing import Callable
import requests

from app.api.bs import get_character, get_model_by_name


DEFAULT_MODEL = os.getenv(
    "DEFAULT_MODEL", "QWen 2.5 1m 14b")


class AI:
    def __init__(self, character_id: str, model: str):
        self.set_model(model)
        self.set_character(character_id)

    def set_character(self, character_id: str):
        if character_id:
            self.character = get_character(character_id)
            self.settings = self.character['settings']
        else:
            self.character = None
            self.settings = None

    def set_model(self, model: str):
        self.model = model

    async def chat(self, message: str, history: list, message_handler: Callable):
        if not self.model:
            self.model = DEFAULT_MODEL

        model = get_model_by_name(self.model)
        print("model:", model)
        if not model:
            raise Exception("Model not found")

        url = model['api']
        headers = {
            "Content-Type": "application/json",
        }
        if model['api_key']:
            headers['Authorization'] = f"Bearer {model['api_key']}"

        messages = [{'role': 'system', 'content': self.settings}]
        for i in history:
            messages.append(
                {'role': 'user' if not i['from_bot'] else 'assistant', 'content': i['content']})
        messages.append({'role': 'user', 'content': message})

        print("messages", messages)
        print(f"model: {self.model} default: {DEFAULT_MODEL}")
        print(f"api: {url}, headers: {headers}")

        data = {
            "messages": messages,
            "stream": True,
            "model": model['model'],
        }
        print("extra_args", model['extra_args'], type(model['extra_args']))
        if model['extra_args']:
            data.update(model['extra_args'])

        stream = requests.post(
            url, headers=headers, json=data, stream=True)

        content = ""
        for l in stream.iter_lines():
            l = l.decode("utf-8")
            print("l:", l)
            if l.startswith("data:"):
                l = l[5:]
            if l.startswith("event: "):
                l = l[6:]
            if l.startswith("data: "):
                l = l[5:]
            try:
                d = json.loads(l)
                # print("d:", d)
            except:
                continue

            if "message" not in d:
                continue

            if "content" not in d["message"]:
                continue

            word = d["message"]["content"]
            content += word
            await message_handler(word)

        return content


if __name__ == "__main__":
    pass