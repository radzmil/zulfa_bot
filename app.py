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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VERIFY_TOKEN_VAL = os.getenv("VERIFY_TOKEN", "sbleisure_secure_token")

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

CUTI_UMUM = [
    "31/08/2026", # Hari Kebangsaan
    "16/09/2026", # Hari Malaysia
    "25/12/2026", # Hari Krismas
]

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

def validasi_tarikh(tarikh_str):
    try:
        t = datetime.strptime(tarikh_str.strip(), "%d/%m/%Y")
        hari_ini = datetime.now().date()
        min_tarikh = hari_ini + timedelta(days=8)
        
        tarikh_semak_str = t.strftime("%d/%m/%Y")

        if t.date() < hari_ini:
            return False, "Tarikh tempahan telah lepas."
        elif t.date() < min_tarikh:
            return False, "Tempahan kurang dari 8 hari (Urgent booking)."
        elif tarikh_semak_str in CUTI_UMUM:
            return False, "Tarikh tersebut adalah Hari Cuti Umum."
        
        return True, t
    except:
        return False, "Format tarikh salah (Guna format DD/MM/YYYY)."

def kira_harga(destinasi, teks_penuh, jarak_km=70):
    dest = destinasi.lower()
    
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

    extra_km_price = 0
    if jarak_km > 50:
        extra_km_price = (jarak_km - 50) * 3

    one_way_total = base_price + extra_km_price

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

def tanya_gemini(text):
    if not GEMINI_API_KEY:
        return None
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        prompt = f"""
        Awak adalah Zulfa, staf khidmat pelanggan rasmi untuk syarikat SBL TRANSPORT (Shahril Basri Leisure Enterprise).
        Gaya bahasa awk: Mesra, ramah, guna bahasa Melayu santai/pasar (awk, kitorang, tau, etc.), sopan, dan prihatin macam manusia betul.
        Syarikat kita khusus menyediakan sewaan BAS 44 SEAT sahaja buat masa ni.
        Kalau pelanggan tanya pasal sewa bas atau harga, jemput mereka isi borang sewaan bas 44 seat.
        Link WhatsApp Sales rasmi kita ialah: {SALES_LINK}
        
        Mesej daripada pelanggan: "{text}"
        
        Jawab mesej pelanggan ini dengan bijak, natural, dan ringkas sebagai Zulfa:
        """
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        res = requests.post(url, json=payload, headers=headers)
        data = res.json()
        
        # Semak selamat sebelum ambil data candidates
        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"Gemini API Response Invalid: {data}")
            return "Hai awk! 😊 Sila isi borang sewaan bas 44 seat untuk semak harga laluan kita, atau ada apa-apa lagi yang Zulfa boleh bantu?"
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def proses_mesej(user, text):
    msg = text.lower()

    if "lokasi ambil:" in msg or "lokasi hantar:" in msg:
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

        lokasi_sah = any(lokasi in msg for lokasi in ALLOWED_PICKUP)
        if not lokasi_sah:
            return f"Alamak, sorry tau awk 🙏 Untuk lokasi pickup kat luar kawasan Selangor, KL & KLIA, sistem kitorang tak sokong.\n\nTapi jangan risau, awk boleh terus berhubung dengan team Sales kitorang untuk bincang lanjut kat sini ya 👇\n\n📲 {SALES_LINK}"

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

        simpan_data(user, text + f" | Harga: RM{harga_akhir}")
        if ADMIN:
            hantar(ADMIN, f"📋 *TEMPAHAN BAS 44 SEAT*\n📱 Rujukan: {user}\n💰 Harga Sistem: RM{harga_akhir}\n\n{text}")
        
        if QR_IMAGE_URL:
            hantar(user, f"DuitNow QR - {COMPANY}\n(Rujukan: {user})", type="image", image_url=QR_IMAGE_URL)
            
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

    if "dah bayar" in msg:
        if ADMIN:
            hantar(ADMIN, f"🔔 *SEMAKAN BAYARAN (BAS)*\nPelanggan: {user}\nBalas 'done {user}' jika sah.")
        return "Baik awk! Terima kasih. Saya sedang semak dengan admin. Tunggu sebentar ya! 🙏"

    jawapan_ai = tanya_gemini(text)
    if jawapan_ai:
        return jawapan_ai

    return "Hai awk! 😊 Sila isi borang sewaan bas 44 seat untuk semak harga laluan kita, atau ada apa-apa lagi yang Zulfa boleh bantu?"

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
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        user, body = msg["from"], msg["text"]["body"]
        
        if ADMIN and user == ADMIN and body.lower().startswith("done"):
            target = body.split()[1]
            hantar(target, "Alhamdulillah! Pembayaran anda telah disahkan. Tempahan sah! 🎉")
        else:
            hantar(user, proses_mesej(user, body))
    except Exception as e:
        print(f"Webhook Error: {e}")
        pass
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))