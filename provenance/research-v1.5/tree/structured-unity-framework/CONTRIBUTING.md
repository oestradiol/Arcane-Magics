# Contributor Guide

## 1. Who this guide is for

Anyone proposing edits to Structured Unity Framework public materials: maintainers, future-you, or collaborators.

## 2. Before editing anything

Use `docs/INDEX.md` to locate files. Read `docs/frontdoor/claims-and-boundaries.md`, `framework/framework-interface.md`, `framework/research-program.md`, and `meta/publication-scope.md` before making scope-sensitive edits.

Use the status surfaces by role:

- `docs/project-status.md` = current package state
- `docs/current-execution-order.md` = shortest live sequencing surface for the active pass
- `ROADMAP.md` = future-facing direction
- `docs/pending-inventory.md` = open and deferred items

## 3. What is locked vs what is revisable

**High-friction to change without discussion:** public name, four-layer theory roles, weak naturalization, claim-type discipline, the applications split between demonstrated routes and research-map nodes, and the bounded status of the New Zealand route.

**Revisable with care:** wording clarity, diagrams, standard and extended reading-list entries, atlas nodes, roadmap priorities, typos, and contributor guidance.

## 4. Architecture preservation rules

- do not collapse the theory stack into one file
- do not let `README.md` absorb the whole project
- keep demonstrated routes and research-map nodes distinct
- keep applications honest: breadth is not proof
- keep public status files in their designated roles

## 5. Where different kinds of edits belong

| Change type | Where |
|-------------|--------|
| Layer content | `framework/` |
| Methods posture | `framework/research-program.md` |
| Citation routing | `framework/literature-guide.md` + `references/` |
| Demonstrated route work | `applications/demonstrated-routes/` |
| Atlas-node work | `applications/research-map/` |
| Policies | `meta/` |
| Entry / navigation | `docs/`, `README.md` |

## 6. Rules for applications work

State boundaries, windows, units, and limits explicitly. Do not silently upgrade an atlas node into a demonstrated route or a demonstrated route into universal validation.

## 7. Rules for references and citations

Use the literature guide. Add references with role discipline, not bulk accumulation.

## 8. Changelog expectations

- patch-scale work: wording, links, light diagram fixes
- minor-scale work inside `0.x`: meaningful new public structure or route additions
- document scope or claim changes clearly in `CHANGELOG.md`

## 9. Stale reference cleanup

Do not introduce filenames, handoff artifacts, or deprecated control names that are not part of this public export.
