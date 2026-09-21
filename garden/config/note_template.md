---
# DIGITAL GARDEN — CANONICAL NOTE TEMPLATE
# Copy this file and fill in all fields.
# Delete all comments before writing content.

note_id: NAMESPACE_TYPE_SHORTNAME       # e.g. qm_def_hermitian_operator
type: definition                         # definition | lemma | theorem | postulate
                                         # concept | method | example | connection
title: "Full Human-Readable Title"
status: draft                            # draft | verified | stable
rigor: formal                            # formal | physical | heuristic

tags: []                                 # free-form keywords for BM25 search

# Hierarchical location — MUST match a leaf or node in garden/config/topics.yaml
# Format: top > sub > leaf   (use > as separator)
topic_path: quantum_mechanics > operators > hermitian_operators

# Soft token target (helps RAG budgeting). Count after writing.
estimated_tokens: 0

# Knowledge graph edges (use note_id strings, NOT file paths)
depends_on: []        # notes this note USES (must exist before this note is verified)
used_by: []           # notes that USE this note (fill in as those notes are created)
related: []           # non-dependency conceptual neighbours

# Bibliographic references — human-readable, no file paths
# Each source pinpoints exactly where the content comes from.
sources:
  - book: "Author, Full Title (Year)"
    chapter: 0
    section: "Section Title"
    # Optional: specific claim attribution
    notes: ""

convention_note: null   # Describe any notation disagreement across sources, or null.

# For `example` type only — list of section headings within this file
# (enables section-level retrieval by the garden_query script)
sections: []

last_updated: "YYYY-MM-DD"
---

<!--
NOTE TYPE GUIDANCE:
  definition  → Introduce a concept formally. Include all hypotheses and the full quantified statement.
  lemma       → State a small technical result. Include a proof only if it is short and illuminating.
  theorem     → State a major named result. No proof required; reference the Stage 3 notes for derivations.
  postulate   → Axiomatic assertion. State clearly what is assumed.
  concept     → Physical/intuitive insight that resists full formalization. Be honest about rigor.
  method      → Systematic procedure. Include steps or a recipe.
  example     → Canonical worked case. Use ## sections for different cases (1D, 2D, relativistic, …).
  connection  → Explicit bridge between two notes or two books' treatments of the same idea.

PROOF POLICY:
  - No proof is required in the garden.
  - Include a proof only when it is concise AND genuinely illuminating.
  - If a "physical argument" replaces a rigorous proof, set rigor: physical.
  - Never truncate a proof to the point of logical gaps — if it cannot be honest
    in a short form, omit it and point to the Stage 3 note.

NOTATION:
  - ALWAYS use the canonical macros from config/notation.json.
  - Kets: \ket{\psi}   Bras: \bra{\phi}   Brackets: \braket{\phi}{\psi}
  - Differentials: \dd x  (upright d), e.g. \int f(x) \, \dd x
  - Operators carry a hat: \hat{H}, \hat{p}, \hat{A}
  - Eigenvalues / c-numbers do NOT carry a hat: p_0 = \sqrt{2mE}
-->

## Statement

<!-- Write the precise statement here. For definitions, include domain and quantifiers.
     For theorems and lemmas, list hypotheses explicitly. -->

## Remarks

<!-- Optional: 2–5 bullet points of physical intuition, special cases, or caveats. -->

## Physical Argument / Proof

<!-- Include ONLY if it satisfies the proof policy above.
     Label with rigor: physical in YAML if not fully rigorous. -->

## See Also

<!-- Wikilinks to directly related notes.
     These should already be reflected in the YAML edges above. -->
