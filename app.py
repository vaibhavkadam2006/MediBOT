from flask import Flask, request, jsonify, render_template # <--- Added render_template
from flask_cors import CORS
import traceback
import re
import os

# Import engines
from ai_engine import AIEngine
from doctor_search import DoctorSearchEngine
from knowledge_graph import MedicalGraph
from deep_translator import GoogleTranslator

# --- CONFIGURATION FOR DEPLOYMENT ---
# We tell Flask where the HTML (templates) and CSS/JS (static) are located
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

print("⏳ Starting Medical Backend...")

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

# --- NEW: SERVE FRONTEND (Root URL) ---
@app.route('/')
def home():
    return render_template('index.html')

# --- API ENDPOINT ---
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_id = data.get('user_id', 'guest')
        user_msg_native = data.get('message', '')
        lang_code = data.get('language', 'en')
        
        if user_id not in user_sessions:
            user_sessions[user_id] = []
        
        history = user_sessions[user_id]

        # 1. Translate & Append User Message
        user_msg_en = translate_to_en(user_msg_native, lang_code)
        history.append(f"Patient: {user_msg_en}")

        # 2. Get AI Decision
        ai_response_en = ai_engine.generate_question(history)
        
        # --- DIAGNOSIS PHASE ---
        if "[STOP]" in ai_response_en:
            print(f"🛑 STOP Triggered. History length: {len(history)}")
            
            full_context = " ".join(history).lower()
            final_specialty = "General Medicine" 

            # A. Knowledge Graph Check
            try:
                kg_specialty, _ = kg.find_specialty(full_context)
                if kg_specialty:
                    final_specialty = kg_specialty
                    print(f"   (Graph Match: {kg_specialty})")
            except Exception as e:
                print(f"⚠️ Graph Error: {e}")

            # B. LLM Analysis
            if not kg_specialty:
                llm_report = ai_engine.analyze_urgency_and_specialty(history)
                match = re.search(r"SPECIALTY:\s*([A-Za-z\s]+)", llm_report, re.IGNORECASE)
                if match:
                    extracted = match.group(1).split("|")[0].strip()
                    final_specialty = re.sub(r'[^\w\s]', '', extracted)
            
            # C. Search Doctor
            doctors = search_engine.search_doctor(final_specialty, top_k=1)
            doc_match = doctors[0] if doctors else None
            
            # D. Response
            specialty_native = translate_to_user(final_specialty, lang_code)
            report_msg = translate_to_user("Based on your symptoms, I have identified the specialist.", lang_code)
            
            user_sessions[user_id] = [] # Reset Session
            
            return jsonify({
                "type": "diagnosis",
                "message": f"{report_msg} ({specialty_native})",
                "specialty": final_specialty,
                "doctor": doc_match,
                "action": "video_call" if doc_match else "schedule"
            })

        else:
            # --- QUESTION PHASE ---
            clean_q_en = ai_response_en.replace("Question:", "").strip()
            history.append(f"Nurse: {clean_q_en}")
            q_native = translate_to_user(clean_q_en, lang_code)
            
            return jsonify({
                "type": "question",
                "message": q_native
            })

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {traceback.format_exc()}")
        return jsonify({
            "type": "question", 
            "message": "Technical error. Please refresh."
        }), 500

if __name__ == '__main__':
    # Debug=False is better for Docker/Production
    app.run(host='0.0.0.0', port=5000, debug=False)