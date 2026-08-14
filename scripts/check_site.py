from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DATA = ROOT / "data"
BASE_PATH = "/hermann-gottlieb/"
REQUIRED_PAGES = {
    "index.html",
    "biography.html",
    "timeline.html",
    "hotels-places.html",
    "people.html",
    "sources.html",
    "research-questions.html",
    "methodology.html",
    "about.html",
    "404.html",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()
        self.has_title = False
        self.has_viewport = False
        self.has_main = False
        self.badge_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if tag == "title":
            self.has_title = True
        if tag == "meta" and values.get("name") == "viewport":
            self.has_viewport = True
        if tag == "main":
            self.has_main = True
        if "evidence-badge" in (values.get("class") or "").split():
            self.badge_count += 1
        for attribute in ("href", "src"):
            if values.get(attribute):
                self.links.append((attribute, values[attribute] or ""))


def load_yaml(filename: str, key: str) -> list[dict]:
    return yaml.safe_load((DATA / filename).read_text(encoding="utf-8"))[key]


def validate_data() -> tuple[list[str], dict[str, set[str]]]:
    errors: list[str] = []
    datasets = {
        "sources": load_yaml("sources.yml", "sources"),
        "claims": load_yaml("claims.yml", "claims"),
        "events": load_yaml("timeline.yml", "events"),
        "people": load_yaml("people.yml", "people"),
        "places": load_yaml("places.yml", "places"),
        "organizations": load_yaml("organizations.yml", "organizations"),
    }
    ids: dict[str, set[str]] = {}
    for kind, records in datasets.items():
        record_ids = [record.get("id") for record in records]
        if None in record_ids:
            errors.append(f"{kind}: record without an ID")
        if len(record_ids) != len(set(record_ids)):
            errors.append(f"{kind}: duplicate IDs")
        ids[kind] = set(record_ids)

    reference_fields = {
        "sources": {"claims": "claims", "research_targets": "claims"},
        "claims": {"subjects": "people", "organizations": "organizations", "places": "places", "sources": "sources", "conflicts_with": "claims", "potential_resolution_sources": "sources", "research_targets": "sources"},
        "events": {"subjects": "people", "organizations": "organizations", "places": "places", "claims": "claims", "sources": "sources", "research_targets": "sources"},
        "people": {"claims": "claims", "source_mentions": "sources"},
        "places": {"claims": "claims", "source_mentions": "sources", "parent_place": "places"},
        "organizations": {"claims": "claims", "source_mentions": "sources", "place": "places"},
    }
    for kind, fields in reference_fields.items():
        for record in datasets[kind]:
            for field, target_kind in fields.items():
                references = record.get(field, [])
                if references is None:
                    continue
                if not isinstance(references, list):
                    references = [references]
                for reference in references:
                    if reference not in ids[target_kind]:
                        errors.append(f"{record['id']}.{field}: missing {reference}")
            if kind == "people":
                for link in record.get("identity_links", []):
                    if link.get("target") not in ids["people"]:
                        errors.append(f"{record['id']}.identity_links: missing {link.get('target')}")

    for claim in datasets["claims"]:
        if claim["status"] != "open-question" and not claim.get("sources"):
            errors.append(f"{claim['id']}: non-open claim has no source")
    for event in datasets["events"]:
        if event["status"] != "open-question" and not event.get("sources"):
            errors.append(f"{event['id']}: non-open event has no source")
    return errors, ids


def local_target(value: str, current_page: Path) -> tuple[Path | None, str | None]:
    parsed = urlsplit(value)
    if parsed.scheme in {"http", "https", "mailto", "tel"}:
        return None, parsed.fragment or None
    if value.startswith("#"):
        return current_page, parsed.fragment or None
    path = unquote(parsed.path)
    if path.startswith("/"):
        if not path.startswith(BASE_PATH):
            return Path("__invalid_base__"), parsed.fragment or None
        path = path[len(BASE_PATH) :]
    if not path or path.endswith("/"):
        path += "index.html"
    return DIST / path, parsed.fragment or None


def validate_pages(source_ids: set[str]) -> list[str]:
    errors: list[str] = []
    missing_pages = REQUIRED_PAGES - {path.name for path in DIST.glob("*.html")}
    if missing_pages:
        errors.append(f"Missing pages: {', '.join(sorted(missing_pages))}")
    parsed_pages: dict[Path, PageParser] = {}
    for page in DIST.glob("*.html"):
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        parsed_pages[page.resolve()] = parser
        if not parser.has_title:
            errors.append(f"{page.name}: missing title")
        if not parser.has_viewport:
            errors.append(f"{page.name}: missing viewport meta")
        if not parser.has_main:
            errors.append(f"{page.name}: missing main landmark")
        if page.name != "404.html" and parser.badge_count == 0:
            errors.append(f"{page.name}: no visible evidence-status label")

    for page, parser in parsed_pages.items():
        for attribute, value in parser.links:
            target, fragment = local_target(value, page)
            if target is None:
                continue
            if target == Path("__invalid_base__"):
                errors.append(f"{page.name}: {attribute} escapes {BASE_PATH}: {value}")
                continue
            target = target.resolve()
            if not target.exists():
                errors.append(f"{page.name}: broken {attribute}: {value}")
                continue
            if fragment and target.suffix == ".html":
                target_parser = parsed_pages.get(target)
                if target_parser is None:
                    target_parser = PageParser()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                    parsed_pages[target] = target_parser
                if fragment not in target_parser.ids:
                    errors.append(f"{page.name}: missing fragment #{fragment} in {target.name}")

    source_page = parsed_pages.get((DIST / "sources.html").resolve())
    if source_page:
        missing_source_anchors = source_ids - source_page.ids
        if missing_source_anchors:
            errors.append(f"sources.html: missing stable IDs {', '.join(sorted(missing_source_anchors))}")
    return errors


def main() -> None:
    if not DIST.exists():
        raise SystemExit("dist/ is missing; build the site first")
    data_errors, ids = validate_data()
    page_errors = validate_pages(ids["sources"])
    errors = data_errors + page_errors
    if errors:
        print("Site validation failed:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    print("Validated structured evidence and generated site.")
    print(f"Checked {len(REQUIRED_PAGES)} HTML pages, {len(ids['sources'])} source anchors, and all internal links.")


if __name__ == "__main__":
    main()
