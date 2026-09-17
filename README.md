
# PDF Ingestion Pipeline & Agentic Verification Framework

## Objective
A deterministic, memory-safe state-machine designed to extract legacy scientific documents (e.g., Physics textbooks) into atomic Markdown notes for Obsidian and standardized LaTeX fragments. The pipeline decouples the heavy Vision-Language Model (VLM) extraction from the semantic verification, allowing specialized AI subagents to iteratively verify physical consistency and LaTeX syntax without risking system hallucinations.

## Architectural Constraints
- **SOLID Principles:** Strict enforcement of Dependency Inversion. Core logic (`src/core/`) is entirely decoupled from the extraction tools (`src/tools/`) and inference servers (`infra/`).
- **Deterministic State-Machine:** Execution is segmented into immutable stages tracked by Data Version Control (DVC).
- **Agentic Isolation:** LLM agents do not write code or execute bash commands directly unless bounded by their specific system prompts in `env/prompts/`.
- **Memory Safety:** To prevent WSL2 kernel panics (OOM), PDF parsing is chunked, and the `vllm` inference server is isolated with explicit VRAM bounds and pinned memory (UVA) configurations.

## Directory Schema & State Flow
- `data/01_raw/`: Input binary PDFs.
- `data/02_segmented/`: Raw JSON outputs from chunked OCR extraction (`marker-pdf`).
- `data/03_stitched/`: Deterministic regex-based cross-page merging. **[Agent Interception Point]**
- `data/04_verified/`: Verified JSON state after multi-agent consensus.
- `data/05_assets/`: Physical image crops isolated from text.
- `data/06_final_md/`: Atomic Markdown chunks structured with YAML frontmatter.
- `data/07_final_tex/`: Fragmented, compilable `.tex` files.
- `infra/vllm_env/`: Isolated virtual environment containing the native vLLM HTTP server.

## Agentic Hierarchy (AGY Framework)
1. **Orchestrator (Gemini 1.5 Pro):** Manages state transitions at Stage 3. Routes mathematical errors to `LaTeX_Fixer`, conceptual discrepancies to `Physics_Checker`, and diagram analysis to the `Vision` agent.
2. **LaTeX Fixer (Gemini 1.5 Flash):** Loops with `tectonic` compiler to resolve syntax violations.
3. **Physics Checker (Gemini 1.5 Flash):** Cross-references OCR mathematical symbols against surrounding textual physics context to detect hallucinated variables.
4. **Vision Agent (Gemini 1.5 Pro):** Generates dense, mathematically rigorous alt-text for physical diagrams routed to `data/05_assets/`.

## Execution Protocol
```bash
# Start the local vLLM server and execute the full deterministic extraction (Stages 1, 1.5, 2)
make run

# Once data/03_stitched/ is populated, initialize the AGY Orchestrator
agy start --workspace ./ --system-prompt env/prompts/orchestrator.txt

# After agent verification is complete, execute Semantic Assembly (Stage 4)
make run-fast
```
