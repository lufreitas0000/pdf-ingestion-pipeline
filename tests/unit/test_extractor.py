import json
import pytest
from pathlib import Path
from src.tools.extractor import MarkerExtractor
from src.core.schemas import ExtractionResult

def test_marker_extractor_success(mocker, tmp_path):
    # Setup mock file paths
    pdf_path = tmp_path / "test_book.pdf"
    pdf_path.touch()
    output_dir = tmp_path / "output"
    
    # Setup mock marker-pdf output structure
    expected_sub_dir = output_dir / "test_book"
    expected_sub_dir.mkdir(parents=True)
    mock_json_file = expected_sub_dir / "test_book.json"
    
    mock_payload = {
        "metadata": {"languages": ["eng"]},
        "pages": [
            {
                "page_number": 1,
                "blocks": [{"id": "1", "block_type": "Text", "content": "Quantum Mechanics"}]
            }
        ]
    }
    mock_json_file.write_text(json.dumps(mock_payload))

    # Mock subprocess.run to simulate successful CLI execution without invoking PyTorch
    mock_run = mocker.patch("subprocess.run")
    mock_run.return_value.returncode = 0
    mock_run.return_value.stderr = ""

    # Execute
    extractor = MarkerExtractor()
    result = extractor.extract(pdf_path, output_dir)

    # Assertions
    assert isinstance(result, ExtractionResult)
    assert len(result.pages) == 1
    assert result.pages[0].blocks[0].content == "Quantum Mechanics"
    mock_run.assert_called_once()
