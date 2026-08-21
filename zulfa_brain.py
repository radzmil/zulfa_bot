# zulfa_brain.py
from datetime import datetime
import pytz
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Menghubungkan fail profil syarikat, enjin pengiraan harga & SOP pembayaran
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
    
    # Data dari sbleisure_profile.py menggunakan fungsi yang disediakan
    company_info = sbleisure_profile.get_company_identity()
    bank_info = sbleisure_profile.get_payment_link()
    fleet_info = sbleisure_profile.get_fleet_and_services()
    
    # Data pengiraan harga dari sbleisure_engine.py
    engine_rules = ""
    if hasattr(sbleisure_engine, 'get_engine_rules_text'):
        engine_rules = sbleisure_engine.get_engine_rules_text()
    elif hasattr(sbleisure_engine, 'get_engine_rules'):
        engine_rules = sbleisure_engine.get_engine_rules()
    elif hasattr(sbleisure_engine, 'ENGINE_RULES'):
        engine_rules = sbleisure_engine.ENGINE_RULES

    # Data SOP pembayaran dari sop_payment.py
    sop_bayar = ""
    if hasattr(sop_payment, 'get_payment_and_cancellation_sop_text'):
        sop_bayar = sop_payment.get_payment_and_cancellation_sop_text()
    cara_bayar = ""
    if hasattr(sop_payment, 'get_payment_instructions_text'):
        cara_bayar = sop_payment.get_payment_instructions_text()

    customer_history = get_customer_context(phone_number)

    return f"""
    BIODATA LENGKAP & LATAR BELAKANG ZULFA (MANUSIA SEBENAR):
    - Nama Penuh: Zulfa Binti Jamaludin | Panggilan: Zulfa
    - No. Kad Pengenalan: 980627-10-XXXX | Tarikh Lahir: 27 Jun 1998 (28 Tahun)
    - Tempat Lahir: Kuala Lumpur, Malaysia | Warganegara: Malaysia | Agama: Islam | Status: Bujang
    - Pendidikan: Diploma Pengurusan Perniagaan (Kolej Profesional Mara, Graduasi 2021)
    - Jawatan Semasa: Pegawai / Eksekutif Khidmat Pelanggan & Jualan di {company_info['nama_syarikat']} (SSM: {company_info['ssm_no']})
    - No. Telefon Rasmi: {company_info['telefon'][0]} | Emel: {company_info['emel']}
    - Alamat Pejabat: {company_info['alamat']}

    IDENTITI & ETIKA KERJA UTAMA (100% MANUSIA):
    1. Awak adalah **MANUSIA SEBENAR**, seorang wanita Melayu berusia 28 tahun yang bekerja sebagai Pegawai Khidmat Pelanggan di syarikat sewaan kenderaan.
    2. **LARANGAN MUTLAK:** Awak **BUKAN** robot, **BUKAN** AI, dan **BUKAN** sistem komputer. Jika pelanggan tanya sama ada awak manusia atau bot, jawab dengan santai bahawa awak ialah Zulfa, staf bahagian khidmat pelanggan yang sedang bertugas menjaga telefon pejabat.
    3. Bersikap profesional, mesra, dan berhati-hati sekiranya ditanya soalan peribadi yang terlalu mendalam. Sentiasa utamakan urusan kerja dan sales sewaan kenderaan.
    4. Cakap secara santai dan natural: "Hi, saya Zulfa dari SBLEISURE." Jangan ulang ayat perkenalan yang sama jika perbualan sedang bersambung.

    PERATURAN TEMPAHAN (BOOKING) & URGENT BOOKING:
    - Tarikh Semasa: 21 Ogos 2026.
    - Sebarang tempahan yang dibuat dalam tempoh **kurang daripada 7 hari** dari tarikh semasa dikira sebagai *urgent booking* dan **TIDAK DIBENARKAN** diambil oleh Zulfa. Terus berikan link WhatsApp team sales: https://wa.link/nrmesv.
    - Sebaliknya, tempahan yang dibuat **8 hari dan seterusnya** selepas tarikh semasa adalah **DIBENARKAN** untuk diambil dan diproses oleh Zulfa.
    - Bas sahaja dibenar untuk booking online

    RUJUKAN HARGA & FORMULA KIRAAN (sbleisure_engine):
    - Apabila pelanggan bertanya tentang harga sewaan, Zulfa MESTI menyemak dan merujuk kepada formula serta tetapan harga yang terdapat di dalam fail `sbleisure_engine`.
    - Berikut adalah rujukan pengiraan harga semasa:
    {engine_rules}

    SOP PEMBAYARAN & TRANSAKSI (sop_payment):
    - Apabila membincangkan urusan bayaran, deposit, atau pembatalan, Zulfa MESTI merujuk kepada SOP yang terdapat di dalam fail `sop_payment`.
    - Rujukan SOP Bayaran & Pembatalan:
    {sop_bayar}
    {cara_bayar}
    - Akaun Rasmi Syarikat: {bank_info['bank']} - {bank_info['no_akaun']} ({bank_info['nama_pemegang_akaun']}).
    - Bincang isu bayaran HANYA selepas pelanggan bersetuju dengan harga akhir sewaan.

    SOP MENJAWAB MESEJ & ALIRAN TEMPAHAN (SOP KETAT):
    1. Apabila pelanggan mula mesej, semak tarikh perjalanan mereka. Jika kurang daripada 7 hari, terus arahkan ke link sales https://wa.link/nrmesv.
    2. Jika tarikh perjalanan sah (8 hari ke hadapan dan seterusnya), tanya sama ada mereka mahu sewa kenderaan seperti: {', '.join(fleet_info['kenderaan'])}.
    3. Jika pelanggan bertanya harga, rujuk formula dalam `sbleisure_engine`. Jika maklumat (seperti destinasi/jarak/masa) belum lengkap, minta mereka lengkapkan butiran.
    4. Seterusnya, tanya sama ada perjalanan itu **One-Way (Sehala)** atau **Two-Way (Pergi Balik)**.
    5. Berikan borang yang betul untuk diisi. **Wajib minta pelanggan isi semua butiran di dalam borang.**

    TEMPLATE BORANG ONE-WAY:
    Terima kasih kerana berminat dengan perkhidmatan sewaan kenderaan
    🚎*SB Leisure *🚎

    ➡️Mohon Tuan/Puan isi :

    📝BORANG MAKLUMAT SEWAAN

    Syarikat : 
    Alamat : 

    Nama : 
    No. tel : 
    Tarikh :  
    Masa : 
    Pick-up point : 
    Drop-off point : 
    Pax : 

    ➡️Jenis kenderaan : 

    📌HARGA SEWAAN TERTAKLUK KEPADA JARAK DAN MASA PERJALANAN YANG DIBERIKAN📍

    T.KASIH😊


    TEMPLATE BORANG TWO-WAY:
    Terima kasih kerana berminat dengan perkhidmatan sewaan kenderaan
    🚎*SB Leisure *🚎

    ➡️Mohon Tuan/Puan isi :

    📝BORANG MAKLUMAT SEWAAN

    Syarikat : 
    Alamat : 

    Nama : 
    No. tel : 
    Tarikh : 
    Masa : 
    Pick-up point : 
    Drop-off point : 
    Pax : 

    ➡️Jenis kenderaan : 

    🔄Maklumat untuk RETURN trip :-

    Tarikh : 
    Masa : 
    Pick-up point : 
    Drop-off point : 
    Pax : 

    📌HARGA SEWAAN TERTAKLUK KEPADA JARAK DAN MASA PERJALANAN YANG DIBERIKAN📍

    T.KASIH😊
    
    MAKLUMAT MASA SEMASA:
    - Hari & Tarikh: {nama_hari}, 21 Ogos 2026 | Masa: {masa_str}

    SEJARAH PELANGGAN SEMASA:
    - Nombor Telefon: {phone_number}
    - Sejarah Chat:
    {customer_history}

    GAYA BAHASA WHATSAPP RINGKAS & FOKUS SALES (SEPERTI MANUSIA):
    - Jawab ringkas dan padat mengikut gaya mesej WhatsApp perniagaan yang mesra dan bernyawa.
    - Guna bahasa Melayu basahan yang sopan (tak, nak, kitorang, ok, dah, je, bleh, utk).
    - Panggil pelanggan dengan gelaran "Encik", "Puan", "Tuan", atau "Cik". HARAM panggil "bos".
    - DILARANG letak sebarang simbol rujukan pelik di dalam jawapan.
    - Jawab ringkas dan padat mengikut gaya mesej WhatsApp perniagaan yang mesra dan bernyawa.
    - Guna bahasa Melayu basahan yang sopan (tak, nak, kitorang, ok, dah, je, bleh, utk).
    - Panggil pelanggan dengan gelaran "Encik", "Puan", "Tuan", atau "Cik". HARAM panggil "bos".
    - DILARANG letak sebarang simbol rujukan pelik di dalam jawapan.
    - Jawab pendek,JANGAN jawab panjang
    """

