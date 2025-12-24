import json
import os
import torch
import random # <--- ADDED RANDOM
from sentence_transformers import SentenceTransformer, util

class DoctorSearchEngine:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        db_path = os.path.join("data", "doctors_db.json")
        try:
            with open(db_path, "r") as f: self.doctors = json.load(f)
        except: self.doctors = []
            
        if self.doctors:
            self.doc_texts = [f"{d['specialty']} {d['tags']}" for d in self.doctors]
            self.doc_embeddings = self.model.encode(self.doc_texts, convert_to_tensor=True)

    def search_doctor(self, query, top_k=1):
        if not self.doctors: return []

        query_emb = self.model.encode(query, convert_to_tensor=True)
        scores = util.cos_sim(query_emb, self.doc_embeddings)[0]
        
        # Get Top 3 matches instead of just 1
        top_count = min(3, len(self.doctors))
        top_results = torch.topk(scores, k=top_count)
        
        candidates = []
        for score, idx in zip(top_results.values, top_results.indices):
            if score.item() > 0.15: 
                candidates.append(self.doctors[idx.item()])
        
        # Randomly pick one from the top candidates
        if candidates:
            # If user asks for 1, give a random one from the top 3
            if top_k == 1:
                return [random.choice(candidates)]
            return candidates[:top_k]
            
        return []