import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --------------------------------------------------
# MAKLUMAT KORPORAT & PASUKAN (SHAHRILL BASRI LEISURE ENTERPRISE)
# --------------------------------------------------
COMPANY_PROFILE = {
    "commercial_name": "SB LEiSURE TRANSPORTATION",
    "legal_name": "Shahril Basri Leisure Enterprise",
    "registration_no": "202203168334 (003413019-W)",
    "ssm_expiry": "Sah sehingga 28 Ogos 2028",
    "slogan": "Your Destination, Our Priority!",
    "address": "No. 8-1, 9-1, First Floor, Laman Niaga@Ampang Waterfront, Jalan AWF 3A, Ampang Waterfront, 68000 Ampang, Selangor",
    "operating_hours": "24 Jam / 7 Hari Seminggu",
    "email": "sbltransport.my@gmail.com",
    "social_media": "@sbleisure.my",
    "linktree": "https://linktr.ee/SBLeisure.my",
    "contacts": [
        "+60 16-260 1885",
        "+60 13-243 4200",
        "+60 12-392 1885"
    ]
}

GOV_AND_FINANCE = {
    "mof_certificate_no": "K98267180554388213",
    "mof_validity": "27/03/2026 – 26/03/2029",
    "bank": "CIMB Bank Berhad",
    "account_no": "860 5247 780",
    "swift_code": "CIBBMYKLXXX"
}

MANAGEMENT = {
    "director": "Puan Asiah binti Abdul Rahman",
    "operations_manager": "Encik Mohd Shahril bin Noor Basri",
    "assistant_operations_manager": "Shamsul",
    "hr_admin_executive": "Sidek",
    "customer_service_officer": {
        "full_name": "Zulfa Jamaludin",
        "nickname": "Zulfa",
        "birth_year": 1988,
        "birth_state": "Perak",
        "current_location": "Ampang",
        "position": "Pegawai Khidmat Pelanggan",
        "facebook_profile": "https://www.facebook.com/profile.php?id=61592928645216"
    }
}

SERVICES = {
    "mof_codes": [
        {"code": "110103", "description": "Pengangkutan, komponen dan aksesori kenderaan bermotor dan tidak bermotor/kereta"},
        {"code": "110104", "description": "Pengangkutan, komponen dan aksesori kenderaan bermotor dan tidak bermotor/lori"},
        {"code": "110105", "description": "Pengangkutan, komponen dan aksesori kenderaan bermotor dan tidak bermotor/bas"},
        {"code": "110203", "description": "Pengangkutan, komponen dan aksesori jentera berat trailler dan aksesori"},
        {"code": "221503", "description": "Perkhidmatan/penyewaan dan pengurusan/kenderaan/jentera/kenderaan rekreasi"}
    ],
    "fleet_types": ["Bas Persiaran", "Van", "MPV (Toyota Vellfire, Innova)", "Lori Logistik & Van Bagasi"],
    "operations_scope": [
        "Percutian & Rombongan Keluarga", "Lawatan Individu atau Berkumpulan",
        "Lawatan Sekolah, Kolej & Universiti", "Lawatan Syarikat, Seminar & Kursus",
        "Program Organisasi Kerajaan & Swasta", "Airport Transfer (KLIA & KLIA2)",
        "Perjalanan Merentas Sempadan (Singapura & Thailand)", "Perkhidmatan Pemandu Pelancong (Tour Guide)"
    ]
}

# --------------------------------------------------
# KONFIGURASI WHATSAPP & BOT
# --------------------------------------------------
TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
ADMIN = os.getenv("GROUP_ADMIN_NUMBER")
QR_IMAGE_URL = os.getenv("QR_IMAGE_URL", "")
TOYYIBPAY_LINK = os.getenv("TOYYIBPAY_LINK", "https://toyyibpay.com/link-pembayaran-anda")
SALES_WHATSAPP_LINK = os.getenv("SALES_WHATSAPP_LINK", "https://wa.link/o3z1bz")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Storan sesi dan data pelanggan mengikut nombor unik
SESSION_STATE = {}
DATA_CUSTOMER_FILE = "data_customers.json"

