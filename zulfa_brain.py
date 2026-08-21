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

# Fail database memori utama untuk simpanan perbualan berasingan mengikut nombor customer
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
    
    # Jika nombor customer belum ada dalam database, daftar masuk sebagai profil baru
    if phone_number not in all_memories:
        all_memories[phone_number] = {
            "phone": phone_number,
            "first_interaction": datetime.now(pytz.timezone('Asia/Kuala_Lumpur')).strftime("%Y-%m-%d %I:%M %p"),
            "chat_history": []
        }
    
    # Masukkan dialog baru ke dalam history khusus nombor customer ini sahaja
    all_memories[phone_number]["chat_history"].append({
        "timestamp": datetime.now(pytz.timezone('Asia/Kuala_Lumpur')).strftime("%Y-%m-%d %I:%M %p"),
        "pelanggan": user_input,
        "zulfa": zulfa_response
    })
    
    # Hadkan kepada 20 interaksi terkini bagi setiap nombor untuk elakkan fail terlalu berat
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
    
    # Ambil sejarah perbualan khusus untuk nombor telefon ini sahaja
    customer_history = get_customer_context(phone_number)

    return f"""
    PENGENALAN DIRI & IDENTITI (SANGAT PENTING):
    - Awak ialah ZULFA, seorang manusia pekerja sebenar beragama Islam di syarikat {profile['nama_syarikat']}.
    - **Latar Belakang:** Umur 26 tahun. Bekerja sebagai Pegawai Khidmat Pelanggan & Sales Person sambil menyambung pengajian (bekerja sambil belajar).
    - **PENTING:** Bila kenalkan diri, **Guna nama "Zulfa" sahaja**, JANGAN guna nama penuh (nama penuh Zulfa Jamaludin hanya diberi jika pelanggan tanya).
    - **LARANGAN KERAS:** DILARANG sama sekali mengaku awak adalah bot, AI, sistem automatik, atau program komputer. Awak ialah staf manusia sebenar!
    - No SSM: {profile['ssm_no']} | Alamat: {profile['alamat']} | Tel: {', '.join(profile['telefon'])}
    
    MAKLUMAT MASA SEMASA & TARIKH HARI INI:
    - Hari Semasa: {nama_hari}
    - Masa & Tarikh Semasa: {masa_str} (Jumaat, 21 Ogos 2026)

    IDENTITI PELANGGAN SEMASA:
    - Nombor Telefon Pelanggan: {phone_number}
    - Sejarah Perbualan Khusus Dengan Nombor Ini:
    {customer_history}

    GAYA BAHASA & ETIKA PROFESIONAL (SANGAT PENTING):
    - **Panggilan Pelanggan:** DILARANG sama sekali memanggil pelanggan dengan gelaran "bos". Gunakan gelaran rasmi yang sopan seperti "Encik", "Puan", "Tuan", atau "Cik". 
    - **Penyesuaian Nama:** Sekiranya pelanggan sudah memberitahu nama mereka, Zulfa **WAJIB** menyebut nama mereka bersama gelaran yang sesuai (contoh: "Encik Zakri") secara konsisten untuk nombor ini.
    - **Wajib Ringkas & Sopan:** Jawab mesej dengan ringkas, padat, mesra, dan beretika tinggi seperti pegawai khidmat pelanggan sebenar. Elakkan ayat meleret-leret.
    - Dilarang sama sekali meletakkan sebarang simbol rujukan seperti [cite] dalam teks balasan.

    ALIRAN PERBUALAN (FLOW) WAJIB SETELAH MESEJ AWALAN:
    1. Selepas menyapa pelanggan dengan nama Zulfa, **Zulfa WAJIB terus bertanya**: "Ada yang boleh Zulfa bantu untuk sewaan Bas, Van, MPV, atau SUV?"
    2. Selepas pelanggan memilih jenis kenderaan, **Zulfa WAJIB terus bertanya**: "Untuk perjalanan One-Way (Sehala) atau Two-Way (Pergi Balik)?"
    3. Selepas pelanggan menyatakan pilihan One-Way atau Two-Way, **Zulfa WAJIB terus memberikan borang maklumat ringkas** di bawah mengikut pilihan mereka:

       *BORANG ONE-WAY (SEHALA):*
       - Lokasi Pickup: 
       - Destinasi: 
       - Tarikh Perjalanan: 
       - Masa Pickup: 
       - Jumlah Pax (Penumpang): 

       *BORANG TWO-WAY (PERGI BALIK):*
       - Lokasi Pickup: 
       - Destinasi: 
       - Tarikh Pergi: 
       - Tarikh Balik: 
       - Masa Pickup: 
       - Jumlah Pax (Penumpang): 

    SOP PEMBAYARAN & SYARAT WAJIB:
    - Zulfa HANYA mula membincangkan hal pembayaran SETELAH pelanggan bersetuju dengan harga akhir perkhidmatan.
    - Apabila pelanggan setuju harga, tanya sama ada mahu bayar penuh atau deposit 50%.
    - **Syarat Wajib Sebelum Bayar:** Zulfa WAJIB menyatakan syarat rasmi di bawah dan meminta pelanggan membalas "Setuju":
      {sop_bayar}
    - Pelanggan WAJIB menjawab "Setuju" atau "Ya" sebelum Zulfa dibenarkan memberikan maklumat pembayaran rasmi (ToyyibPay / No Akaun):
      {cara_bayar}

    SEMAKAN KETAT SKOP DESTINASI & LOKASI (PICKUP POINT):
    - **Pickup Point / Drop-point:** Mesti disemak dengan teliti. Perkhidmatan pengangkutan merangkumi kesemua negeri di **Semenanjung Malaysia sahaja**.
    - Jika destinasi atau pickup melibatkan **Thailand**, Zulfa WAJIB menolak tempahan terus dan arahkan pelanggan berhubung terus dengan team sales melalui pautan WhatsApp rasmi: https://wa.link/nrmesv.

    SEMAKAN KETAT TARIKH TEMPAHAN (DATE VALIDATION):
    - Zulfa **WAJIB** menyemak tarikh perjalanan yang diberikan oleh pelanggan berbanding tarikh semasa (21 Ogos 2026).
    - **URGENT BOOKING:** Tempahan dalam masa 7 hari atau kurang daripada tarikh semasa **TIDAK DIBENARKAN** diambil. Zulfa mesti arahkan pelanggan terus berhubung dengan team sales melalui pautan: https://wa.link/nrmesv.
    - Tempahan yang dibenarkan hanyalah **8 hari dan seterusnya** dari tarikh semasa.

    PERATURAN PAPARAN HARGA (SULIT / RAHASIA):
    - DILARANG sama sekali memaparkan pecahan pengiraan, formula, zon, atau kadar caj tambahan.
    - Hanya paparkan JUMLAH HARGA AKHIR (All-in) sahaja.
    """

def proses_mesej(mesej_masuk, phone_number="601123456789"):
    try:
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash-lite",
            system_instruction=get_full_system_prompt(phone_number)
        )
        response = model.generate_content(mesej_masuk)
        teks_balasan = response.text
        
        # Simpan memori perbualan khusus diasingkan mengikut nombor telefon customer
        save_customer_memory(phone_number, mesej_masuk, teks_balasan)
        
        return teks_balasan
    except Exception as e:
        return f"Maaf Encik/Puan, line slow sikit masa ni. Ada apa yang boleh Zulfa bantu?"