from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import re
import os

# Import engines
from ai_engine import AIEngine
from doctor_search import DoctorSearchEngine
from knowledge_graph import MedicalGraph
from deep_translator import GoogleTranslator

# Initialize Flask as a PURE API
app = Flask(__name__)
CORS(app) # Allow your external website to talk to this API

print("⏳ Starting Medical Backend API...")

# --- LOAD ENGINES ---
try:
    ai_engine = AIEngine()
    kg = MedicalGraph()
    search_engine = DoctorSearchEngine()
    print("✅ Backend Ready.")
except Exception as e:
    print(f"❌ Initialization Error: {e}")

user_sessions = {}

# --- HELPER FUNCTIONS ---
def translate_to_en(text, lang_code):
    if lang_code == 'en': return text
    try: return GoogleTranslator(source='auto', target='en').translate(text)
    except: return text

def translate_to_user(text, lang_code):
    if lang_code == 'en': return text
    try: return GoogleTranslator(source='en', target=lang_code).translate(text)
    except: return text

# --- HEALTH CHECK ENDPOINT ---
# Frontend can call this to see if Chatbot is online
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "online", "service": "MediBot API"})

# --- MAIN CHAT ENDPOINT ---
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # 1. Parse Input
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        user_id = data.get('user_id', 'guest')
        user_msg_native = data.get('message', '')
        lang_code = data.get('language', 'en')
        
        if user_id not in user_sessions:
            user_sessions[user_id] = []
        
        history = user_sessions[user_id]

        # 2. Translate & Process
        user_msg_en = translate_to_en(user_msg_native, lang_code)
        history.append(f"Patient: {user_msg_en}")

        # 3. Get AI Decision
        ai_response_en = ai_engine.generate_question(history)
        
        # --- SCENARIO A: DIAGNOSIS COMPLETE (STOP) ---
        if "[STOP]" in ai_response_en:
            full_context = " ".join(history).lower()
            final_specialty = "General Medicine" 

            # Knowledge Graph Step
            try:
                kg_specialty, _ = kg.find_specialty(full_context)
                if kg_specialty: final_specialty = kg_specialty
            except: pass

            # LLM Analysis Step (if Graph failed)
            if not kg_specialty:
                llm_report = ai_engine.analyze_urgency_and_specialty(history)
                match = re.search(r"SPECIALTY:\s*([A-Za-z\s]+)", llm_report, re.IGNORECASE)
                if match:
                    extracted = match.group(1).split("|")[0].strip()
                    final_specialty = re.sub(r'[^\w\s]', '', extracted)
            
            # Find Doctor
            doctors = search_engine.search_doctor(final_specialty, top_k=1)
            doc_match = doctors[0] if doctors else None
            
            # Translate outputs
            specialty_native = translate_to_user(final_specialty, lang_code)
            message_native = translate_to_user("Diagnosis complete. I have identified the specialist.", lang_code)
            
            # Clear session
            user_sessions[user_id] = []
            
            # RETURN PURE JSON DATA
            return jsonify({
                "type": "diagnosis",
                "message": message_native,
                "data": {
                    "specialty": final_specialty,
                    "specialty_translated": specialty_native,
                    "doctor": doc_match, # Contains name, link, experience
                    "recommended_action": "video_call" if doc_match else "schedule_visit"
                }
            })

        # --- SCENARIO B: ASK NEXT QUESTION ---
        else:
            clean_q_en = ai_response_en.replace("Question:", "").strip()
            history.append(f"Nurse: {clean_q_en}")
            q_native = translate_to_user(clean_q_en, lang_code)
            
            return jsonify({
                "type": "question",
                "message": q_native,
                "data": None
            })

    except Exception as e:
        print(f"❌ ERROR: {traceback.format_exc()}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)