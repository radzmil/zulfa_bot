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

# Tetapan harga tetap mengikut kenderaan (Boleh ubah nilai RM di sini)
KADAR_HARGA = {
    "mpv": 250,
    "van": 350,
    "bas": 600
}

BORANG_ONE_WAY = (
    "📝 *BORANG MAKLUMAT SEWAAN (ONE WAY)*\n\n"
    "Jenis Trip (One Way / Two Way) : One Way\n"
    "Syarikat : \n"
    "Nama : \n"
    "No. tel : \n"
    "Tarikh & Masa (Pergi) : \n"
    "Pick-up point : \n"
    "Drop-off point : \n"
    "Pax : \n"
    "Jenis Kenderaan (MPV/Van/Bas) : \n\n"
    "📌 *Sila lengkapkan semua butiran di atas.*"
)

BORANG_TWO_WAY = (
    "📝 *BORANG MAKLUMAT SEWAAN (TWO WAY)*\n\n"
    "Jenis Trip (One Way / Two Way) : Two Way\n"
    "Syarikat : \n"
    "Nama : \n"
    "No. tel : \n"
    "Tarikh & Masa (Pergi) : \n"
    "Pick-up point : \n"
    "Drop-off point : \n"
    "Pax : \n"
    "Jenis Kenderaan (MPV/Van/Bas) : \n\n"
    "🔄 *Maklumat Return Trip :-*\n"
    "Tarikh & Masa (Balik) : \n"
    "Pick-up point : \n"
    "Drop-off point : \n"
    "Pax : \n\n"
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
        Periksa teks ini. Adakah pelanggan telah mengisi maklumat borang sewaan ini dengan lengkap (nama, no telefon, tarikh, pick-up, drop-off, pax, jenis kenderaan)?
        Jika masih ada ruangan kosong, tandatangan kosong, atau hanya hantar templat kosong, balas: TIDAK_LENGKAP.
        Jika sudah diisi dengan maklumat sebenar, balas: LENGKAP.
        
        Teks: "{text_borang}"
        """
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"})
        return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
    except: return "LENGKAP"

def kira_harga_tetap(text_borang):
    text_lower = text_borang.lower()
    harga = 350 # Harga default jika jenis kenderaan tidak dijumpai
    jenis_kenderaan = "Kenderaan"
    
    if "bas" in text_lower:
        harga = KADAR_HARGA["bas"]
        jenis_kenderaan = "Bas"
    elif "van" in text_lower:
        harga = KADAR_HARGA["van"]
        jenis_kenderaan = "Van"
    elif "mpv" in text_lower:
        harga = KADAR_HARGA["mpv"]
        jenis_kenderaan = "MPV"
        
    # Jika Two Way, gandakan harga (atau letak formula anda di sini)
    if "two way" in text_lower or "pergi balik" in text_lower or "balik" in text_lower:
        harga = harga * 2
        
    return f"RM {harga}", jenis_kenderaan

def proses_mesej(user, text):
    msg = text.lower()
    
    # 1. Pilihan Jenis Trip
    if user in SESSION_STATE and SESSION_STATE[user].get("status") == "tunggu_jenis_trip":
        if any(k in msg for k in ["one way", "one", "sehala"]):
            SESSION_STATE[user].update({"status": "tunggu_borang", "trip_type": "One Way"})
            return f"Sila lengkapkan borang ini:\n\n{BORANG_ONE_WAY}"
        elif any(k in msg for k in ["two way", "two", "balik", "pergi balik"]):
            SESSION_STATE[user].update({"status": "tunggu_borang", "trip_type": "Two Way"})
            return f"Sila lengkapkan borang ini:\n\n{BORANG_TWO_WAY}"
        return "Sila beritahu sama ada anda ingin buat tempahan untuk *One Way* atau *Two Way*."

    # 2. Pilihan Bayaran
    if user in SESSION_STATE and SESSION_STATE[user].get("status") == "tunggu_pilihan_bayar":
        borang_data = SESSION_STATE[user]["borang"]
        del SESSION_STATE[user]
        if any(k in msg for k in ["qr", "qrcode", "duitnow"]):
            hantar(user, "Sila buat bayaran melalui DuitNow QR di bawah:", type="image", image_url=QR_IMAGE_URL)
            if ADMIN: hantar(ADMIN, f"📋 *TEMPAHAN SAH (QR)*\n\n{borang_data}")
            return "Sila hantar resit di sini selepas selesai bayar. Terima kasih! 🙏"
        elif any(k in msg for k in ["online", "banking", "toyyibpay", "bank"]):
            if ADMIN: hantar(ADMIN, f"📋 *TEMPAHAN SAH (Online Banking)*\n\n{borang_data}")
            return f"Sila buat bayaran melalui pautan berikut:\n{TOYYIBPAY_LINK}\n\nSila hantar resit di sini selepas selesai bayar. Terima kasih! 🙏"
        return "Adakah anda ingin buat pembayaran melalui *QR Code* atau *Online Banking*?"

    # 3. Persetujuan Harga
    if user in SESSION_STATE and SESSION_STATE[user].get("status") == "tunggu_persetujuan":
        if any(k in msg for k in ["setuju", "ok", "proceed", "terus", "ya"]):
            SESSION_STATE[user]["status"] = "tunggu_pilihan_bayar"
            return "Adakah anda ingin buat bayaran melalui *QR Code* atau *Online Banking*?"
        del SESSION_STATE[user]
        return f"Tempahan dibatalkan. Sila hubungi pihak sales jika ada sebarang pertanyaan: {SALES_WHATSAPP_LINK}"

    # 4. Semak Borang Wajib Lengkap & Kira Harga Tetap
    if user in SESSION_STATE and SESSION_STATE[user].get("status") == "tunggu_borang":
        status_semakan = semak_borang_lengkap(text)
        if "TIDAK_LENGKAP" in status_semakan:
            trip_jenis = SESSION_STATE[user].get("trip_type", "One Way")
            template_pilihan = BORANG_ONE_WAY if trip_jenis == "One Way" else BORANG_TWO_WAY
            return f"⚠️ Maaf, borang anda kelihatan belum lengkap diisi. Sila lengkapkan semua butiran berikut:\n\n{template_pilihan}"
        
        # Kira harga tetap berasaskan jenis kenderaan
        jumlah_harga, jenis_k = kira_harga_tetap(text)
        SESSION_STATE[user].update({"status": "tunggu_persetujuan", "borang": text})
        return f"💰 *Jumlah Sebut Harga ({jenis_k}):* {jumlah_harga}\n\nAdakah anda bersetuju dengan harga ini? Sila balas *Setuju* untuk meneruskan pembayaran."

    # Default: Mula
    SESSION_STATE[user] = {"status": "tunggu_jenis_trip"}
    return f"Selamat datang ke *{COMPANY}*.\nAdakah anda ingin tempah kenderaan untuk *One Way* (Sehala) atau *Two Way* (Pergi-Balik)?"

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