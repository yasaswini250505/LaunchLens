from launchlens.benchmark import BenchmarkRunner


class FakeClient:
    def __init__(self, model: str) -> None:
        self.model = model

def __enter__(self):
    return self

def __exit__(self, *args):
    return None

def complete(self, prompt: str):
    return object()

def test_benchmark_records_successes() -> None:
    result = BenchmarkRunner(lambda model: FakeClient(model)).run(["model-a"], "pitch", 2)
    assert result[0].successful == 2
    assert result[0].failed == 0