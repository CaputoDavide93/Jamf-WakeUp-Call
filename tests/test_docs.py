"""Docs stay linked and plain: every relative link resolves, and no em or en dashes."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "llms.txt", *sorted((ROOT / "docs").glob("*.md"))]
LINK = re.compile(r"(?:\]\(|src(?:set)?=\")([^)\"#]+)")


def _relative_targets(page):
    for target in LINK.findall(page.read_text(encoding="utf-8")):
        if not target.startswith(("http://", "https://", "mailto:")):
            yield target


def test_relative_links_and_images_exist():
    missing = [
        f"{page.relative_to(ROOT)} -> {target}"
        for page in PAGES
        for target in _relative_targets(page)
        if not (page.parent / target).exists()
    ]
    assert not missing, missing


def test_no_em_or_en_dashes():
    bad = [page.name for page in PAGES if re.search("[–—]", page.read_text(encoding="utf-8"))]
    assert not bad, bad


def test_docs_are_listed_in_the_index():
    index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    unlisted = [p.name for p in (ROOT / "docs").glob("*.md") if p.name != "README.md" and p.name not in index]
    assert not unlisted, unlisted
