"""Lightweight Markdown -> plain text converter for Telegram output.

This avoids adding heavy dependencies and handles common Markdown features:
- headings, bold/italic, inline/code blocks, links/images, blockquotes,
- basic strikethrough, and removes most formatting tokens (**, __, ##, `, ```).
"""
from __future__ import annotations
import re


_RE_CODE_FENCE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
_RE_INLINE_CODE = re.compile(r"`([^`]*)`")
_RE_BOLD = re.compile(r"\*\*(.*?)\*\*|__(.*?)__", re.DOTALL)
_RE_ITALIC = re.compile(r"(?<!\*)\*(?!\*)([^\n*]+?)\*(?!\*)|_([^\n_]+?)_", re.DOTALL)
_RE_H = re.compile(r"^\s{0,3}#+\s*", re.MULTILINE)
_RE_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_RE_IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_RE_BLOCKQUOTE = re.compile(r"^\s*>\s?", re.MULTILINE)
_RE_STRIKE = re.compile(r"~~(.*?)~~", re.DOTALL)


def md_to_text(md: str) -> str:
    if not isinstance(md, str) or not md:
        return "" if md is None else str(md)

    text = md

    # Remove fenced code blocks but keep inner content
    def _unfence(m: re.Match) -> str:
        block = m.group(0)
        # strip the ``` fences
        inner = re.sub(r"^```[a-zA-Z0-9_-]*\n?|```$", "", block, flags=re.MULTILINE)
        return inner

    text = _RE_CODE_FENCE.sub(_unfence, text)

    # Inline code -> content only
    text = _RE_INLINE_CODE.sub(lambda m: m.group(1), text)

    # Images: keep alt and url
    text = _RE_IMG.sub(lambda m: f"{m.group(1).strip()} ({m.group(2).strip()})".strip(), text)

    # Links: text (url)
    text = _RE_LINK.sub(lambda m: f"{m.group(1).strip()} ({m.group(2).strip()})", text)

    # Headings: remove leading #+
    text = _RE_H.sub("", text)

    # Blockquotes: remove >
    text = _RE_BLOCKQUOTE.sub("", text)

    # Bold / Italic / Strikethrough -> plain
    text = _RE_BOLD.sub(lambda m: (m.group(1) or m.group(2) or ""), text)
    text = _RE_ITALIC.sub(lambda m: (m.group(1) or m.group(2) or ""), text)
    text = _RE_STRIKE.sub(lambda m: m.group(1) or "", text)

    # Replace table pipes with spaces (basic)
    text = re.sub(r"\s*\|\s*", " ", text)

    # Normalize list bullets spacing
    text = re.sub(r"^\s*[-*+]\s+", "- ", text, flags=re.MULTILINE)
    # Numbered lists: '1. ' -> '1) '
    text = re.sub(r"^\s*(\d+)\.\s+", r"\1) ", text, flags=re.MULTILINE)

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Trim trailing spaces per line
    text = re.sub(r"[ \t]+\n", "\n", text)

    return text.strip()
