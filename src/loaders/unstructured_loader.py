from typing import Iterator
from unstructured.partition.auto import partition
from unstructured.documents.elements import ElementType, Text
from unstructured.partition.utils.constants import PartitionStrategy
from unstructured.cleaners.core import (
    clean_non_ascii_chars,
    group_bullet_paragraph,
    group_broken_paragraphs,
    clean_extra_whitespace,
    clean_ordered_bullets
)
from graphrag_sdk.document import Document

class UnstructuredLoader:
    """
    A loader class for processing various document types using Unstructured-IO library.
    Handles text extraction and cleaning from documents.
    """
    
    # Text cleaning functions to be applied on extracted content
    cleaners = [
        clean_non_ascii_chars,
        group_bullet_paragraph,
        group_broken_paragraphs,
        clean_extra_whitespace,
        clean_ordered_bullets
    ]
    
    # Supported element types for text extraction
    types = [
        ElementType.NARRATIVE_TEXT,
        ElementType.TITLE,
        ElementType.ABSTRACT,
        ElementType.PARAGRAPH,
        ElementType.COMPOSITE_ELEMENT
    ]
    
    def __init__(self, path: str) -> None:
        """
        Initialize the UnstructuredLoader.

        Args:
            path (str): File path to the document to be processed
        """
        self.path = path
        self.processed = False
        
    def load(self, use_cache: bool = True) -> Iterator[Document]:
        """
        Load and process the document, yielding cleaned text content.
        
        Args:
            use_cache (str): Whether to use cached data or not

        Returns:
            Iterator[Document]: Iterator yielding Document objects containing processed text
        
        Raises:
            Exception: If document parsing fails
        """
        if not self.processed or not use_cache:
            try:
                # Extract elements from document
                elements = [
                    el for el in partition(
                        filename=self.path,
                        strategy=PartitionStrategy.FAST
                    )
                    if el.category in self.types and len(el.text) > 0
                ]
                
                # Clean each text element
                clean_elements = [self._clean_element(el) for el in elements if isinstance(el, Text)]
                                                    
                self.content = "\n".join([str(el) for el in clean_elements])
                self.processed = True

            except Exception as e:
                print(f"\nUnstructured partition error: {e}")
                return Document('')
            
        yield Document(self.content)
        
    def _clean_element(self, element: Text):
        for cleaner in UnstructuredLoader.cleaners:
            element.text = cleaner(element.text)
            if isinstance(element.text, list):
                element.text = ''.join(element.text)
        return element