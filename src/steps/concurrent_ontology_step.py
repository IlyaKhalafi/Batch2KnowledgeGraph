from multiprocessing import Process, Queue
from concurrent.futures import ThreadPoolExecutor
from graphrag_sdk.steps.create_ontology_step import CreateOntologyStep
from graphrag_sdk.ontology import Ontology
from ..sources.unstructured_source import UnstructuredSource

class ConcurrentCreateOntologyStep(CreateOntologyStep):
    """
    Extends CreateOntologyStep to provide concurrent processing capabilities
    for ontology creation from multiple sources.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the concurrent ontology creation step.

        Args:
            *args: Variable length argument list for parent class
            **kwargs: Arbitrary keyword arguments for parent class
        """
        super().__init__(*args, **kwargs)
    
    def run(self, boundaries: str = None, workers: int = 15):
        """
        Run the concurrent ontology creation process.

        Args:
            boundaries (str, optional): Boundaries for ontology creation. Defaults to None.
            workers (int, optional): Number of worker threads. Defaults to 15.

        Returns:
            Ontology: The created/updated ontology

        Raises:
            Exception: If the resulting ontology is empty
        """
        documents_queue = Queue()
        ontology_queue = Queue()
        signal_queue = Queue()
        thread_per_process = workers

        def loading_process(sources, documents_queue, signal_queue):
            """
            Process for loading documents from sources concurrently.
            
            Args:
                sources: List of source objects
                documents_queue: Queue for storing loaded documents
                signal_queue: Queue for process communication signals
            """
            def load_source(source):
                for doc in source.load():
                    documents_queue.put(doc)
                    signal_queue.put(1)
                print(f"\nLoaded source: {source.path}")

            with ThreadPoolExecutor(max_workers=thread_per_process) as pool:
                futures = [pool.submit(load_source, source) for source in sources]
                for future in futures:
                    future.result()

            signal_queue.put(0)
            print('\nAll sources are loaded. Stopping the loading process...')

        def ontology_process(documents_queue, signal_queue, ontology_queue, ontology):
            """
            Process for creating ontology parts from loaded documents.
            
            Args:
                documents_queue: Queue containing loaded documents
                signal_queue: Queue for process communication signals
                ontology_queue: Queue for storing created ontology parts
                ontology: Base ontology object
            """
            active_tasks = 0
            loading_completion_signal = False

            def create_ontology(doc):
                nonlocal active_tasks
                try:
                    chat = self._create_chat()
                    # New ontology is passed because self._process_source also uses merge_with
                    # If we pass a non-empty ontology, this will significantly increase the number of prompts needed!
                    new_ontology = self._process_source(chat, doc, Ontology(), boundaries) 
                    ontology_queue.put(new_ontology)
                finally:
                    signal_queue.put(-1)

            with ThreadPoolExecutor(max_workers=thread_per_process) as pool:
                while not (loading_completion_signal and active_tasks == 0):
                    try:
                        doc = documents_queue.get(timeout=1)
                        pool.submit(create_ontology, doc)
                    except Exception:
                        pass

                    while not signal_queue.empty():
                        signal = signal_queue.get()
                        if signal == 1:
                            active_tasks += 1
                        elif signal == -1:
                            active_tasks -= 1
                        elif signal == 0:
                            loading_completion_signal = True

            ontology_queue.put(None)
            print('\nOntology generation finished. Stopping the ontology process')

        def merge_process(from_b_queue):
            """
            Process for merging created ontology parts.
            
            Args:
                from_b_queue: Queue containing ontology parts to be merged
            """
            stopped_threads = 0
            while True:
                ontology_part = from_b_queue.get()
                if ontology_part is None:
                    stopped_threads += 1
                else:
                    self.ontology = self.ontology.merge_with(ontology_part)

                if stopped_threads > 0 and from_b_queue.empty():
                    break

        # Start concurrent processes
        loading = Process(target=loading_process, 
                         args=(self.sources, documents_queue, signal_queue))
        loading.start()

        creation = Process(target=ontology_process, 
                          args=(documents_queue, signal_queue, ontology_queue, Ontology()))
        creation.start()

        merge_process(ontology_queue)

        loading.join()
        creation.join()

        if len(self.ontology.entities) == 0:
            raise Exception("\nFailed to create ontology: Ontology is empty")

        self.ontology = self._fix_ontology(self._create_chat(), self.ontology)
        return self.ontology