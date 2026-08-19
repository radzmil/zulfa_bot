import os
import csv
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

# Senarai Cuti Umum (Format DD/MM/YYYY)
CUTI_UMUM = [
    "31/08/2026", # Hari Kebangsaan
    "16/09/2026", # Hari Malaysia
    "25/12/2026", # Hari Krismas
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

# Fungsi Semak Tarikh (Mesti 8 hari ke atas & Bukan Hari Cuti Umum)
def validasi_tarikh(tarikh_str):
    try:
        t = datetime.strptime(tarikh_str.strip(), "%d/%m/%Y")
        hari_ini = datetime.now().date()
        min_tarikh = hari_ini + timedelta(days=8)
        
        tarikh_semak_str = t.strftime("%d/%m/%Y")

        if t.date() < hari_ini:
            return False, "Tarikh tempahan telah lepas (lampau)."
        elif t.date() < min_tarikh:
            return False, "Tempahan kurang dari 8 hari (Urgent booking)."
        elif tarikh_semak_str in CUTI_UMUM:
            return False, "Tarikh tersebut adalah Hari Cuti Umum."
        
        return True, t
    except:
        return False, "Format tarikh salah. Sila guna format DD/MM/YYYY (Contoh: 30/08/2026)."

# Fungsi Pengiraan Harga Automatik (Base Zon + Extra KM)
def kira_harga(destinasi, teks_penuh, jarak_km=70):
    dest = destinasi.lower()
    
    # 1. Tentukan Harga Asas Zon (Asas 50km pertama)
    if any(x in dest for x in ["genting", "bukit tinggi"]):
        base_price = 1000
    elif "bentong" in dest:
        base_price = 1200
    elif any(x in dest for x in ["ipoh", "seremban", "melaka", "port dickson", "temerloh"]):
        base_price = 1300
    elif any(x in dest for x in ["cameron", "kuantan"]):
        base_price = 1500
    elif any(x in dest for x in ["terengganu", "kelantan", "johor", "jb", "kedah", "perlis", "penang"]):
        base_price = 1700
    elif any(x in dest for x in ["kajang", "semenyih", "klia", "hulu selangor"]):
        base_price = 850
    else:
        base_price = 700

    # 2. Kira Kos Tambahan KM (Jika melebihi 50km, caj RM3/km)
    extra_km_price = 0
    if jarak_km > 50:
        extra_km_price = (jarak_km - 50) * 3

    one_way_total = base_price + extra_km_price

    # 3. Semak Trip Sehala atau Pergi Balik
    is_two_way = False
    if "return" in teks_penuh.lower() or "pergi balik" in teks_penuh.lower():
        is_two_way = True

    if is_two_way:
        final_price = one_way_total * 1.5
        trip_label = "Two Way (Pergi Balik)"
    else:
        final_price = one_way_total
        trip_label = "One Way (Sehala)"

    return trip_label, int(final_price)

# Main Logic / Zulfa's Persona & Flow
def proses_mesej(user, text):
    msg = text.lower()

    # 1. Initial Greeting / Filtering Vehicle
    if any(x in msg for x in ["hi", "hello", "sewa", "tanya"]):
        return "Hai, assalammualaikum! 😊\nSy Zulfa dr team SBL TRANSPORT. Tq sbb pm kitorang tau.\n\nBole Zulfa tau, awk nk sewa bas (44 seat), van, atau MPV ya?"
    
    if any(x in msg for x in ["mpv", "suv", "van"]):
        return f"Untuk sewaan van & MPV, kitorang belum buka tempahan online lagi bos 🙏\n\nTapi kalau awk berminat, awk boleh terus berhubung dengan team Sales kitorang untuk bincang lanjut kat sini ya 👇\n\n📲 {SALES_LINK}"
    
    if "tour" in msg or "rombongan" in msg or "jalan" in msg:
        return f"Wah seronoknya nk pegi jalan2! 🚌✨\n\nUtk pakej tour / rombongan pulak, harga ikut itinerary & berapa hari trip awk. Utk dpt harga paling ngam, kawan sy dr bahagian Sales bole tolong kirakan terus tau.\n\nAwk bole klik link ni utk terus sembang dgn team Sales kitorang ya:\n📲 {SALES_LINK}"

    # 2. Berikan Borang Kosong Jika Tanya Harga / Bas
    if "harga" in msg or "ke " in msg or "dr " in msg or "dari " in msg or "bas" in msg or "44" in msg:
        return (
            f"Orite! Utk bas 44 seat ni, tolong isi & lengkapkan borang maklumat bawah ni dulu ya supaya Zulfa bole semak laluan & kirakan harga tepat utk awk 👇\n\n"
            f"📝 *BORANG MAKLUMAT SEWAAN*\n"
            f"Syarikat: \n"
            f"Alamat: \n"
            f"Nama: \n"
            f"No. tel: \n"
            f"Tarikh: \n"
            f"Masa: \n"
            f"Lokasi Ambil: \n"
            f"Lokasi Hantar: \n"
            f"Jumlah Penumpang: \n\n"
            f"🔄 *Maklumat RETURN trip* (Wajib isi jika Two Way / Kosongkan jika One Way):\n"
            f"Tarikh: \n"
            f"Masa: \n"
            f"Pick-up: \n"
            f"Drop-off: \n"
            f"Pax: \n\n"
            f"*(Salin borang di atas, isi butiran anda, dan hantar semula di sini)* 😊"
        )

    # 3. Semakan Borang, Tarikh, Kawasan & Pengiraan Harga Automatik
    if "lokasi ambil:" in msg or "lokasi hantar:" in msg:
        # A. Semak Tarikh
        tarikh_raw = ""
        try:
            for line in text.split("\n"):
                if "tarikh:" in line.lower():
                    val = line.split(":", 1)[1].strip()
                    if val:
                        tarikh_raw = val
                        break
        except:
            pass

        is_valid_date, date_msg = validasi_tarikh(tarikh_raw)
        if not is_valid_date:
            return (
                f"Alamak, maaf sangat tau awk! 🙏 ({date_msg})\n\n"
                f"Untuk tempahan urgent, tarikh cuti umum, atau tempahan kurang dari 8 hari, sistem online tak sokong.\n\n"
                f"Tapi jangan risau, awk boleh terus berhubung dengan team Sales kitorang untuk semak kekosongan bas kat sini ya 👇\n\n"
                f"📲 {SALES_LINK}"
            )

        # B. Semak Kawasan Pickup Dibenarkan
        lokasi_sah = any(lokasi in msg for lokasi in ALLOWED_PICKUP)
        if not lokasi_sah:
            return f"Alamak, sorry tau awk 🙏 Untuk lokasi pickup kat luar kawasan Selangor, KL & KLIA, sistem kitorang tak sokong.\n\nTapi jangan risau, awk boleh terus berhubung dengan team Sales kitorang untuk bincang lanjut kat sini ya 👇\n\n📲 {SALES_LINK}"

        # C. Ekstrak Lokasi Hantar & Kira Harga
        destinasi_hantar = "Kuala Lumpur"
        try:
            for line in text.split("\n"):
                if "lokasi hantar:" in line.lower():
                    val = line.split(":", 1)[1].strip()
                    if val:
                        destinasi_hantar = val
        except:
            pass

        label_trip, harga_akhir = kira_harga(destinasi_hantar, text)

        # D. Simpan Data & Hantar Notifikasi ke Admin
        simpan_data(user, text + f" | Harga: RM{harga_akhir}")
        if ADMIN:
            hantar(ADMIN, f"📋 *TEMPAHAN BAS 44 SEAT*\n📱 Rujukan: {user}\n💰 Harga Sistem: RM{harga_akhir}\n\n{text}")
        
        if QR_IMAGE_URL:
            hantar(user, f"DuitNow QR - {COMPANY}\n(Rujukan: {user})", type="image", image_url=QR_IMAGE_URL)
            
        # E. Respon Sebut Harga & Kaedah Pembayaran
        return (
            f"Zulfa dah semak borang awk! Tarikh sah & laluan dibenarkan. Ni anggaran harga trip awk ya 😊\n\n"
            f"📊 *SEMAKAN SEBUT HARGA*\n"
            f"🗺️ *Destinasi:* {destinasi_hantar}\n"
            f"🛣️ *Jenis Trip:* {label_trip}\n"
            f"💵 *JUMLAH HARGA:* RM {harga_akhir}\n\n"
            f"Sila pilih kaedah pembayaran anda:\n\n"
            f"1️⃣ *Online Banking (ToyyibPay):*\n👉 {TOYYIBPAY_LINK}\n\n"
            f"2️⃣ *Scan DuitNow QR (CIMB)* di atas & letak no fon (*{user}*) sebagai rujukan.\n\n"
            f"Dah siap bayar, sila balas *'dah bayar'* kat sini ya! 🙏"
        )

    # 4. Pengesahan Bayaran Manual
    if "dah bayar" in msg:
        if ADMIN:
            hantar(ADMIN, f"🔔 *SEMAKAN BAYARAN (BAS)*\nPelanggan: {user}\nBalas 'done {user}' jika sah.")
        return "Baik awk! Terima kasih. Saya sedang semak dengan admin. Tunggu sebentar ya! 🙏"

    return "Orite awk, ada apa-apa lagi yang Zulfa boleh bantu untuk sewaan bas kita? 😊"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return request.args.get("hub.challenge"), 200
    
    data = request.get_json()
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        user, body = msg["from"], msg["text"]["body"]
        
        # Admin confirmation shortcut
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