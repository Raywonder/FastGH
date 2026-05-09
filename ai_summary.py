"""AI summary providers for repository and release text."""

from __future__ import annotations

import requests


MAX_SUMMARY_INPUT = 12000
SUMMARY_TIMEOUT = 90


class SummaryError(Exception):
    """Raised when an AI summary request cannot be completed."""


def _pref(prefs, key: str, default=""):
    if prefs is None:
        return default
    try:
        return prefs.get(key, default)
    except AttributeError:
        return getattr(prefs, key, default)


def _trim_text(text: str) -> str:
    text = text or ""
    if len(text) <= MAX_SUMMARY_INPUT:
        return text
    return text[:MAX_SUMMARY_INPUT] + "\n\n[Input trimmed for summary length.]"


def _messages(title: str, text: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "Summarize Git repository information for a developer. "
                "Be concise, factual, and include likely next actions when useful. "
                "Do not invent details that are not in the supplied text."
            ),
        },
        {
            "role": "user",
            "content": f"Title: {title}\n\nContent:\n{_trim_text(text)}",
        },
    ]


def summarize_text(prefs, title: str, text: str) -> str:
    """Summarize text using the configured provider."""
    provider = (_pref(prefs, "ai_summary_provider", "disabled") or "disabled").lower()
    if provider in ("", "disabled", "none"):
        raise SummaryError("AI summaries are disabled. Enable Ollama or a compatible provider in Options.")

    if provider == "ollama":
        return _summarize_with_ollama(prefs, title, text)

    if provider == "openclaw":
        return _summarize_with_openclaw(prefs, title, text)

    if provider in ("copilot", "compatible", "openai", "ai_router"):
        return _summarize_with_compatible_api(prefs, title, text)

    raise SummaryError(f"Unknown AI summary provider: {provider}")


def _summarize_with_ollama(prefs, title: str, text: str) -> str:
    host = (_pref(prefs, "ai_ollama_host", "http://127.0.0.1:11434") or "").rstrip("/")
    model = _pref(prefs, "ai_ollama_model", "qwen2.5:14b") or "qwen2.5:14b"
    if not host:
        raise SummaryError("Ollama host is not configured.")

    payload = {
        "model": model,
        "stream": False,
        "messages": _messages(title, text),
    }
    response = requests.post(f"{host}/api/chat", json=payload, timeout=SUMMARY_TIMEOUT)
    if response.status_code >= 400:
        raise SummaryError(f"Ollama summary failed ({response.status_code}): {response.text[:300]}")

    data = response.json()
    message = data.get("message") or {}
    content = message.get("content") or data.get("response") or ""
    if not content.strip():
        raise SummaryError("Ollama returned an empty summary.")
    return content.strip()


def _summarize_with_openclaw(prefs, title: str, text: str) -> str:
    url = (_pref(prefs, "ai_openclaw_url", "http://100.64.0.2:18790/api/chat") or "").strip()
    model = (_pref(prefs, "ai_openclaw_model", "qwen2.5:14b") or "").strip()
    token = (_pref(prefs, "ai_openclaw_token", "") or "").strip()
    if not url:
        raise SummaryError("OpenClaw gateway URL is not configured.")

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {
        "model": model,
        "messages": _messages(title, text),
        "stream": False,
    }
    response = requests.post(url, json=payload, headers=headers, timeout=SUMMARY_TIMEOUT)
    if response.status_code >= 400:
        raise SummaryError(f"OpenClaw summary failed ({response.status_code}): {response.text[:300]}")

    data = response.json()
    if isinstance(data.get("message"), dict):
        content = data["message"].get("content", "")
    else:
        content = data.get("summary") or data.get("content") or data.get("response") or ""
    if not content.strip():
        raise SummaryError("OpenClaw returned an empty summary.")
    return content.strip()


def _summarize_with_compatible_api(prefs, title: str, text: str) -> str:
    url = (_pref(prefs, "ai_compatible_url", "") or "").strip()
    model = (_pref(prefs, "ai_compatible_model", "") or "").strip()
    token = (_pref(prefs, "ai_compatible_token", "") or "").strip()

    if not url:
        raise SummaryError("Compatible API URL is not configured.")
    if not model:
        raise SummaryError("Compatible API model is not configured.")
    if not token:
        raise SummaryError("Compatible API token is not configured.")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": _messages(title, text),
        "temperature": 0.2,
    }
    response = requests.post(url, json=payload, headers=headers, timeout=SUMMARY_TIMEOUT)
    if response.status_code >= 400:
        raise SummaryError(f"Compatible API summary failed ({response.status_code}): {response.text[:300]}")

    data = response.json()
    choices = data.get("choices") or []
    if not choices:
        raise SummaryError("Compatible API returned no summary choices.")
    message = choices[0].get("message") or {}
    content = message.get("content") or choices[0].get("text") or ""
    if not content.strip():
        raise SummaryError("Compatible API returned an empty summary.")
    return content.strip()
