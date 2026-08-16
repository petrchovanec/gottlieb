from __future__ import annotations

import html
import re
import shutil
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SITE_DIR = ROOT / "site"
DIST_DIR = ROOT / "dist"
BASE_PATH = "/gottlieb/"
PUBLIC_URL = "https://petrchovanec.github.io/gottlieb/"

NAVIGATION = [
    ("home", "Home", "index.html"),
    ("biography", "Biography", "biography.html"),
    ("timeline", "Timeline", "timeline.html"),
    ("hotels", "Hotels & Places", "hotels-places.html"),
    ("people", "People", "people.html"),
    ("sources", "Sources", "sources.html"),
    ("questions", "Research Questions", "research-questions.html"),
    ("methodology", "Methodology", "methodology.html"),
    ("about", "About", "about.html"),
]

STATUS_LABELS = {
    "verified-direct": "Verified direct",
    "prior-chat-verified": "Previously verified",
    "catalog-verified": "Catalog verified",
    "user-supplied": "User supplied",
    "indexed-lead": "Indexed lead",
    "needs-recheck": "Needs recheck",
    "conflict": "Conflicting evidence",
    "research-lead": "Research lead",
    "high-priority-research-lead": "High-priority lead",
    "open-question": "Open question",
    "official-secondary": "Official secondary",
    "working-identity": "Working identity",
    "source-attested-initials-unresolved": "Source-attested initials",
    "unresolved-secondary-source-name": "Unresolved name",
    "named-in-secondary-source": "Named in secondary source",
    "source-author": "Source author",
}

STATUS_DEFINITIONS = [
    ("verified-direct", "The source or a sufficiently detailed source record has been inspected."),
    ("prior-chat-verified", "Previously inspected, but the exact scan or page should be reacquired before publication where possible."),
    ("catalog-verified", "The source's existence and bibliographic identity are verified; its contents have not yet been inspected."),
    ("official-secondary", "An official or archival institution's secondary historical account was inspected; any underlying primary files remain separately qualified."),
    ("user-supplied", "Supplied through family or genealogical research and not independently established here."),
    ("indexed-lead", "Indicated by a catalog, listing, result, or OCR index; the primary source has not been adequately inspected."),
    ("needs-recheck", "An earlier finding lacks enough current documentation to be published as fact."),
    ("conflict", "The evidence conflicts with stronger or other evidence and must remain visible."),
    ("research-lead", "A source or record set to investigate, not evidence for a biographical fact."),
    ("open-question", "An explicitly unresolved question, not a factual assertion."),
]


def load_records(filename: str, key: str) -> list[dict[str, Any]]:
    document = yaml.safe_load((DATA_DIR / filename).read_text(encoding="utf-8"))
    return document[key]


sources = load_records("sources.yml", "sources")
claims = load_records("claims.yml", "claims")
events = load_records("timeline.yml", "events")
people = load_records("people.yml", "people")
places = load_records("places.yml", "places")
organizations = load_records("organizations.yml", "organizations")

SOURCE_BY_ID = {item["id"]: item for item in sources}
CLAIM_BY_ID = {item["id"]: item for item in claims}
PERSON_BY_ID = {item["id"]: item for item in people}
PLACE_BY_ID = {item["id"]: item for item in places}
ORG_BY_ID = {item["id"]: item for item in organizations}


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def internal_url(page: str = "index.html", fragment: str | None = None) -> str:
    path = BASE_PATH if page == "index.html" else f"{BASE_PATH}{page}"
    if fragment:
        path += f"#{fragment}"
    return path


def external_url(url: str, label: str) -> str:
    return f'<a href="{esc(url)}" rel="noreferrer">{esc(label)}<span aria-hidden="true"> ↗</span></a>'


def status_badge(status: str, scope: str | None = None) -> str:
    label = STATUS_LABELS.get(status, status.replace("-", " ").title())
    title = f' title="{esc(scope)}"' if scope else ""
    return f'<span class="evidence-badge status-{esc(status)}"{title}>{esc(label)}</span>'


def source_citations(source_ids: list[str], label: str = "Sources") -> str:
    if not source_ids:
        return '<span class="citation citation-empty">No supporting source yet — open question</span>'
    links = ", ".join(
        f'<a href="{internal_url("sources.html", source_id)}">{esc(source_id)}</a>'
        for source_id in source_ids
    )
    return f'<span class="citation"><span>{esc(label)}:</span> {links}</span>'


def caution(text: str | None) -> str:
    if not text:
        return ""
    return f'<p class="caution"><strong>Caution:</strong> {esc(text)}</p>'


