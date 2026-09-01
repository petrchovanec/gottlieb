# Hermann Gottlieb Historical Research

An evidence-led public research site about Sylvester Hermann Gottlieb and the
source-attested hotelier S. H. Gottlieb. The project keeps verified facts,
conflicting evidence, hypotheses, and research leads visibly distinct.

Planned public URL:
[petrchovanec.github.io/gottlieb](https://petrchovanec.github.io/gottlieb/)

## Research architecture

- `research.md` is the consolidated current research dossier.
- `research/` preserves dated research snapshots, supporting notes, and local
  evidence images as an audit trail.
- `AGENTS.md` contains the mandatory historical and evidence rules.
- `data/sources.yml` stores stable source records.
- `data/claims.yml` links exact historical statements to source IDs.
- `data/timeline.yml`, `data/people.yml`, `data/places.yml`, and
  `data/organizations.yml` organize sourced claims for presentation.
- `scripts/build_site.py` generates the static site in `dist/`.

To add evidence, update the source record first, then the claims it supports or
contradicts, and only then update timeline or entity records. Never place a new
historical assertion only in presentation code.

## Build locally

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python scripts\build_site.py
.\.venv\Scripts\python scripts\check_site.py
.\.venv\Scripts\python scripts\serve_site.py
```

The preview is served at
`http://127.0.0.1:8000/gottlieb/`, matching the GitHub Pages base path.

## GitHub Pages

The Pages workflow builds and validates the site from the structured YAML on
every push to `main`, then deploys the generated static files. All internal and
asset URLs are rooted under `/gottlieb/`.
