# app.py
import os
import requests
from flask import Flask, request, jsonify
import zulfa_brain
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "sbleisure_secure_token")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

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
    return "Hello world", 200

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    try:
        body = request.get_json()
        print("Webhook received:", body)
        
        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    
                    if messages:
                        message = messages[0]
                        # Meta Cloud API letak nombor pengirim dalam key 'from' di peringkat objek message
                        phone_number = message.get("from") 
                        
                        if message.get("type") == "text":
                            user_message = message.get("text", {}).get("body", "")
                            
                            if phone_number and user_message:
                                print(f"Processing message from {phone_number}: {user_message}")
                                zulfa_reply = zulfa_brain.proses_mesej(user_message, phone_number)
                                print(f"Generated reply: {zulfa_reply}")
                                send_whatsapp_message(phone_number, zulfa_reply)

        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error webhook: {e}")
        return jsonify({"status": "error"}), 500

def send_whatsapp_message(recipient_phone, message_text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone,
        "type": "text",
        "text": {"body": message_text}
    }
    response = requests.post(url, json=payload, headers=headers)
    print(f"WhatsApp API Response Status: {response.status_code}")
    print(f"WhatsApp API Response Body: {response.text}")
    return response.json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))