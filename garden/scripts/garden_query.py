#!/usr/bin/env python3
"""
garden_query.py — Smart RAG retrieval for the Digital Garden.

Usage:
    python3 garden/scripts/garden_query.py "von Neumann entropy" [--max-tokens 6000] [--hops 1]

Returns a bundle of relevant garden notes (YAML header + body) for use as
LLM context. Three-stage retrieval:
  A. BM25 keyword search over parsed YAML headers (fast, <10ms)
  B. Knowledge graph expansion via depends_on edges (1-hop by default)
  C. Section-level filtering for `example` notes

Output: plain text bundle ready to paste into an LLM context or AGY prompt.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

GARDEN_ROOT = Path(__file__).parent.parent
NOTES_ROOT  = GARDEN_ROOT / "notes"
INDEX_DIR   = GARDEN_ROOT / "index"
GRAPH_FILE  = INDEX_DIR / "graph.json"

# ---------------------------------------------------------------------------
# 1. Parse all note YAML headers into a lightweight index
# ---------------------------------------------------------------------------

def _extract_yaml(text: str) -> dict:
    """Extract key fields from a YAML front-matter block."""
    result = {}
    in_block = False
    yaml_lines = []
    for line in text.splitlines():
        if line.strip() == "---":
            if not in_block:
                in_block = True
                continue
            else:
                break
        if in_block:
            yaml_lines.append(line)

    for line in yaml_lines:
        m = re.match(r'^(\w[\w_]*):\s*(.*)$', line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            val = val.strip('"\'')
            result[key] = val

    # Parse list fields
    for list_key in ('tags', 'depends_on', 'used_by', 'related', 'sections'):
        raw = result.get(list_key, '')
        if raw.startswith('[') and raw.endswith(']'):
            inner = raw[1:-1]
            result[list_key] = [x.strip().strip('"\'') for x in inner.split(',') if x.strip()]
        else:
            result[list_key] = []

    return result


def build_header_index() -> list[dict]:
    """Walk all .md files in garden/notes/ and return a list of header dicts."""
    index = []
    for path in NOTES_ROOT.rglob("*.md"):
        text = path.read_text(encoding='utf-8')
        meta = _extract_yaml(text)
        meta['_path'] = str(path)
        meta['_text'] = text
        index.append(meta)
    return index


# ---------------------------------------------------------------------------
# 2. BM25 scorer
# ---------------------------------------------------------------------------

def _tokenize(s: str) -> list[str]:
    return re.findall(r'\w+', s.lower())


def bm25_scores(query: str, docs: list[dict], k1=1.5, b=0.75) -> list[float]:
    """Score each doc against the query using BM25 over searchable fields."""
    q_tokens = set(_tokenize(query))

    # Build corpus from searchable YAML fields
    corpora = []
    for doc in docs:
        field_text = ' '.join([
            doc.get('title', ''),
            doc.get('topic_path', ''),
            ' '.join(doc.get('tags', [])),
            doc.get('note_id', ''),
            doc.get('type', ''),
        ])
        corpora.append(_tokenize(field_text))

    avg_dl = sum(len(c) for c in corpora) / max(len(corpora), 1)

    # Document frequency
    df: dict[str, int] = {}
    for corpus in corpora:
        for tok in set(corpus):
            df[tok] = df.get(tok, 0) + 1

    N = len(docs)
    scores = []
    for corpus in corpora:
        tf: dict[str, int] = {}
        for tok in corpus:
            tf[tok] = tf.get(tok, 0) + 1
        dl = len(corpus)
        score = 0.0
        for qt in q_tokens:
            if qt not in df:
                continue
            idf = math.log((N - df[qt] + 0.5) / (df[qt] + 0.5) + 1)
            f = tf.get(qt, 0)
            score += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * dl / avg_dl))
        scores.append(score)
    return scores


# ---------------------------------------------------------------------------
# 3. Knowledge graph expansion
# ---------------------------------------------------------------------------

def load_graph() -> dict:
    if GRAPH_FILE.exists():
        return json.loads(GRAPH_FILE.read_text())
    return {}


def expand_via_graph(note_ids: list[str], graph: dict, hops: int = 1) -> set[str]:
    """Add depends_on neighbours up to `hops` hops."""
    result = set(note_ids)
    frontier = set(note_ids)
    for _ in range(hops):
        next_frontier = set()
        for nid in frontier:
            for dep in graph.get(nid, {}).get('depends_on', []):
                if dep not in result:
                    next_frontier.add(dep)
        result |= next_frontier
        frontier = next_frontier
    return result


# ---------------------------------------------------------------------------
# 4. Section-level retrieval for example notes
# ---------------------------------------------------------------------------

def extract_section(text: str, query_tokens: set[str]) -> str:
    """For example notes, return only the most relevant section."""
    sections = re.split(r'^## ', text, flags=re.MULTILINE)
    if len(sections) <= 2:
        return text  # No sections to filter
    # Score each section by query overlap
    best_score, best_section = -1, sections[0]
    for sec in sections[1:]:
        score = sum(1 for t in query_tokens if t in sec.lower())
        if score > best_score:
            best_score = score
            best_section = '## ' + sec
    return sections[0] + best_section  # YAML header + best section


# ---------------------------------------------------------------------------
# 5. Main
# ---------------------------------------------------------------------------

def query(q: str, max_tokens: int = 6000, top_n: int = 10, hops: int = 1) -> str:
    index = build_header_index()
    if not index:
        return "Garden is empty. Run stage5_indexer.py first."

    scores = bm25_scores(q, index)
    ranked = sorted(zip(scores, index), key=lambda x: x[0], reverse=True)

    # Stage A: top N by BM25
    top_ids = [doc['note_id'] for score, doc in ranked[:top_n] if score > 0]

    # Stage B: graph expansion
    graph = load_graph()
    expanded_ids = expand_via_graph(top_ids, graph, hops=hops)

    # Rebuild map for fast lookup
    id_to_doc = {doc['note_id']: doc for doc in index if 'note_id' in doc}

    # Stage C: assemble bundle
    q_tokens = set(_tokenize(q))
    bundle_parts = []
    total_tokens = 0

    # Prioritise directly matched notes first
    ordered_ids = top_ids + [nid for nid in expanded_ids if nid not in top_ids]

    for nid in ordered_ids:
        doc = id_to_doc.get(nid)
        if doc is None:
            continue
        est = int(doc.get('estimated_tokens', 400))
        if total_tokens + est > max_tokens:
            break

        text = doc['_text']
        if doc.get('type') == 'example' and doc.get('sections'):
            text = extract_section(text, q_tokens)

        bundle_parts.append(f"<!-- NOTE: {nid} -->\n{text}")
        total_tokens += est

    if not bundle_parts:
        return f"No garden notes found for query: {q!r}"

    header = (
        f"<!-- Garden context for query: {q!r} -->\n"
        f"<!-- Notes included: {len(bundle_parts)} | Est. tokens: {total_tokens} -->\n\n"
    )
    return header + "\n\n---\n\n".join(bundle_parts)


def main():
    parser = argparse.ArgumentParser(description="Query the Digital Garden for RAG context.")
    parser.add_argument("query", help="Natural language query")
    parser.add_argument("--max-tokens", type=int, default=6000)
    parser.add_argument("--top-n", type=int, default=10)
    parser.add_argument("--hops", type=int, default=1)
    args = parser.parse_args()

    result = query(args.query, max_tokens=args.max_tokens, top_n=args.top_n, hops=args.hops)
    print(result)


if __name__ == "__main__":
    main()
