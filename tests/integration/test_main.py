import json
import pytest
from pathlib import Path
from click.testing import CliRunner
from src.main import cli
from src.core.schemas import ExtractionResult, Page, Block

def test_run_pipeline_skip_ocr(mocker, tmp_path):
    """Tests the state-machine execution bypassing the heavy OCR layer."""
    runner = CliRunner()
    
    # Mock paths by patching the project_root in main.py
    mock_root = tmp_path / "project_root"
    for d in ["02_segmented", "03_stitched", "04_verified", "06_final_md", "07_final_tex"]:
        (mock_root / "data" / d).mkdir(parents=True, exist_ok=True)
        
    mocker.patch("src.main.Path.parent", return_value=mock_root)
    mocker.patch("src.main.dvc_track")  # Bypass actual DVC calls in tests

    # Create dummy PDF path
    pdf_path = mock_root / "test_book.pdf"
    pdf_path.touch()

    # Pre-seed the segmented JSON to simulate skip_ocr
    state_segmented = mock_root / "data" / "02_segmented" / "test_book.json"
    mock_data = ExtractionResult(
        pages=[Page(page_number=1, blocks=[Block(id="1", block_type="Text", content="1.2 Probability Density\n\nThe wave function")])]
    )
    with open(state_segmented, "w", encoding="utf-8") as f:
        json.dump(mock_data.model_dump(), f)

    # Execute CLI
    result = runner.invoke(cli, ["run-pipeline", str(pdf_path), "--skip-ocr"])
    
    assert result.exit_code == 0
    assert "Stage 1: Loading existing extraction" in result.output
    assert "Stage 4: Semantic Chunking and Assembly" in result.output
    
    # Verify outputs
    md_file = mock_root / "data" / "06_final_md" / "01_02_Probability_Density.md"
    tex_file = mock_root / "data" / "07_final_tex" / "01_02_Probability_Density.tex"
    
    assert md_file.exists()
    assert tex_file.exists()
