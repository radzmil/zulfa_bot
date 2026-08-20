import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Konfigurasi
TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SALES_WHATSAPP_LINK = os.getenv("SALES_WHATSAPP_LINK", "https://wa.me/60100000000")
QR_IMAGE_URL = os.getenv("QR_IMAGE_URL", "")
FB_COMPANY_LINK = "https://www.facebook.com/sewabaspersiaranmurah"
FB_ZULFA_LINK = "https://www.facebook.com/profile.php?id=61592928645216"

SESSION_STATE = {}

def hantar(to, msg, type="text", image_url=None):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    payload = {"messaging_product": "whatsapp", "to": to, "type": type}
    if type == "text": payload["text"] = {"body": msg}
    elif type == "image": payload["image"] = {"link": image_url, "caption": msg}
    requests.post(url, json=payload, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})

def zulfa_reply(text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        prompt = f"Awak Zulfa, staf SB Leisure. Jawab ringkas (max 2 ayat), santai, guna 'awk'. Mesej: {text}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"})
        return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except:
        return "Ada apa-apa lagi yang Zulfa boleh bantu awk? 😊"

def proses_mesej(user, text):
    msg = text.lower()
    
    # 1. Link Facebook
    if "fb zulfa" in msg or "facebook zulfa" in msg:
        return f"Ni profil FB saya awk: {FB_ZULFA_LINK}. Jangan lupa add tau! 😊"
    if "facebook" in msg or "fb" in msg:
        return f"Ni link FB syarikat kitorang: {FB_COMPANY_LINK}. Jemput like ya! 😊"
    
    # 2. Tapisan Kenderaan
    if any(k in msg for k in ["bot", "speed boat", "lori", "moto", "kereta"]):
        return "Maaf awk, kitorang hanya ada MPV, Van, dan Bas Persiaran je. 🚌"

    # 3. Flow Harga
    if user in SESSION_STATE and SESSION_STATE[user]["status"] == "tunggu_setuju":
        if any(k in msg for k in ["setuju", "ok", "proceed", "teruskan"]):
            hantar(user, "Terima kasih awk! Sila buat bayaran kat sini ya & hantar resit:", type="image", image_url=QR_IMAGE_URL)
            del SESSION_STATE[user]
            return "Dah bayar nanti terus hantar resit kat sini tau! 🙏"
        else:
            del SESSION_STATE[user]
            return f"Orite, kalau nak bincang lanjut boleh terus WhatsApp sales team: {SALES_WHATSAPP_LINK}"

    if any(k in msg for k in ["sewa", "harga", "nak booking"]):
        SESSION_STATE[user] = {"status": "tunggu_setuju"}
        return "Boleh awk! Anggaran harga kasar RM350 - RM500 ikut destinasi. Setuju ke nak kitorang proceed ke payment?"

    return zulfa_reply(text)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET": return request.args.get("hub.challenge")
    data = request.get_json()
    try:
        user = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        body = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        hantar(user, proses_mesej(user, body))
    except: pass
    return jsonify({"status": "success"}), 200

if __name__ == "__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))