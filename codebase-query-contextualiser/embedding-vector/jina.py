from pathlib import Path
from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn.functional as F
from qdrant_client.models import PointStruct
from qdrant_client import QdrantClient

class JinaCodeEmbeddings:
    """
    A class for embedding and searching code using the Jina embeddings model.
    
    This class provides functionality to:
    - Generate embeddings for code snippets using the Jina embeddings model
    - Store and search code embeddings using Qdrant vector database
    - Process and chunk code files intelligently based on their type (HTML, CSS, etc.)
    - Perform semantic code search using natural language queries
    
    The embeddings are optimized for code understanding and search.
    """

    def __init__(self, collection_name="code_chunks"):
        """
        Initialize the JinaCodeEmbeddings class.
        
        Args:
            collection_name (str): Name of the Qdrant collection to store embeddings
        """
        self.tokenizer = AutoTokenizer.from_pretrained('jinaai/jina-embeddings-v2-base-code')
        self.model = AutoModel.from_pretrained('jinaai/jina-embeddings-v2-base-code', trust_remote_code=True)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)
        self._output_dim = 768  # Changed from 1024 to 768 to match model's output dimension
        
        # Initialize Qdrant client
        self.client = QdrantClient(":memory:")  # Using in-memory storage for demo
        self.collection_name = collection_name
        self.setup_collection()

    def setup_collection(self):
        """
        Setup the Qdrant collection for storing code embeddings.
        Creates a new collection with the specified name and vector configuration.
        Deletes existing collection if it exists.
        """
        # Check if collection exists and delete if it does
        if self.client.get_collections().collections:
            self.client.delete_collection(collection_name=self.collection_name)
            
        # Create new collection
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                "size": self._output_dim,
                "distance": "Cosine"
            }
        )

    def mean_pooling(self, model_output, attention_mask):
        """
        Perform mean pooling on model outputs using attention mask.
        
        Args:
            model_output: Output tensors from the model
            attention_mask: Attention mask for the input
            
        Returns:
            Pooled embeddings tensor
        """
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def encode(self, texts, max_length=8192):
        """
        Generate embeddings for the given text(s).
        
        Args:
            texts (str or list): Input text(s) to encode
            max_length (int): Maximum sequence length for tokenization
            
        Returns:
            numpy.ndarray: Normalized embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
            
        # Tokenize sentences
        encoded_input = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors='pt'
        ).to(self.device)

        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)

        # Perform mean pooling
        embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        
        # Normalize embeddings
        embeddings = F.normalize(embeddings, p=2, dim=1)
        
        return embeddings.cpu().numpy()
    
    def get_output_dim(self):
        """
        Get the output dimension of the embeddings.
        
        Returns:
            int: Dimension of the embedding vectors
        """
        return self._output_dim

    def process_sample_codebase(self):
        """Process and embed the sample codebase files with code-aware chunking"""
        codebase_dir = Path("sameple-codebase")
        files_to_process = [
            codebase_dir / "index.html",
            codebase_dir / "styles/main.css"
        ]
        
        idx = 0
        for file_path in files_to_process:
            if file_path.exists():
                with open(file_path) as f:
                    content = f.read()
                    
                    # Split content into meaningful chunks
                    chunks = []
                    if file_path.suffix == '.html':
                        # Split HTML by semantic sections
                        import re
                        # Match elements with their content
                        elements = ['html', 'head', 'body', 'header', 'nav', 'main', 'section', 'footer', 'form', 'div']
                        pattern = f'(<(?:{"|".join(elements)})[^>]*>.*?</(?:{"|".join(elements)})>)'
                        matches = re.finditer(pattern, content, re.DOTALL)
                        
                        for match in matches:
                            chunk = match.group(1)
                            # Add context about the matched element
                            element_type = re.match(r'<(\w+)', chunk).group(1)
                            chunks.append({
                                'content': chunk,
                                'context': f'HTML {element_type} element and its contents'
                            })
                    else:
                        # Split CSS by rules and group related rules
                        import re
                        # Match complete CSS rules including nested blocks
                        css_blocks = re.findall(r'(?:/\*[^*]*\*+(?:[^/*][^*]*\*+)*/\s*)?([^{}]+{[^}]+})', content)
                        
                        for block in css_blocks:
                            # Extract selector and properties
                            selector = re.match(r'([^{]+){', block).group(1).strip()
                            chunks.append({
                                'content': block,
                                'context': f'CSS styles for {selector}'
                            })
                    
                    # Process each chunk
                    for chunk in chunks:
                        # Create metadata string with context
                        processed_content = (
                            f"FILE: {file_path}\n"
                            f"TYPE: {file_path.suffix[1:]}\n"
                            f"CONTEXT: {chunk['context']}\n\n"
                            f"CONTENT:\n{chunk['content']}"
                        )
                        
                        # Get embedding
                        embedding = self.encode(processed_content)
                        
                        # Create point for Qdrant
                        point = PointStruct(
                            id=idx,
                            vector=embedding[0].tolist(),
                            payload={"text": processed_content}
                        )
                        
                        # Store in vector storage
                        self.client.upsert(
                            collection_name=self.collection_name,
                            points=[point]
                        )
                        idx += 1
                        
                print(f"Processed: {file_path}")

    def demo_code_search(self):
        """Demonstrate code search capabilities with sample queries"""
        print("\n=== Jina Code Search Demo ===\n")
        
        sample_queries = [
            # HTML structure queries
            "Show me the navigation menu structure",
            "Find the contact form HTML",
            "What's in the footer section?",
            
            # CSS styling queries
            "How is the navigation styled?",
            "What are the form input styles?",
            "Show me all button styles",
            "What's the color scheme?",
            
            # Mixed queries
            "How is the header implemented and styled?",
            "Show me everything related to forms",
            "Find responsive design related code",
            
            # Semantic queries
            "Where is user interaction handled?",
            "Show me the main content area",
            "Find code related to layout structure",
            
            # Technical queries
            "Find all flex layouts",
            "Show me media queries",
            "List all CSS selectors for interactive elements"
        ]
        
        for query in sample_queries:
            print(f"\nQuery: {query}")
            # Get query embedding
            query_embedding = self.encode(query)
            # Search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding[0].tolist(),
                limit=2  # Show top 2 results for demo
            )
            
            print("\nTop Results:")
            for i, result in enumerate(results, 1):
                # Extract and format the relevant parts
                content = result.payload["text"]
                context = content.split("\nCONTENT:\n")[0]  # Get metadata
                code = content.split("\nCONTENT:\n")[1][:200]  # Get first 200 chars of code
                print(f"\n{i}. {context}")
                print(f"Code Preview: {code}...")
            print("\n" + "="*50)

    def process_and_demo(self):
        """Process the codebase and run the demo"""
        self.process_sample_codebase()
        self.demo_code_search()

def main():
    # Create and run the demo
    jina_embeddings = JinaCodeEmbeddings()
    jina_embeddings.process_and_demo()

if __name__ == "__main__":
    main()
