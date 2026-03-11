import os
import re
import sys

import httpx


OLLAMA_MESSAGE_HISTORY_MAX = 5
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_TIMEOUT_SEC = float(os.environ.get("OLLAMA_TIMEOUT_SEC", "120"))
OLLAMA_WARMUP_TIMEOUT_SEC = float(
    os.environ.get("OLLAMA_WARMUP_TIMEOUT_SEC", str(OLLAMA_TIMEOUT_SEC))
)
OLLAMA_KEEP_ALIVE = os.environ.get("OLLAMA_KEEP_ALIVE")


class Ollama:
    def __init__(self, first_assistant_content=None):
        self.ollama_messages = []
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        self.timeout_sec = OLLAMA_TIMEOUT_SEC
        self.warmup_timeout_sec = OLLAMA_WARMUP_TIMEOUT_SEC
        self.keep_alive = OLLAMA_KEEP_ALIVE

        system_prompt = """
        You are my friend. You are a girl.
        Consider the emotion icon at the end of my messages when responding.
        End your responses with 0 or more emotion icons that reflect your current feeling,
        using 🥰 for happiness, 💢 for anger, 😱 for fear, and 😭 for sadness.
        Keep responses concise, within 2 sentences, and avoid bullet points.
        Tailor language and tone to match my emotional state.
        Respond in Japanese, aiming for a natural, empathetic conversation.
        Use emotion icons after each sentence when possible.
        Do not use periods at the end of sentences.
        """
        self.ollama_messages.append({"role": "system", "content": system_prompt})
        if first_assistant_content:
            self.ollama_messages.append({"role": "assistant", "content": first_assistant_content})
        print("Using Ollama", file=sys.stderr)

    def _request_payload(self, extra_payload=None):
        payload = {"model": self.model}
        if self.keep_alive:
            payload["keep_alive"] = self.keep_alive
        if extra_payload:
            payload.update(extra_payload)
        return payload

    def wait_until_ready(self):
        try:
            with httpx.Client(timeout=self.warmup_timeout_sec) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json=self._request_payload({"stream": False}),
                )
                response.raise_for_status()
        except Exception as e:
            print(f"ollama: Failed to warm up model: {e}", file=sys.stderr)
            return False

        print(f"ollama: Model {self.model} is ready", file=sys.stderr)
        return True

    def play_response(self, user_input):
        queue = []
        self.ollama_messages.append({"role": "user", "content": user_input})

        try:
            with httpx.Client(timeout=self.timeout_sec) as client:
                response = client.post(
                    f"{self.base_url}/api/chat",
                    json=self._request_payload(
                        {
                            "messages": self.ollama_messages,
                            "stream": False,
                        }
                    ),
                )
                response.raise_for_status()
                payload = response.json()
                completion_text = payload["message"]["content"]
        except Exception as e:
            print(f"ollama: Failed to connect to Ollama API: {e}", file=sys.stderr)
            del self.ollama_messages[-1]
            return ["***END***"]

        completion_text = re.sub(r"[\n\r]+", "", completion_text)
        self.ollama_messages.append({"role": "assistant", "content": completion_text})

        max_messages = OLLAMA_MESSAGE_HISTORY_MAX * 2 + 2
        while len(self.ollama_messages) > max_messages:
            self.ollama_messages.pop(1)

        # Keep the same split behavior as Gemini client.
        emoji_chars = r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF]"
        punctuation = r"[、。！？]"
        pattern = f".*?(?:{emoji_chars}|{punctuation})|.+$"
        sentences = re.findall(pattern, completion_text)
        for sentence in sentences:
            if sentence:
                queue.append(sentence)

        queue.append("***END***")
        print(f"返答: {completion_text}", file=sys.stderr)
        return queue
