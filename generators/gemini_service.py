import os
import time
from typing import Optional

from dotenv import load_dotenv
from google import genai

from scheduler.schedule import resolve_path


class GeminiService:
    """Reusable wrapper for Gemini API calls with retry and error handling."""

    def __init__(self, model: str = "gemini-3.5-flash", max_retries: int = 3, retry_delay_seconds: float = 1.0) -> None:
        self.model = model
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds
        self._client: Optional[genai.Client] = None

    def _load_environment(self) -> None:
        # Keep .env loading consistent with the existing project behavior.
        load_dotenv(dotenv_path=resolve_path(".env"))

    def _get_client(self) -> Optional[genai.Client]:
        if self._client is None:
            self._load_environment()
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return None
            self._client = genai.Client(api_key=api_key)
        return self._client

    def _build_fallback_content(self, prompt: str) -> str:
        prompt_preview = " ".join(prompt.split())[:180]
        return (
            "LinkedIn draft generated locally because GEMINI_API_KEY is not available.\n\n"
            f"Prompt preview: {prompt_preview}\n\n"
            "This fallback keeps the automation pipeline running so you can review and refine the content."
        )

    def generate_content(self, prompt: str) -> str:
        """Generate text from Gemini with automatic retry for transient 503 errors."""
        self._load_environment()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return self._build_fallback_content(prompt)

        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                response = self._get_client().models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                return response.text
            except Exception as exc:
                last_error = exc
                message = str(exc).lower()

                # Retry automatically only for transient service errors.
                if "503" in message or "service unavailable" in message or "temporarily unavailable" in message:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay_seconds)
                        continue

                raise RuntimeError(f"Gemini API request failed: {exc}") from exc

        if last_error is not None:
            raise RuntimeError(f"Gemini API request failed after retries: {last_error}") from last_error

        raise RuntimeError("Gemini API request failed without a captured error.")
