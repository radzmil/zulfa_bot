import os
import csv
import traceback
import requests
from datetime import datetime, timedelta
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
COMPANY = "SHAHRIL BASRI LEISURE ENTERPRISE"
DATA_FILE = "data_pelanggan.csv"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VERIFY_TOKEN_VAL = os.getenv("VERIFY_TOKEN", "sbleisure_secure_token")

# Maklumat Akaun Syarikat (CIMB)
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
    "🔄 *Maklumat untuk RETURN trip :-*\n\n"
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
    
    if type == "text":
        payload["text"] = {"body": msg}
    elif type == "image":
        payload["image"] = {"link": image_url, "caption": msg}
    
    try:
        res = requests.post(url, json=payload, headers=headers)
        print(f"Hantar response status: {res.status_code}, body: {res.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

def simpan_data(no_tel, detail):
    file_exists = os.path.isfile(DATA_FILE)
    try:
        with open(DATA_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["No Telefon", "Detail Tempahan"])
            writer.writerow([no_tel, detail])
    except Exception as e:
        print(f"Error saving data: {e}")

def tanya_gemini(text):
    if not GEMINI_API_KEY:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        prompt = f"""
        Awak adalah Zulfa, staf khidmat pelanggan rasmi untuk syarikat {COMPANY} (Shahril Basri Leisure Enterprise).
        Gaya bahasa awk: Mesra, ramah, guna bahasa Melayu santai (awk, kitorang, tau, etc.).
        Syarikat kita HANYA menyediakan perkhidmatan sewaan MPV, Van, dan Bas Persiaran sahaja.
        PENTING: Jangan sekali-kali bagi sebarang link luar.
        
        Mesej daripada pelanggan: "{text}"
        
        Jika pelanggan bertanya pasal sewa bot, motosikal, lori, atau benda lain yang KITORANG TAK ADA, tolak secara baik dan mesra, beritahu kitorang hanya ada MPV, Van, dan Bas Persiaran. JANGAN HANTAR BORANG.
        
        Jika pelanggan bertanya pasal sewa MPV, Van, Bas, atau kenderaan kitorang, balas dengan mesra.
        """
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        res = requests.post(url, json=payload, headers=headers)
        data = res.json()
        
        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return None
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def proses_mesej(user, text):
    msg = text.lower()

    # Jika pelanggan hantar borang yang telah diisi
    if "borang maklumat sewaan" in msg or "pick-up point" in msg or "drop-off point" in msg or "syarikat :" in msg:
        simpan_data(user, text)
        if ADMIN:
            hantar(ADMIN, f"📋 *BORANG TEMPAHAN BARU*\n📱 Rujukan: {user}\n\n{text}")
        
        if QR_IMAGE_URL:
            hantar(user, f"DuitNow QR - {COMPANY}\nBank: {BANK_INFO['bank']} ({BANK_INFO['no_akaun']})\n(Rujukan: {user})", type="image", image_url=QR_IMAGE_URL)
            
        return (
            f"Terima kasih banyak awk! 😊 Zulfa dah terima borang maklumat sewaan awk tu. "
            f"Admin kitorang akan semak jarak & masa perjalanan secepat mungkin untuk bagi sebut harga rasmi ya.\n\n"
            f"Sambil tu, awk boleh buat bayaran deposit melalui:\n"
            f"1️⃣ *Online Banking (ToyyibPay):*\n👉 {TOYYIBPAY_LINK}\n\n"
            f"2️⃣ *Manual Transfer / DuitNow QR*\n"
            f"• Bank: *{BANK_INFO['bank']}*\n"
            f"• No Akaun: *{BANK_INFO['no_akaun']}*\n"
            f"• Rujukan: No telefon (*{user}*)\n\n"
            f"Dah siap bayar, terus balas *'dah bayar'* kat sini ya! 🙏"
        )

    if "dah bayar" in msg:
        if ADMIN:
            hantar(ADMIN, f"🔔 *SEMAKAN BAYARAN*\nPelanggan: {user}\nBalas 'done {user}' jika sah.")
        return "Baik awk! Terima kasih. Saya sedang semak dengan admin. Tunggu sebentar ya! 🙏"

    # Hanya beri borang jika mesej jelas menyentuh kenderaan yang kitorang ada (mpv, van, bas, sewa, harga, nak sewa)
    kenderaan_sedia_ada = ["mpv", "van", "bas", "bus", "persiaran"]
    ada_kaitan_kenderaan = any(k in msg for k in kenderaan_sedia_ada)
    
    # Jika pelanggan kata "nak sewa" tapi tak sebut bot/moto, atau sebut kenderaan kitorang
    if ada_kaitan_kenderaan or ("nak sewa" in msg and not any(x in msg for x in ["bot", "moto", "motosikal", "lori", "kereta"]));
        return BORANG_TEMPLATE

    # Kalau tanya benda lain (macam sewa bot, dsb), biar AI Gemini handle untuk tolak dengan baik
    jawapan_ai = tanya_gemini(text)
    if jawapan_ai:
        return jawapan_ai

    return "Ada apa-apa lagi yang Zulfa boleh bantu untuk sewaan MPV, Van, atau Bas persiaran kitorang? 😊"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode and token:
            if mode == "subscribe" and token == VERIFY_TOKEN_VAL:
                return challenge, 200
            else:
                return "Verification failed", 403
        return "Hello World", 200

    data = request.get_json()
    print(f"Incoming Webhook Data: {data}")
    try:
        value = data["entry"][0]["changes"][0]["value"]
        if "messages" in value:
            msg = value["messages"][0]
            user, body = msg["from"], msg["text"]["body"]
            
            if ADMIN and user == ADMIN and body.lower().startswith("done"):
                target = body.split()[1]
                hantar(target, "Alhamdulillah! Pembayaran anda telah disahkan. Tempahan sah! 🎉")
            else:
                hantar(user, proses_mesej(user, body))
        else:
            print("Webhook bukan mesej teks. Diabaikan.")
    except Exception as e:
        print(f"WEBHOOK ERROR KRONIK: {e}")
        traceback.print_exc()
        pass
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))