# ==========================================
# BOT.PY - ZULFA (SBL TRANSPORT - GEMINI)
# ==========================================

import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")

# Memori sementara untuk simpan perbualan (supaya bot ingat & makin pandai)
chat_history = []

def tanya_gemini(mesej_user):
    global chat_history
    
    # Masukkan mesej user ke dalam memori
    chat_history.append({"role": "user", "parts": [{"text": mesej_user}]})
    
    # Ambil 6 mesej terakhir supaya ada konteks perbualan
    history_context = chat_history[-6:]
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": history_context,
        "system_instruction": {
            "parts": [{
                "text": "TAGLINE: DESTINASI ANDA, KEUTAMAAN KAMI!\nAnda adalah Zulfa, wakil SBL Transport. Gaya: Santai, peramah, mesra macam kawan, guna shortform Malaysia (nk, utk, sbb, sy, dlm, dgn, kt). Kawasan pickup sah: Selangor, KL, KLIA, Cyberjaya, Putrajaya. ATURAN: Jawab pendek, satu point sahaja setiap kali mesej. Ingat perbualan sebelumnya supaya nampak natural dan belajar dari soalan user."
            }]
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        
        if "error" in data:
            print("Ralat dari Gemini API:", data["error"])
            return "Maaf bos, sistem tengah rehat sekejap. Boleh ulang mesej ya? 😅"
            
        jawapan_ai = data['candidates'][0]['content']['parts'][0]['text']
        
        # Simpan jawapan bot pula dalam memori
        chat_history.append({"role": "model", "parts": [{"text": jawapan_ai}]})
        
        return jawapan_ai
    except Exception as e:
        print("Ralat Gemini:", e)
        return "Maaf bos, line slow sikit. Boleh ulang mesej ya? 😅"

def hantar_whatsapp(recipient_phone, message_text):
    url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
        "type": "text",
        "text": {"body": message_text},
    }
    requests.post(url, json=payload, headers=headers)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode and token:
            return challenge, 200
        return "Hello World", 200

    if request.method == "POST":
        data = request.get_json()
        try:
            changes = data["entry"][0]["changes"][0]["value"]
            if "messages" in changes:
                msg = changes["messages"][0]
                sender_phone = msg["from"]
                user_text = msg["text"]["body"]
                
                print(f"Mesej masuk dari {sender_phone}: {user_text}")
                
                # Dapatkan jawapan dari Gemini
                balasan_ai = tanya_gemini(user_text)
                
                print(f"Balasan AI: {balasan_ai}")
                
                # Hantar semula ke WhatsApp
                hantar_whatsapp(sender_phone, balasan_ai)
        except Exception as e:
            print("Ralat Webhook:", e)
            
        return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)