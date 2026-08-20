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
FB_COMPANY_LINK = "https://www.facebook.com/sewabaspersiaranmurah"
FB_ZULFA_LINK = "https://www.facebook.com/profile.php?id=61592928645216"

def hantar(to, msg):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": msg}
    }
    requests.post(url, json=payload, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})

def zulfa_reply(text):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        prompt = f"Awak Zulfa, staf SB Leisure (sewaan MPV, Van, Bas Persiaran). Jawab mesej pelanggan ni dengan santai, peramah, guna 'awk', dan SANGAT RINGKAS (1-2 ayat je). Mesej: {text}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"})
        return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except:
        return "Ada apa-apa lagi yang boleh Zulfa bantu awk? 😊"

def proses_mesej(text):
    msg = text.lower()
    
    # 1. Soalan spesifik link FB (Direct & Pantas)
    if "fb zulfa" in msg or "facebook zulfa" in msg:
        return f"Ni profil FB saya awk: {FB_ZULFA_LINK} 😊"
    if "facebook" in msg or "fb" in msg:
        return f"Ni link FB syarikat kitorang: {FB_COMPANY_LINK} 😊"
    
    # 2. Tapisan kenderaan luar
    if any(k in msg for k in ["bot", "speed boat", "lori", "moto", "kereta"]):
        return "Maaf awk, kitorang hanya ada sewaan MPV, Van, dan Bas Persiaran je tau. 🚌"

    # 3. Kalau nak sewa/booking, terus arahkan ke sales team dengan mesra
    if any(k in msg for k in ["sewa", "harga", "booking", "nak guna"]):
        return f"Boleh sangat awk! Untuk semak harga dan tempahan, boleh terus berurusan dengan team sales kitorang kat sini ya: {SALES_WHATSAPP_LINK}"

    # 4. Lain-lain dibalas oleh Gemini secara santai
    return zulfa_reply(text)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET": 
        return request.args.get("hub.challenge")
    
    data = request.get_json()
    try:
        user = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        body = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        hantar(user, proses_mesej(body))
    except: 
        pass
        
    return jsonify({"status": "success"}), 200

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))