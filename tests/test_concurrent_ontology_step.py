import pytest
from multiprocessing import Queue
from src.steps.concurrent_ontology_step import ConcurrentCreateOntologyStep
from graphrag_sdk import Ontology
from graphrag_sdk.source import AbstractSource
from src.sources.unstructured_source import UnstructuredSource
from unittest.mock import MagicMock, patch, call

class TestConcurrentCreateOntologyStep:
    
    @pytest.fixture
    def sample_source(self, tmp_path):
        # Create a temporary text file
        file_path = tmp_path / "test.txt"
        file_path.write_text("Sample content for testing")
        return UnstructuredSource(str(file_path))
    
    @pytest.fixture
    def ontology_step(self):
        return ConcurrentCreateOntologyStep(
            sources=[],
            ontology=Ontology(),
            # model=OpenAiGenerativeModel(model_name='gpt-4o-mini'),
            model=MagicMock(),
            config={
                "max_workers": 4,
                "max_input_tokens": 1000,
                "max_output_tokens": 500
            }
        )
    
    @pytest.fixture
    def mock_ontology(self):
        """
        Mocks an ontology object.
        """
        ontology = MagicMock()
        ontology.entities = ["Entity1", "Entity2"]
        ontology.merge_with.return_value = ontology
        return ontology
    
    def test_initialization(self, ontology_step):
        assert isinstance(ontology_step.ontology, Ontology)
        assert isinstance(ontology_step.model, MagicMock)
    
    # @patch("src.steps.concurrent_ontology_step.ConcurrentCreateOntologyStep._create_chat", autospec=True)
    # @patch("src.steps.concurrent_ontology_step.ConcurrentCreateOntologyStep._process_source", autospec=True)
    # @patch("src.steps.concurrent_ontology_step.ConcurrentCreateOntologyStep._fix_ontology", autospec=True)
    # def test_run_success(self, mock_create_chat, mock_process_source, mock_fix_ontology, sample_source, mock_ontology):
    #     """
    #     Test the run method when everything executes successfully.
    #     """
    #     # Configure mocks
    #     mock_sources = [sample_source]
    #     mock_create_chat.return_value = MagicMock()
    #     mock_process_source.side_effect = lambda chat, doc, ontology, boundaries: ontology
    #     mock_fix_ontology.return_value = mock_ontology

    #     # Initialize ConcurrentCreateOntologyStep instance
    #     step = ConcurrentCreateOntologyStep(sources=mock_sources, ontology=mock_ontology, model=MagicMock())
    #     step_ontology = step.ontology

    #     # Call run method
    #     result = step.run(boundaries="some-boundary", workers=2)

    #     # Assert result and calls
    #     assert result == step_ontology
    #     mock_create_chat.assert_called()
    #     mock_fix_ontology.assert_called_once_with(mock_create_chat.return_value, step_ontology)
