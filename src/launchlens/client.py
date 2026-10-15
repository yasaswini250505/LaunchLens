from __future__ import annotations

from dbm import error
import json
from collections.abc import Callable
import token

import httpx

from launchlens.constants import GROQ_BASE_URL
from launchlens.decorators import retry_api, timed
from launchlens.errors import APIError, ResponseError
from launchlens.schemas import ChatMessage, ChatRequest, ChatResponse


class GroqClient:
    def __init__(self, api_key: str, model: str, timeout_seconds: float = 60.0, base_url: str = GROQ_BASE_URL) -> None:
        if not api_key.strip():
            raise ValueError("Groq API key cannot be blank")
        self.model = model
        self.http = httpx.Client(
            base_url=base_url,
            timeout=httpx.Timeout(timeout_seconds),
            headers={"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"},
        )

    def __enter__(self) -> "GroqClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.http.close()

    def _request(self, prompt: str, stream: bool = False) -> ChatRequest:
        return ChatRequest(
            model=self.model,
            messages=[
                ChatMessage(role="system", content="You are LaunchLens, a precise technical storyteller."),
                ChatMessage(role="user", content=prompt),
            ],
            stream=stream,
        )

    @timed
    @retry_api()
    def complete(self, prompt: str) -> ChatResponse:
        try:
            response = self.http.post("/chat/completions", json=self._request(prompt).model_dump())
        except httpx.TimeoutException as error:
            raise APIError("Groq request timed out") from error
        except httpx.HTTPError as error:
            raise APIError(f"network error: {error}") from error
        if response.is_error:
            raise APIError(f"Groq returned HTTP {response.status_code} : {response.text[:400]}", response.status_code)
        try:
            return ChatResponse.model_validate(response.json())
        except (ValueError, TypeError) as error:
            raise ResponseError("unexpected Groq response JSON") from error
        
    def stream(self, prompt: str, on_token: Callable[[str], None] | None = None) -> str:
        """Read Groq Server-Sent Events and yield text deltas through a callback."""
        chunks: list[str] = []
        try:
            with self.http.stream("POST", "/chat/completions", json=self._request(prompt, True).model_dump()) as response:
                if response.is_error:
                    raise APIError(f"Groq returned HTTP {response.status_code}: {response.text[:400]}", response.status_code)
                for line in response.iter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    try:
                        payload = line.removeprefix("data:").strip()
                    except AttributeError:
                        continue
                    if payload == "[DONE]":
                        break
                    try:
                        event = json.loads(payload)
                    except json.JSONDecodeError as error:
                        raise ResponseError("malformed SSE JSON") from error
                    choices = event.get("choices", [])
                    delta = choices[0].get("delta", {}) if choices else {}
                    token = delta.get("content") or ""
                    if token:
                        chunks.append(token)
                        if on_token:
                            on_token(token)
        except httpx.TimeoutException as error:
            raise APIError("Groq streaming request timed out") from error
        except httpx.HTTPError as error:
            raise APIError(f"streaming network error: {error}") from error
        return "".join(chunks)