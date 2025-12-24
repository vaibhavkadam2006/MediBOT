import json
import os
from rapidfuzz import process, fuzz

class DoctorSearchEngine:
    def __init__(self):
        print("⏳ Loading Doctor Search Engine (Lightweight)...")
        
        # Load Data
        db_path = os.path.join("data", "doctors_db.json")
        try:
            with open(db_path, "r") as f:
                self.doctors = json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: Could not find {db_path}")
            self.doctors = []
            
        print(f"✅ Loaded {len(self.doctors)} doctors.")

    def search_doctor(self, query, top_k=1):
        if not self.doctors:
            return []

        # 1. Prepare strings to search against
        doc_strings = [f"{d['specialty']} {d['tags']}" for d in self.doctors]
        
        # 2. Fuzzy Match (Switching to partial_ratio for better accuracy)
        results = process.extract(
            query, 
            doc_strings, 
            scorer=fuzz.partial_ratio,  # <--- CHANGED THIS
            limit=top_k
        )
        
        final_docs = []
        for match in results:
            score = match[1]
            idx = match[2]
            
            # Since partial_ratio is generous, we increase threshold to 60
            if score >= 60: 
                final_docs.append(self.doctors[idx])
                
        return final_docs