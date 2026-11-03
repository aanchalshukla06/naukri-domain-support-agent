import chromadb
from chromadb.utils import embedding_functions

def evaluate_retrieval():
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    fixed_collection = chroma_client.get_collection(name="fixed_chunks", embedding_function=sentence_transformer_ef)
    sentence_collection = chroma_client.get_collection(name="sentence_chunks", embedding_function=sentence_transformer_ef)
    
    # 5 Real Questions (In-Scope) + 2 Fake Questions (Out-of-Scope)
    test_queries = [
        {"query": "How long is the notice period for someone on probation?", "target_topic": "notice-period policy"},
        {"query": "When do I need to schedule my interview by?", "target_topic": "interview-scheduling process"},
        {"query": "Are HR executives eligible for the referral bonus?", "target_topic": "referral-bonus policy"},
        {"query": "How many days a week must hybrid workers be in the office?", "target_topic": "remote-work eligibility"},
        {"query": "How long do you keep my resume on file?", "target_topic": "applicant-data-retention policy"},
        {"query": "What is the recipe for baking a chocolate cake?", "target_topic": "OUT_OF_SCOPE"},
        {"query": "How do I fix a flat tire on my bicycle?", "target_topic": "OUT_OF_SCOPE"}
    ]
    
    print("--- CHUNKING STRATEGY EVALUATION ---")
    
    for collection, name in [(fixed_collection, "Fixed Chunks"), (sentence_collection, "Sentence Chunks")]:
        print(f"\nEvaluating: {name}")
        correct_retrievals = 0
        
        for q in test_queries:
            results = collection.query(query_texts=[q["query"]], n_results=1)
            retrieved_topic = results['metadatas'][0][0]['topic'] if results['metadatas'][0] else "None"
            distance = results['distances'][0][0] if results['distances'][0] else 999
            
            # ChromaDB uses distance (lower is better). We can convert to rough similarity.
            similarity_score = 1 - distance
            
            print(f"Q: '{q['query']}'")
            print(f"   Target: {q['target_topic']} | Retrieved: {retrieved_topic} | Sim Score: {similarity_score:.4f}")
            
            if q["target_topic"] == retrieved_topic:
                correct_retrievals += 1
                
        # Recall/Precision (At k=1, accuracy is equivalent to precision/recall for a single target)
        accuracy = (correct_retrievals / 5) * 100 # Only scoring against the 5 in-scope questions
        print(f"-> {name} Document-Level Accuracy (k=1): {accuracy}%")

if __name__ == "__main__":
    evaluate_retrieval()