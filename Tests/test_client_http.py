import httpx
import respx

from launchlens.client import GroqClient


@respx.mock
def test_client_sends_bearer_header_and_json() -> None:
    route = respx.post("https://api.test/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={
            "id" : "1", 
            "model" : "test- model", 
            "choices" : [{"message": {"role": "assistant", "content": "pitch"}}]})
    )
    with GroqClient("test-key", "test-model",
    base_url="https://api.test/v1") as client:
        response = client.complete("write a pitch")
    assert response.text == "pitch"
    assert route.calls.last.request.headers["authorization"] == "Bearer test-key"
    assert b"write a pitch" in route.calls.last.request.content