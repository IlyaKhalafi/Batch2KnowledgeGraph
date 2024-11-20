from src.sources.unstructured_source import UnstructuredSource
import pytest

@pytest.fixture
def sample_source(tmp_path):
    # Create a temporary text file
    file_path = tmp_path / "test.txt"
    file_path.write_text("Sample content for testing")
    return UnstructuredSource(str(file_path))