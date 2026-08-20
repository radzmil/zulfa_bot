import os
import csv
import traceback
import requests
from datetime import datetime
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

BORANG_TEMPLATE = (
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
    "🔄 *Maklumat Return Trip (Isi jika TWO WAY sahaja) :-*\n"
    "Tarikh & Masa (Balik) : \n"
    "Pick-up point : \n"
    "Drop-off point : \n"
    "Pax : \n\n"
    "📌 *Sila lengkapkan borang di atas untuk pengiraan sebut harga.*"
)

BANK_INFO = {
    "bank": "CIMB Bank Berhad",
    "no_akaun": "860 5247 780"
}

def hantar(to, msg, type="text", image_url=None):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    payload = {"messaging_product": "whatsapp", "to": to, "type": type}
    if type == "text": payload["text"] = {"body": msg}
    elif type == "image": payload["image"] = {"link": image_url, "caption": msg}
    requests.post(url, json=payload, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})

def semak_sop_borang(text_borang):
    if not GEMINI_API_KEY: return "LENGKAP"
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        prompt = f"""
        Awak adalah sistem pemantau SOP untuk {COMPANY}. Semak borang ini:
        1. Jika jenis trip 'Two Way', adakah ruangan return trip diisi? Jika tidak, balas: TIDAK_LENGKAP
        2. Jika jenis trip 'One Way', adakah maklumat utama lengkap? Jika tidak, balas: TIDAK_LENGKAP
        3. Jika tarikh tempahan kurang 8 hari dari hari ini ({datetime.now().strftime('%Y-%m-%d')}), balas: URGENT
        Jika semua syarat dipenuhi, balas: LENGKAP
        
        Mesej: "{text_borang}"
        """
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"})
        return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
    except: return "LENGKAP"

def kira_harga_sewaan(text_borang):
    if not GEMINI_API_KEY: return "RM 350 - RM 600"
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        prompt = f"Berdasarkan maklumat borang ini, berikan anggaran sebut harga kasar dalam RM: {text_borang}. Berikan harga sahaja secara ringkas."
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"})
        return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except: return "RM 350 - RM 600"

def proses_mesej(user, text):
    msg = text.lower()
    
    # 1. Tapisan Kenderaan Luar (Strict)
    if any(k in msg for k in ["bot", "speed boat", "lori", "moto", "kereta"]):
        return f"Maaf, {COMPANY} hanya menyediakan perkhidmatan sewaan MPV, Van, dan Bas Persiaran sahaja."

    # 2. Status Menunggu Persetujuan Harga
    if user in SESSION_STATE and SESSION_STATE[user].get("status") == "tunggu_persetujuan":
        if any(k in msg for k in ["setuju", "ok", "proceed", "terus"]):
            borang_data = SESSION_STATE[user]["borang"]
            del SESSION_STATE[user]
            hantar(user, f"Maklumat Pembayaran DuitNow QR / ToyyibPay:\nBank: {BANK_INFO['bank']}\nNo Akaun: {BANK_INFO['no_akaun']}\nLink: {TOYYIBPAY_LINK}", type="image", image_url=QR_IMAGE_URL)
            if ADMIN:
                hantar(ADMIN, f"📋 *TEMPAHAN SAH & DIPERSETUJUI*\nDari: {user}\n\n{borang_data}")
            return "Sila buat bayaran deposit/penuh dan hantar resit di sini."
        else:
            del SESSION_STATE[user]
            return f"Tempahan dibatalkan atau tidak disetujui. Sila hubungi sales: {SALES_WHATSAPP_LINK}"

    # 3. Penerimaan & Semakan Borang
    if "borang" in msg or "pick-up" in msg or "drop-off" in msg or "one way" in msg or "two way" in msg:
        status_sop = semak_sop_borang(text)
        
        if "URGENT" in status_sop:
            return f"Tempahan ini adalah URGENT (kurang 8 hari). Sila berurusan terus dengan team sales: {SALES_WHATSAPP_LINK}"
        if "TIDAK_LENGKAP" in status_sop:
            return f"Borang tidak lengkap mengikut SOP One Way / Two Way. Sila isi semula mengikut format:\n\n{BORANG_TEMPLATE}"
        
        # Kira Harga & Simpan State
        anggaran = kira_harga_sewaan(text)
        SESSION_STATE[user] = {"borang": text, "status": "tunggu_persetujuan"}
        return f"📊 Anggaran Sebut Harga: {anggaran}\n\nAdakah anda bersetuju dengan harga ini? Sila balas 'Setuju' untuk mendapatkan maklumat pembayaran."

    # Default jika bukan borang: Minta borang
    return f"Sila lengkapkan borang tempahan berikut untuk memulakan pengiraan harga:\n\n{BORANG_TEMPLATE}"

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