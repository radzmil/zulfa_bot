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
TOYYIBPAY_LINK = os.getenv("TOYYIB_PAY_LINK", "https://toyyibpay.com/link-pembayaran-anda")
SALES_WHATSAPP_LINK = os.getenv("SALES_WHATSAPP_LINK", "https://wa.link/o3z1bz")
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
    url = f"https://graph.facebook.com/v20.0/{PHONE_ID}/messages"
    payload = {"messaging_product": "whatsapp", "to": to, "type": type}
    if type == "text": payload["text"] = {"body": msg}
    elif type == "image": payload["image"] = {"link": image_url, "caption": msg}
    requests.post(url, json=payload, headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})

def tanya_ai_seperti_manusia(user, text):
    if not GEMINI_API_KEY:
        return "Hai! Maaf ya, sistem tengah ada hal sikit. Ada apa yang boleh saya bantu untuk urusan sewaan bas atau kenderaan hari ni?"
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
        
        # Arahan ketat agar AI bercakap betul-betul seperti manusia sebenar (natural, mesra, bahasa Malaysia santai)
        system_instruction = (
            "Anda adalah manusia sebenar yang bertindak sebagai pegawai khidmat pelanggan bagi syarikat "
            "SB Leisure Transportation (Shahril Basri Leisure Enterprise). "
            "PENTING: Jangan sekali-kali bercakap macam robot, jangan guna skrip meleret-leret yang kaku. "
            "Gunakan gaya bahasa Melayu harian yang santai, mesra, ramah (friendly), kadang-kadang boleh guna singkatan "
            "yang biasa rakyat Malaysia pakai (contoh: 'ok', 'boleh', 'takpe', 'tau') tapi tetap sopan dan profesional. "
            "Syarikat kita sediakan perkhidmatan sewaan bas persiaran, van, MPV (Vellfire/Innova), dan lori logistik "
            "untuk seluruh Semenanjung Malaysia, Singapura, dan Thailand. "
            "Tugas anda adalah bersembang dan melayan pelanggan macam kawan atau staf kaunter yang mesra. "
            "Kalau pelanggan tanya harga atau lokasi, jawab terus terang dengan bijak dan tanya details yang perlu (macam tarikh, tempat ambil, dsb) secara santai."
        )
        
        # Ambil sejarah perbualan lepas pelanggan ni kalau ada (supaya AI ingat konteks)
        all_data = muat_data_customer()
        chat_history = []
        if user in all_data and "history" in all_data[user]:
            # Ambil 5 mesej terakhir untuk jimatkan token dan kekalkan konteks
            chat_history = all_data[user]["history"][-5:]

        contents = [{"parts": [{"text": system_instruction}]}]
        
        # Masukkan sejarah perbualan supaya AI betul-betul kenal pelanggan ni
        for h in chat_history:
            role_text = "Pelanggan" if h["sender"] == "customer" else "Anda"
            contents.append({"parts": [{"text": f"{role_text}: {h['message']}"}]})
            
        contents.append({"parts": [{"text": f"Pelanggan terkini berkata: {text}"}]})

        payload = {"contents": contents}
        
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        response_data = res.json()
        return response_data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        return "Eh, line internet saya macam terputus sekejap tadi. Boleh ulang semula tak soalan awak?"

def proses_mesej(user, text):
    # Simpan mesej masuk pelanggan
    simpan_info_pelanggan(user, {"sender": "customer", "message": text})
    
    # Dapatkan jawapan manusia jadi-jadian daripada AI
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
        
        balasan = proses_mesej(user, body)
        hantar(user, balasan)
    except Exception as e:
        pass
    return jsonify({"status": "success"}), 200

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)