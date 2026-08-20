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
SALES_WHATSAPP_LINK = os.getenv("SALES_WHATSAPP_LINK", "https://wa.me/60100000000")
COMPANY = "SHAHRIL BASRI LEISURE ENTERPRISE"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SESSION_STATE = {}

BORANG_ONE_WAY = (
    "📝 *BORANG MAKLUMAT SEWAAN*\n\n"
    "Jenis Trip (One Way / Two Way) : \n"
    "Syarikat : \n"
    "Nama : \n"
    "No. tel : \n"
    "Tarikh & Masa (Pergi) : \n"
    "Pick-up point : \n"
    "Drop-off point : \n"
    "Pax : \n"
    "Jenis Kenderaan (MPV/Van/Bas) : \n"
)

BORANG_TWO_WAY = (
    "📝 *BORANG MAKLUMAT SEWAAN*\n\n"
    "Jenis Trip (One Way / Two Way) : \n"
    "Syarikat : \n"
    "Nama : \n"
    "No. tel : \n"
    "Tarikh & Masa (Pergi) : \n"
    "Pick-up point : \n"
    "Drop-off point : \n"
    "Pax : \n"
    "Jenis Kenderaan (MPV/Van/Bas) : \n\n"
    "🔄 *Maklumat Return Trip (Isi jika TWO WAY sahaja) :-\n"
    "Tarikh & Masa (Balik) : \n"
    "Pick-up point : \n"
    "Drop-off point : \n"
    "Pax : *"
)

def hantar(to, msg, type="text", image_url=None):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    payload = {"messaging_product": "whatsapp", "to": to, "type": type}
    if type == "text": payload["text"] = {"body": msg}
    elif type == "image": payload["image"] = {"link": image_url, "caption": msg}
    requests.post(url, json=payload, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})

def kira_harga_sewaan(text_borang):
    if not GEMINI_API_KEY: return "RM 350 - RM 600"
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        prompt = f"Berdasarkan borang maklumat sewaan ini, berikan anggaran sebut harga kasar dalam RM: {text_borang}. Berikan jawapan harga pendek sahaja."
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"})
        return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except: return "RM 350 - RM 600"

def proses_mesej(user, text):
    msg = text.lower()
    
    # 1. Pilihan Jenis Trip
    if user in SESSION_STATE and SESSION_STATE[user].get("status") == "tunggu_jenis_trip":
        if any(k in msg for k in ["one", "1", "sehala"]):
            SESSION_STATE[user].update({"status": "tunggu_borang", "trip_type": "One Way"})
            return f"Sila lengkapkan borang tempahan berikut:\n\n{BORANG_ONE_WAY}"
        elif any(k in msg for k in ["two", "2", "balik"]):
            SESSION_STATE[user].update({"status": "tunggu_borang", "trip_type": "Two Way"})
            return f"Sila lengkapkan borang tempahan berikut:\n\n{BORANG_TWO_WAY}"
        return "Sila balas 1 untuk *One Way* atau 2 untuk *Two Way*."

    # 2. Pilihan Bayaran
    if user in SESSION_STATE and SESSION_STATE[user].get("status") == "tunggu_pilihan_bayar":
        borang_data = SESSION_STATE[user]["borang"]
        del SESSION_STATE[user]
        if any(k in msg for k in ["qr", "qrcode"]):
            hantar(user, "Sila buat bayaran melalui DuitNow QR di bawah:", type="image", image_url=QR_IMAGE_URL)
            if ADMIN: hantar(ADMIN, f"📋 *TEMPAHAN (QR)*\n{borang_data}")
            return "Sila hantar resit di sini ya. Terima kasih!"
        elif any(k in msg for k in ["online", "bank"]):
            if ADMIN: hantar(ADMIN, f"📋 *TEMPAHAN (Online)*\n{borang_data}")
            return f"Sila buat bayaran melalui link ini:\n{TOYYIBPAY_LINK}\n\nSila hantar resit di sini. Terima kasih!"
        return "Sila pilih kaedah pembayaran: *QR Code* atau *Online Banking*."

    # 3. Persetujuan Harga
    if user in SESSION_STATE and SESSION_STATE[user].get("status") == "tunggu_persetujuan":
        if any(k in msg for k in ["setuju", "ok"]):
            SESSION_STATE[user]["status"] = "tunggu_pilihan_bayar"
            return "Sila pilih kaedah pembayaran:\n1. *QR Code*\n2. *Online Banking*"
        del SESSION_STATE[user]
        return "Tempahan dibatalkan."

    # 4. Input Borang
    if user in SESSION_STATE and SESSION_STATE[user].get("status") == "tunggu_borang":
        anggaran = kira_harga_sewaan(text)
        SESSION_STATE[user].update({"status": "tunggu_persetujuan", "borang": text})
        return f"📊 *Anggaran Harga:* {anggaran}\n\nAdakah anda bersetuju? Balas 'Setuju' untuk teruskan."

    # Default: Mula
    SESSION_STATE[user] = {"status": "tunggu_jenis_trip"}
    return "Selamat datang ke *SHAHRIL BASRI LEISURE ENTERPRISE*.\nNak sewa kenderaan untuk trip jenis apa?\n1. *One Way*\n2. *Two Way*"

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