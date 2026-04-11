import re

import httpx


class SourceReader:
    """
    Minimal HTTP source reader.

    One request, short timeout, no JS rendering, no crawling.
    """

    def __init__(self, timeout: float = 3.0) -> None:
        self.timeout = timeout

    def read_url(self, url: str) -> dict:
        response = httpx.get(url, timeout=self.timeout, follow_redirects=True)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        text = response.text

        title = self._extract_title(text) if "html" in content_type else None
        plain_text = self._extract_text(text)

        return {
            "url": str(response.url),
            "title": title,
            "text": plain_text,
        }

    def _extract_title(self, text: str) -> str | None:
        match = re.search(r"<title>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return None
        return self._normalize_whitespace(match.group(1))

    def _extract_text(self, text: str) -> str:
        without_scripts = re.sub(r"<script.*?>.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
        without_styles = re.sub(r"<style.*?>.*?</style>", " ", without_scripts, flags=re.IGNORECASE | re.DOTALL)
        without_tags = re.sub(r"<[^>]+>", " ", without_styles)
        return self._normalize_whitespace(without_tags)

    def _normalize_whitespace(self, value: str) -> str:
        return " ".join(value.split())
