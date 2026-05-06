import json
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from django.core.management.base import BaseCommand

from chat.services import KNOWLEDGE_BASE_DIR, SOURCE_DOCUMENTS, build_knowledge_chunks, write_chunks


class _TextHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "svg", "noscript"}:
            self.skip = True

    def handle_endtag(self, tag):
        if tag in {"script", "style", "svg", "noscript"}:
            self.skip = False
        if tag in {"p", "li", "h1", "h2", "h3", "tr", "section", "article"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text:
                self.parts.append(text)

    def text(self):
        return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", "\n".join(self.parts))).strip()


class Command(BaseCommand):
    help = "Download official diet/activity guideline sources and build chat RAG chunks."

    def add_arguments(self, parser):
        parser.add_argument("--download", action="store_true", help="Download configured source documents first.")

    def handle(self, *args, **options):
        source_dir = KNOWLEDGE_BASE_DIR / "sources"
        source_dir.mkdir(parents=True, exist_ok=True)

        if options["download"]:
            for source in SOURCE_DOCUMENTS:
                path = source_dir / source["filename"]
                path.parent.mkdir(parents=True, exist_ok=True)
                self.stdout.write(f"Downloading {source['source']} -> {path}")
                request = urllib.request.Request(source["url"], headers={"User-Agent": "FitGenius/1.0"})
                with urllib.request.urlopen(request, timeout=60) as response:
                    path.write_bytes(response.read())

        documents = []
        for source in SOURCE_DOCUMENTS:
            path = source_dir / source["filename"]
            if not path.exists():
                self.stdout.write(self.style.WARNING(f"Missing source, skipped: {path}"))
                continue
            text = _extract_text(path)
            if text:
                documents.append({**source, "text": text})

        chunks = build_knowledge_chunks(documents)
        output_path = write_chunks(chunks)
        manifest_path = KNOWLEDGE_BASE_DIR / "manifest.json"
        manifest_path.write_text(json.dumps(SOURCE_DOCUMENTS, indent=2), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Wrote {len(chunks)} chunks to {output_path}"))


def _extract_text(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("Install pypdf to extract PDF knowledge-base sources.") from exc
        reader = PdfReader(str(path))
        return "\n\n".join(page.extract_text() or "" for page in reader.pages).strip()

    content = path.read_bytes()
    text = content.decode("utf-8", errors="ignore")
    if suffix in {".html", ".htm"}:
        parser = _TextHTMLParser()
        parser.feed(text)
        return parser.text()
    return text
