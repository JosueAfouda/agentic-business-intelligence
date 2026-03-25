from __future__ import annotations

import subprocess

from llm.base import GenerationResult, LLMProvider, LLMProviderError


class GeminiProvider(LLMProvider):
    name = "gemini"

    def generate(self, prompt: str) -> GenerationResult:
        command = ["gemini", "run"]

        try:
            result = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
            )
        except FileNotFoundError as exc:
            raise LLMProviderError("Gemini CLI is not installed or not available in PATH.") from exc

        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip() or "Gemini CLI execution failed."
            raise LLMProviderError(error_output)

        return GenerationResult(
            text=result.stdout,
            provider_name=self.name,
            command=command,
            stdout=result.stdout,
            stderr=result.stderr,
        )
