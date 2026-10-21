import httpx
import respx

from launchlens.client import GroqClient


@respx.mock
def test_client_streams_sse_chunks() -> None:
    body = """data: {\"choices\":[{\"delta\":
{\"content\":\"Build\"}}]}\n\ndata: {\"choices\":[{\"delta\":
{\"content\":\" boldly\"}}]}\n\ndata: [DONE]\n\n"""

    respx.post("https://api.test/v1/chat/completions").mock(return_value=httpx.
Response(200, text = body, headers={"content-type": "text/event-stream"}))
tokens: list[str] = []
with GroqClient("test-key", "test-model",
base_url="https://api.test/v1") as client:
        result = client.stream("pitch", tokens.append)
assert tokens == ["Build", " boldly"]
assert result == "Build boldly"