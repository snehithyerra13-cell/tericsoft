import math
import re
import json
from typing import List, Dict, Any, Optional
from collections import Counter
from sqlalchemy.orm import Session
from backend.models import Product
from backend.database import SessionLocal

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
    "your", "yours", "yourself", "yourselves", "need", "want", "looking", "look"
}

def tokenize(text: str) -> List[str]:
    """Tokenizes text into lowercase alphanumeric words, filtering stopwords."""
    words = re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", text.lower())
    return [w for w in words if w not in STOPWORDS]

class TFIDFRetriever:
    """
    Lightweight, deterministic local TF-IDF and Cosine Similarity retriever.
    Operates without paid vector databases, external embedding APIs, or GPUs.
    Supports weighted fields (name, category, solution, features, description).
    """

    def __init__(self, products: List[Dict[str, Any]]):
        self.products = products
        self.doc_count = len(products)
        self.idf: Dict[str, float] = {}
        self.doc_vectors: List[Dict[str, float]] = []
        self.doc_norms: List[float] = []
        self._build_index()

    def _build_index(self):
        doc_term_freqs = []
        doc_freq = Counter()

        for prod in self.products:
            # Parse features if JSON string
            features_list = prod.get("features", [])
            if isinstance(features_list, str):
                try:
                    features_list = json.loads(features_list)
                except Exception:
                    features_list = [features_list]

            # Weighted field representation
            name_tokens = tokenize(prod.get("name", "")) * 3
            category_tokens = tokenize(prod.get("category", "")) * 2
            solution_tokens = tokenize(prod.get("solution", "")) * 2
            feature_tokens = tokenize(" ".join(features_list)) * 1
            desc_tokens = tokenize(prod.get("description", "")) * 1

            all_tokens = name_tokens + category_tokens + solution_tokens + feature_tokens + desc_tokens
            tf = Counter(all_tokens)
            doc_term_freqs.append(tf)

            # Document frequency for IDF
            for term in set(all_tokens):
                doc_freq[term] += 1

        # Calculate smooth IDF: log((1 + N) / (1 + df)) + 1
        for term, df in doc_freq.items():
            self.idf[term] = math.log((1 + self.doc_count) / (1 + df)) + 1.0

        # Build TF-IDF document vectors and compute Euclidean norms
        for tf in doc_term_freqs:
            vec = {}
            norm_sq = 0.0
            for term, count in tf.items():
                weight = (1 + math.log(count)) * self.idf.get(term, 1.0)
                vec[term] = weight
                norm_sq += weight * weight
            self.doc_vectors.append(vec)
            self.doc_norms.append(math.sqrt(norm_sq) if norm_sq > 0 else 1.0)

    def query(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_tokens = tokenize(query_text)
        if not query_tokens:
            # Fallback to general top products if query is empty after stopword removal
            return [
                {**self._format_product(p), "score": 0.1}
                for p in self.products[:top_k]
            ]

        query_tf = Counter(query_tokens)
        query_vec = {}
        query_norm_sq = 0.0

        for term, count in query_tf.items():
            idf = self.idf.get(term, math.log(1 + self.doc_count) + 1.0)
            weight = (1 + math.log(count)) * idf
            query_vec[term] = weight
            query_norm_sq += weight * weight

        query_norm = math.sqrt(query_norm_sq) if query_norm_sq > 0 else 1.0

        # Calculate Cosine Similarity with all documents
        scores = []
        for idx, (doc_vec, doc_norm) in enumerate(zip(self.doc_vectors, self.doc_norms)):
            dot_product = 0.0
            for term, q_weight in query_vec.items():
                if term in doc_vec:
                    dot_product += q_weight * doc_vec[term]

            cos_sim = dot_product / (query_norm * doc_norm) if (query_norm * doc_norm) > 0 else 0.0
            scores.append((idx, cos_sim))

        # Sort descending by cosine similarity score
        scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, sim in scores[:top_k]:
            prod = self.products[idx]
            formatted = self._format_product(prod)
            # Normalize display score between 0.0 and 1.0, minimum baseline 0.15 for top matches
            display_score = round(max(sim, 0.05 if sim > 0 else 0.0), 3)
            formatted["score"] = display_score
            results.append(formatted)

        return results

    def _format_product(self, prod: Dict[str, Any]) -> Dict[str, Any]:
        features = prod.get("features", [])
        if isinstance(features, str):
            try:
                features = json.loads(features)
            except Exception:
                features = [features]

        return {
            "id": prod.get("id", 0),
            "name": prod.get("name", ""),
            "category": prod.get("category", ""),
            "description": prod.get("description", ""),
            "features": features,
            "solution": prod.get("solution", "")
        }

def retrieve_relevant_products(
    query: str,
    top_k: int = 3,
    db: Optional[Session] = None,
    products_cache: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Main retrieval entry point.
    Searches the product knowledge base using TF-IDF and returns the top_k most relevant items.
    """
    if products_cache:
        raw_products = products_cache
    else:
        close_session = False
        if db is None:
            db = SessionLocal()
            close_session = True
        try:
            db_products = db.query(Product).all()
            raw_products = [
                {
                    "id": p.id,
                    "name": p.name,
                    "category": p.category,
                    "description": p.description,
                    "features": p.features,
                    "solution": p.solution
                }
                for p in db_products
            ]
        finally:
            if close_session:
                db.close()

    if not raw_products:
        return []

    retriever = TFIDFRetriever(raw_products)
    return retriever.query(query, top_k=top_k)
