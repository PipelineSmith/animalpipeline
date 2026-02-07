import sys
import types
import unittest

try:
    import openai  # noqa: F401
except ModuleNotFoundError:
    fake_openai = types.ModuleType("openai")
    fake_openai.OpenAI = object
    sys.modules["openai"] = fake_openai

try:
    import dotenv  # noqa: F401
except ModuleNotFoundError:
    fake_dotenv = types.ModuleType("dotenv")

    def _load_dotenv(*_args, **_kwargs):
        return None

    fake_dotenv.load_dotenv = _load_dotenv
    sys.modules["dotenv"] = fake_dotenv

from openaigenerator.animalfacts import impl


class _FakeResponse:
    def __init__(self, content: str):
        self.choices = [_FakeChoice(content)]


class _FakeChoice:
    def __init__(self, content: str):
        self.message = _FakeMessage(content)


class _FakeMessage:
    def __init__(self, content: str):
        self.content = content


class _FakeChatCompletions:
    def __init__(self, content: str | None, error: Exception | None = None):
        self._content = content
        self._error = error

    def create(self, model: str, messages: list[dict], temperature: float, max_tokens: int):
        if self._error:
            raise self._error
        return _FakeResponse(self._content or "")


class _FakeChat:
    def __init__(self, content: str | None, error: Exception | None = None):
        self.completions = _FakeChatCompletions(content, error=error)


class _FakeClient:
    def __init__(self, content: str | None, error: Exception | None = None):
        self.chat = _FakeChat(content, error=error)


class NormalizeAnimalTests(unittest.TestCase):
    def test_normalizes_punctuation_and_articles(self):
        self.assertEqual(impl._normalize_animal('"A red panda."'), "red panda")
        self.assertEqual(impl._normalize_animal("The   Fennec   Fox!"), "fennec fox")

    def test_normalizes_separators(self):
        self.assertEqual(impl._normalize_animal("cat, dog"), "cat")
        self.assertEqual(impl._normalize_animal("otter or seal"), "otter")
        self.assertEqual(impl._normalize_animal("pika and rabbit"), "pika")

    def test_normalizes_empty_content(self):
        self.assertIsNone(impl._normalize_animal(""))
        self.assertIsNone(impl._normalize_animal("   "))
        self.assertIsNone(impl._normalize_animal("###"))


class GenerateRandomAnimalTests(unittest.TestCase):
    def test_returns_normalized_animal(self):
        client = _FakeClient("A red panda.")
        self.assertEqual(impl.generate_random_animal(client), "red panda")

    def test_rejects_long_output(self):
        client = _FakeClient("a" * 41)
        self.assertIsNone(impl.generate_random_animal(client))

    def test_handles_empty_output(self):
        client = _FakeClient("")
        self.assertIsNone(impl.generate_random_animal(client))

    def test_handles_exceptions(self):
        client = _FakeClient(None, error=RuntimeError("boom"))
        self.assertIsNone(impl.generate_random_animal(client))


if __name__ == "__main__":
    unittest.main()