def muat_data_customer():
    if os.path.exists(DATA_CUSTOMER_FILE):
        try:
            with open(DATA_CUSTOMER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def simpan_data_customer(data):
    with open(DATA_CUSTOMER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def simpan_info_pelanggan(user, mesej_baru):
    all_data = muat_data_customer()
    if user not in all_data:
        all_data[user] = {"history": [], "details": {}}
    
    all_data[user]["history"].append(mesej_baru)
    simpan_data_customer(all_data)

# --------------------------------------------------
# SENARAI KAWASAN PICKUP YANG DIBENARKAN (GATEKEEPING)
# --------------------------------------------------
KAWASAN_PICKUP_DIBENARKAN = {
    "selangor": {
        "petaling": ["bukit raja", "damansara", "petaling", "sungai buloh"],
        "hulu langat": ["ampang", "beranang", "cheras", "hulu langat", "kajang", "semenyih"],
        "klang": ["kapar", "klang"],
        "gombak": ["ampang", "batu", "rawang", "setapak", "ulu kelang"],
        "kuala langat": ["bandar", "batu", "jugra", "kelanang", "morib", "tanjong duabelas", "telok panglima garang"],
        "kuala selangor": ["api-api", "batang berjuntai", "bestari jaya", "ijok", "jeram", "kuala selangor", "pasangan", "tanjong karang", "ujong pematang", "ulu tinggi"],
        "sepang": ["dengkil", "labu", "sepang"],
        "sabak bernam": ["bagan nakhoda omar", "panchang bedena", "pasiran panjang", "sabak", "sungai panjang"],
        "hulu selangor": ["ampang pecah", "batang kali", "buloh telor", "kalumpang", "kerling", "kuala kalumpang", "peretak", "rasa", "serendah", "sungai gumut", "sungai tinggi", "ulu bernam", "ulu yam"]
    },
    "kuala lumpur": [
        "kuala lumpur", "batu", "setapak", "ampang", "ulu kelang"
    ],
    "lain_lain": ["klia", "cyberjaya", "putrajaya"]
}

HARGA_ASAS_PICKUP = {
    "bukit raja": 900, "sungai buloh": 900, "damansara": 800, "petaling": 800,
    "ampang": 700, "cheras": 700, "ulu langat": 700, "beranang": 900,
    "kajang": 800, "semenyih": 800, "kapar": 900, "klang": 900,
    "batu": 700, "setapak": 700, "ulu kelang": 700, "rawang": 800,
    "dengkil": 800, "labu": 800, "sepang": 800
}

def hantar(to, msg, type="text", image_url=None):
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    payload = {"messaging_product": "whatsapp", "to": to, "type": type}
    if type == "text": payload["text"] = {"body": msg}
    elif type == "image": payload["image"] = {"link": image_url, "caption": msg}
    requests.post(url, json=payload, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})

def tanya_ai_seperti_manusia(user, text):
    if not GEMINI_API_KEY:
        return f"Hai, terima kasih kerana menghubungi {COMPANY_PROFILE['commercial_name']}[cite: 1, 2]. Ada apa yang boleh kami bantu hari ini?"
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        
        system_instruction = (
            f"Anda adalah pembantu khidmat pelanggan rasmi bagi syarikat {COMPANY_PROFILE['commercial_name']} "
            f"({COMPANY_PROFILE['legal_name']})[cite: 1, 2]. Gaya bahasa anda ramah, profesional, bertutur mesra seperti manusia biasa (friendly), "
            f"menggunakan bahasa Melayu harian yang santai tetapi sopan. Syarikat menyediakan perkhidmatan sewaan bas persiaran, "
            f"van, MPV (Vellfire, Innova), dan lori logistik untuk seluruh Semenanjung Malaysia, Singapura, dan Thailand[cite: 1, 2]. "
            f"Jawab pertanyaan pelanggan dengan membantu, memberikan maklumat tepat berdasarkan profil syarikat, dan sentiasa galakkan mereka untuk berurusan."
        )
        
        payload = {
            "contents": [
                {"parts": [{"text": system_instruction}, {"text": f"Pelanggan berkata: {text}"}]}
            ]
        }
        
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        response_data = res.json()
        return response_data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        return f"Maaf, sistem sedang sibuk sebentar. Sila ajukan pertanyaan anda kepada wakil jualan kami di {COMPANY_PROFILE['contacts'][0]}."

def proses_mesej(user, text):
    # Simpan mesej masuk pelanggan ke dalam fail data berasingan mengikut nombor unik
    simpan_info_pelanggan(user, {"sender": "customer", "message": text})
    
    # Gunakan AI untuk respons seperti manusia
    balasan_ai = tanya_ai_seperti_manusia(user, text)
    
    # Simpan respons bot
    simpan_info_pelanggan(user, {"sender": "bot", "message": balasan_ai})
    
    return balasan_ai

@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": f"Selamat datang ke sistem API {COMPANY_PROFILE['commercial_name']}",
        "company": COMPANY_PROFILE,
        "finance": GOV_AND_FINANCE,
        "management": MANAGEMENT,
        "services": SERVICES
    })

@app.route("/api/company")
def get_company_info():
    return jsonify(COMPANY_PROFILE)

@app.route("/api/services")
def get_services():
    return jsonify(SERVICES)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET": return request.args.get("hub.challenge")
    data = request.get_json()
    try:
        user = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        body = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        
        # Proses mesej secara unik untuk setiap pelanggan & hantar respons
        balasan = proses_mesej(user, body)
        hantar(user, balasan)
    except Exception as e:
        pass
    return jsonify({"status": "success"}), 200

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)