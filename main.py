import os
from dotenv import load_dotenv
from graphrag_sdk import KnowledgeGraph
from graphrag_sdk.models.openai import OpenAiGenerativeModel
from graphrag_sdk.model_config import KnowledgeGraphModelConfig
from src.sources.unstructured_source import UnstructuredSource
from src.ontology.ontology_hub import OntologyHub
import config

def main():
    """
    Main execution function for the knowledge graph generation process.
    """
    # Configure source directory and paths
    source_dir = './tests/data'
    source_paths = [os.path.join(source_dir, path) 
                   for path in os.listdir(source_dir)]
    sources = [UnstructuredSource(path=path) for path in source_paths]
    
    # Initialize model and ontology hub
    model = OpenAiGenerativeModel(model_name='gpt-4o-mini')
    ontology_file = "ontology-output.json"
    
    # Create and extend ontology
    ontology_hub = OntologyHub(model=model)
    ontology_hub.extend_ontology(sources)
    
    # Save ontology to disk
    ontology_hub.save_json(ontology_file)
    
    # Create knowledge graph
    kg = KnowledgeGraph(
        name="knowledge_graph",
        model_config=KnowledgeGraphModelConfig.with_model(model),
        ontology=ontology_hub.get_ontology(),
    )
    
    # Process sources
    kg.process_sources(ontology_hub._sources)

if __name__ == '__main__':
    main()