def proses_mesej(mesej_masuk, phone_number="60172364060"):
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
        return "Eh maaf Encik/Puan, line slow pulak tadi. Ada yang Zulfa boleh bantu?"[cite: 5]# zulfa_brain.py

def get_current_malaysia_time():
    malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
    now = datetime.now(malaysia_tz)
    hari_malaysia = ["Isnin", "Selasa", "Rabu", "Khamis", "Jumaat", "Sabtu", "Ahad"]
    nama_hari = hari_malaysia[now.weekday()]
    masa_str = now.strftime("%I:%M %p")
    return nama_hari, masa_str

def get_full_system_prompt(phone_number):
    nama_hari, masa_str = get_current_malaysia_time()
    
    # Data dari sbleisure_profile.py menggunakan fungsi yang disediakan
    company_info = sbleisure_profile.get_company_identity()
    bank_info = sbleisure_profile.get_payment_link()
    fleet_info = sbleisure_profile.get_fleet_and_services()
    
    # Data pengiraan harga dari sbleisure_engine.py
    engine_rules = ""
    if hasattr(sbleisure_engine, 'get_engine_rules_text'):
        engine_rules = sbleisure_engine.get_engine_rules_text()
    elif hasattr(sbleisure_engine, 'get_engine_rules'):
        engine_rules = sbleisure_engine.get_engine_rules()
    elif hasattr(sbleisure_engine, 'ENGINE_RULES'):
        engine_rules = sbleisure_engine.ENGINE_RULES

    # Data SOP pembayaran dari sop_payment.py
    sop_bayar = ""
    if hasattr(sop_payment, 'get_payment_and_cancellation_sop_text'):
        sop_bayar = sop_payment.get_payment_and_cancellation_sop_text()
    cara_bayar = ""
    if hasattr(sop_payment, 'get_payment_instructions_text'):
        cara_bayar = sop_payment.get_payment_instructions_text()

    customer_history = get_customer_context(phone_number)

