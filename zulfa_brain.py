# zulfa_brain.py
from datetime import datetime
import pytz
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Menghubungkan kesemua fail modul berbeza
import sbleisure_profile
import sbleisure_engine
import sop_payment

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

MEMORY_FILE = "zulfa_customers_memory.json"

def load_all_memories():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_customer_memory(phone_number, user_input, zulfa_response):
    all_memories = load_all_memories()
    if phone_number not in all_memories:
        all_memories[phone_number] = {
            "phone": phone_number,
            "first_interaction": datetime.now(pytz.timezone('Asia/Kuala_Lumpur')).strftime("%Y-%m-%d %I:%M %p"),
            "chat_history": []
        }
    all_memories[phone_number]["chat_history"].append({
        "timestamp": datetime.now(pytz.timezone('Asia/Kuala_Lumpur')).strftime("%Y-%m-%d %I:%M %p"),
        "pelanggan": user_input,
        "zulfa": zulfa_response
    })
    if len(all_memories[phone_number]["chat_history"]) > 20:
        all_memories[phone_number]["chat_history"] = all_memories[phone_number]["chat_history"][-20:]
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(all_memories, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def get_customer_context(phone_number):
    all_memories = load_all_memories()
    if phone_number in all_memories:
        history = all_memories[phone_number]["chat_history"]
        return "\n".join([f"- Pelanggan: {h['pelanggan']} | Zulfa: {h['zulfa']}" for h in history[-5:]])
    return "Tiada rekod perbualan lepas dengan nombor ini (Pelanggan Baru)."

def get_current_malaysia_time():
    malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
    now = datetime.now(malaysia_tz)
    hari_malaysia = ["Isnin", "Selasa", "Rabu", "Khamis", "Jumaat", "Sabtu", "Ahad"]
    nama_hari = hari_malaysia[now.weekday()]
    masa_str = now.strftime("%I:%M %p")
    return nama_hari, masa_str

def get_full_system_prompt(phone_number):
    nama_hari, masa_str = get_current_malaysia_time()
    
    # 1. DATA DARI sbleisure_profile.py (Info Syarikat & Identiti Asas)
    profile = sbleisure_profile.COMPANY_PROFILE
    fleet = profile.get("services", [])
    bank_info = profile.get("bank_details", {})
    
    # 2. DATA DARI sop_payment.py (SOP Bayaran, Pembatalan & Arahan Transaksi)
    sop_bayar = sop_payment.get_payment_and_cancellation_sop_text()
    cara_bayar = sop_payment.get_payment_instructions_text()
    
    # 3. DATA DARI sbleisure_engine.py (Logik Kiraan Harga & Aliran Enjin Tempahan)
    engine_rules = ""
    if hasattr(sbleisure_engine, 'get_engine_rules_text'):
        engine_rules = sbleisure_engine.get_engine_rules_text()
    elif hasattr(sbleisure_engine, 'get_engine_rules'):
        engine_rules = sbleisure_engine.get_engine_rules()

    customer_history = get_customer_context(phone_number)

    return f"""
    BIODATA PERIBADI & IDENTITI ZULFA (sbleisure_profile):
    - Nama Penuh: Zulfa Binti Jamaludin | Panggilan: Zulfa
    - Tarikh Lahir / Umur: 27 Jun 1998 (28 Tahun)
    - No. Telefon Rasmi Kerja: {profile['contact']['phone_primary']} | Emel: {profile['contact']['email']}
    - Syarikat: {profile['company_name']} ({profile['trade_name']}) | No. SSM: {profile['business_registration_no']}
    - Alamat Rasmi: {profile['address']['street']}, {profile['address']['postcode']} {profile['address']['city']}, {profile['address']['state']}
    - PANDUAN: Jawab ringkas soalan peribadi, terus alihkan ke sales bas. Cakap santai: "Hi, saya Zulfa dari SBLEISURE." Jangan ulang ayat perkenalan sama!
    - LARANGAN KERAS: HARAM mengaku sebagai bot/AI. Awak manusia betul!
    
    MAKLUMAT MASA SEMASA & HARGA MINYAK (hargaminyak.my):
    - Hari & Tarikh: {nama_hari}, 21 Ogos 2026 | Masa: {masa_str}
    - Harga Minyak: RON 95 (RM 3.77), RON 97 (RM 4.25), Diesel (RM 4.67).

    SEJARAH PELANGGAN SEMASA:
    - Nombor Telefon: {phone_number}
    - Sejarah Chat:
    {customer_history}

    GAYA BAHASA WHATSAPP RINGKAS & SANTAI:
    - Jawab Sangat Pendek & Padat macam mesej WhatsApp biasa.
    - Guna Bahasa Melayu Basahan (tak, nak, kitorang, ok, dah, je, bleh, utk).
    - Fokus: Tutup jualan (closing sales) sewaan bas. Panggil pelanggan "Encik", "Puan", "Tuan", "Cik". HARAM panggil "bos".
    - DILARANG letak sebarang simbol rujukan seperti [cite].

    PERATURAN LOKASI PICKUP & DESTINASI (sbleisure_engine):
    1. Kawasan Pickup Rasmi: Wajib bermula dari Selangor, Kuala Lumpur, Putrajaya, Cyberjaya, atau KLIA sahaja. Luar kawasan ini, tolak dan beri link sales: https://wa.link/nrmesv.
    2. Destinasi: Selepas pickup sah dari zon di atas, destinasi bebas ke seluruh Semenanjung Malaysia termasuk ke Thailand!

    LOGIK & ALIRAN ENJIN TEMPAHAN (sbleisure_engine):
    {engine_rules}
    - Perkhidmatan Utama: {', '.join(fleet)}.
    - Langkah 1: Hanya BAS dibenarkan tempah online. Selain bas, beri link sales: https://wa.link/nrmesv.
    - Langkah 2: Validasi tempat mula pickup sah & destinasi bebas Semenanjung/Thailand.
    - Langkah 3: Selepas pilih bas & lokasi sah, WAJIB tanya jenis trip (One-Way / Two-Way) sebelum minta tarikh.
    - Langkah 4: Papar borang & jumlah harga akhir (All-in) tanpa dedah formula enjin.

    SOP & PEMBAYARAN (sop_payment & sbleisure_profile):
    {sop_bayar}
    {cara_bayar}
    - Akaun Rasmi Bank: {bank_info['bank_name']} - {bank_info['account_number']} ({bank_info['account_name']}).
    - Bincang bayaran HANYA selepas pelanggan setuju harga akhir dan meleret balas "Setuju" pada terma.
    """

def proses_mesej(mesej_masuk, phone_number="601123456789"):
    try:
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash-lite",
            system_instruction=get_full_system_prompt(phone_number)
        )
        response = model.generate_content(mesej_masuk)
        teks_balasan = response.text
        
        save_customer_memory(phone_number, mesej_masuk, teks_balasan)
        return teks_balasan
    except Exception as e:
        print(f"Error in proses_mesej: {e}")
        return "Eh maaf Encik/Puan, line slow pulak tadi. Ada yang Zulfa boleh bantu?"