from pathlib import Path
from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn.functional as F
from qdrant_client.models import PointStruct
from qdrant_client import QdrantClient
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class CodeEmbeddings:
    def __init__(self, collection_name="code_chunks"):
        self.tokenizer = AutoTokenizer.from_pretrained('jinaai/jina-embeddings-v2-base-code')
        self.model = AutoModel.from_pretrained('jinaai/jina-embeddings-v2-base-code', trust_remote_code=True)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)
        self._output_dim = 768  
        
        # Initialize Qdrant for vector storage
        self.client = QdrantClient(path="qdrant.db")  # Persistent local storage
        self.collection_name = collection_name
        self.setup_collection()

    def setup_collection(self):
        """Sets up a Qdrant collection to store code embeddings."""
        if self.collection_name in [col.name for col in self.client.get_collections().collections]:
            self.client.delete_collection(collection_name=self.collection_name)

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                "size": self._output_dim,
                "distance": "Cosine"
            }
        )

    def mean_pooling(self, model_output, attention_mask):
        """Performs mean pooling to generate a single embedding per input."""
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def encode(self, texts, max_length=8192):
        """Encodes text inputs into embeddings."""
        if isinstance(texts, str):
            texts = [texts]
        
        encoded_input = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors='pt'
        ).to(self.device)

        with torch.no_grad():
            model_output = self.model(**encoded_input)

        embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
        embeddings = F.normalize(embeddings, p=2, dim=1)
        
        return embeddings.cpu().numpy()

    def process_sample_codebase(self):
        """Reads and processes code files, extracts functions, and stores embeddings."""
        codebase_dir = Path("data")
        allowed_extensions = {'.js', '.c', '.cpp', '.cs', '.py', '.java', '.ts', '.go', '.rb', '.php', '.html', '.css'}
        files_to_process = [f for f in codebase_dir.glob("**/*") if f.suffix in allowed_extensions]

        idx = 0
        for file_path in files_to_process:
            logging.info(f"Processing file: {file_path}")
            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()

                    chunks = []
                    ext = file_path.suffix

                    # Extract functions/classes/methods based on file type
                    function_pattern = None
                    if ext in {'.c', '.cpp', '.cs', '.java', '.go'}:
                        function_pattern = re.compile(r'\b\w+\s+\w+\s*\([^)]*\)\s*\{.*?\}', re.DOTALL)
                    elif ext in {'.py'}:
                        function_pattern = re.compile(r'def\s+\w+\s*\(.*?\):\s*(?:.*?\n)*?(?=\n\S|\Z)', re.DOTALL)
                    elif ext in {'.js', '.ts'}:
                        function_pattern = re.compile(r'(async\s+)?function\s+\w+\s*\(.*?\)\s*\{.*?\}', re.DOTALL)
                    elif ext in {'.rb'}:
                        function_pattern = re.compile(r'def\s+\w+\s*\(.*?\)\s*(?:.*?\n)*?(?=\n\S|\Z)', re.DOTALL)
                    elif ext in {'.php'}:
                        function_pattern = re.compile(r'function\s+\w+\s*\(.*?\)\s*\{.*?\}', re.DOTALL)
                    
                    matches = function_pattern.findall(content) if function_pattern else []
                    
                    for match in matches:
                        function_name = match.split('(')[0].split()[-1]  # Extract function name
                        chunks.append({
                            'content': match,
                            'context': f'Function: {function_name}'
                        })

                    for chunk in chunks:
                        processed_content = (
                            f"FILE: {file_path}\n"
                            f"TYPE: {file_path.suffix[1:]}\n"
                            f"CONTEXT: {chunk['context']}\n\n"
                            f"CONTENT:\n{chunk['content']}"
                        )

                        embedding = self.encode(processed_content)

                        point = PointStruct(
                            id=idx,
                            vector=embedding[0].tolist(),
                            payload={"text": processed_content}
                        )

                        self.client.upsert(
                            collection_name=self.collection_name,
                            points=[point]
                        )
                        idx += 1

                logging.info(f"✅ Processed: {file_path}")
            except Exception as e:
                logging.error(f"❌ Error processing {file_path}: {e}")

    def query_code(self, query_text, top_k=3):
        """Searches the stored codebase using natural language queries."""
        query_embedding = self.encode(query_text)

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding[0].tolist(),
            limit=top_k
        )

        print("\n🔍 **Query:**", query_text)
        print("\n🎯 **Top Matches:**")

        for i, result in enumerate(results, 1):
            content = result.payload["text"]
            context, code_snippet = content.split("\nCONTENT:\n", 1)

            print(f"\n{i}. {context}")
            print(f"📌 **Code Preview:**\n{code_snippet[:300]}...\n")  # Preview first 300 chars
            print("-" * 80)

    def process_and_demo(self):
        """Processes the codebase and runs queries."""
        self.process_sample_codebase()

        # Sample Queries
        sample_queries = [
            "Give me generate_response_groq function"
        ]
        
        for query in sample_queries:
            self.query_code(query)

def main():
    code_embeddings = CodeEmbeddings()
    try:
        code_embeddings.process_and_demo()
    finally:
        code_embeddings.client.close()  # Ensure the client is closed gracefully

if __name__ == "__main__":
    main()
