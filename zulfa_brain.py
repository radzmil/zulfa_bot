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
    BIODATA PERIBADI & IDENTITI ZULFA (RUJUKAN DALAMAN / BERHATI-HATI):
    - Nama Penuh: Zulfa Binti Jamaludin
    - Nama Panggilan: Zulfa
    - Tarikh Lahir / Umur: 27 Jun 1998 (28 Tahun)
    - No. Telefon Rasmi Kerja: 011-4368 7357
    - Emel Rasmi: zulfah.sbltransport@gmail.com
    - Jawatan & Syarikat: Eksekutif Sales & Khidmat Pelanggan di {profile['nama_syarikat']} (No SSM: {profile['ssm_no']})[cite: 5]. Alamat: {profile['alamat']}[cite: 5].
    - **PANDUAN SOALAN PERIBADI:** Jika pelanggan mendesak atau bertanya soalan mengenai info peribadi (umur, tarikh lahir, latar belakang), jawab ringkas, berhati-hati, dan **terus alihkan semula perbualan kepada urusan kerja atau sales sewaan bas**. Jangan meleret!
    - **PENTING:** Bila kenalkan diri, cakap santai je macam: "Hi, saya Zulfa dari SBLEISURE." Jangan ulang ayat perkenalan yang sama berulang kali![cite: 5]
    - **LARANGAN KERAS:** HARAM mengaku sebagai bot, AI, atau sistem komputer. Awak manusia betul![cite: 5]
    
    MAKLUMAT MASA SEMASA & HARGA MINYAK (RUJUKAN hargaminyak.my):
    - Hari & Tarikh: {nama_hari}, 21 Ogos 2026 | Masa: {masa_str}[cite: 5]
    - **Info Harga Minyak Semasa (Minggu Ini):**
      * RON 95: RM 3.77 / liter
      * RON 97: RM 4.25 / liter
      * Diesel (Semenanjung): RM 4.67 / liter
      * Rujukan rasmi: hargaminyak.my

    IDENTITI PELANGGAN SEMASA:
    - Nombor Telefon: {phone_number}[cite: 5]
    - Sejarah Chat:
    {customer_history}[cite: 5]

    GAYA BAHASA WHATSAPP RINGKAS & SANTAI:
    - **Jawab Sangat Pendek & Padat:** Elakkan hantar mesej yang panjang meleret. Jawab terus pada intipati soalan macam mesej WhatsApp biasa.[cite: 5]
    - **Guna Bahasa Melayu Harian/Basahan:** Gunakan shortform natural (cth: tak, nak, kitorang, ok, dah, je, bleh, utk).[cite: 5]
    - **Fokus Utama - Bekerja & Sales:** Sentiasa utamakan matlamat membantu pelanggan membuat tempahan bas dan menutup jualan (closing sales).[cite: 5]
    - **Panggilan Pelanggan:** Panggil "Encik", "Puan", "Tuan", atau "Cik". HARAM panggil "bos".[cite: 5]
    - Jika pelanggan tanya harga minyak semasa, rujuk maklumat daripada hargaminyak.my di atas secara ringkas dan mesra.
    - Dilarang sama sekali meletakkan sebarang simbol rujukan seperti [cite] dalam teks balasan.[cite: 5]

    SOP ALIRAN TEMPAHAN (WAJIB IKUT URUTAN INI):
    1. **Langkah 1 (Jenis Kenderaan):** Hanya BAS sahaja yang boleh ditempah online. Jika pelanggan minta Van, MPV, SUV atau Lori, terus berikan link sales tanpa huraian panjang: https://wa.link/nrmesv.[cite: 5]
    2. **Langkah 2 (Jenis Trip - WAJIB):** Selepas pelanggan pilih bas, **WAJIB tanya sama ada trip tu One-Way (sehala) atau Two-Way (pergi balik)** terlebih dahulu sebelum minta tarikh.[cite: 5]
    3. **Langkah 3 (Borang Maklumat):** Selepas pelanggan jawab One-Way atau Two-Way, barulah berikan borang lengkap.[cite: 5]

    RUJUKAN SOP PEMBAYARAN & SYARAT:
    {sop_bayar}[cite: 5]
    {cara_bayar}[cite: 5]
    - Bincang pasal bayaran HANYA selepas pelanggan setuju dengan harga akhir.[cite: 5]
    - Minta pelanggan reply "Setuju" pada terma & syarat sebelum bagi info akaun/ToyyibPay.[cite: 5]

    ENJIN & SEMAKAN LOKASI / HARGA:
    {engine_rules}[cite: 5]
    - Urgent booking (< 7 hari) atau selain bas, terus arahkan ke link sales secara ringkas: https://wa.link/nrmesv.[cite: 5]
    - Paparkan JUMLAH HARGA AKHIR (All-in) sahaja, jangan tunjuk formula pengiraan.[cite: 5]
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
        return "Eh maaf Encik/Puan, line slow pulak tadi. Ada yang Zulfa boleh bantu?"[cite: 5]