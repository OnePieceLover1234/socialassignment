import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv

# Load env variables
load_dotenv(override=True)

app = Flask(__name__)

# --- CONFIGURATION ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")

# Initialize Client
client = None
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    print("❌ CRITICAL ERROR: GROQ_API_KEY is missing from .env file!")

# --- MR. MANGO'S KNOWLEDGE BASE (UPDATED WITH LEGAL FRAMEWORK) ---
SYSTEM_PROMPT = """
You are Mr. Mango, the Chief Immigration Officer for The Mango Republic.
Your job is to assist applicants with the C.H.U.D. Act (Citizenship, Humanitarian & Unified Development).

# LEGAL FRAMEWORK (C.H.U.D. ACT):
1. **Foundation:** A domestic statute for a sovereign micronation. Value-driven and self-contained.
2. **Refugee Definition:** Based on "credible fear of persecution." Prioritizes humanitarian urgency.
3. **Non-Refoulement:** Absolute protection against forced return to danger.
4. **Screening:** Criminal checks, anti-extremism verification, and health screening (only excludes unmanageable risks).
5. **Decision Body:** Administrative Refugee Officers make decisions. Independent appeals board handles reviews.
6. **Rights:** Immediate work rights, language training, and community mentorship.

# POINTS SYSTEM (PASS MARK: 70/100):
- **Education (Max 25):** PhD(25), Masters(22), Bachelors(18), Trade(15), High School(8).
- **Experience (Max 20):** 5yr+(20), 3-4yr(15), 1-2yr(10), <1yr(5).
- **Language (Max 20):** Fluent(20), Moderate(12), Basic(5).
- **Age (Max 10):** 22-35(10), 36-45(7), 46-55(4), Other(2).
- **Job Offer (Max 15):** Confirmed(15), In-Demand(10), General(5).
- **Adaptability (Max 10):** Family/Work in Mango(5 each).

# BEHAVIOR:
- **Tone:** Professional, Authoritative but Welcoming.
- **Format:** Use Markdown. Use Bold for emphasis.
- **Style:** Direct answers. No fluff.
"""

@app.route('/')
def home():
    return render_template('index.html')

# --- QUIZ CALCULATION ENDPOINT ---
@app.route('/assess', methods=['POST'])
def assess():
    data = request.json
    try:
        score = 0
        score += int(data.get('education', 0))
        score += int(data.get('experience', 0))
        score += int(data.get('language', 0))
        score += int(data.get('age', 0))
        score += int(data.get('job', 0))
        score += int(data.get('adaptability', 0))

        passed = score >= 70
        
        return jsonify({
            "score": score,
            "passed": passed,
            "message": "Congratulations! You meet the C.H.U.D. Act eligibility requirements." if passed else "You do not currently meet the pass mark of 70."
        })
    except:
        return jsonify({"error": "Invalid data"}), 400

# --- CHATBOT ENDPOINT ---
@app.route('/ask', methods=['POST'])
def ask():
    if not client:
        return jsonify({"response": "❌ **System Error:** API Key missing."}), 500

    data = request.json
    user_message = data.get('message', '')
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            model=GROQ_MODEL,
            temperature=0.5,
            max_tokens=1024,
        )
        return jsonify({"response": chat_completion.choices[0].message.content})

    except Exception as e:
        return jsonify({"response": f"**Error:** {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
