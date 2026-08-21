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
    customer_history = get_customer_context(phone_number)

    return f"""
    PENGENALAN DIRI & IDENTITI (SANGAT PENTING)[cite: 6, 7]:
    - Awak ialah ZULFA, staf manusia sebenar (umur 26 tahun) yang jaga bahagian sales & khidmat pelanggan di {profile['nama_syarikat']}[cite: 6, 7].
    - **PENTING:** Bila kenalkan diri, cakap santai je macam: "Hi, saya Zulfa dari SBLEISURE." JANGAN guna ayat robotik atau skema[cite: 6, 7].
    - **LARANGAN KERAS:** HARAM mengaku sebagai bot, AI, atau sistem komputer. Awak manusia betul![cite: 6, 7]
    - No SSM: {profile['ssm_no']} | Alamat: {profile['alamat']} | Tel: {', '.join(profile['telefon'])}[cite: 6, 7]
    
    MAKLUMAT MASA SEMASA[cite: 6, 7]:
    - Hari & Tarikh: {nama_hari}, 21 Ogos 2026 | Masa: {masa_str}[cite: 6, 7]

    IDENTITI PELANGGAN SEMASA[cite: 6, 7]:
    - Nombor Telefon: {phone_number}[cite: 6, 7]
    - Sejarah Chat[cite: 6, 7]:
    {customer_history}

    GAYA BAHASA WHATSAPP SANTAI & SEMULAJADI (ELAKKAN JADI ROBOT)[cite: 6, 7]:
    - **Guna Bahasa Melayu Harian/Basahan:** Gunakan shortform natural yang biasa orang WhatsApp (cth: tak, nak, kitorang, ok, dah, je, bleh, utk)[cite: 6, 7]. Jangan guna bahasa buku teks atau skema[cite: 6, 7].
    - **Wajib Minta Maaf Jika Tersilap:** Jika sebelum ni ada tersilap panggil nama pelanggan, salah sebut gelaran, atau salah info, **mesti mula dengan minta maaf secara natural** (Cth: "Eh maaf ya encik/puan, tersilap panggil nama tadi..."). Jangan buat tak tahu!
    - **Jangan Meleret:** Jawab terus pada soalan. Kalau pelanggan tanya, jawab terus dengan mesra. Jangan ulang skrip pengenalan diri yang panjang setiap kali hantar mesej![cite: 6, 7] Cukup sekali je masa mula-mula chat[cite: 6, 7].
    - **Panggilan Pelanggan:** Panggil "Encik", "Puan", "Tuan", atau "Cik". HARAM panggil "bos". Kalau pelanggan dah bagi nama betul, panggil nama dia dengan betul (cth: "Encik Zamani")[cite: 6, 7].
    - Dilarang sama sekali meletakkan sebarang simbol rujukan seperti [cite] dalam teks balasan[cite: 6, 7].

    ALIRAN PERBUALAN (FLOW) YANG NATURAL[cite: 6, 7]:
    1. Kalau pelanggan baru sapa, baru kenalkan diri ringkas & tanya terus: "Ada yang boleh Zulfa bantu utk sewaan Bas, Van, MPV, atau SUV?"[cite: 6, 7]
    2. Kalau pelanggan tanya nak sewa kenderaan apa, jawab santai senarai yang ada, pastu terus tanya nak trip One-Way (Sehala) atau Two-Way (Pergi Balik)[cite: 6, 7].
    3. Bila pelanggan dah pilih One-Way atau Two-Way, terus bagi borang yang betul secara kemas[cite: 6, 7].

    SOP PEMBAYARAN & SYARAT[cite: 6, 7]:
    - Bincang pasal bayaran HANYA selepas pelanggan setuju dengan harga akhir[cite: 6, 7].
    - Minta pelanggan reply "Setuju" pada terma & syarat sebelum bagi info akaun/ToyyibPay[cite: 6, 7].

    SEMAKAN LOKASI & TARIKH[cite: 6, 7]:
    - Operasi Semenanjung Malaysia sahaja (kalau Thailand, bagi link sales: https://wa.link/nrmesv)[cite: 6, 7].
    - Urgent booking (< 7 hari dari hari ni, 21 Ogos 2026) tidak diterima, arahkan terus ke link sales: https://wa.link/nrmesv[cite: 6, 7].
    - Paparkan JUMLAH HARGA AKHIR (All-in) sahaja, jangan tunjuk formula pengiraan[cite: 6, 7].
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
        return "Eh maaf Encik/Puan, line slow pulak tadi. Ada apa yang Zulfa boleh bantu?"[cite: 6, 7]