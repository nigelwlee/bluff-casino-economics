"""
Layer 1 & 2: Static knowledge loader.

Reads markdown files from memory/domain/ and memory/company/,
caches them with lru_cache for performance.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

MEMORY_DIR = Path(__file__).parent


@lru_cache(maxsize=1)
def load_domain_knowledge() -> str:
    """Read all .md files from memory/domain/ and concatenate them."""
    domain_dir = MEMORY_DIR / "domain"
    if not domain_dir.exists():
        return ""
    parts: list[str] = []
    for md_file in sorted(domain_dir.glob("*.md")):
        parts.append(md_file.read_text(encoding="utf-8").strip())
    return "\n\n---\n\n".join(parts)


@lru_cache(maxsize=1)
def load_company_knowledge() -> str:
    """Read all .md files from memory/company/ and concatenate them."""
    company_dir = MEMORY_DIR / "company"
    if not company_dir.exists():
        return ""
    parts: list[str] = []
    for md_file in sorted(company_dir.glob("*.md")):
        parts.append(md_file.read_text(encoding="utf-8").strip())
    return "\n\n---\n\n".join(parts)


def reload_knowledge() -> None:
    """Clear caches to pick up file changes (hot-reload)."""
    load_domain_knowledge.cache_clear()
    load_company_knowledge.cache_clear()
