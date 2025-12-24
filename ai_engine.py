import os
from groq import Groq

class AIEngine:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile" 

    def generate_question(self, history):
        # 1. Safety Limit (5 questions max)
        nurse_turns = sum(1 for msg in history if "Nurse:" in msg)
        if nurse_turns >= 5: return "[STOP]"

        # 2. Smart Prompt
        context = "\n".join(history)
        
        prompt = f"""[INST] You are a medical triage assistant.
        
        Conversation So Far:
        {context}
        
        CRITICAL RULES:
        1. NO REPETITION: Check the history. If the user already mentioned duration (e.g. "2 days"), DO NOT ask "How long?".
        2. ACCEPT "UNKNOWN": If user says "I don't know" or "I didn't measure", DO NOT ask the same question again. Move to the next symptom immediately.
        3. BE NATURAL BUT BRIEF: Use 1-2 sentences. No robotic checklists.
        4. CHECKLIST:
           - If Fever: Ask about chills, body ache, or cold.
           - If Pain: Ask location and severity.
           - If done: Output [STOP].
        
        Your Next Question: [/INST]"""
        
        # Temperature 0.5 balances creativity (natural) vs strictness (rules)
        return self._call_groq(prompt, temp=0.5)

    def analyze_urgency_and_specialty(self, history):
        context = "\n".join(history)
        prompt = f"""[INST] Diagnose Patient.
        History: {context}
        
        RULES:
        - Chest pain -> Cardiology
        - Headache/Migraine -> Neurology
        - Joint/Bone pain -> Orthopedics
        - Skin/Rash -> Dermatology
        - Fever/Cold -> General Medicine
        - Tooth -> Dentistry
        
        Format: URGENCY: [Level] | SPECIALTY: [One Word] [/INST]"""
        return self._call_groq(prompt, temp=0.1)

    def _call_groq(self, prompt, temp):
        try:
            return self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                max_tokens=80, 
                temperature=temp 
            ).choices[0].message.content.strip()
        except: return "[STOP]"