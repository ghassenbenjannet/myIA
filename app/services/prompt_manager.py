import pathlib
import re

_PROMPTS_DIR = pathlib.Path(__file__).parent.parent / "prompts"


class PromptManager:
    """Loads and renders Markdown prompt templates from app/prompts/."""

    def __init__(self, prompts_dir: pathlib.Path | None = None) -> None:
        self._dir = prompts_dir or _PROMPTS_DIR

    def load(self, name: str) -> str:
        """Return raw template text for *name* (without .md extension)."""
        path = self._dir / f"{name}.md"
        return path.read_text(encoding="utf-8")

    def render(self, name: str, variables: dict) -> str:
        """Load and render a prompt template, substituting {key} placeholders.

        Missing keys are replaced with an empty string rather than raising.
        None values are rendered as the string "non fourni".
        """
        template = self.load(name)
        safe = {
            k: (str(v) if v is not None else "non fourni") for k, v in variables.items()
        }
        # Replace {key} placeholders; leave unknown placeholders untouched
        def replacer(m: re.Match) -> str:
            key = m.group(1)
            return safe.get(key, m.group(0))

        return re.sub(r"\{(\w+)\}", replacer, template)


prompt_manager = PromptManager()
