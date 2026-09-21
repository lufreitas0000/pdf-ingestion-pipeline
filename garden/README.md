# Digital Garden — Stage 5 Knowledge Graph

This directory is the **Stage 5 Digital Garden** — a cross-book network of atomic
physics and mathematics notes for use in RAG-assisted book writing.
It is the **fast-memory tier** of a three-tier knowledge system:

```
TIER 1 — garden/               ← this directory (fast, atomic, cross-book)
TIER 2 — books/*/03_verified_md/  ← chapter-level notes, book-specific
TIER 3 — books/*/04_final_tex/    ← typeset book + solutions, bibliography
```

---

## Directory Structure

```
garden/
  notes/              ← All atomic notes (.md), organized by topic
    quantum_mechanics/
      operators/      ← definitions, lemmas, theorems about QM operators
      states/         ← Hilbert spaces, density matrices, Dirac notation
      dynamics/       ← Schrödinger/Heisenberg pictures, perturbation theory
      scattering/     ← S-matrix, Born approximation, optical theorem
      examples/       ← Canonical examples (free particle, harmonic osc., …)
    condensed_matter/
      periodic_potentials/
      magnetism/
      correlations/
      examples/
    mathematical_physics/ (future)
  index/
    approved_notes.yaml   ← Master note creation list (human-editable)
    proposals/            ← Agent 1 raw output YAMLs (one per source file)
    master_index.md       ← Auto-generated table of all notes
    graph.json            ← Adjacency list: note_id → {depends_on, used_by}
    tree.json             ← Topic-path hierarchy for tree navigation
  config/
    topics.yaml           ← Canonical topic taxonomy (see §Topic Taxonomy below)
    note_template.md      ← Canonical template for new notes
  scripts/
    garden_query.py       ← Smart RAG retrieval (BM25 + graph expansion)
    stage5_proposer.py    ← Agent 1 orchestration helper
    stage5_refactor.py    ← Agent 2 orchestration helper
    stage5_creator.py     ← Agent 3 orchestration helper (sequential)
    stage5_crosscheck.py  ← Agent 4 notation + self-containedness check
    stage5_indexer.py     ← Agent 5: builds master_index, graph.json, tree.json
  mcp/
    garden_server.py      ← MCP server for AGY CLI integration (Phase 2)
```

---

## Five-Agent Pipeline (Stage 5)

Notes are not written by hand — they are produced by a structured agent pipeline.

### Agent 1 — Proposer (`stage5_proposer.py`)
**Input:** One Stage 3 markdown file (one chapter section).  
**Task:** Reads the file and identifies every distinct intellectual unit
(definition, theorem, lemma, concept, method, example). For each one it produces
a short *proposal card*: `title`, `type`, one-sentence description, suggested
`note_id`, and source citation (book/chapter/section).  
**Output:** A YAML file in `garden/index/proposals/` — e.g.
`baym_ch04_01_hermitian_operators.yaml`.  
**Model:** Can run on a fast/light model (flash or local Qwen2.5-Coder 3B) —
it is a reading + classification task, not a reasoning task.  
**Parallelisable:** Yes — one agent per source file.

### Agent 2 — Refactor (`stage5_refactor.py`)
**Input:** All proposal YAMLs from Agent 1.  
**Task:** Global pass over the entire proposal set. Merges duplicate concepts
(same idea in two books → one note with two `sources:`), splits over-broad
proposals, flags derivation steps that are not garden-worthy, and produces
a topologically sorted `garden/index/approved_notes.yaml`.  
**Output:** `approved_notes.yaml` — the authoritative note creation list.  
**Human checkpoint:** You review and edit this file before Agent 3 begins.  
**Model:** Needs a capable model (pro or flash) — requires cross-file reasoning.

### Agent 3 — Creator (`stage5_creator.py`, **sequential**)
**Input:** One entry from `approved_notes.yaml` + the current state of the garden.  
**Task:** Reads the referenced Stage 3 section(s), scans existing garden notes for
duplication, then writes the atomic note following `config/note_template.md`.
May send small edit requests to earlier notes to update `used_by` fields or add
cross-links. Creation order follows the topological sort in `approved_notes.yaml`
(definitions first, theorems after).  
**Output:** One `.md` file in `garden/notes/`.  
**Why sequential:** Each new note reads the garden so that language and
cross-links converge organically. It can detect duplication and request
corrections to earlier notes. Quality over speed.

### Agent 4 — Crosschecker (`stage5_crosscheck.py`)
**Input:** A freshly created garden note.  
**Three passes:**
1. **Notation** — enforces `config/notation.json` (same as the notation_upgrader
   skill used in Stages 3 & 4).
2. **Self-containedness** — every symbol in the note is either defined in the
   note itself or linked via `depends_on` to another garden note.
3. **Precision** — is the statement as sharp and minimal as it can be without
   sacrificing correctness?

