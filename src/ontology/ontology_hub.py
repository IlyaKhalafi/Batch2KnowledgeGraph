import json
from typing import List
from graphrag_sdk import Ontology
from graphrag_sdk.source import AbstractSource
from graphrag_sdk.models.openai import OpenAiGenerativeModel
from ..steps.concurrent_ontology_step import ConcurrentCreateOntologyStep

class OntologyHub:
    """
    Central hub for managing ontology operations including creation,
    extension, saving, and loading.
    """
    
    def __init__(
        self,
        ontology: Ontology = Ontology(),
        model: OpenAiGenerativeModel = OpenAiGenerativeModel(model_name='gpt-4o-mini'),
        sources: List[AbstractSource] = None
    ) -> None:
        """
        Initialize OntologyHub.

        Args:
            ontology (Ontology, optional): Base ontology. Defaults to empty Ontology.
            model (OpenAiGenerativeModel, optional): AI model for processing.
            sources (List[AbstractSource], optional): List of data sources.
        """
        self._ontology = ontology
        self._model = model
        self._sources = sources or []
        
    def extend_ontology(
        self,
        sources: List[AbstractSource],
        boundaries: str = None,
        workers: int = 16
    ) -> Ontology:
        """
        Extend existing ontology with new sources.

        Args:
            sources (List[AbstractSource]): Sources to process
            boundaries (str, optional): Boundaries for ontology creation
            workers (int, optional): Number of worker threads

        Returns:
            Ontology: Updated ontology
        """
        self._ontology = ConcurrentCreateOntologyStep(
            sources=sources,
            ontology=self._ontology,
            model=self._model,
            config={
                "max_workers": workers,
                "max_input_tokens": 500000,
                "max_output_tokens": 8192
            }
        ).run(boundaries=boundaries)
        self._sources.extend(sources)
        return self._ontology
    
    def save_json(self, path: str) -> None:
        """
        Save ontology to JSON file.

        Args:
            path (str): File path for saving
        """
        if not path.endswith('.json'):
            path += '.json'
        
        with open(path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(self._ontology.to_json(), indent=2))
        
    def load_json(self, path: str, sources: List[AbstractSource] = []) -> 'OntologyHub':
        """
        Load ontology from JSON file.

        Args:
            path (str): Path to JSON file

        Returns:
            OntologyHub: Self reference for method chaining
        """
        if not path.endswith('.json'):
            path += '.json'
        
        with open(path, "r", encoding="utf-8") as file:
            self._ontology = Ontology.from_json(json.loads(file.read()))
        self._sources.extend(sources)
        return self
            
    def get_ontology(self) -> Ontology:
        """
        Get the current ontology.

        Returns:
            Ontology: Current ontology object
        """
        return self._ontology