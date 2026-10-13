"""Explicitly local deterministic test responder; remote LLMs are not implemented."""
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Digital Twin Physiological Simulator"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return (
            f"[{self.system_name} mock responder]: This is a deterministic placeholder. "
            "No independent inference, physiological simulation, or clinical "
            f"verification was performed. Query excerpt: {prompt[:60]!r}"
        )


class LLMFactory:
    """Only mock execution is supported; never silently emulate remote providers."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Digital Twin Physiological Simulator"):
        if str(provider).lower() in ("mock", "deterministic", "test"):
            return MockLLM(system_name)
        raise ValueError(
            f"Provider {provider!r} is not implemented. Use the local 'mock' provider."
        )
