# Research and Evidence Rules

These instructions apply to the entire repository. Top-level `research.md` is
the current consolidated research dossier. The dated and source Markdown files
in `research/` are cumulative evidence snapshots and the audit trail. The files
in `data/` are structured representations of that evidence base; they do not
supersede it.

## Non-negotiable historical standards

1. Never invent a historical fact, date, name, relationship, quotation, source,
   citation, archival reference, URL, or image right.
2. Never silently turn an inference, family tradition, search result, catalog
   description, OCR hit, or research lead into an established fact.
3. Preserve uncertainty in both data and prose. Clearly label verified facts,
   user-supplied information, hypotheses, unresolved questions, research leads,
   and conflicting evidence.
4. Every factual historical claim must reference one or more stable source IDs.
   A claim with no source must remain an explicit open question and must not be
   presented as fact.
5. Prefer primary and contemporary sources. A secondary source does not override
   contradictory contemporary evidence without an explicit explanation.
6. Preserve conflicts until evidence resolves them. Do not choose the convenient
   account, merge incompatible dates, or hide a contradiction from the website.
7. Do not assume that every `Hermann Gottlieb`, `S. Gottlieb`, `S. H. Gottlieb`,
   `Silvester Gottlieb`, or bare `Gottlieb` denotes the same person. Require
   corroboration such as occupation, hotel, location, birth information,
   residence, or a compatible chronology before merging identities.
8. Do not create speculative family relationships or biographical details.

## Evidence statuses

Preserve the dossier's evidence status and its qualification. Use these statuses
without promoting them:

- `verified-direct`: the source or a sufficiently detailed source record was
  inspected.
- `prior-chat-verified`: previously inspected, but the exact scan or page should
  be reacquired before publication where possible.
- `catalog-verified`: the source's existence and bibliographic identity are
  verified, but its contents have not been inspected.
- `official-secondary`: an official or archival institution's secondary
  historical account was inspected, while any underlying primary files remain
  separately qualified.
- `user-supplied`: supplied through family or genealogical research and not yet
  independently established here.
- `indexed-lead`: indicated by a catalog, result, listing, OCR index, or similar
  record; the underlying primary source has not been adequately inspected.
- `needs-recheck`: an earlier finding lacks enough current documentation to be
  published as fact.
- `conflict`: evidence conflicts with stronger or other evidence.
- `research-lead` and `high-priority-research-lead`: a source or record set to
  investigate, not evidence for a biographical fact.
- `open-question`: an explicitly unresolved question, not a factual assertion.

In particular, never silently promote `indexed-lead`, `needs-recheck`, or
`user-supplied` material into an established fact.

## Source, claim, and presentation separation

Maintain three distinct layers:

1. `data/sources.yml` describes historical sources and research targets.
2. `data/claims.yml` records what those sources support, contradict, or merely
   suggest.
3. Timeline, people, places, organizations, and future narrative or UI files
   consume claim and source IDs; they do not become independent authorities.

Do not hard-code historical facts only in components, templates, or prose. Store
the evidence-bearing record in `data/` first, then render it in the website.
Presentation code must not erase qualifications or display unresolved material
as verified.

## Stable IDs and data integrity

- Give every source, claim, event, person, place, and organization a unique,
  stable ID using the existing prefixes (`SRC-`, `CLAIM-`, `EVT-`, `PERSON-`,
  `PLACE-`, and `ORG-`).
- Never reuse an ID for a different record.
- Never delete a source merely because its URL stops working. Preserve its
  bibliographic description and set `url_status: unavailable`.
- Keep source references as arrays, even when only one source supports a record.
- Keep unresolved identity links explicit. Do not merge person records until a
  person-level source justifies the merge.
- Record an evidence conflict on all relevant claims and link the competing claim
  IDs where possible.
- Use `null` or an explicit unknown field when the dossier does not supply a
  value. Do not fill gaps from general knowledge.

## Workflow for new evidence

For every new source:

1. Add or update its source record with a stable ID and evidence status.
2. Record exactly which claims it supports, contradicts, or suggests.
3. Add or update claim records without overstating the source.
4. Update timeline and entity records only through those sourced claims.
5. Update narrative content only after the structured evidence is current.
6. Preserve a visible conflict until evidence actually resolves it.
7. Record the change in the future research log when one exists.

## Current mandatory cautions

- The 1871 St. Johann Nepomuk register directly verifies a Vienna baptismal
  identity named Sylvester Hermann Gottlieb. It does not by itself establish a
  later hotel career.
- The Zürich hotelier `S. H. Gottlieb`, the full-name Baden-Baden hotelier
  `Sylvester Hermann Gottlieb`, and the verified Vienna baptismal identity form
  strongly compatible but still distinct evidence layers. Do not merge them
  until a direct person-level record links the careers and birth information.
- Do not state as established fact that Gottlieb became director of Baur en Ville
  in exactly 1910, left in 1918, directed Grand Hotel Victoria in 1924, owned the
  Hotel Messmer property, died in 1934, or died in Baden-Baden.
- Describe the directly attested 1931 Hotel Messmer role as `Pächter`, lessee,
  or operator. Do not infer the reason that the bankruptcy proceeding appeared
  in the `Aufhebungen` section.
- Do not decide that `I. Gottlieb` in the secondary Savoy chronology is a typo.
- Preserve the conflict between the direct 1922 listing of `S. H. Gottlieb` as
  director and the secondary chronology assigning Fritz Giger to 1918-1926.
- Preserve the conflict between the official account reporting Hotel Messmer
  closed since 1930 and the un-reacquired later telephone-directory findings.

## Images and publication

An old image is not automatically free to reproduce. Before public use, record
its source, creator or publisher if known, date if known, holding institution,
permanent URL, rights statement, permission status, caption, and source ID. An
image may remain a research lead even when it cannot be published.

Do not expose unnecessary private family information. Do not build or expand the
public presentation layer unless the current task explicitly requests it.
