import pytest
import os
from src.sources.unstructured_source import UnstructuredSource
from graphrag_sdk.document import Document
from unstructured.documents.elements import NarrativeText
from unstructured.partition.auto import partition
from unittest.mock import patch, MagicMock

class TestUnstructuredSource:
    
    @pytest.fixture
    def sample_source(self, tmp_path):
        # Create a temporary text file
        file_path = tmp_path / "test.txt"
        file_path.write_text("Sample content for testing")
        return UnstructuredSource(str(file_path))
    
    def test_initialization(self, sample_source):
        assert sample_source.path is not None
        assert os.path.exists(sample_source.path)
        
    def test_load_text_file(self, sample_source):
        documents = list(sample_source.load())
        assert len(documents) > 0
        assert all([isinstance(doc, Document) for doc in documents])
        
    @patch('src.loaders.unstructured_loader.partition')
    def test_load_pdf(self, mock_loader, tmp_path):
        mock_loader.return_value = [NarrativeText("PDF content")]
        
        pdf_path = tmp_path / "test.pdf"
        
        source = UnstructuredSource(str(pdf_path))
        documents = list(source.load())
        
        assert len(documents) == 1
        assert documents[0].content == "PDF content"