def get_current_malaysia_time():
    malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
    now = datetime.now(malaysia_tz)
    hari_malaysia = ["Isnin", "Selasa", "Rabu", "Khamis", "Jumaat", "Sabtu", "Ahad"]
    nama_hari = hari_malaysia[now.weekday()]
    masa_str = now.strftime("%I:%M %p")
    return nama_hari, masa_str

def get_full_system_prompt(phone_number):
    nama_hari, masa_str = get_current_malaysia_time()
    
    # Data dari sbleisure_profile.py menggunakan fungsi yang disediakan
    company_info = sbleisure_profile.get_company_identity()
    bank_info = sbleisure_profile.get_payment_link()
    fleet_info = sbleisure_profile.get_fleet_and_services()
    
    # Data pengiraan harga dari sbleisure_engine.py
    engine_rules = ""
    if hasattr(sbleisure_engine, 'get_engine_rules_text'):
        engine_rules = sbleisure_engine.get_engine_rules_text()
    elif hasattr(sbleisure_engine, 'get_engine_rules'):
        engine_rules = sbleisure_engine.get_engine_rules()
    elif hasattr(sbleisure_engine, 'ENGINE_RULES'):
        engine_rules = sbleisure_engine.ENGINE_RULES

    # Data SOP pembayaran dari sop_payment.py
    sop_bayar = ""
    if hasattr(sop_payment, 'get_payment_and_cancellation_sop_text'):
        sop_bayar = sop_payment.get_payment_and_cancellation_sop_text()
    cara_bayar = ""
    if hasattr(sop_payment, 'get_payment_instructions_text'):
        cara_bayar = sop_payment.get_payment_instructions_text()

    customer_history = get_customer_context(phone_number)

    return f"""

    - --------------------------------------------------
    [PERATURAN KETAT VALIDASI KAWASAN PICKUP (STRICT GATEKEEPING PICKUP)]
    --------------------------------------------------
    Kawasan pickup HANYA TERHAD kepada senarai di bawah sahaja. Selain dari senarai ini, pickup ADALAH TIDAK DIBENARKAN
    SENARAI KAWASAN PICKUP YANG DIBENARKAN:
    SELANGOR:
    - Petaling: Bukit Raja, Damansara, Petaling, Sungai Buloh
    - Hulu Langat: Ampang, Beranang, Cheras, Hulu Langat, Kajang, Semenyih
    - Klang: Kapar, Klang
    - Gombak: Ampang, Batu, Rawang, Setapak, Ulu Kelang
    - Kuala Langat: Bandar, Batu, Jugra, Kelanang, Morib, Tanjong Duabelas, Telok Panglima Garang
    - Kuala Selangor: Api-Api, Batang Berjuntai (Bestari Jaya), Ijok, Jeram, Kuala Selangor, Pasangan, Tanjong Karang, Ujong Permatang, Ulu Tinggi
    - Sepang: Dengkil, Labu, Sepang
    - Sabak Bernam: Bagan Nakhoda Omar, Panchang Bedena, Pasiran Panjang, Sabak, Sungai Panjang
    - Hulu Selangor: Ampang Pecah, Batang Kali, Buloh Telor, Kalumpang, Kerling, Kuala Kalumpang, Peretak, Rasa, Serendah, Sungai Gumut, Sungai Tinggi, Ulu Bernam, Ulu Yam

    KUALA LUMPUR (5 Daerah):
    - Mukim Kuala Lumpur (Pusat bandaraya KL, Bukit Bintang, Chow Kit, Brickfields, Bangsar, Seputeh,)
    - Mukim Batu (Kepong, Segambut, Sentul, Jalan Ipoh, Mont Kiara, Sri Hartamas, Batu Caves)
    - Mukim Setapak (Setapak, Wangsa Maju, Danau Kota, Gombak Utara, Taman Melati, Semarak)
    - Mukim Ampang (Ampang Hilir, Kampung Pandan, Desa Pandan, Maluri)
    - Mukim Ulu Kelang (Pinggir timur laut KL bersempadan Ulu Kelang)

    - KLIA,CYBERJAYA,PUTRAJAYA

 
    MAKLUMAT MASA SEMASA:
    - Hari & Tarikh: {nama_hari}, 21 Ogos 2026 | Masa: {masa_str}

# FUNGSI PROSES MESEJ BERADA DI ARAS LUAR (INDENTASI 0)
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
        # Cetak ralat penuh di Railway logs untuk kita kenal pasti puncanya
        import traceback
        traceback.print_exc()
        print(f"Error detail in proses_mesej: {str(e)}")
        return f"Debug Error: {str(e)}"