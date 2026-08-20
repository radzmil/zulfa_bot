import os
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
COMPANY = COMPANY_PROFILE["legal_name"]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SESSION_STATE = {}

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

# --------------------------------------------------
# SENARAI KADAR HARGA ASAS MENGIKUT MUKIM / KAWASAN PICKUP
# --------------------------------------------------
HARGA_ASAS_PICKUP = {
    "bukit raja": 900, "sungai buloh": 900,
    "damansara": 800, "petaling": 800,
    "ampang": 700, "cheras": 700, "ulu langat": 700,
    "beranang": 900,
    "kajang": 800, "semenyih": 800,
    "kapar": 900, "klang": 900,
    "batu": 700, "setapak": 700, "ulu kelang": 700, "rawang": 800,
    "bandar": 1000, "jugra": 1000, "kelanang": 1000, "morib": 1000, "tanjong duabelas": 1000, "telok panglima garang": 1000,
    "api-api": 1200, "batang berjuntai": 1200, "bestari jaya": 1200, "ijok": 1200, "jeram": 1200, "kuala selangor": 1200, "pasangan": 1200, "tanjong karang": 1200, "ujong pematang": 1200, "ulu tinggi": 1200,
    "dengkil": 800, "labu": 800, "sepang": 800,
    "bagan nakhoda omar": 1200, "panchang bedena": 1200, "pasiran panjang": 1200, "sabak": 1200, "sungai panjang": 1200,
    "ampang pecah": 1000, "batang kali": 1000, "buloh telor": 1000, "kalumpang": 1000, "kerling": 1000, "kuala kalumpang": 1000, "peretak": 1000, "rasa": 1000, "serendah": 1000, "sungai gumut": 1000, "sungai tinggi": 1000, "ulu bernam": 1000, "ulu yam": 1000,
    "ampangan": 1200, "lenggeng": 1200, "pantai": 1200, "rantau": 1200, "rasah": 1200, "seremban": 1200, "setul": 1200,
    "jimah": 1200, "linggi": 1200, "port dickson": 1200, "si rusa": 1200,
    "batu kikir": 1400, "chembong": 1400, "gadong": 1400, "kota": 1400, "kundor": 1400, "legong hilir": 1400, "legong hulu": 1400, "mambau": 1400, "nerasau": 1400, "pedas": 1400, "pilin": 1400, "seberang": 1400, "titian bintangor": 1400, "batu hampar": 1400, "gadong hilir": 1400, "rembau bandar": 1400,
    "ampang tinggi": 1400, "johol": 1400, "juasseh": 1400, "kepas": 1400, "kuala pilah": 1400, "langkap": 1400, "seri menanti": 1400, "ulu jempol": 1400, "terachi": 1400, "parit tinggi": 1400,
    "glami lemi": 1400, "hulu klawang": 1400, "klawang": 1400, "pertang": 1400, "peradong": 1400, "kenaboi": 1400, "triang hilir": 1400, "ulu triang": 1400,
    "jelai": 1600, "serting ilir": 1600, "serting hulu": 1600, "palong": 1600,
    "ayer kuning": 1600, "gemencheh": 1600, "gemas": 1600, "kepis": 1600, "ladang": 1600, "tampin tengah": 1600, "tampin": 1600
}

BORANG_MAKLUMAT = (
    "📝 *BORANG MAKLUMAT SEWAAN*\n\n"
    "Tarikh: \n"
    "Masa: \n"
    "Lokasi Ambil: \n"
    "Lokasi Hantar: \n"
    "Jumlah Penumpang: \n\n"
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
        Periksa teks ini. Adakah pelanggan telah mengisi maklumat borang sewaan ini dengan lengkap (Tarikh, Masa, Lokasi Ambil, Lokasi Hantar, Jumlah Penumpang)?
        Jika masih ada ruangan kosong, balas: TIDAK_LENGKAP.
        Jika sudah diisi, balas: LENGKAP.
        
        Teks: "{text_borang}"
        """
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, headers={"Content-Type": "application/json"})
        return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
    except: return "LENGKAP"

def muat_data_harga_fail(nama_fail="harga_bas.txt"):
    senarai_harga = {}
    if os.path.exists(nama_fail):
        with open(nama_fail, "r", encoding="utf-8") as f:
            for baris in f:
                if not baris.strip() or baris.startswith("#"):
                    continue
                data = baris.strip().split("|")
                if len(data) == 3:
                    ambil = data[0].strip().lower()
                    hantar_lokasi = data[1].strip().lower()
                    try:
                        harga = float(data[2].strip())
                        senarai_harga[(ambil, hantar_lokasi)] = harga
                    except ValueError:
                        continue
    return senarai_harga

def kira_harga_bas(lokasi_ambil, lokasi_hantar, jarak_km):
    lokasi_ambil = lokasi_ambil.strip().lower()
    lokasi_hantar = lokasi_hantar.strip().lower()
    
    data_fail = muat_data_harga_fail("harga_bas.txt")
    if (lokasi_ambil, lokasi_hantar) in data_fail:
        harga_tetap = data_fail[(lokasi_ambil, lokasi_hantar)]
        return f"✅ Anggaran Harga Bas (44 Seat): RM {harga_tetap:.2f} (Sumber: Harga Tetap Fail | Pickup: {lokasi_ambil.title()} ke {lokasi_hantar.title()})"

    sah = False
    for daerah, senarai in KAWASAN_PICKUP_DIBENARKAN["selangor"].items():
        if lokasi_ambil in senarai:
            sah = True
            break
    if not sah and lokasi_ambil in KAWASAN_PICKUP_DIBENARKAN["kuala lumpur"]:
        sah = True
    if not sah and lokasi_ambil in KAWASAN_PICKUP_DIBENARKAN["lain_lain"]:
        sah = True
        
    if not sah:
        return "❌ Maaf, kawasan pickup anda adalah TIDAK DIBENARKAN mengikut peraturan ketat syarikat."

    harga_asas = HARGA_ASAS_PICKUP.get(lokasi_ambil, 700)
    
    if jarak_km <= 30:
        jumlah_harga = harga_asas
    else:
        jarak_lebihan = jarak_km - 30
        jumlah_harga = harga_asas + (jarak_lebihan * 12.00)
        
    return f"✅ Anggaran Harga Bas (44 Seat): RM {jumlah_harga:.2f} (Pickup: {lokasi_ambil.title()}, Jarak: {jarak_km}km)"

def proses_mesej(user, text):
    return "Sila hantarkan pertanyaan atau gunakan format tempahan yang disediakan."

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
        hantar(user, proses_mesej(user, body))
    except: pass
    return jsonify({"status": "success"}), 200

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)