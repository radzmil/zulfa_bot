import os
import csv
import requests
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
SALES_LINK = "https://wa.link/o3z1bz"
COMPANY = "SHAHRIL BASRI LEISURE ENTERPRISE"
BANK_NAME = "CIMB Bank / DuitNow QR"
DATA_FILE = "data_pelanggan.csv"

# Function to send messages via WhatsApp API
def hantar(to, msg, type="text", image_url=None):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": type}
    
    if type == "text":
        payload["text"] = {"body": msg}
    elif type == "image":
        payload["image"] = {"link": image_url, "caption": msg}
    
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Error sending message: {e}")

# Function to save customer data
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

# Main Logic
def proses_mesej(user, text):
    msg = text.lower()

    # 1. Initial Greeting / Filtering
    if any(x in msg for x in ["hi", "hello", "sewa", "tanya"]):
        return "Hai awk, blh sy bantu awk cari MPV, SUV, Van atau Bas Super 44 Seat utk disewa hr ni?"
    
    # 2. Filtering Vehicles
    if any(x in msg for x in ["mpv", "suv", "van"]):
        return f"Oh utk kenderaan tu, awk blh terus berhubung dgn team sales sy di sini ya: {SALES_LINK}"
    
    # 3. Bus Booking Process
    if "bas" in msg or "44" in msg:
        return (
            f"Salam/Hai, saya Zulfa dari {COMPANY}.☺️\n"
            "Terima kasih berminat dengan sewaan Bus Super 44 Seat kami.\n\n"
            "➡️Mohon Tuan/Puan isi borang ini untuk memudahkan urusan:\n\n"
            "📝*BORANG MAKLUMAT SEWAAN*\n"
            "Syarikat: \nAlamat: \nNama: \nNo. tel: \nTarikh: \nMasa: \nPick-up: \nDrop-off: \nPax: \n\n"
            "🔄*Maklumat RETURN trip*:\n"
            "Tarikh: \nMasa: \nPick-up: \nDrop-off: \nPax: \n\n"
            "📌*Harga sewaan tertakluk kepada jarak & masa perjalanan.* T.KASIH😊"
        )
        
    # 4. Booking Submission & 2 Payment Options
    if "submit booking" in msg:
        simpan_data(user, text)
        if ADMIN:
            hantar(ADMIN, f"📋 *TEMPAHAN BAS 44 SEAT*\n📱 Rujukan: {user}\n\n{text}")
        
        # Hantar gambar QR jika ada untuk pilihan ke-2
        if QR_IMAGE_URL:
            hantar(user, f"DuitNow QR - {COMPANY}\n(Rujukan: {user})", type="image", image_url=QR_IMAGE_URL)
            
        return (
            f"Terima kasih! Booking anda diterima. Sila pilih kaedah pembayaran anda:\n\n"
            f"1️⃣ *Online Banking (ToyyibPay):*\n"
            f"👉 Klik link ni untuk bayar terus: {TOYYIBPAY_LINK}\n\n"
            f"2️⃣ *Scan DuitNow QR (CIMB):*\n"
            f"👉 Imbas gambar QR di atas dan letak nombor telefon anda (*{user}*) sebagai rujukan.\n\n"
            f"Dah siap bayar, sila balas *'dah bayar'* dan hantar resit di sini ya! 😊"
        )

    # 5. Payment Confirmation
    if "dah bayar" in msg:
        if ADMIN:
            hantar(ADMIN, f"🔔 *SEMAKAN BAYARAN MANUAL (BAS)*\nPelanggan: {user}\nBalas 'done {user}' jika sah.")
        return "Baik awk! Terima kasih. Saya sedang semak dengan admin. Tunggu sebentar ya! 🙏"

    return "Sekejap ya awk, sy tengah semak jadual kejap."

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return request.args.get("hub.challenge"), 200
    
    data = request.get_json()
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        user, body = msg["from"], msg["text"]["body"]
        
        # Admin confirmation
        if ADMIN and user == ADMIN and body.lower().startswith("done"):
            target = body.split()[1]
            hantar(target, "Alhamdulillah! Pembayaran anda telah disahkan. Tempahan sah! 🎉")
        else:
            hantar(user, proses_mesej(user, body))
    except:
        pass
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))