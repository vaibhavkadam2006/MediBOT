import networkx as nx

class MedicalGraph:
    def __init__(self):
        print("⏳ Building Extended Medical Knowledge Graph...")
        self.G = nx.DiGraph()
        self._build_graph()
        print(f"✅ Knowledge Graph Built ({self.G.number_of_nodes()} nodes).")

    def _build_graph(self):
        # Format: self._add_path(Symptom, Disease, Weight, Specialty)
        
        # --- 1. CARDIOLOGY (Heart) ---
        for sym in ["chest pain", "chest hurts", "heart pain", "pain in chest"]:
            self._add_path(sym, "Heart Attack", 1.0, "Cardiology")
        self._add_path("shortness of breath", "Heart Failure", 0.9, "Cardiology")
        self._add_path("palpitations", "Arrhythmia", 0.9, "Cardiology")

        # --- 2. NEUROLOGY (Brain) ---
        # ADDED SYNONYMS HERE:
        for sym in ["headache", "head pain", "head hurts", "my head is hurting", "severe headache"]:
            self._add_path(sym, "Migraine", 0.9, "Neurology")
            
        self._add_path("dizziness", "Vertigo", 0.9, "Neurology")
        self._add_path("seizure", "Epilepsy", 1.0, "Neurology")
        self._add_path("slurred speech", "Stroke", 1.0, "Neurology")

        # --- 3. ORTHOPEDICS (Bones) ---
        for sym in ["back pain", "back hurts", "spine pain"]:
            self._add_path(sym, "Sciatica", 0.9, "Orthopedics")
        for sym in ["knee pain", "joint pain", "knee hurts"]:
            self._add_path(sym, "Arthritis", 0.8, "Orthopedics")
        self._add_path("fracture", "Bone Fracture", 1.0, "Orthopedics")

        # --- 4. DERMATOLOGY (Skin) ---
        self._add_path("rash", "Eczema", 0.9, "Dermatology")
        self._add_path("itch", "Allergies", 0.8, "Dermatology")
        self._add_path("redness", "Rosacea", 0.8, "Dermatology")
        self._add_path("hair loss", "Alopecia", 1.0, "Dermatology")

        # --- 5. OPHTHALMOLOGY (Eyes) --- 
        for sym in ["blurry vision", "cant see clearly", "vision loss"]:
            self._add_path(sym, "Cataracts", 0.9, "Ophthalmology")
        self._add_path("eye pain", "Glaucoma", 0.9, "Ophthalmology")

        # --- 6. PULMONOLOGY (Lungs) ---
        self._add_path("wheezing", "Asthma", 1.0, "Pulmonology")
        self._add_path("coughing blood", "Tuberculosis", 1.0, "Pulmonology")

        # --- 7. GASTROENTEROLOGY (Stomach) ---
        for sym in ["stomach pain", "stomach ache", "belly pain", "abdominal pain"]:
            self._add_path(sym, "Gastritis", 0.9, "Gastroenterology")
        self._add_path("acid reflux", "GERD", 1.0, "Gastroenterology")

        # --- 8. UROLOGY ---
        self._add_path("painful urination", "UTI", 1.0, "Urology")
        self._add_path("blood in urine", "Kidney Stones", 1.0, "Urology")

        # --- 9. DENTISTRY ---
        for sym in ["toothache", "tooth pain", "teeth hurt"]:
            self._add_path(sym, "Cavity", 1.0, "Dentistry")

        # --- 10. GENERAL MEDICINE ---
        self._add_path("fever", "Viral Infection", 0.9, "General Medicine")
        self._add_path("cough", "Viral Infection", 0.8, "General Medicine")
        self._add_path("weakness", "General Fatigue", 0.7, "General Medicine")
        self._add_path("vomiting", "Gastroenteritis", 0.9, "General Medicine")

    def _add_path(self, symptom, disease, weight, specialty):
        """Helper to create the Symptom -> Disease -> Specialty chain"""
        self.G.add_edge(symptom, disease, weight=weight)
        self.G.add_edge(disease, specialty, type="treated_by")

    def find_specialty(self, user_symptoms):
        possible_specialties = {}
        user_symptoms = user_symptoms.lower()

        # Check every symptom node in our graph
        for node in self.G.nodes():
            # EXACT MATCH or SUBSTRING match
            # If "head pain" is in "i have head pain from yesterday"
            if node in user_symptoms and self.G.out_degree(node) > 0:
                
                diseases = list(self.G.successors(node))
                for disease in diseases:
                    specialties = list(self.G.successors(disease))
                    
                    for spec in specialties:
                        if spec not in possible_specialties:
                            possible_specialties[spec] = 0
                        
                        weight = self.G[node][disease].get('weight', 0.5)
                        possible_specialties[spec] += weight

        if not possible_specialties:
            return None, "No direct graph match found."

        # Return the highest scored specialty
        best_specialty = max(possible_specialties, key=possible_specialties.get)
        return best_specialty, f"Graph Logic: {possible_specialties}"