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
# SOP KAWASAN PICKUP & HARGA ASAS BAS
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
    "kuala lumpur": ["kuala lumpur", "batu", "setapak", "ampang", "ulu kelang"],
    "lain_lain": ["klia", "cyberjaya", "putrajaya"]
}

HARGA_ASAS_PICKUP = {
    "bukit raja": 900, "sungai buloh": 900, "damansara": 800, "petaling": 800,
    "ampang": 700, "cheras": 700, "ulu langat": 700, "beranang": 900,
    "kajang": 800, "semenyih": 800, "kapar": 900, "klang": 900,
    "batu": 700, "setapak": 700, "ulu kelang": 700, "rawang": 800,
    "dengkil": 800, "labu": 800, "sepang": 800
}

# --------------------------------------------------
# KONFIGURASI WHATSAPP & BOT
# --------------------------------------------------
TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
ADMIN = os.getenv("GROUP_ADMIN_NUMBER")
QR_IMAGE_URL = os.getenv("QR_IMAGE_URL", "")
TOYYIBPAY_LINK = os.getenv("TOYYIBPAY_LINK", "https://toyyibpay.com/link-pembayaran-anda")
SALES_WHATSAPP_LINK = "https://wa.link/nrmesv"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

def hantar(to, msg, type="text", image_url=None):
    if not TOKEN or not PHONE_ID:
        return
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    payload = {"messaging_product": "whatsapp", "to": to, "type": type}
    if type == "text": payload["text"] = {"body": msg}
    elif type == "image": payload["image"] = {"link": image_url, "caption": msg}
    try:
        requests.post(url, json=payload, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}, timeout=10)
    except Exception:
        pass

def tanya_ai_seperti_manusia(user, text):
    if not GEMINI_API_KEY:
        return "Hai! Ada apa yang boleh Zulfa bantu untuk sewaan bas?"
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        
        system_instruction = (
            f"Anda adalah Zulfa, pegawai khidmat pelanggan SB Leisure Transportation. "
            f"Sesi perbualan ini adalah KHUSUS untuk pelanggan dengan nombor ID/telefon: {user}. "
            "Jangan pernah mencampuradukkan ingatan atau perbualan pelanggan ini dengan nombor telefon atau pelanggan lain. "
            "PERWATAKAN & GAYA BAHASA: "
            "1. Bahasa Melayu Malaysia yang santai, mesra, ramah, dan profesional. "
            "2. Jawab secara PENDEK, RINGKAS, PADAT, dan terus kepada poin gaya WhatsApp (maksimum 1-2 ayat pendek). "
            "SKOP TUGAS & SOP BORANG: "
            "1. Zulfa HANYA uruskan SEWAAN BAS sahaja. Jika pelanggan nak sewa Van, MPV, atau Lori, arahkan ke link sales: https://wa.link/nrmesv. "
            "2. SEGERA SELEPAS pelanggan bertanya tentang sewaan bas atau harga perjalanan (cth: dari Ampang ke Port Dickson), "
            "selain menjawab ringkas, anda WAJIB terus berikan borang tempahan ringkas untuk mereka isi mengikut format berikut:\n\n"
            "📋 **BORANG TEMPAHAN BAS**\n"
            "• Jenis Perjalanan: [One Way / Two Way]\n"
            "• Tempat Pickup:\n"
            "• Destinasi:\n"
            "• Tarikh & Masa Pergi:\n"
            "• Tarikh & Masa Pulang (Jika Two Way):\n"
            "• Bilangan Penumpang:\n\n"
            "3. Kawalan Perbualan (Guardrail): Jika pelanggan melalut, tegur secara lembut dan sopan."
        )
        
        all_data = muat_data_customer()
        chat_history = []
        if user in all_data and "history" in all_data[user]:
            chat_history = all_data[user]["history"][-4:]

        contents = [{"parts": [{"text": system_instruction}]}]
        for h in chat_history:
            role_text = "Pelanggan" if h["sender"] == "customer" else "Anda"
            contents.append({"parts": [{"text": f"{role_text}: {h['message']}"}]})
            
        contents.append({"parts": [{"text": f"Pelanggan terkini berkata: {text}"}]})

        payload = {"contents": contents}
        
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        response_data = res.json()
        return response_data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        return "Maaf ya, line internet Zulfa sekejap tadi tersangkut. Boleh ulang semula?"

def proses_mesej(user, text):
    simpan_info_pelanggan(user, {"sender": "customer", "message": text})
    balasan_ai = tanya_ai_seperti_manusia(user, text)
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
    if request.method == "GET": return request.args.get("hub.challenge", "")
    data = request.get_json()
    try:
        user = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        body = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
        
        balasan = proses_mesej(user, body)
        hantar(user, balasan)
    except Exception as e:
        pass
    return jsonify({"status": "success"}), 200

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=False)