def claim_card(claim_id: str, compact: bool = False) -> str:
    claim = CLAIM_BY_ID[claim_id]
    classes = "evidence-card evidence-card-compact" if compact else "evidence-card"
    conflicts = ""
    if claim.get("conflicts_with"):
        links = ", ".join(
            f'<a href="{internal_url("biography.html", conflict_id)}">{esc(conflict_id)}</a>'
            for conflict_id in claim["conflicts_with"]
        )
        conflicts = f'<p class="conflict-links"><strong>Conflicts with:</strong> {links}</p>'
    return f"""
    <article class="{classes}" id="{esc(claim_id)}">
      <div class="record-heading">
        <span class="record-id">{esc(claim_id)}</span>
        {status_badge(claim["status"], claim.get("status_scope"))}
      </div>
      <p class="claim-statement">{esc(claim["statement"])}</p>
      {source_citations(claim.get("sources", []))}
      {conflicts}
      {caution(claim.get("caution"))}
    </article>
    """


def evidence_key() -> str:
    key_statuses = ["verified-direct", "official-secondary", "prior-chat-verified", "user-supplied", "indexed-lead", "needs-recheck", "conflict", "open-question"]
    badges = "".join(status_badge(status) for status in key_statuses)
    return f'<aside class="evidence-key" aria-label="Evidence status key"><strong>Evidence key</strong><div>{badges}</div></aside>'


def page_layout(page_id: str, title: str, description: str, content: str) -> str:
    nav = "".join(
        f'<a href="{internal_url(page)}"' + (' aria-current="page"' if nav_id == page_id else "") + f'>{esc(label)}</a>'
        for nav_id, label, page in NAVIGATION
    )
    canonical = PUBLIC_URL if page_id == "home" else f"{PUBLIC_URL}{next(page for nav_id, _, page in NAVIGATION if nav_id == page_id)}"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} · Hermann Gottlieb Research</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)} · Hermann Gottlieb Research">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{PUBLIC_URL}assets/og.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)} · Hermann Gottlieb Research">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{PUBLIC_URL}assets/og.png">
  <link rel="stylesheet" href="{BASE_PATH}assets/styles.css">
  <script src="{BASE_PATH}assets/site.js" defer></script>
</head>
<body data-page="{esc(page_id)}">
  <a class="skip-link" href="#main-content">Skip to content</a>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="{BASE_PATH}" aria-label="Hermann Gottlieb Research home">
        <span>Historical research dossier</span>
        <strong>Sylvester Hermann Gottlieb</strong>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-navigation">Menu</button>
      <nav id="primary-navigation" class="primary-nav" aria-label="Primary navigation">{nav}</nav>
    </div>
  </header>
  <main id="main-content">{content}</main>
  <footer class="site-footer">
    <div>
      <p><strong>Hermann Gottlieb Historical Research</strong></p>
      <p>An evidence-led public dossier. Research updated 16 August 2026.</p>
    </div>
    <div class="footer-links">
      <a href="{internal_url('methodology.html')}">Evidence methodology</a>
      <a href="{internal_url('sources.html')}">Source catalogue</a>
      <a href="{internal_url('research-questions.html')}">Open questions</a>
    </div>
  </footer>
