"""
Embeds the catalog once, then retrieves top-K relevant tests for any query.
"""
import json
import numpy as np
from sentence_transformers import SentenceTransformer

class CatalogRetriever:
    def __init__(self, catalog_path="catalog.json", model_name="all-MiniLM-L6-v2"):
        print("Loading embedding model...")
        self.model = SentenceTransformer(model_name)
        with open(catalog_path, encoding="utf-8") as f:
            self.catalog = json.load(f)
        print(f"Embedding {len(self.catalog)} catalog items...")
        self.texts = [
            f"{p['name']}. {p['description']} Tags: {', '.join(p.get('tags', []))}. Type: {p['test_type']}"
            for p in self.catalog
        ]
        self.embeddings = self.model.encode(self.texts, normalize_embeddings=True, show_progress_bar=False)
        print("✅ Retriever ready.")

    def search(self, query: str, top_k: int = 15) -> list:
        """Return top_k catalog items most relevant to the query."""
        q_emb = self.model.encode([query], normalize_embeddings=True)[0]
        scores = self.embeddings @ q_emb
        top_idx = np.argsort(scores)[::-1][:top_k]
        results = []
        for i in top_idx:
            item = self.catalog[i].copy()
            item["score"] = float(scores[i])
            results.append(item)
        return results

    def get_by_name(self, name: str):
        name_lower = name.lower()
        for p in self.catalog:
            if p["name"].lower() == name_lower:
                return p
        return None