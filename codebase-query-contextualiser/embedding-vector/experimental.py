# Just for experimental purposes for trying out different models
# Not that much efficient results yet
from pathlib import Path
from sentence_transformers import SentenceTransformer
from camel.retrievers import VectorRetriever
from camel.storages.vectordb_storages import QdrantStorage
from qdrant_client.models import PointStruct
from transformers import AutoTokenizer, AutoModel
import torch

def setup_vector_storage():
    """Initialize the vector storage with CodeBERT embeddings"""
    # Load CodeBERT model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    model = AutoModel.from_pretrained("microsoft/codebert-base")
    
    # Create a wrapper class for CodeBERT
    class CodeBERTWrapper:
        def __init__(self, model, tokenizer):
            self.model = model
            self.tokenizer = tokenizer
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model.to(self.device)
            self._output_dim = 768  # CodeBERT's output dimension
            
        def encode(self, text):
            self.model.eval()
            with torch.no_grad():
                inputs = self.tokenizer(text, padding=True, truncation=True, 
                                     max_length=512, return_tensors="pt")
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                outputs = self.model(**inputs)
                # Use [CLS] token embedding as the sequence representation
                embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                return embeddings[0]  # Return the first (and only) embedding
    
    code_model = CodeBERTWrapper(model, tokenizer)
    sample_embedding = code_model.encode("test")
    vector_dim = len(sample_embedding)
    
    # Create storage path inside camel folder
    storage_path = Path(__file__).parent / "storage" / "sample_codebase"
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    vector_storage = QdrantStorage(
        vector_dim=vector_dim,
        collection_name="sample_codebase",
        path=str(storage_path),
    )
    return code_model, vector_storage

def process_codebase(vector_retriever, vector_storage, model):
    """Process and embed the sample codebase files"""
    codebase_dir = Path("sameple-codebase")
    files_to_process = [
        codebase_dir / "index.html",
        codebase_dir / "styles/main.css"
    ]
    
    for idx, file_path in enumerate(files_to_process):
        if file_path.exists():
            with open(file_path) as f:
                content = f.read()
                # Create metadata string
                processed_content = f"FILE: {file_path}\nTYPE: {file_path.suffix[1:]}\n\nCONTENT:\n{content}"
                # Get embedding
                embedding = model.encode(processed_content)
                # Create point for Qdrant
                point = PointStruct(
                    id=idx,
                    vector=embedding.tolist(),
                    payload={"text": processed_content}
                )
                # Store in vector storage
                vector_storage.client.upsert(
                    collection_name=vector_storage.collection_name,
                    points=[point]
                )
            print(f"Processed: {file_path}")

def search_codebase(query, vector_storage, model, top_k=3):
    """Search the codebase with a query"""
    query_embedding = model.encode(query)
    results = vector_storage.client.search(
        collection_name=vector_storage.collection_name,
        query_vector=query_embedding.tolist(),
        limit=top_k
    )
    return [result.payload["text"] for result in results]

def main():
    # Setup
    model, vector_storage = setup_vector_storage()
    
    class EmbeddingWrapper:
        def __init__(self, model):
            self.model = model
            self._output_dim = len(self.model.encode("test"))
            
        def get_output_dim(self):
            return self._output_dim
            
        def embed(self, text):
            return self.model.encode(text)
    
    wrapped_model = EmbeddingWrapper(model)
    vector_retriever = VectorRetriever(embedding_model=wrapped_model)
    
    # Process codebase
    process_codebase(vector_retriever, vector_storage, model)
    
    # Example queries
    queries = [
        # "What are the main navigation elements?",
        "How is the contact form styled?",
        # "What color scheme is used in the CSS?"
        # "List of navigation items"
        # "Change footer color to red?"
        # "Search for footer code in index"
        # "show me only index file code"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        results = search_codebase(query, vector_storage, model)
        print(f"Results: {results}")

if __name__ == "__main__":
    main()
