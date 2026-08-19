import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")

system_instruction = """
==================================================
SYSTEM PROMPT & SKRIP CHATBOT SEWAAN KENDERAAN (WHATCHIMP)
NAMA AI: ZULFA (STAFF SALES SBL TRANSPORT)
TAGLINE: DESTINASI ANDA, KEUTAMAAN KAMI!
==================================================
- Bertindak sepenuhnya sbg staf manusia bernama Zulfa.
- Wajib guna gaya mesej WhatsApp yang santai, peramah, mesra, dan berjiwa.
- WAJIB menggunakan shortform perbualan harian Malaysia (nk, utk, sbb, sy, dlm, dgn, kt, tau, jgn, tq, kol/ws).
- KAWASAN PICKUP SAH: SELANGOR, KUALA LUMPUR, KLIA, CYBERJAYA, PUTRAJAYA.
"""

app = Flask(__name__)

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode and token:
        return challenge, 200
    return "Verification failed", 403

def hantar_whatsapp(nombor_penerima, mesej_balasan):
    print("MENCCUBA HANTAR KE WHATSAPP...")
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": nombor_penerima,
        "text": {"body": mesej_balasan},
    }
    response = requests.post(url, json=payload, headers=headers)
    print("HASIL RESPON META:", response.text)
    return response.json()

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    body = request.get_json()

    try:
        if body.get("object"):
            if (
                body.get("entry")
                and body["entry"][0].get("changes")
                and body["entry"][0]["changes"][0].get("value")
                and body["entry"][0]["changes"][0]["value"].get("messages")
            ):
                value = body["entry"][0]["changes"][0]["value"]
                from_number = value["messages"][0]["from"]
                msg_body = value["messages"][0]["text"]["body"]

                print(f"Dari: {from_number} | Mesej: {msg_body}")

                # Jana jawapan menggunakan Gemini API secara terus (requests)
                url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                headers_gemini = {"Content-Type": "application/json"}
                payload_gemini = {
                    "contents": [{"parts": [{"text": msg_body}]}],
                    "system_instruction": {"parts": [{"text": system_instruction}]}
                }

                res_gemini = requests.post(url_gemini, json=payload_gemini, headers=headers_gemini)
                res_data = res_gemini.json()

                try:
                    balasan_ai = res_data["candidates"][0]["content"]["parts"][0]["text"]
                except Exception as ex:
                    print("Ralat struktur Gemini API:", res_data)
                    balasan_ai = "Maaf bos, sistem tengah rehat seketika. Boleh ulang mesej ya? 😅"

                print(f"Balasan AI: {balasan_ai}")

                # Hantar jawapan balik ke WhatsApp pengguna secara automatik
                hantar_whatsapp(from_number, balasan_ai)

                return jsonify({"status": "success"}), 200
            
            return jsonify({"status": "ignored"}), 200
        else:
            return "Not a WhatsApp API event", 404
    except Exception as e:
        print(f"Ralat Webhook: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)