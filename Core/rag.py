import json
import chromadb
from chromadb.utils import embedding_functions

def setup_rag_collections():
    # 1. Initialize local ChromaDB in a folder called 'chroma_db'
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    # 2. Use a free, local SentenceTransformer model for embeddings
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # 3. Create two separate collections for our two chunking strategies
    fixed_collection = chroma_client.get_or_create_collection(name="fixed_chunks", embedding_function=sentence_transformer_ef)
    sentence_collection = chroma_client.get_or_create_collection(name="sentence_chunks", embedding_function=sentence_transformer_ef)
    
    # 4. Load the Knowledge Base data
    with open("data/knowledge_base.json", "r") as f:
        kb_data = json.load(f)
        
    fixed_ids, fixed_texts, fixed_metadatas = [], [], []
    sent_ids, sent_texts, sent_metadatas = [], [], []
    
    for i, doc in enumerate(kb_data):
        text = doc["text"]
        topic = doc["topic"]
        
        # Strategy A: Fixed-size chunks (e.g., splitting roughly in half for short docs)
        midpoint = len(text) // 2
        chunk1 = text[:midpoint]
        chunk2 = text[midpoint:]
        
        fixed_texts.extend([chunk1, chunk2])
        fixed_metadatas.extend([{"topic": topic, "chunk_type": "fixed"}, {"topic": topic, "chunk_type": "fixed"}])
        fixed_ids.extend([f"doc_{i}_fixed_1", f"doc_{i}_fixed_2"])
        
        # Strategy B: Sentence-level chunks (splitting by periods)
        sentences = [s.strip() + "." for s in text.split(".") if s.strip()]
        for j, sentence in enumerate(sentences):
            sent_texts.append(sentence)
            sent_metadatas.append({"topic": topic, "chunk_type": "sentence"})
            sent_ids.append(f"doc_{i}_sent_{j}")
            
    # 5. Insert chunks into their respective collections
    fixed_collection.upsert(ids=fixed_ids, documents=fixed_texts, metadatas=fixed_metadatas)
    sentence_collection.upsert(ids=sent_ids, documents=sent_texts, metadatas=sent_metadatas)
    
    print("Successfully indexed documents into ChromaDB!")
    return fixed_collection, sentence_collection

if __name__ == "__main__":
    setup_rag_collections()