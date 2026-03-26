from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from llm.base import GenerationResult, LLMProvider, LLMProviderError


class CodexProvider(LLMProvider):
    name = "codex"

    def generate(self, prompt: str) -> GenerationResult:
        with tempfile.NamedTemporaryFile(prefix="codex-last-message-", suffix=".txt", delete=False) as temp_file:
            output_path = Path(temp_file.name)

        command = [
            "codex",
            "exec",
            "--color",
            "never",
            "--sandbox",
            "read-only",
            "-o",
            str(output_path),
            "-",
        ]

        try:
            result = subprocess.run(
                command,
                input=prompt,
                text=True,
                capture_output=True,
            )
            generated_text = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        except FileNotFoundError as exc:
            raise LLMProviderError("Codex CLI is not installed or not available in PATH.") from exc
        finally:
            output_path.unlink(missing_ok=True)

        if result.returncode != 0:
            error_output = result.stderr.strip() or result.stdout.strip() or "Codex CLI execution failed."
            raise LLMProviderError(error_output)

        if not generated_text.strip():
            error_output = result.stderr.strip() or result.stdout.strip() or "Codex CLI returned an empty response."
            raise LLMProviderError(error_output)

        return GenerationResult(
            text=generated_text,
            provider_name=self.name,
            command=command,
            stdout=result.stdout,
            stderr=result.stderr,
        )
