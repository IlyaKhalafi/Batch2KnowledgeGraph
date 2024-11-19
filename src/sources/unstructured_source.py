from graphrag_sdk.source import AbstractSource
from ..loaders.unstructured_loader import UnstructuredLoader

class UnstructuredSource(AbstractSource):
    """
    Source class for handling unstructured documents.
    Extends AbstractSource from GraphRAG-SDK.
    """
        
    def __init__(self, path: str):
        """
        Initialize UnstructuredSource.

        Args:
            path (str): Path to the document file
        """
        super().__init__(path)
        self.loader = UnstructuredLoader(self.path)

    def load(self):
        """
        Load document using UnstructuredLoader.

        Returns:
            Iterator yielding Document objects
        """
        return self.loader.load()