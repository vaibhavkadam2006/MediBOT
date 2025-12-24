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

        # 1. Prepare a list of strings to search against
        # We combine Specialty + Tags for better matching
        doc_strings = [f"{d['specialty']} {d['tags']}" for d in self.doctors]
        
        # 2. Fuzzy Match (Finds the string most similar to the query)
        # Returns a list of tuples: (matched_string, score, index)
        results = process.extract(
            query, 
            doc_strings, 
            scorer=fuzz.token_sort_ratio, 
            limit=top_k
        )
        
        # 3. Retrieve the actual doctor objects based on index
        final_docs = []
        for match in results:
            # match format: (string, score, index)
            score = match[1]
            idx = match[2]
            
            if score > 30: # strictness threshold
                final_docs.append(self.doctors[idx])
                
        return final_docs