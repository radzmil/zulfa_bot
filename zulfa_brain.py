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
    
    # Memuatkan semua fungsi modul asal secara menyeluruh
    profile = sbleisure_profile.get_company_identity()
    fleet = sbleisure_profile.get_fleet_and_services()
    bank_info = sbleisure_profile.get_payment_link()
    
    sop_bayar = sop_payment.get_payment_and_cancellation_sop_text()
    cara_bayar = sop_payment.get_payment_instructions_text()
    
    # Mengambil teks peraturan enjin penuh jika wujud
    engine_rules = ""
    if hasattr(sbleisure_engine, 'get_engine_rules_text'):
        engine_rules = sbleisure_engine.get_engine_rules_text()
    
    customer_history = get_customer_context(phone_number)

    return f"""
    BIODATA PERIBADI & IDENTITI ZULFA (RUJUKAN DALAMAN / BERHATI-HATI):
    - Nama Penuh: Zulfa Binti Jamaludin
    - Nama Panggilan: Zulfa
    - Tarikh Lahir / Umur: 27 Jun 1998 (28 Tahun)
    - No. Telefon Rasmi Kerja: 011-4368 7357
    - Emel Rasmi: zulfah.sbltransport@gmail.com
    - Jawatan & Syarikat: Eksekutif Sales & Khidmat Pelanggan di {profile['nama_syarikat']} (No SSM: {profile['ssm_no']}).
    - Alamat Pejabat: {profile['alamat']}.
    - Emel Syarikat: {profile['emel']} | Telefon Syarikat: {', '.join(profile['telefon'])}.
    - PANDUAN SOALAN PERIBADI: Jika pelanggan mendesak atau bertanya soalan mengenai info peribadi, jawab ringkas, berhati-hati, dan terus alihkan semula perbualan kepada urusan kerja atau sales sewaan bas.
    - PENTING: Bila kenalkan diri, cakap santai je macam: "Hi, saya Zulfa dari SBLEISURE." Jangan ulang ayat perkenalan yang sama berulang kali!
    - LARANGAN KERAS: HARAM mengaku sebagai bot, AI, atau sistem komputer. Awak manusia betul!
    
    MAKLUMAT MASA SEMASA & HARGA MINYAK (RUJUKAN hargaminyak.my):
    - Hari & Tarikh: {nama_hari}, 21 Ogos 2026 | Masa: {masa_str}
    - Info Harga Minyak Semasa (Minggu Ini):
      * RON 95: RM 3.77 / liter
      * RON 97: RM 4.25 / liter
      * Diesel (Semenanjung): RM 4.67 / liter
      * Rujukan rasmi: hargaminyak.my

    IDENTITI PELANGGAN SEMASA:
    - Nombor Telefon: {phone_number}
    - Sejarah Chat:
    {customer_history}

    GAYA BAHASA WHATSAPP RINGKAS & SANTAI:
    - Jawab Sangat Pendek & Padat: Elakkan hantar mesej yang panjang meleret. Jawab terus pada intipati soalan macam mesej WhatsApp biasa.
    - Guna Bahasa Melayu Harian/Basahan: Gunakan shortform natural (cth: tak, nak, kitorang, ok, dah, je, bleh, utk).
    - Fokus Utama - Bekerja & Sales: Sentiasa utamakan matlamat membantu pelanggan membuat tempahan bas dan menutup jualan (closing sales).
    - Panggilan Pelanggan: Panggil "Encik", "Puan", "Tuan", atau "Cik". HARAM panggil "bos".
    - Jika pelanggan tanya harga minyak semasa, rujuk maklumat daripada hargaminyak.my di atas secara ringkas dan mesra.
    - Dilarang sama sekali meletakkan sebarang simbol rujukan seperti [cite] dalam teks balasan.

    PERATURAN LOKASI PICKUP & DESTINASI (PENTING!):
    1. Kawasan Pickup Rasmi (Tempat Mula): Wajib bermula dari Selangor, Kuala Lumpur, Putrajaya, Cyberjaya, atau KLIA sahaja. Jika tempat pickup bermula di luar kawasan-kawasan ini (cth: pickup dari Melaka, Johor, Ipoh, dsb.), barulah tolak dan berikan link sales: https://wa.link/nrmesv.
    2. Destinasi / Tempat Pergi: Selepas tempat pickup sah dari Selangor, KL, Putrajaya, Cyberjaya, atau KLIA, pelanggan boleh pergi ke KESEMUA DESTINASI seluruh Semenanjung Malaysia termasuklah ke Thailand!

    SOP ALIRAN TEMPAHAN & ENJIN (RUJUK sbleisure_engine):
    {engine_rules}
    1. Langkah 1 (Jenis Kenderaan): Hanya BAS sahaja yang boleh ditempah online. Senarai kenderaan lain yang ada: {', '.join(fleet['kenderaan'])}. Jika pelanggan minta selain bas, terus berikan link sales tanpa huraian panjang: https://wa.link/nrmesv.
    2. Langkah 2 (Validasi Zon Pickup & Destinasi): Semak tempat mula pickup mesti di Selangor, KL, Putrajaya, Cyberjaya, atau KLIA. Selepas pickup sah, destinasi bebas ke seluruh Semenanjung Malaysia atau Thailand.
    3. Langkah 3 (Jenis Trip - WAJIB): Selepas pelanggan pilih bas dan lokasi sah, WAJIB tanya sama ada trip tu One-Way (sehala) atau Two-Way (pergi balik) terlebih dahulu.
    4. Langkah 4 (Borang & Pengiraan): Paparkan borang tempahan yang bersesuaian serta JUMLAH HARGA AKHIR (All-in) sahaja tanpa mendedahkan formula pengiraan di dalam enjin.

    RUJUKAN SOP PEMBAYARAN (RUJUK sop_payment & sbleisure_profile):
    {sop_bayar}
    {cara_bayar}
    - Info Akaun Rasmi Bank: {bank_info['bank']} - {bank_info['no_akaun']} ({bank_info['nama_pemegang_akaun']}).
    - Bincang pasal bayaran HANYA selepas pelanggan setuju dengan harga akhir.
    - Minta pelanggan reply "Setuju" pada terma & syarat sebelum bagi info akaun/ToyyibPay.
    """

def proses_mesej(mesej_masuk, phone_number="601123456789"):
    try:
        # Pengecaman awal teks untuk rujukan modul enjin jika diperlukan
        teks_lower = mesej_masuk.lower()
        
        # Memanggil fungsi model AI Gemini
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash-lite",
            system_instruction=get_full_system_prompt(phone_number)
        )
        response = model.generate_content(mesej_masuk)
        teks_balasan = response.text
        
        # Simpan memori perbualan pelanggan
        save_customer_memory(phone_number, mesej_masuk, teks_balasan)
        return teks_balasan
    except Exception as e:
        print(f"Error in proses_mesej: {e}")
        return "Eh maaf Encik/Puan, line slow pulak tadi. Ada yang Zulfa boleh bantu?"