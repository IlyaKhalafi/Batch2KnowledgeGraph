import pytest
import json
from src.ontology.ontology_hub import OntologyHub
from graphrag_sdk import Ontology
from src.sources.unstructured_source import UnstructuredSource
from unittest.mock import MagicMock, patch, call

class TestOntologyHub:
    
    @pytest.fixture
    def ontology_hub(self):
        return OntologyHub(
            ontology=Ontology(),
            model=MagicMock()
        )
    
    @pytest.fixture
    def sample_ontology_json(self, tmp_path):
        ontology_data = {
            "entities": [
                {"name": "Person", "properties": ["name", "age"]},
                {"name": "Organization", "properties": ["name", "location"]}
            ],
            "relationships": [
                {"name": "WORKS_FOR", "source": "Person", "target": "Organization"}
            ]
        }
        
        file_path = tmp_path / "test_ontology.json"
        with open(file_path, 'w') as f:
            json.dump(ontology_data, f)
        return str(file_path)
    
    def test_initialization(self, ontology_hub):
        assert isinstance(ontology_hub._ontology, Ontology)
        assert isinstance(ontology_hub._model, MagicMock)
        assert ontology_hub._sources == []
        
    def test_save_and_load_json(self, ontology_hub, tmp_path):
        save_path = tmp_path / "ontology.json"
        
        ontology_hub.save_json(str(save_path))
        assert save_path.exists()
        
        loaded_hub = OntologyHub().load_json(str(save_path))
        assert isinstance(loaded_hub.get_ontology(), Ontology)
        
    @patch('src.ontology.ontology_hub.ConcurrentCreateOntologyStep.run') 
    def test_extend_ontology(self, mock_run, sample_source, ontology_hub, tmp_path):
        mock_run.side_effect = lambda boundaries: ontology_hub._ontology
        source = sample_source
        
        updated_ontology = ontology_hub.extend_ontology([source], workers=1)
        assert updated_ontology == ontology_hub._ontology
        assert isinstance(updated_ontology, Ontology)
        assert source in ontology_hub._sources