</body>
</html>
"""


def page_header(kicker: str, title: str, intro: str) -> str:
    return f"""
    <header class="page-hero container">
      <p class="kicker">{esc(kicker)}</p>
      <h1>{esc(title)}</h1>
      <p class="lede">{esc(intro)}</p>
    </header>
    """


def build_home() -> str:
    identity = CLAIM_BY_ID["CLAIM-IDENTITY-SYLVESTER-AND-SH"]
    content = f"""
    <section class="home-hero">
      <div class="container home-hero-grid">
        <div>
          <p class="kicker">Historical and genealogical research dossier</p>
          <h1>A historical life reconstructed source by source.</h1>
          <p class="hero-summary">This public research project examines the life and hotel career associated with the names Sylvester Hermann Gottlieb and S. H. Gottlieb, while keeping evidence, uncertainty, and conflict visible.</p>
          <div class="hero-actions">
            <a class="button button-primary" href="{internal_url('biography.html')}">Read the working biography</a>
            <a class="button button-secondary" href="{internal_url('sources.html')}">Browse {len(sources)} sources</a>
          </div>
        </div>
        <aside class="identity-card">
          <div class="record-heading"><span class="record-id">Identity note</span>{status_badge(identity['status'])}</div>
          <p>{esc(identity['statement'])}</p>
          {source_citations(identity['sources'])}
          {caution(identity['caution'])}
        </aside>
      </div>
    </section>
    <section class="section container">
      <div class="section-heading">
        <div><p class="kicker">Documented anchors</p><h2>What the evidence currently supports</h2></div>
        <p>The strongest findings are presented with their qualifications and source IDs intact.</p>
      </div>
      <div class="card-grid card-grid-2">
        {claim_card('CLAIM-BAUR-BIBLOS-OCR', compact=True)}
        {claim_card('CLAIM-SAVOY-1922', compact=True)}
        {claim_card('CLAIM-SYLVESTER-BADEN-HOTELIER-1931', compact=True)}
        {claim_card('CLAIM-MESSMER-LESSEE-1931', compact=True)}
      </div>
    </section>
    <section class="section section-tinted">
      <div class="container split-feature">
        <div>
          <p class="kicker">Research priority</p>
          <h2>Trace the full-name hotelier.</h2>
          <p>Baden-Baden address books and the court file behind the 1931 bankruptcy notice may reveal residence, birth information, nationality, family status, and business arrangements—details needed to test the Zürich identity link.</p>
          {source_citations(['SRC-020', 'SRC-023'], 'Research leads')}
        </div>
        <div class="route-list">
          <a href="{internal_url('timeline.html')}"><strong>Follow the chronology</strong><span>See every event with its evidence status.</span></a>
          <a href="{internal_url('hotels-places.html')}"><strong>Explore hotels and places</strong><span>Separate documented associations from unresolved leads.</span></a>
          <a href="{internal_url('methodology.html')}"><strong>Understand the method</strong><span>Learn how facts, claims, and conflicts are handled.</span></a>
        </div>
      </div>
    </section>
    <div class="container">{evidence_key()}</div>
    """
    return page_layout("home", "Home", "An evidence-led historical research dossier about Sylvester Hermann Gottlieb and the source-attested hotelier S. H. Gottlieb.", content)


def build_biography() -> str:
    content = page_header(
        "Working biography",
        "Biography",
        "A source-led account that distinguishes direct evidence from genealogical information, prior findings, and unresolved identity questions.",
    )
    content += f"""
    <div class="container narrow">
      <aside class="editorial-note">
        <p class="kicker">Mandatory caveat</p>
        <p>{esc(CLAIM_BY_ID['CLAIM-IDENTITY-SYLVESTER-AND-SH']['public_wording'])}</p>
        {status_badge('open-question')} {source_citations(CLAIM_BY_ID['CLAIM-IDENTITY-SYLVESTER-AND-SH']['sources'])}
      </aside>
      <section class="biography-section">
        <p class="chapter-number">01</p><h2>Vienna origins</h2>
        <p>The current dossier contains one cautious working claim about birth. Exact birth and baptism dates, parish, parentage, and address remain unavailable until the original entry is inspected.</p>
        {claim_card('CLAIM-BIRTH-VIENNA-1871')}
      </section>
      <section class="biography-section">
        <p class="chapter-number">02</p><h2>Zürich and the Savoy-Baur en Ville</h2>
        <p>Several sources associate the initials S. H. Gottlieb with the hotel. The sequence now includes a verified 1914 guide entry and a verified 1922 listing, but the separate dates do not prove continuous service.</p>
        {source_citations(['SRC-001', 'SRC-002', 'SRC-003', 'SRC-004', 'SRC-019'])}
        {claim_card('CLAIM-SAVOY-1911')}
        {claim_card('CLAIM-BAUR-BIBLOS-OCR')}
        {claim_card('CLAIM-BAUR-POSTCARD')}
        {claim_card('CLAIM-SAVOY-1922')}
      </section>
      <section class="biography-section conflict-section">
        <p class="chapter-number">03</p><h2>The unresolved Savoy chronology</h2>
        <p>A secondary management sequence conflicts with the direct 1922 listing. The project preserves both accounts and adopts none of the possible explanations without further evidence.</p>
        {source_citations(['SRC-001', 'SRC-018'])}
        {claim_card('CLAIM-SAVOY-SECONDARY-DUFFING-1909-1910')}
        {claim_card('CLAIM-SAVOY-SECONDARY-GOTTLIEB-1910-1918')}
        {claim_card('CLAIM-SAVOY-SECONDARY-GIGER-1918-1926')}
      </section>
      <section class="biography-section">
        <p class="chapter-number">04</p><h2>A possible later Zürich connection</h2>
        <p>The 1922 guide names A. Kummer-Wenger with Hotel Victoria. A separate possible Gottlieb connection around 1924 remains unverified.</p>
        {claim_card('CLAIM-VICTORIA-1922-KUMMER-WENGER')}
        {claim_card('CLAIM-GRAND-VICTORIA-1924')}
      </section>
      <section class="biography-section">
        <p class="chapter-number">05</p><h2>Baden-Baden and Hotel Messmer</h2>
        <p>A contemporary notice dated 20 March 1931 gives the full name Sylvester Hermann Gottlieb, calls him a hotelier, and describes him as Pächter—lessee or operator—of Hotel Meßmer. It does not establish ownership of the property. An official historical account's reported 1930 closure conflicts with later directory leads and remains unresolved.</p>
        {source_citations(['SRC-007', 'SRC-008', 'SRC-009', 'SRC-020', 'SRC-021'])}
        {claim_card('CLAIM-MESSMER-1929')}
        {claim_card('CLAIM-MESSMER-CLOSED-SINCE-1930')}
        {claim_card('CLAIM-SYLVESTER-BADEN-HOTELIER-1931')}
        {claim_card('CLAIM-MESSMER-LESSEE-1931')}
        {claim_card('CLAIM-GOTTLIEB-BANKRUPTCY-AUFHEBUNG-1931')}
        {claim_card('CLAIM-MESSMER-C1932')}
        {claim_card('CLAIM-MESSMER-1934')}
        {claim_card('CLAIM-MESSMER-LASSMANN-PROPERTY')}
      </section>
      <section class="biography-section">
        <p class="chapter-number">06</p><h2>Later life</h2>
        {claim_card('CLAIM-DEATH-UNRESOLVED')}
      </section>
    </div>
    """
    return page_layout("biography", "Biography", "A cautious working biography built from source-linked claims and explicit evidence statuses.", content)


def build_timeline() -> str:
    items = []
    for event in events:
        items.append(f"""
        <article class="timeline-item" id="{esc(event['id'])}">
          <div class="timeline-date"><span>{esc(event['date_label'])}</span></div>
          <div class="timeline-content">
            <div class="record-heading"><span class="record-id">{esc(event['id'])}</span>{status_badge(event['status'], event.get('status_scope'))}</div>
            <h2>{esc(event['event'])}</h2>
            {source_citations(event.get('sources', []))}
            {caution(event.get('caution'))}
          </div>
        </article>
        """)
    content = page_header("Chronology", "Timeline", "A working chronology in which approximate dates remain approximate and unresolved events remain visibly unresolved.")
    content += f'<div class="container"><div class="timeline">{"".join(items)}</div>{evidence_key()}</div>'
    return page_layout("timeline", "Timeline", "The evidence-status timeline for the Hermann Gottlieb historical research project.", content)


def entity_claims(claim_ids: list[str]) -> str:
    if not claim_ids:
        return '<p class="muted">No biographical claim is attached to this record.</p>'
    rows = []
    for claim_id in claim_ids:
        claim = CLAIM_BY_ID[claim_id]
        rows.append(f"""
        <li>
          <div>{status_badge(claim['status'])}<span class="record-id">{esc(claim_id)}</span></div>
          <p>{esc(claim['statement'])}</p>
          {source_citations(claim.get('sources', []))}
        </li>
        """)
    return f'<ul class="entity-claims">{"".join(rows)}</ul>'


def build_hotels_places() -> str:
    featured_ids = ["ORG-SAVOY-BAUR-EN-VILLE", "ORG-GRAND-HOTEL-VICTORIA", "ORG-HOTEL-MESSMER"]
    hotel_cards = []
    for org_id in featured_ids:
        org = ORG_BY_ID[org_id]
        place_name = PLACE_BY_ID[org["place"]]["preferred_name"]
        hotel_cards.append(f"""
        <article class="entity-card" id="{esc(org_id)}">
          <p class="kicker">{esc(place_name)} · Hotel</p>
          <h2>{esc(org['preferred_name'])}</h2>
          {entity_claims(org.get('claims', []))}
          {caution(org.get('caution'))}
        </article>
        """)
    place_cards = []
    for place in places:
        place_cards.append(f"""
        <article class="place-card" id="{esc(place['id'])}">
          <div class="record-heading"><span class="record-id">{esc(place['id'])}</span>{status_badge(place['status']) if place.get('status') else ''}</div>
          <h3>{esc(place['preferred_name'])}</h3>
          <p>{esc(place['research_role'])}</p>
          {source_citations(place.get('source_mentions', []), 'Related sources')}
          {caution(place.get('caution'))}
        </article>
        """)
    content = page_header("Geography and institutions", "Hotels & Places", "The hotels and cities at the center of the research, with uncertain associations kept distinct from verified ones.")
    content += f"""
    <section class="section container"><div class="stack">{"".join(hotel_cards)}</div></section>
    <section class="section section-tinted"><div class="container"><div class="section-heading"><div><p class="kicker">Research geography</p><h2>Places</h2></div><p>Locations are research contexts, not automatic proof of residence or employment.</p></div><div class="card-grid card-grid-2">{"".join(place_cards)}</div></div></section>
    """
    return page_layout("hotels", "Hotels & Places", "Hotels and places in the Hermann Gottlieb research dossier, each tied to evidence-status claims.", content)


def build_people() -> str:
    cards = []
    for person in people:
        variants = ""
        names = person.get("research_name_variants") or person.get("attested_or_reported_forms")
        if names:
            variants = f'<p class="name-variants"><strong>Names used in research:</strong> {", ".join(esc(name) for name in names)}</p>'
        links = ""
        if person.get("identity_links"):
            link_rows = []
            for link in person["identity_links"]:
                target = PERSON_BY_ID[link["target"]]
                link_rows.append(f'<li>{esc(link["relationship"].replace("-", " "))}: <a href="#{esc(link["target"])}">{esc(target["preferred_name"])}</a> — {status_badge(link["status"])}</li>')
            links = f'<div class="identity-links"><strong>Identity links</strong><ul>{"".join(link_rows)}</ul></div>'
        cards.append(f"""
        <article class="person-card" id="{esc(person['id'])}">
          <div class="record-heading"><span class="record-id">{esc(person['id'])}</span>{status_badge(person['identity_status'])}</div>
          <h2>{esc(person['preferred_name'])}</h2>
          <p>{esc(person['record_scope'])}</p>
          {variants}{links}
          {entity_claims(person.get('claims', []))}
          {source_citations(person.get('source_mentions', []), 'Source mentions') if person.get('source_mentions') else ''}
          {caution(person.get('caution'))}
        </article>
        """)
    content = page_header("Identity-aware records", "People", "Separate person records prevent similar names and initials from being merged without corroborating evidence.")
    content += f"""
    <div class="container">
      <aside class="editorial-note"><p class="kicker">Identity rule</p><p>A matching surname or initial is not enough. Occupation, hotel, location, birth information, residence, or chronology must corroborate an identity.</p></aside>
      <div class="stack">{"".join(cards)}</div>
    </div>
    """
    return page_layout("people", "People", "Identity-aware person records for the Hermann Gottlieb historical research project.", content)


def render_detail_list(label: str, items: list[str] | None) -> str:
    if not items:
        return ""
    return f'<details><summary>{esc(label)}</summary><ul>{"".join(f"<li>{esc(item)}</li>" for item in items)}</ul></details>'


def build_sources() -> str:
    status_options = "".join(f'<option value="{esc(status)}">{esc(STATUS_LABELS.get(status, status.replace("-", " ").title()))}</option>' for status in sorted({source["status"] for source in sources}))
    cards = []
    for source in sources:
        metadata = []
        for label, field in [("Type", "type"), ("Date", "date_label"), ("Author", "author"), ("Repository", "repository"), ("Publisher", "publisher"), ("Series", "series"), ("Printed page", "printed_page"), ("Section", "section"), ("Archival reference", "archival_reference"), ("Accession", "accession")]:
            if source.get(field) is not None:
                metadata.append(f'<div><dt>{esc(label)}</dt><dd>{esc(source[field])}</dd></div>')
        descriptions = []
        for field in ["description", "establishes", "earlier_finding", "indexed_evidence", "subject_description", "coverage_note", "notes"]:
            if source.get(field):
                descriptions.append(f'<p>{esc(source[field])}</p>')
        url = f'<p class="source-link">{external_url(source["url"], "Open source record")}</p>' if source.get("url") else ""
        related = ""
        if source.get("claims"):
            related = f'<p class="related-records"><strong>Related claim IDs:</strong> {", ".join(f"<code>{esc(item)}</code>" for item in source["claims"])}</p>'
        search_text = " ".join(str(value) for value in source.values() if isinstance(value, (str, int)))
        cards.append(f"""
        <article class="source-card" id="{esc(source['id'])}" data-source-card data-status="{esc(source['status'])}" data-search="{esc(search_text.lower())}">
          <div class="record-heading"><span class="record-id">{esc(source['id'])}</span>{status_badge(source['status'], source.get('status_scope'))}</div>
          <h2>{esc(source['title'])}</h2>
          <dl class="source-meta">{"".join(metadata)}</dl>
          {''.join(descriptions)}
          {related}{url}
          {caution(source.get('caution'))}
          {render_detail_list('Missing or still needed', source.get('missing'))}
          {render_detail_list('Potential records', source.get('potential_records'))}
          {render_detail_list('Research value', source.get('research_value'))}
          {render_detail_list('Potential topics', source.get('potential_topics'))}
          {render_detail_list('Potential sources', source.get('potential_sources'))}
        </article>
        """)
    content = page_header("Annotated catalogue", "Sources", "Stable source IDs keep evidence synchronized across claims, timelines, entities, and future narrative pages.")
    content += f"""
    <div class="container">
      <div class="source-tools" aria-label="Filter sources">
        <label>Search sources<input type="search" data-source-search placeholder="Title, repository, ID…"></label>
        <label>Evidence status<select data-source-status><option value="">All statuses</option>{status_options}</select></label>
        <p aria-live="polite"><strong data-source-count>{len(sources)}</strong> sources shown</p>
      </div>
      <div class="source-list">{"".join(cards)}</div>
      <p class="no-results" data-source-empty hidden>No sources match those filters.</p>
    </div>
    """
    return page_layout("sources", "Sources", "The annotated source catalogue with stable IDs and explicit evidence statuses.", content)


RESEARCH_QUESTIONS = [
    ("Identity", [
        "What was Gottlieb's exact date of birth?",
        "Who were his parents?",
        "Which Vienna parish recorded his birth?",
        "Can a Zürich or Baden-Baden registration record link the full name Sylvester Hermann Gottlieb with the hotelier S. H. Gottlieb?",
    ]),
    ("Zürich career", [
        "When exactly did he join the Baur en Ville?",
        "Was he already director in 1910?",
        "What exactly does the 1911 advertisement say?",
        "Why does a secondary history end the Gottlieb management period in 1918 when a 1922 guide names S. H. Gottlieb as director?",
        "What role did Fritz Giger have in 1918–1926?",
        "When did Gottlieb leave the Savoy?",
        "Did he move directly to another Zürich hotel?",
        "Was he associated with Grand Hotel Victoria?",
        "If yes, in what capacity and for what dates?",
    ]),
    ("Baden-Baden", [
        "When did Gottlieb arrive in Baden-Baden?",
        "When did he take over Hotel Messmer?",
        "What were the terms and duration of his documented lease of Hotel Messmer?",
        "Who legally owned the hotel property during Gottlieb's association with it?",
        "Was he proprietor in 1929?",
        "How long did he remain associated with the hotel?",
        "Why do later directory leads appear after the hotel was reportedly closed in 1930?",
        "Why was the bankruptcy proceeding listed under Aufhebungen in March 1931?",
        "Where did he live?",
        "Was he married, and did family members live with him?",
    ]),
    ("Business connections", [
        "Was the Jakob Lassmann associated with Zürich's Baur en Ville the same person whose family was connected with Hotel Messmer?",
        "What does the Hotel Messmer restitution file reveal about ownership, leases, and Gottlieb's contractual role?",
    ]),
    ("Death", [
        "When and where did Gottlieb die?",
        "Is there an obituary?",
        "Is there a Baden-Baden civil death record?",
        "Did he leave an estate or probate file?",
    ]),
]

RESEARCH_PRIORITIES = [
    ("01", "Search Baden-Baden address books", "Check the 1928, 1930, 1932, 1935, and 1938 volumes for residence, occupation, household, and disappearance from the directory.", ["SRC-023"]),
    ("02", "Inspect the 1929 Hotel Messmer advertisement", "Verify its date, wording, and Gottlieb's stated role from the original item.", ["SRC-007"]),
    ("03", "Identify the 1931 bankruptcy court file", "Seek birth, nationality, residence, marital status, creditors, and business arrangements behind the notice.", ["SRC-020"]),
    ("04", "Search the Schweizer Hotel-Revue", "Search 1908–1925 for appointments, departures, hotel changes, advertisements, and personal notices.", ["SRC-024"]),
    ("05", "Search Zürich registration and address records", "Trace first appearance, residence, departure, and any person-level link to the full name.", ["SRC-005", "SRC-012"]),
    ("06", "Inspect the 1938 Savoy centenary book", "Search the volume for Gottlieb, predecessors, successors, and the unresolved management chronology.", ["SRC-010"]),
    ("07", "Reopen the 1932 and 1934 directory pages", "Capture exact scans, bibliographic data, and commercial wording before interpreting Inhaber.", ["SRC-008", "SRC-009"]),
    ("08", "Investigate the Lassmann connection", "Test the possible Zürich–Baden property link without assuming it explains Gottlieb's move.", ["SRC-018", "SRC-021", "SRC-022", "SRC-026"]),
    ("09", "Return to Vienna records with stronger identifiers", "Use any precise age, date, nationality, or residence recovered in Baden or Zürich to locate the original birth record.", ["SRC-011", "SRC-025"]),
    ("10", "Search Baden-Baden death records and press", "Work forward after 1931 without assuming a death date or place.", ["SRC-013", "SRC-017"]),
]


def build_questions() -> str:
    question_sections = []
    number = 1
    for title, questions in RESEARCH_QUESTIONS:
        items = []
        for question in questions:
            items.append(f'<li><span>{number:02d}</span><p>{esc(question)}</p></li>')
            number += 1
        question_sections.append(f'<section class="question-group"><h2>{esc(title)}</h2><ol>{"".join(items)}</ol></section>')
    priorities = "".join(f"""
      <article class="priority-card"><span>{esc(number)}</span><div><h3>{esc(title)}</h3><p>{esc(description)}</p>{source_citations(source_ids, 'Research targets')}</div></article>
    """ for number, title, description, source_ids in RESEARCH_PRIORITIES)
    content = page_header("Open research agenda", "Research Questions", "Uncertainty is part of the public record. These questions define what the project still needs to establish.")
    content += f"""
    <section class="section container">
      <aside class="editorial-note"><div class="record-heading"><span class="record-id">Research status</span>{status_badge('open-question')}</div><p>Questions on this page are research objectives, not biographical facts. They remain open until source-linked claims resolve them.</p></aside>
      <div class="question-layout">{"".join(question_sections)}</div>
    </section>
    <section class="section section-tinted"><div class="container"><div class="section-heading"><div><p class="kicker">Next work</p><h2>Priority research queue</h2></div><p>The order favors records most likely to resolve identity and chronology.</p></div><div class="priority-list">{priorities}</div></div></section>
    """
    return page_layout("questions", "Research Questions", "The unresolved questions and prioritized research queue for the Hermann Gottlieb project.", content)


def build_methodology() -> str:
    status_rows = "".join(f'<div class="status-definition">{status_badge(status)}<p>{esc(description)}</p></div>' for status, description in STATUS_DEFINITIONS)
    content = page_header("Evidence before narrative", "Methodology", "The project makes the path from source to public statement visible and keeps uncertainty attached to every claim.")
    content += f"""
    <section class="section container narrow">
      <div class="method-flow" aria-label="Sources support claims, which support public presentation">
        <div><span>01</span><strong>Sources</strong><p>Stable bibliographic and archival records.</p></div>
        <div class="flow-arrow" aria-hidden="true">→</div>
        <div><span>02</span><strong>Claims</strong><p>Exact statements with status and citations.</p></div>
        <div class="flow-arrow" aria-hidden="true">→</div>
        <div><span>03</span><strong>Presentation</strong><p>Biography, timeline, people, and places.</p></div>
      </div>
      <section class="method-section"><h2>Evidence statuses</h2><div class="status-definitions">{status_rows}</div></section>
      <section class="method-section"><h2>Rules for historical claims</h2><ol class="rule-list"><li>Never invent facts, dates, citations, archival references, or relationships.</li><li>Every factual historical claim links to one or more stable source IDs.</li><li>Inference, family tradition, catalog metadata, OCR, and research leads remain labeled.</li><li>Primary and contemporary evidence is preferred, but contradictions remain visible.</li><li>A dead URL does not erase a source record; its bibliography and stable ID remain.</li></ol></section>
      <section class="method-section"><h2>Identity resolution</h2><p>Similar names and initials are not automatically the same person. The model keeps Vienna-born Sylvester Hermann Gottlieb separate from the source-attested hotelier S. H. Gottlieb until a municipal or other person-level record links them.</p>{claim_card('CLAIM-IDENTITY-SYLVESTER-AND-SH', compact=True)}</section>
      <section class="method-section"><h2>Conflicting evidence</h2><p>The direct 1922 hotel listing and the secondary Savoy chronology are both retained. Hotel Messmer's reported 1930 closure is likewise shown beside later directory leads. The site does not select a convenient explanation.</p>{claim_card('CLAIM-SAVOY-1922', compact=True)}{claim_card('CLAIM-SAVOY-SECONDARY-GIGER-1918-1926', compact=True)}{claim_card('CLAIM-MESSMER-CLOSED-SINCE-1930', compact=True)}{claim_card('CLAIM-MESSMER-1934', compact=True)}</section>
      <section class="method-section"><h2>Images and rights</h2><p>An old image is not assumed to be free to reproduce. Publication requires a recorded source, creator or publisher when known, date when known, holding institution, permanent URL, rights statement, permission status, caption, and source ID.</p></section>
    </section>
    """
    return page_layout("methodology", "Methodology", "How the project distinguishes sources, claims, conflicts, hypotheses, and public presentation.", content)


def build_about() -> str:
    content = page_header("About the project", "About", "A public historical and genealogical research site designed to grow without hiding uncertainty or disconnecting narrative from evidence.")
    content += f"""
    <div class="container narrow">
      <section class="about-intro"><p class="drop-cap">This project investigates the life and Central European hotel career associated with Sylvester Hermann Gottlieb and the initials S. H. Gottlieb. Its purpose is not to force a complete biography from incomplete evidence, but to publish what the sources support and show what remains unresolved.</p></section>
      <section class="stats-grid" aria-label="Structured research data counts">
        <div><strong>{len(sources)}</strong><span>Sources and research targets</span></div>
        <div><strong>{len(claims)}</strong><span>Evidence-status claims</span></div>
        <div><strong>{len(events)}</strong><span>Timeline records</span></div>
        <div><strong>{len(people)}</strong><span>Identity-aware people</span></div>
      </section>
      <section class="about-section"><h2>Version 1</h2><p>This first public version turns the structured YAML research layer into nine static pages. There is no database, account system, or backend. Future evidence can be added to the source and claim files, validated, and regenerated into the site.</p></section>
      <section class="about-section"><h2>Current bottom line</h2>{claim_card('CLAIM-BAUR-BIBLOS-OCR', compact=True)}{claim_card('CLAIM-SAVOY-1922', compact=True)}{claim_card('CLAIM-MESSMER-LESSEE-1931', compact=True)}<p>These sources establish two compatible hotel-career clusters, but they do not directly join the Zürich initials to the full Baden-Baden name or to the reported Vienna birth.</p>{claim_card('CLAIM-IDENTITY-SYLVESTER-AND-SH', compact=True)}</section>
      <section class="about-section"><h2>Corrections and future evidence</h2><p>New material should identify the source, its holding institution or publication, date and page where available, and the exact claim it supports or contradicts. Source records remain stable even if an external URL later becomes unavailable.</p><a class="button button-secondary" href="{internal_url('methodology.html')}">Read the evidence method</a></section>
    </div>
    """
    return page_layout("about", "About", "About the evidence-led Hermann Gottlieb historical research project and its static data-driven architecture.", content)


def build_404() -> str:
    content = f"""
    <section class="not-found container"><p class="kicker">404</p><h1>Page not found</h1><p>The requested page is not part of this research dossier.</p><a class="button button-primary" href="{BASE_PATH}">Return home</a></section>
    """
    page = page_layout("home", "Page not found", "The requested page was not found.", content)
    return page.replace('<meta name="description"', '<meta name="robots" content="noindex">\n  <meta name="description"', 1)


PAGES = {
    "index.html": build_home,
    "biography.html": build_biography,
    "timeline.html": build_timeline,
    "hotels-places.html": build_hotels_places,
    "people.html": build_people,
    "sources.html": build_sources,
    "research-questions.html": build_questions,
    "methodology.html": build_methodology,
    "about.html": build_about,
    "404.html": build_404,
}


def validate_base_paths(markup: str, filename: str) -> None:
    for attribute, value in re.findall(r'(href|src)="([^"]+)"', markup):
        if value.startswith("/") and not value.startswith(BASE_PATH):
            raise ValueError(f"{filename}: {attribute} uses an invalid root path: {value}")


def main() -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    assets_source = SITE_DIR / "assets"
    if not assets_source.exists():
        raise SystemExit("site/assets is missing")
    shutil.copytree(assets_source, DIST_DIR / "assets", dirs_exist_ok=True)
    for filename, builder in PAGES.items():
        markup = "\n".join(line.rstrip() for line in builder().splitlines()) + "\n"
        validate_base_paths(markup, filename)
        (DIST_DIR / filename).write_text(markup, encoding="utf-8", newline="\n")
    (DIST_DIR / ".nojekyll").write_text("", encoding="utf-8")
    (DIST_DIR / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {PUBLIC_URL}sitemap.xml\n", encoding="utf-8")
    sitemap = "\n".join(f"  <url><loc>{PUBLIC_URL if page == 'index.html' else PUBLIC_URL + page}</loc></url>" for _, _, page in NAVIGATION)
    (DIST_DIR / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap}\n</urlset>\n', encoding="utf-8")
    print(f"Built {len(PAGES)} HTML files in {DIST_DIR}")


if __name__ == "__main__":
    main()
