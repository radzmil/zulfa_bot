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
DATA_FILE = "data_pelanggan.csv"

# Senarai Mukim Pickup Dibenarkan (Selangor & KL)
ALLOWED_PICKUP = [
    "bukit raja", "damansara", "petaling", "sungai buloh",
    "ampang", "beranang", "cheras", "hulu langat", "kajang", "semenyih",
    "kapar", "klang", "batu", "rawang", "setapak", "ulu kelang",
    "bandar", "jugra", "kelanang", "morib", "tanjong duabelas", "telok panglima garang",
    "api-api", "bestari jaya", "batang berjuntai", "ijok", "jeram", "kuala selangor", "pasangan", "tanjong karang", "ujong permatang", "ulu tinggi",
    "dengkil", "labu", "sepang", "bagan nakhoda omar", "panchang bedena", "pasiran panjang", "sabak", "sungai panjang",
    "ampang pecah", "batang kali", "buloh telor", "kalumpang", "kerling", "kuala kalumpang", "peretak", "rasa", "serendah", "sungai gumut", "sungai tinggi", "ulu bernam", "ulu yam",
    "kuala lumpur", "bukit bintang", "chow kit", "brickfields", "bangsar", "seputeh",
    "kepong", "segambut", "sentul", "jalan ipoh", "mont kiara", "sri hartamas", "batu caves",
    "wangsa maju", "danau kota", "taman melati", "semarak", "kampung pandan", "desa pandan", "maluri",
    "klia", "cyberjaya", "putrajaya"
]

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

# Fungsi Pengiraan Harga Automatik Bas 44 Seat
def kira_harga(destinasi, jenis_trip, jarak_km=50):
    dest = destinasi.lower()
    base_price = 700  # Default Zon 1A

    # Tentukan Zon Harga Asas 50km Pertama
    if any(x in dest for x in ["genting", "bukit tinggi"]):
        base_price = 1000
    elif "bentong" in dest:
        base_price = 1200
    elif any(x in dest for x in ["ipoh", "seremban", "melaka", "port dickson"]):
        base_price = 1300
    elif any(x in dest for x in ["cameron", "kuantan"]):
        base_price = 1500
    elif any(x in dest for x in ["terengganu", "kelantan", "johor", "jb", "kedah", "perlis", "penang", "pulau pinang"]):
        base_price = 1700
    elif any(x in dest for x in ["kajang", "semenyih", "klia", "hulu selangor"]):
        base_price = 850
    else:
        base_price = 700 # Zon 1A (KL & Selangor berdekatan)

    # Tambahan jika lebih 50km (RM3/km)
    extra_km_price = 0
    if jarak_km > 50:
        extra_km_price = (jarak_km - 50) * 3

    one_way_total = base_price + extra_km_price

    # Formula Two Way (Pergi Balik)
    if "two way" in jenis_trip or "pergi balik" in jenis_trip:
        if "hari lain" in jenis_trip or "esok" in jenis_trip:
            final_price = one_way_total * 2.0  # Hari lain (+100%)
        else:
            final_price = one_way_total * 1.5  # Hari sama (+50%)
        trip_label = "Two Way (Pergi Balik)"
    else:
        final_price = one_way_total
        trip_label = "One Way (Sehala)"

    return trip_label, jarak_km, int(final_price)

