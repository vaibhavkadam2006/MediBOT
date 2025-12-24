const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const langSelect = document.getElementById("languageDropdown");

// --- 1. UI DICTIONARY (Updated with Button & Specialties) ---
const uiText = {
    en: {
        greeting: "Hello! I am your AI Nurse. Please describe your symptoms.",
        thinking: "AI is thinking...",
        error: "Could not connect to the server. Is app.py running?",
        no_doc: "No doctors are currently available online. Please schedule an appointment.",
        match: "Match Found",
        join_btn: "Join Video Call",
        specialties: {
            "General Medicine": "General Medicine",
            "Cardiology": "Cardiology",
            "Neurology": "Neurology",
            "Dermatology": "Dermatology",
            "Orthopedics": "Orthopedics",
            "Dentistry": "Dentistry"
        }
    },
    hi: {
        greeting: "नमस्ते! मैं आपकी AI नर्स हूँ। कृपया अपने लक्षणों का वर्णन करें।",
        thinking: "AI सोच रहा है...",
        error: "सर्वर से कनेक्ट नहीं हो सका।",
        no_doc: "वर्तमान में कोई डॉक्टर ऑनलाइन उपलब्ध नहीं है।",
        match: "डॉक्टर मिले",
        join_btn: "वीडियो कॉल शुरू करें",
        specialties: {
            "General Medicine": "सामान्य चिकित्सा (General Medicine)",
            "Cardiology": "हृदयरोग विशेषज्ञ (Cardiology)",
            "Neurology": "न्यूरोलॉजिस्ट (Neurology)",
            "Dermatology": "त्वचा विशेषज्ञ (Dermatology)",
            "Orthopedics": "हड्डी रोग विशेषज्ञ (Orthopedics)",
            "Dentistry": "दंत चिकित्सक (Dentist)"
        }
    },
    mr: {
        greeting: "नमस्कार! मी तुमची एआय नर्स आहे. कृपया तुमच्या लक्षणांचे वर्णन करा.", // Changed 'करें' to 'करा'
        thinking: "AI विचार करत आहे...",
        error: "सर्व्हरशी कनेक्ट होऊ शकलो नाही.",
        no_doc: "सध्या कोणतेही डॉक्टर ऑनलाइन उपलब्ध नाहीत.",
        match: "डॉक्टर सापडले",
        join_btn: "व्हिडिओ कॉल सुरू करा",
        specialties: {
            "General Medicine": "जनरल फिजिशियन (General Medicine)",
            "Cardiology": "हृदयरोग तज्ञ (Cardiologist)",
            "Neurology": "मेंदू विकार तज्ञ (Neurologist)",
            "Dermatology": "त्वचा रोग तज्ञ (Dermatologist)",
            "Orthopedics": "अस्थिरोग तज्ञ (Orthopedic)",
            "Dentistry": "दंत चिकित्सक (Dentist)"
        }
    }
};

const userID = "user_" + Math.random().toString(36).substr(2, 9);

sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

langSelect.addEventListener("change", () => {
    const lang = langSelect.value;
    const firstBotMsg = document.querySelector(".bot-message .text");
    if (firstBotMsg) firstBotMsg.innerText = uiText[lang].greeting;
});

async function sendMessage() {
    const text = userInput.value.trim();
    const language = langSelect.value;
    
    if (text === "") return;

    addMessage(text, "user");
    userInput.value = "";
    userInput.focus();

    const loader = document.createElement("div");
    loader.className = "loader";
    loader.innerText = uiText[language].thinking;
    chatBox.appendChild(loader);
    scrollToBottom();

    try {
        const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: userID,
            message: text,
            language: language
        })
    });

        const data = await response.json();
        chatBox.removeChild(loader);

        if (data.type === "question") {
            addMessage(data.message, "bot");
        } 
        else if (data.type === "diagnosis") {
            addMessage(data.message, "bot");
            if (data.action === "video_call" && data.doctor) {
                showVideoCallCard(data.doctor, language, data.specialty);
            } else {
                addMessage(uiText[language].no_doc, "bot");
            }
        }
    } catch (error) {
        if(chatBox.contains(loader)) chatBox.removeChild(loader);
        addMessage(uiText[language].error, "bot");
        console.error(error);
    }
}

function addMessage(text, sender) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.innerHTML = sender === "user" ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-user-nurse"></i>';

    const textDiv = document.createElement("div");
    textDiv.className = "text";
    textDiv.innerText = text;

    if (sender === "bot") {
        msgDiv.appendChild(avatar);
        msgDiv.appendChild(textDiv);
    } else {
        msgDiv.appendChild(textDiv);
        msgDiv.appendChild(avatar); 
    }
    chatBox.appendChild(msgDiv);
    scrollToBottom();
}

// --- UPDATED VIDEO CARD FUNCTION ---
function showVideoCallCard(doctor, lang, rawSpecialty) {
    const card = document.createElement("div");
    card.className = "message bot-message";
    
    // 1. Get Translated Specialty
    // Use the raw English specialty from backend to lookup the Marathi/Hindi text
    let displaySpecialty = uiText[lang].specialties[rawSpecialty] || doctor.specialty;

    // 2. Get Translated Button Text
    const btnText = uiText[lang].join_btn;

    const content = `
        <div class="avatar"><i class="fa-solid fa-video"></i></div>
        <div class="text">
            <div class="action-card">
                <strong>${uiText[lang].match}: ${doctor.name}</strong><br>
                <small>${displaySpecialty}</small><br>
                <small style="color:#666; font-size:0.8em">Exp: ${doctor.experience}</small><br>
                <a href="${doctor.meet_link}" target="_blank" class="video-btn">
                    <i class="fa-solid fa-video"></i> ${btnText}
                </a>
            </div>
        </div>
    `;
    
    card.innerHTML = content;
    chatBox.appendChild(card);
    scrollToBottom();
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}