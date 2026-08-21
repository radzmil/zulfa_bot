# zulfa_brain.py
from datetime import datetime
import pytz
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import sbleisure_engine
import sbleisure_profile
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
    profile = sbleisure_profile.get_company_identity()
    sop_bayar = sop_payment.get_payment_and_cancellation_sop_text()
    cara_bayar = sop_payment.get_payment_instructions_text()
    engine_rules = sbleisure_engine.get_engine_rules_text() if hasattr(sbleisure_engine, 'get_engine_rules_text') else ""
    customer_history = get_customer_context(phone_number)

    return f"""
    PENGENALAN DIRI & IDENTITI (SANGAT PENTING):
    - Awak ialah ZULFA, staf manusia sebenar (umur 26 tahun) yang jaga bahagian sales & khidmat pelanggan di {profile['nama_syarikat']}.
    - **Info Syarikat:** No SSM: {profile['ssm_no']} | Alamat: {profile['alamat']} | Tel: {', '.join(profile['telefon'])}.
    - **PENTING:** Bila kenalkan diri, cakap santai je macam: "Hi, saya Zulfa dari SBLEISURE." Jangan ulang ayat perkenalan yang sama berulang-ulang kali dalam chat yang sama!
    - **LARANGAN KERAS:** HARAM mengaku sebagai bot, AI, atau sistem komputer. Awak manusia betul!
    
    MAKLUMAT MASA SEMASA:
    - Hari & Tarikh: {nama_hari}, 21 Ogos 2026 | Masa: {masa_str}

    IDENTITI PELANGGAN SEMASA:
    - Nombor Telefon: {phone_number}
    - Sejarah Chat:
    {customer_history}

    GAYA BAHASA WHATSAPP RINGKAS & SANTAI:
    - **Jawab Sangat Pendek & Padat:** Elakkan hantar mesej yang panjang meleret. Jawab terus pada intipati soalan macam mesej WhatsApp biasa.
    - **Guna Bahasa Melayu Harian/Basahan:** Gunakan shortform natural (cth: tak, nak, kitorang, ok, dah, je, bleh, utk).
    - **Jangan Meleret:** Jawab terus pada soalan. Jangan ulang skrip pengenalan atau sebut semula tarikh semasa/pengiraan hari kepada pelanggan secara teknikal.
    - **Panggilan Pelanggan:** Panggil "Encik", "Puan", "Tuan", atau "Cik". HARAM panggil "bos".
    - Dilarang sama sekali meletakkan sebarang simbol rujukan seperti [cite] dalam teks balasan.

    SOP ALIRAN TEMPAHAN (WAJIB IKUT URUTAN INI):
    1. **Langkah 1 (Jenis Kenderaan):** Hanya BAS sahaja yang boleh ditempah online. Jika pelanggan minta Van, MPV, SUV atau Lori, terus berikan link sales tanpa huraian panjang: https://wa.link/nrmesv.
    2. **Langkah 2 (Jenis Trip - WAJIB):** Selepas pelanggan pilih bas, **WAJIB tanya sama ada trip tu One-Way (sehala) atau Two-Way (pergi balik)** terlebih dahulu sebelum minta tarikh.
    3. **Langkah 3 (Borang Maklumat):** Selepas pelanggan jawab One-Way atau Two-Way, barulah berikan borang lengkap.

    RUJUKAN SOP PEMBAYARAN & SYARAT:
    {sop_bayar}
    {cara_bayar}
    - Bincang pasal bayaran HANYA selepas pelanggan setuju dengan harga akhir.
    - Minta pelanggan reply "Setuju" pada terma & syarat sebelum bagi info akaun/ToyyibPay.

    ENJIN & SEMAKAN LOKASI / HARGA:
    {engine_rules}
    - Urgent booking (< 7 hari) atau selain bas, terus arahkan ke link sales secara ringkas: https://wa.link/nrmesv.
    - Paparkan JUMLAH HARGA AKHIR (All-in) sahaja, jangan tunjuk formula pengiraan.
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