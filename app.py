import os
import csv
import traceback
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
ADMIN = os.getenv("GROUP_ADMIN_NUMBER")
QR_IMAGE_URL = os.getenv("QR_IMAGE_URL", "")
TOYYIBPAY_LINK = os.getenv("TOYYIBPAY_LINK", "https://toyyibpay.com/link-pembayaran-anda")
SALES_WHATSAPP_LINK = os.getenv("SALES_WHATSAPP_LINK", "https://wa.me/60100000000")
COMPANY = "SHAHRIL BASRI LEISURE ENTERPRISE"
DATA_FILE = "data_pelanggan.csv"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VERIFY_TOKEN_VAL = os.getenv("VERIFY_TOKEN", "sbleisure_secure_token")

SESSION_STATE = {}

BANK_INFO = {
    "bank": "CIMB Bank Berhad",
    "no_akaun": "860 5247 780",
    "swift": "CIBBMYKLXXX"
}

BORANG_TEMPLATE = (
    "Terima kasih kerana berminat dengan perkhidmatan sewaan Mpv/Van/Bas persiaran\n"
    "🚎 *SB Leisure* 🚎\n\n"
    "➡️ Mohon Tuan/Puan isi :\n\n"
    "📝 *BORANG MAKLUMAT SEWAAN*\n\n"
    "Jenis Trip (One Way / Two Way) : \n"
    "Syarikat : \n"
    "Alamat : \n\n"
    "Nama : \n"
    "No. tel : \n"
    "Tarikh : \n"
    "Masa : \n"
    "Pick-up point : \n"
    "Drop-off point : \n"
    "Pax : \n\n"
    "➡️ Jenis sewaan (Mpv/Van/Bas) : \n\n"
    "🔄 *Maklumat untuk RETURN trip (Isi jika TWO WAY sahaja) :-*\n\n"
    "Tarikh : \n"
    "Masa : \n"
    "Pick-up point : \n"
    "Drop-off point : \n"
    "Pax : \n\n"
    "📌 *HARGA SEWAAN TERTAKLUK KEPADA JARAK DAN MASA PERJALANAN YANG DIBERIKAN* 📍\n\n"
    "T.KASIH 😊"
)

def hantar(to, msg, type="text", image_url=None):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": type}
    if type == "text": payload["text"] = {"body": msg}
    elif type == "image": payload["image"] = {"link": image_url, "caption": msg}
    requests.post(url, json=payload, headers=headers)

def semak_sop_borang_gemini(text_borang):
    if not GEMINI_API_KEY: return "LENGKAP"
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        prompt = f"""
        Awak adalah sistem pemantau SOP untuk {COMPANY}. 
        Semak borang ini:
        1. Jika 'Two Way', adakah semua ruangan Return Trip diisi? Jika tidak, balas: TIDAK_LENGKAP
        2. Jika 'One Way', adakah maklumat utama (Nama, Tarikh, Masa, Pick-up, Drop-off, Pax, Jenis Kenderaan) diisi? Jika tidak, balas: TIDAK_LENGKAP
        3. Jika tarikh tempahan (untuk mana-mana trip) dalam tempoh 1-7 hari dari hari ini ({datetime.now().strftime('%Y-%m-%d')}), balas: URGENT
        4. Jika maklumat tidak sah/lepas, balas: TIDAK_SAH
        
        Jika semua syarat dipenuhi, balas: LENGKAP
        
        Mesej: "{text_borang}"
        """
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        res = requests.post(url, json=payload, headers=headers)
        return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
    except: return "LENGKAP"

def kira_harga_gemini(text_borang):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        prompt = f"Berikan anggaran harga untuk tempahan sewaan ini: {text_borang}. Gaya bahasa santai/mesra Zulfa."
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        res = requests.post(url, json=payload, headers=headers)
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except: return "Anggaran harga: Sila rujuk admin."

def proses_mesej(user, text):
    msg = text.lower()
    
    # Pengesahan Harga
    if user in SESSION_STATE and SESSION_STATE[user].get("status") == "menunggu_persetujuan_harga":
        if any(k in msg for k in ["setuju", "on", "ok", "proceed"]):
            borang = SESSION_STATE[user]["borang"]
            del SESSION_STATE[user]
            hantar(user, f"Alhamdulillah, terima kasih! Ini maklumat pembayaran:\nBank: {BANK_INFO['bank']}\nNo: {BANK_INFO['no_akaun']}\nRef: {user}", type="image", image_url=QR_IMAGE_URL)
            return "Sila buat bayaran dan balas 'dah bayar' selepas siap. 🙏"
        else:
            del SESSION_STATE[user]
            return "Baik awk, boleh bincang semula jika ada apa-apa."

    # Proses Borang
    if "borang maklumat sewaan" in msg or "pick-up point" in msg:
        status = semak_sop_borang_gemini(text)
        if "URGENT" in status: return f"Tempahan urgent (1-7 hari). Sila hubungi sales di sini: {SALES_WHATSAPP_LINK}"
        if "TIDAK_LENGKAP" in status or "TIDAK_SAH" in status: return f"Borang tidak ikut SOP (One Way/Two Way). Sila semak semula:\n\n{BORANG_TEMPLATE}"
        
        harga = kira_harga_gemini(text)
        SESSION_STATE[user] = {"borang": text, "status": "menunggu_persetujuan_harga"}
        return f"Terima kasih! 😊 Anggaran harga: {harga}\n\nSetuju dengan harga ni? Balas 'Setuju' untuk teruskan ke pembayaran."

    return "Ada apa-apa Zulfa boleh bantu?"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    data = request.get_json()
    try:
        user = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        body = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        hantar(user, proses_mesej(user, body))
    except: pass
    return jsonify({"status": "success"}), 200

if __name__ == "__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))