# Digital Garden — Stage 5 Knowledge Graph

This directory is the **Stage 5 Digital Garden** — a cross-book network of atomic
physics and mathematics notes for use in RAG-assisted book writing.

## Structure

```
garden/
  notes/              ← All atomic notes (.md), organized by topic
    quantum_mechanics/
    condensed_matter/
    mathematical_physics/   (future)
  index/
    approved_notes.yaml     ← Master note list (human-editable, Agent 2 output)
    proposals/              ← Agent 1 raw proposal YAMLs
    master_index.md         ← Auto-generated human-readable index
    graph.json              ← Knowledge graph adjacency list
    tree.json               ← Topic-path hierarchy for tree navigation
  config/
    topics.yaml             ← Canonical topic taxonomy
    note_template.md        ← Template for new notes
  scripts/
    garden_query.py         ← Smart RAG retrieval (BM25 + graph expansion)
    stage5_proposer.py      ← Agent 1 orchestration
    stage5_refactor.py      ← Agent 2 orchestration
    stage5_creator.py       ← Agent 3 orchestration (sequential)
    stage5_crosscheck.py    ← Agent 4 notation + self-containedness
    stage5_indexer.py       ← Agent 5 index/graph builder
  mcp/
    garden_server.py        ← MCP server for AGY CLI integration (Phase 2)
```

## Querying the Garden

```bash
# From the project root
python3 garden/scripts/garden_query.py "von Neumann entropy" --max-tokens 6000

# With deeper graph expansion (2 hops)
python3 garden/scripts/garden_query.py "Bloch theorem" --hops 2

# Larger context budget for a broad topic
python3 garden/scripts/garden_query.py "scattering theory S-matrix" --max-tokens 12000
```

## Sources

| Book | Stage 3 notes | Garden notes |
|------|--------------|--------------|
| Baym, *Lectures on Quantum Mechanics* (1969) | `books/baym_quantum_mechanics_1969/03_verified_md/` | `garden/notes/quantum_mechanics/` |
| Fazekas, *Lecture Notes on Electron Correlation and Magnetism* (1999) | `books/fazekas_electron_correlation_1999/03_verified_md/` | `garden/notes/condensed_matter/` |

## Design Principles

- **One concept, one note.** A note encodes exactly one intellectual unit.
- **Global note IDs.** `qm_def_hermitian_operator` is a single node even if both Baym and Fazekas discuss it.
- **Modern notation.** All notes use `config/notation.json` — original-book conventions are not reproduced.
- **No file paths in citations.** Sources use book/chapter/section text, not file system paths.
- **Quality over speed.** Notes are created sequentially so each can read the garden for consistency.
- **YAML-first graph.** All connections (`depends_on`, `used_by`, `related`) live in YAML headers so the graph can be rebuilt by parsing headers alone.
