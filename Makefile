.PHONY: all clean run

# Load environment variables silently
include .env
export

# Default target
run:
	./scripts/run_pipeline.sh data/01_raw/gordon_baym_qm.pdf

# Skip heavy OCR extraction and just run the assembly
run-fast:
	./scripts/run_pipeline.sh data/01_raw/gordon_baym_qm.pdf --skip-ocr

# Maintenance cleanup
clean:
	./scripts/clean.sh
