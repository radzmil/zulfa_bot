import os
import csv
import traceback
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Konfigurasi
TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
ADMIN = os.getenv("GROUP_ADMIN_NUMBER")
QR_IMAGE_URL = os.getenv("QR_IMAGE_URL", "")
TOYYIBPAY_LINK = os.getenv("TOYYIBPAY_LINK", "https://toyyibpay.com/link-pembayaran-anda")
SALES_WHATSAPP_LINK = os.getenv("SALES_WHATSAPP_LINK", "https://wa.me/60100000000")
COMPANY = "SHAHRIL BASRI LEISURE ENTERPRISE"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VERIFY_TOKEN_VAL = os.getenv("VERIFY_TOKEN", "sbleisure_secure_token")

SESSION_STATE = {}

BORANG_TEMPLATE = (
    "📝 *BORANG MAKLUMAT SEWAAN*\n\n"
    "Jenis Trip (One Way/Two Way): \n"
    "Nama: \n"
    "Tarikh & Masa: \n"
    "Pick-up/Drop-off: \n"
    "Bilangan Pax: \n"
    "Jenis Kenderaan (MPV/Van/Bas): \n\n"
    "*(Jika Two Way, sila nyatakan maklumat return trip sekali ya!)*"
)

def hantar(to, msg):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": msg}}
    requests.post(url, json=payload, headers=headers)

def semak_gemini(text, mode="chat"):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        # Prompt "Zulfa" yang lebih natural
        prompt = f"""
        Awak adalah Zulfa, staf khidmat pelanggan yang sangat peramah untuk {COMPANY}. 
        Gaya bahasa: Melayu santai, mesra, suka guna panggilan 'awk', 'kitorang', 'tau'.
        Jangan jadi robot. Jangan asyik ulang soalan yang sama.
        
        Konteks: {text}
        
        Tugasan:
        1. Jika pelanggan tanya 'ni syarikat apa', jawab dengan mesra dan ceritakan kitorang pakar sewa MPV/Van/Bas.
        2. Jika pelanggan sekadar menyapa, balas dengan ramah.
        3. JANGAN hantar borang melainkan pelanggan memang tunjuk minat nak sewa.
        4. Jika pelanggan tanya pasal sewaan, baru ajak mereka isi borang.
        """
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"})
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except: return "Boleh saya bantu apa-apa lagi awk? 😊"

def proses_mesej(user, text):
    msg = text.lower()
    
    # Logik perbualan santai
    if any(k in msg for k in ["hi", "hello", "salam", "selamat"]):
        return f"Waalaikumussalam/Hai awk! Saya Zulfa dari {COMPANY}. Ada apa-apa yang saya boleh bantu hari ni? 😊"
    
    if "syarikat" in msg or "sb leisure" in msg:
        return "Ye betul awk! Kitorang adalah SB Leisure (Shahril Basri Leisure Enterprise). Kitorang memang pakar sediakan servis sewaan MPV, Van, dan Bas persiaran untuk trip awk ke mana sahaja. Ada plan nak pergi mana-mana ke tu?"

    # Jika pelanggan tanya pasal sewa
    if any(k in msg for k in ["sewa", "nak guna", "harga"]):
        return f"Boleh sangat awk! Kitorang ada banyak pilihan kenderaan. Untuk kitorang bagi sebut harga yang tepat, boleh awk tolong isikan borang ringkas ni? 😊\n\n{BORANG_TEMPLATE}"

    return semak_gemini(text)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return request.args.get("hub.challenge")
    data = request.get_json()
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        user, body = msg["from"], msg["text"]["body"]
        hantar(user, proses_mesej(user, body))
    except: pass
    return jsonify({"status": "success"}), 200

if __name__ == "__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))