import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = "sbleisure_secure_token"

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Verification failed", 403
            
    return "Hello world, webhook endpoint is active!", 200

@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    print("Mesej diterima:", data)

    try:
        changes = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {})
        if "messages" in changes:
            msg_body = changes["messages"][0]["text"]["body"]
            from_number = changes["messages"][0]["from"]
            phone_number_id = changes["metadata"]["phone_number_id"]
            
            print(f"Mesej daripada {from_number}: {msg_body}")
            
            # Panggil Gemini API secara terus guna requests
            ai_reply = ask_gemini(msg_body)
            
            # Hantar jawapan ke WhatsApp
            send_whatsapp_message(phone_number_id, from_number, ai_reply)
            
    except Exception as e:
        print("Ralat memproses mesej:", e)

    return jsonify({"status": "success"}), 200

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        res_json = response.json()
        return res_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return "Maaf, ada masalah teknikal pada sistem AI."

def send_whatsapp_message(phone_number_id, recipient_phone, message_text):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
        "type": "text",
        "text": {"body": message_text},
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Respons hantar mesej:", response.json())

if __name__ == "__main__":
    app.run(port=5000, debug=True)