Sets `status: verified` in YAML on pass; returns specific corrections on fail.  
**Model:** Flash (light) — mostly pattern matching and consistency checking.

### Agent 5 — Indexer (`stage5_indexer.py`)
**Input:** All verified garden notes.  
**Task:** Parses every YAML header and regenerates:
- `master_index.md` — human-readable table sorted by topic
- `graph.json` — adjacency list for `garden_query.py`
- `tree.json` — topic-path hierarchy for tree navigation

Run after every batch of ~20 new notes.  
**Model:** No LLM needed — pure Python/YAML parsing (deterministic script).

---

## Topic Taxonomy & Its Expansion

The file `garden/config/topics.yaml` defines the canonical hierarchy that every
note's `topic_path` must reference. This ensures consistent tree navigation.

### How `topics.yaml` grows with new books

The strategy is **semi-automated with human approval**:

1. **Detection (deterministic script):** When Agent 1 proposes notes for a new
   book, it may suggest `topic_path` values that do not yet exist in `topics.yaml`.
   The script `stage5_refactor.py` automatically diffs proposed paths against the
   current taxonomy and produces a `topics_patch.yaml` listing the gaps.

2. **Proposal (Agent 2):** Agent 2 (Refactor) reads `topics_patch.yaml` and
   proposes *how* to integrate new topics — whether to add a new leaf, a new
   sub-tree, or merge with an existing topic under a better name.

3. **Human approval:** You review the proposed taxonomy extension (typically
   just a few new lines) before it is committed. This keeps the hierarchy
   coherent and avoids proliferation of near-duplicate topics.

**Rule of thumb:** Do not create a new top-level topic for fewer than ~5 notes.
A new sub-topic needs at least 2 notes. Lone concepts go under `general` within
an existing topic.

---

## Querying the Garden

`garden_query.py` implements three-stage retrieval:

1. **BM25 header search** — keyword match over `title`, `tags`, `topic_path`,
   `note_id` fields (parses YAML headers only, no body reads, < 10 ms).
2. **Graph expansion** — adds `depends_on` neighbours (1 hop by default) to
   ensure the context bundle is self-consistent (theorems land with their
   definitions).
3. **Section filtering** — for `example` notes, extracts only the most relevant
   section (by heading match) rather than the full file.

```bash
# From the project root
python3 garden/scripts/garden_query.py "von Neumann entropy" --max-tokens 6000

# With deeper graph expansion (2 hops — pulls in prerequisite definitions)
python3 garden/scripts/garden_query.py "Bloch theorem" --hops 2

# Larger context budget for a broad topic
python3 garden/scripts/garden_query.py "scattering theory S-matrix" --max-tokens 12000
```

### Token budget rationale

| Scenario | Typical tokens returned | Why |
|----------|------------------------|-----|
| Single precise concept query | 500 – 2 000 | 1–5 notes, mostly short definitions/theorems |
| Topic query (e.g. "scattering") | 3 000 – 6 000 | 8–15 notes incl. graph expansion |
| Broad chapter-level query | 6 000 – 12 000 | 20–30 notes; borderline for 32K ctx window |
| Full garden dump | ~ 480 000 | Never do this; noisy and wasteful |

The default `--max-tokens 6000` is a good starting point for VS Code AGY sessions:
it leaves ample room for the LLM's own reasoning and the output. Increase to
12 000 for complex multi-concept questions. The graph expansion (`--hops 1`)
adds typically 2–5 extra prerequisite notes (~500–1 500 tokens).

---

## Sources

| Book | Stage 3 notes | Garden topic |
|------|--------------|--------------|
| Baym, *Lectures on Quantum Mechanics* (1969) | `books/baym_quantum_mechanics_1969/03_verified_md/` | `quantum_mechanics/` |
| Fazekas, *Lecture Notes on Electron Correlation and Magnetism* (1999) | `books/fazekas_electron_correlation_1999/03_verified_md/` | `condensed_matter/` |

---

## Design Principles

- **One concept, one note.** A note encodes exactly one intellectual unit.
- **Global note IDs.** `qm_def_hermitian_operator` is a single node even if multiple
  books discuss it — the `sources:` list records all of them.
- **Modern notation only.** All notes use `config/notation.json`.
  Original-book conventions are not reproduced in the garden.
- **No file paths in citations.** Sources cite book / chapter / section by name.
  File paths change; chapter titles do not.
- **Quality over speed.** Notes are created sequentially (Agent 3) so each can
  read the current garden, prevent duplication, and evolve cross-links organically.
- **YAML-first graph.** All connections (`depends_on`, `used_by`, `related`) are
  explicit in YAML headers so the entire knowledge graph can be rebuilt by
  parsing headers alone — no body reads required.
- **Honest rigour labelling.** Every note carries `rigor: formal | physical | heuristic`
  so a reader immediately knows the epistemic status of the statement.