# Main Logic / Zulfa's Persona & Flow
def proses_mesej(user, text):
    msg = text.lower()

    # 1. Initial Greeting / Filtering Vehicle
    if any(x in msg for x in ["hi", "hello", "sewa", "tanya"]):
        return "Hai, assalammualaikum! 😊\nSy Zulfa dr team SBL TRANSPORT. Tq sbb pm kitorang tau.\n\nBole Zulfa tau, awk nk sewa bas (44 seat), van, atau MPV ya?"
    
    # Filtering Van & MPV
    if any(x in msg for x in ["mpv", "suv", "van"]):
        return f"Untuk sewaan van & MPV, kitorang belum buka tempahan online lagi bos 🙏\n\nTapi kalau awk berminat, awk boleh terus berhubung dengan team Sales kitorang untuk bincang lanjut kat sini ya 👇\n\n📲 {SALES_LINK}"
    
    # Tour / Rombongan
    if "tour" in msg or "rombongan" in msg or "jalan" in msg:
        return f"Wah seronoknya nk pegi jalan2! 🚌✨\n\nUtk pakej tour / rombongan pulak, harga ikut itinerary & berapa hari trip awk. Utk dpt harga paling ngam, kawan sy dr bahagian Sales bole tolong kirakan terus tau.\n\nAwk bole klik link ni utk terus sembang dgn team Sales kitorang ya:\n📲 {SALES_LINK}"

    # 2. Bus Booking Process Started
    if "bas" in msg or "44" in msg:
        return "Orite! Utk bas 44 seat ni, awk nk sewa utk trip sehala (one way), pergi balik (two way), atau nk buat trip jalan2 / rombongan (tour)?"

    # Trip Type Selection Responses
    if "one way" in msg or "sehala" in msg:
        return "Okey set! Agak2 jam berapa ya perancangan nk bertolak / pickup nanti? 😊"
    
    if "two way" in msg or "pergi balik" in msg:
        return "Okey set! Utk trip pergi balik (two way) tu, awk nk balik pada hari yg sama atau hari lain / esoknya? 😊"

    # Gatekeeping & Validation for Submission / Harga Calculation
    if "submit booking" in msg or "tarikh:" in msg:
        # Semak kawasan pickup
        lokasi_sah = any(lokasi in msg for lokasi in ALLOWED_PICKUP)
        if not lokasi_sah and "lokasi ambil:" in msg:
            return f"Alamak, sorry tau awk 🙏 Untuk lokasi pickup kat luar kawasan Selangor, KL & KLIA, sistem kitorang tak sokong.\n\nTapi jangan risau, awk boleh terus berhubung dengan team Sales kitorang untuk bincang lanjut kat sini ya 👇\n\n📲 {SALES_LINK}"

        # Simulasi ekstrak destinasi (Lokasi Hantar) dan Jenis Trip dari mesej borang pelanggan
        destinasi_hantar = "Kuala Lumpur" # Default fallback
        if "lokasi hantar:" in msg:
            parts = msg.split("lokasi hantar:")
            if len(parts) > 1:
                destinasi_hantar = parts[1].split("\n")[0].strip()

        jenis_trip_dipilih = "One Way"
        if "two way" in msg or "pergi balik" in msg:
            jenis_trip_dipilih = "Two Way"

        # Kira harga automatik
        label_trip, km, harga_akhir = kira_harga(destinasi_hantar, jenis_trip_dipilih, 50)

        # Simpan data pelanggan & hantar notifikasi ke Admin
        simpan_data(user, text + f" | Harga: RM{harga_akhir}")
        if ADMIN:
            hantar(ADMIN, f"📋 *TEMPAHAN BAS 44 SEAT*\n📱 Rujukan: {user}\n💰 Anggaran Harga: RM{harga_akhir}\n\n{text}")
        
        # Hantar QR Code jika ada
        if QR_IMAGE_URL:
            hantar(user, f"DuitNow QR - {COMPANY}\n(Rujukan: {user})", type="image", image_url=QR_IMAGE_URL)
            
        # Paparan Sebut Harga Akhir & Pilihan Pembayaran
        return (
            f"Tq bagi maklumat lengkap! Ni anggaran harga utk trip awk ya 😊\n\n"
            f"📊 *ANGGARAN HARGA ({label_trip})*\n"
            f"🗺️ *Destinasi:* {destinasi_hantar}\n"
            f"💵 *JUMLAH HARGA:* RM {harga_akhir}\n\n"
            f"Sila pilih kaedah pembayaran anda:\n\n"
            f"1️⃣ *Online Banking (ToyyibPay):*\n"
            f"👉 Klik link ni untuk bayar terus: {TOYYIBPAY_LINK}\n\n"
            f"2️⃣ *Scan DuitNow QR (CIMB):*\n"
            f"👉 Imbas gambar QR di atas dan letak nombor telefon anda (*{user}*) sebagai rujukan.\n\n"
            f"Dah siap bayar, sila balas *'dah bayar'* dan hantar resit di sini ya! 😊"
        )

    # 3. Payment Confirmation
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