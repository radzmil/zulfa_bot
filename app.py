import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
ADMIN = os.getenv("GROUP_ADMIN_NUMBER")
QR_IMAGE_URL = os.getenv("QR_IMAGE_URL", "")
TOYYIBPAY_LINK = os.getenv("TOYYIBPAY_LINK", "https://toyyibpay.com/link-pembayaran-anda")
SALES_WHATSAPP_LINK = os.getenv("SALES_WHATSAPP_LINK", "https://wa.link/o3z1bz")
COMPANY = "SHAHRIL BASRI LEISURE ENTERPRISE"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SESSION_STATE = {}

BORANG_MAKLUMAT = (
    "📝 *BORANG MAKLUMAT SEWAAN*\n\n"
    "Tarikh: \n"
    "Masa: \n"
    "Lokasi Ambil: \n"
    "Lokasi Hantar: \n"
    "Jumlah Penumpang: \n\n"
    "📌 *Sila lengkapkan semua butiran di atas.*"
)

def hantar(to, msg, type="text", image_url=None):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    payload = {"messaging_product": "whatsapp", "to": to, "type": type}
    if type == "text": payload["text"] = {"body": msg}
    elif type == "image": payload["image"] = {"link": image_url, "caption": msg}
    requests.post(url, json=payload, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})

def semak_borang_lengkap(text_borang):
    if not GEMINI_API_KEY: return "LENGKAP"
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        prompt = f"""
        Periksa teks ini. Adakah pelanggan telah mengisi maklumat borang sewaan ini dengan lengkap (Tarikh, Masa, Lokasi Ambil, Lokasi Hantar, Jumlah Penumpang)?
        Jika masih ada ruangan kosong, balas: TIDAK_LENGKAP.
        Jika sudah diisi, balas: LENGKAP.
        
        Teks: "{text_borang}"
        """
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"})
        return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
    except: return "LENGKAP"

def proses_mesej(user, text):
    msg = text.lower()


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