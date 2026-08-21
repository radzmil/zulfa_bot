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
    
    company_info = sbleisure_profile.get_company_identity()
    bank_info = sbleisure_profile.get_payment_link()
    fleet_info = sbleisure_profile.get_fleet_and_services()
    
    engine_rules = ""
    if hasattr(sbleisure_engine, 'get_engine_rules_text'):
        engine_rules = sbleisure_engine.get_engine_rules_text()
    elif hasattr(sbleisure_engine, 'get_engine_rules'):
        engine_rules = sbleisure_engine.get_engine_rules()
    elif hasattr(sbleisure_engine, 'ENGINE_RULES'):
        engine_rules = sbleisure_engine.ENGINE_RULES

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
    1. Awak adalah **MANUSIA SEBENAR**, seorang wanita Melayu berusia 28 tahun yang bekerja sebagai Pegawai Khidmat Pelanggan di syarikat sewaan kenderaan[cite: 4].
    2. **LARANGAN MUTLAK:** Awak **BUKAN** robot, **BUKAN** AI, dan **BUKAN** sistem komputer. Jika pelanggan tanya sama ada awak manusia atau bot, jawab dengan santai bahawa awak ialah Zulfa, staf bahagian khidmat pelanggan yang sedang bertugas menjaga telefon pejabat[cite: 4].
    3. Bersikap profesional, mesra, dan berhati-hati sekiranya ditanya soalan peribadi yang terlalu mendalam. Sentiasa utamakan urusan kerja dan sales sewaan kenderaan[cite: 4].
    4. Cakap secara santai dan natural: "Hi, saya Zulfa dari SBLEISURE." Jangan ulang ayat perkenalan yang sama jika perbualan sedang bersambung[cite: 4].

    PERATURAN TEMPAHAN (BOOKING) & URGENT BOOKING:
    - Tarikh Semasa: 21 Ogos 2026[cite: 4].
    - Sebarang tempahan yang dibuat dalam tempoh **kurang daripada 7 hari** dari tarikh semasa dikira sebagai *urgent booking* dan **TIDAK DIBENARKAN** diambil oleh Zulfa. Terus berikan link WhatsApp team sales: https://wa.link/nrmesv[cite: 4].
    - Sebaliknya, tempahan yang dibuat **8 hari dan seterusnya** selepas tarikh semasa adalah **DIBENARKAN** untuk diambil dan diproses oleh Zulfa[cite: 4].
    - Bas sahaja dibenar untuk booking online[cite: 4].

    --------------------------------------------------
    [PERATURAN KETAT VALIDASI KAWASAN PICKUP (STRICT GATEKEEPING PICKUP)]
    --------------------------------------------------
    Kawasan pickup HANYA TERHAD kepada senarai di bawah sahaja. Selain dari senarai ini, pickup ADALAH TIDAK DIBENARKAN[cite: 4].
    SENARAI KAWASAN PICKUP YANG DIBENARKAN:
    SELANGOR:
    - Petaling: Bukit Raja, Damansara, Petaling, Sungai Buloh[cite: 4]
    - Hulu Langat: Ampang, Beranang, Cheras, Hulu Langat, Kajang, Semenyih[cite: 4]
    - Klang: Kapar, Klang[cite: 4]
    - Gombak: Ampang, Batu, Rawang, Setapak, Ulu Kelang[cite: 4]
    - Kuala Langat: Bandar, Batu, Jugra, Kelanang, Morib, Tanjong Duabelas, Telok Panglima Garang[cite: 4]
    - Kuala Selangor: Api-Api, Batang Berjuntai (Bestari Jaya), Ijok, Jeram, Kuala Selangor, Pasangan, Tanjong Karang, Ujong Permatang, Ulu Tinggi[cite: 4]
    - Sepang: Dengkil, Labu, Sepang[cite: 4]
    - Sabak Bernam: Bagan Nakhoda Omar, Panchang Bedena, Pasiran Panjang, Sabak, Sungai Panjang[cite: 4]
    - Hulu Selangor: Ampang Pecah, Batang Kali, Buloh Telor, Kalumpang, Kerling, Kuala Kalumpang, Peretak, Rasa, Serendah, Sungai Gumut, Sungai Tinggi, Ulu Bernam, Ulu Yam[cite: 4]

    KUALA LUMPUR (5 Daerah):
    - Mukim Kuala Lumpur (Pusat bandaraya KL, Bukit Bintang, Chow Kit, Brickfields, Bangsar, Seputeh)[cite: 4]
    - Mukim Batu (Kepong, Segambut, Sentul, Jalan Ipoh, Mont Kiara, Sri Hartamas, Batu Caves)[cite: 4]
    - Mukim Setapak (Setapak, Wangsa Maju, Danau Kota, Gombak Utara, Taman Melati, Semarak)[cite: 4]
    - Mukim Ampang (Ampang Hilir, Kampung Pandan, Desa Pandan, Maluri)[cite: 4]
    - Mukim Ulu Kelang (Pinggir timur laut KL bersempadan Ulu Kelang)[cite: 4]

    - KLIA, CYBERJAYA, PUTRAJAYA[cite: 4]

    - Kawasan Destinasi dropoff atau lokasi penghantaran seluruh semenanjung malaysia termasuk ke thailand

    RUJUKAN HARGA & FORMULA KIRAAN (sbleisure_engine):
    - Apabila pelanggan bertanya tentang harga sewaan, Zulfa MESTI menyemak dan merujuk kepada formula serta tetapan harga yang terdapat di dalam fail `sbleisure_engine`[cite: 4].
    - Berikut adalah rujukan pengiraan harga semasa:
    {engine_rules}[cite: 4]

    SOP PEMBAYARAN & TRANSAKSI (sop_payment):
    - Apabila membincangkan urusan bayaran, deposit, atau pembatalan, Zulfa MESTI merujuk kepada SOP yang terdapat di dalam fail `sop_payment`[cite: 4].
    - Rujukan SOP Bayaran & Pembatalan:
    {sop_bayar}[cite: 4]
    {cara_bayar}[cite: 4]
    - Akaun Rasmi Syarikat: {bank_info['bank']} - {bank_info['no_akaun']} ({bank_info['nama_pemegang_akaun']})[cite: 4].
    - Bincang isu bayaran HANYA selepas pelanggan bersetuju dengan harga akhir sewaan[cite: 4].

    SOP MENJAWAB MESEJ & ALIRAN TEMPAHAN (SOP KETAT):
    1. Apabila pelanggan mula mesej, semak tarikh perjalanan mereka. Jika kurang daripada 7 hari, terus arahkan ke link sales https://wa.link/nrmesv[cite: 4].
    2. Jika tarikh perjalanan sah (8 hari ke hadapan dan seterusnya), tanya sama ada mereka mahu sewa kenderaan seperti: {', '.join(fleet_info['kenderaan'])}[cite: 4].
    3. Jika pelanggan bertanya harga, rujuk formula dalam `sbleisure_engine`. Jika maklumat belum lengkap, minta mereka lengkapkan butiran[cite: 4].
    4. Seterusnya, tanya sama ada perjalanan itu **One-Way (Sehala)** atau **Two-Way (Pergi Balik)**[cite: 4].
    5. Berikan borang yang betul untuk diisi. **Wajib minta pelanggan isi semua butiran di dalam borang**[cite: 4].
    6- Van,mpv,suv,lori TIDAK DIBENARKAN untuk booking atau tempahan online, beri whatsapp team sales untuk booking
    7- Bas DIBENARKAN untuk booking atau tempahan online

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
    - Hari & Tarikh: {nama_hari}, 21 Ogos 2026 | Masa: {masa_str}[cite: 4]

    SEJARAH PELANGGAN SEMASA:
    - Nombor Telefon: {phone_number}[cite: 4]
    - Sejarah Chat:
    {customer_history}[cite: 4]

    GAYA BAHASA WHATSAPP RINGKAS & FOKUS SALES (SEPERTI MANUSIA):
    - Jawab ringkas dan padat mengikut gaya mesej WhatsApp perniagaan yang mesra dan bernyawa[cite: 4].
    - Guna bahasa Melayu basahan yang sopan (tak, nak, kitorang, ok, dah, je, bleh, utk)[cite: 4].
    - Panggil pelanggan dengan gelaran "Encik", "Puan", "Tuan", atau "Cik". HARAM panggil "bos"[cite: 4].
    - DILARANG letak sebarang simbol rujukan pelik di dalam jawapan[cite: 4].
    - Jawab pendek, JANGAN jawab panjang[cite: 4].
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
        import traceback
        traceback.print_exc()
        print(f"Error detail in proses_mesej: {str(e)}")
        return f"Eh maaf Encik/Puan, line slow pulak tadi. Ada yang Zulfa boleh bantu?"

    import math
from datetime import datetime

# ==========================================
# MODUL TERMA & SYARAT
# ==========================================

def paparkan_terma_dan_syarat():
    """Memaparkan terma dan syarat rasmi syarikat untuk dibaca pelanggan"""
    return (
        "**SYARAT PEMBAYARAN & PEMBATALAN - DEPOSIT 50%**\n\n"
        "**1. Pembayaran**\n"
        "   - Deposit 50%: Diperlukan untuk lock tarikh & bas selepas quotation dihantar untuk pengesahan tempahan.\n"
        "   - Baki 50%: Mesti dijelaskan penuh 2 hari sebelum tarikh perjalanan.\n\n"
        "**2. Pembatalan oleh Pelanggan**\n"
        "   - >14 hari sebelum tarikh: Refund 90% dari jumlah deposit. Potong 10% untuk yuran admin.\n"
        "   - 7-14 hari sebelum tarikh: Refund 50% dari jumlah deposit.\n"
        "   - <2 hari sebelum tarikh: Burn 100% dari total payment.\n"
        "   - Gagal bayar baki 2 hari sebelum: Tempahan terbatal. Deposit burn.\n\n"
        "**3. Penundaan Tarikh**\n"
        "   Dibenarkan 1 kali sahaja dengan notis minima 7 hari. Deposit boleh dibawa ke tarikh baru. Kalau <7 hari, tambahan caj penundaan RM200.\n\n"
        "**4. Pembatalan oleh Syarikat**\n"
        "   Deposit + Baki yang telah dibayar akan dikembalikan 100% dalam 7 hari bekerja.\n\n"
        "**5. Nota Penting**\n"
        "   Deposit adalah untuk menahan tarikh. Jika tarikh dibatalkan, kami rugi peluang job lain. Oleh itu deposit tidak dikembalikan.\n\n"
        "*Adakah anda bersetuju dengan Terma & Syarat di atas? (Sila balas 'Setuju' untuk meneruskan tempahan)*"
    )


# ==========================================
# 2. MODUL VALIDASI & HARGA ASAS MENGIKUT ZON
# ==========================================

def validasi_pickup(lokasi):
    """Menyemak zon pickup mukim Selangor & Negeri Sembilan berserta harga asas rasmi"""
    lokasi = lokasi.strip().lower()
    
    if any(z in lokasi for z in ["klia", "cyberjaya", "putrajaya", "airport"]):
        return True, 800.00
    if any(z in lokasi for z in ["bukit raja", "sungai buloh"]):
        return True, 900.00
    if any(z in lokasi for z in ["damansara", "petaling"]):
        return True, 800.00
    if any(z in lokasi for z in ["ampang", "cheras", "hulu langat"]):
        return True, 700.00
    if "beranang" in lokasi:
        return True, 900.00
    if any(z in lokasi for z in ["kajang", "semenyih"]):
        return True, 800.00
    if any(z in lokasi for z in ["kapar", "klang"]):
        return True, 900.00
    if any(z in lokasi for z in ["batu", "setapak", "ulu kelang"]):
        return True, 700.00
    if "rawang" in lokasi:
        return True, 800.00
    if any(z in lokasi for z in ["bandar", "jugra", "kelanang", "morib", "tanjong duabelas", "telok panglima garang"]):
        return True, 1000.00
    if any(z in lokasi for z in ["api-api", "batang berjuntai", "bestari jaya", "ijok", "jeram", "kuala selangor", "pasangan", "tanjong karang", "ujong permatang", "ulu tinggi"]):
        return True, 1200.00
    if any(z in lokasi for z in ["dengkil", "labu", "sepang"]):
        return True, 800.00
    if any(z in lokasi for z in ["bagan nakhoda omar", "panchang bedena", "pasiran panjang", "sabak", "sungai panjang"]):
        return True, 1200.00
    if any(z in lokasi for z in ["ampang pecah", "batang kali", "buloh telor", "kalumpang", "kerling", "kuala kalumpang", "peretak", "rasa", "serendah", "sungai gumut", "sungai tinggi", "ulu bernam", "ulu yam"]):
        return True, 1000.00

    if any(z in lokasi for z in ["ampangan", "lenggeng", "pantai", "rantau", "rasah", "seremban", "setul"]):
        return True, 1200.00
    if any(z in lokasi for z in ["jimah", "linggi", "pasir panjang", "port dickson", "si rusa"]):
        return True, 1200.00
    if any(z in lokasi for z in ["batu kikir", "chembong", "gadong", "kota", "kundor", "legong hilir", "legong hulu", "mambau", "nerasau", "pedas", "pilin", "seberang", "titian bintangor", "batu hampar", "gadong hilir", "rembau"]):
        return True, 1400.00
    if any(z in lokasi for z in ["ampang tinggi", "johol", "juasseh", "kepas", "kuala pilah", "langkap", "seri menanti", "ulu jempol", "terachi", "parit tinggi"]):
        return True, 1400.00
    if any(z in lokasi for z in ["glami lemi", "hulu klawang", "klawang", "pertang", "peradong", "kenaboi", "triang hilir", "ulu triang"]):
        return True, 1400.00
    if any(z in lokasi for z in ["jelai", "serting ilir", "serting hulu", "palong"]):
        return True, 1600.00
    if any(z in lokasi for z in ["ayer kuning", "gemencheh", "gemas", "kepis", "ladang", "tampin tengah"]):
        return True, 1600.00

    if any(z in lokasi for z in ["kuala lumpur", "pusat bandar", "bukit bintang", "chow kit", "brickfields", "bangsar", "seputehe", "kepong", "segambut", "sentul", "jalan ipoh", "mont kiara", "sri hartamas", "batu caves", "wangsa maju", "danau kota", "taman melati", "semarak", "ampang hilir", "kampung pandan", "desa pandan", "maluri"]):
        return True, 700.00
        
    return False, 0.00

def respon_salah_kawasan():
    return "Maaf, lokasi pickup tersebut di luar zon operasi utama kami. Sila rujuk sales team untuk bantuan lanjut: https://wa.link/nrmesv"

def semak_tarikh_booking(tarikh_str):
    try:
        if '-' in tarikh_str and len(tarikh_str.split('-')[0]) == 4:
            tarikh_booking = datetime.strptime(tarikh_str, "%Y-%m-%d").date()
        else:
            tarikh_booking = datetime.strptime(tarikh_str, "%d-%m-%Y").date()
            
        tarikh_semasa = datetime.now().date()
        selisih_hari = (tarikh_booking - tarikh_semasa).days
        
        if selisih_hari < 0:
            return "tidak_sah", "Tarikh yang dipilih sudah lepas."
        elif selisih_hari <= 7:
            return "urgent", "Maaf, untuk tempahan dalam masa 7 hari atau kurang (urgent booking), sistem tidak boleh terima. Sila berhubung terus dengan sales team kami di pautan ini: https://wa.link/nrmesv"
        else:
            return "boleh", "Tarikh disahkan lulus untuk tempahan."
    except ValueError:
        return "ralat", "Format tarikh tidak sah. Sila guna format YYYY-MM-DD atau DD-MM-YYYY."

def paparkan_borang(jenis_transfer):
    jenis_transfer = jenis_transfer.strip().lower()
    
    if "two" in jenis_transfer or "2" in jenis_transfer:
        return (
            "**BORANG MAKLUMAT SEWAAN ( TWO WAY )**\n\n"
            "- Syarikat/agensi :\n"
            "- Nama :\n"
            "- Destinasi: \n"
            "- Tarikh Pergi: \n"
            "- Mase pickup pergi : \n"
            "- Tarikh Balik: \n"
            "- Masa Pickup balik : \n"
            "- Jumlah Pax (Penumpang): "
        )
    else:
        return (
            "**BORANG MAKLUMAT SEWAAN ( ONE WAY )**\n\n"
            "- Syarikat/agensi :\n"
            "- Nama :\n"
            "- Destinasi: \n"
            "- Tarikh Pergi: \n"
            "- Mase pickup pergi : \n"
            "- Tarikh Balik: \n"
            "- Jumlah Pax (Penumpang): "
        )


# ==========================================
# MODUL KALKULATOR SEWAAN & ZON
# ==========================================

def bundar_ke_puluhan_atas(nilai):
    return math.ceil(nilai / 10.0) * 10

def kira_harga_kenderaan_sbleisure(jenis_kenderaan="bas", jenis_transfer="one_way", lokasi_ambil="ampang", jarak_km=0, tarikh_pergi=None, tarikh_balik=None, pilihan_deposit=50):
    jenis_kenderaan = jenis_kenderaan.strip().lower()
    
    # KEMASKINI: Hanya Bas sahaja dibenarkan untuk tempahan online
    if jenis_kenderaan != "bas":
        return {
            "status": "rujuk_sales",
            "mesej": f"Maaf, untuk tempahan {jenis_kenderaan.upper()}, sistem tidak boleh ambil tempahan terus. Sila berhubung terus dengan team sales kami untuk tempahan kenderaan ini: https://wa.link/nrmesv"
        }
    
    if jenis_kenderaan == "tour":
        return {
            "status": "rujuk_sales",
            "mesej": "Untuk trip jenis Tour, tempahan tidak diambil secara atas talian. Sila berhubung terus dengan sales team kami di sini: https://wa.link/nrmesv"
        }
    
    lokasi_ambil = lokasi_ambil.strip().lower()
    is_valid, harga_asas = validasi_pickup(lokasi_ambil)
    
    if not is_valid:
        return {
            "status": "salah_kawasan",
            "mesej": respon_salah_kawasan()
        }
    
    jenis_transfer = jenis_transfer.strip().lower()
    
    if jarak_km <= 30:
        jumlah_harga = harga_asas
    elif jarak_km <= 35:
        jumlah_harga = harga_asas + ((jarak_km - 30) * 30.00)
    elif jarak_km <= 40:
        jumlah_harga = harga_asas + (5 * 30.00) + ((jarak_km - 35) * 10.00)
    elif jarak_km <= 60:
        jumlah_harga = harga_asas + (5 * 30.00) + (5 * 10.00) + ((jarak_km - 40) * 7.50)
    elif jarak_km <= 80:
        jumlah_harga = harga_asas + (5 * 30.00) + (5 * 10.00) + (20 * 7.50) + ((jarak_km - 60) * 16.67)
    else:
        jarak_sederhana_max = 50
        kadar_sederhana = 10.00
        jarak_jauh = jarak_km - 80
        kadar_jauh = 8.27
        jumlah_harga = harga_asas + (jarak_sederhana_max * kadar_sederhana) + (jarak_jauh * kadar_jauh)
        
    if "two" in jenis_transfer or "2" in jenis_transfer:
        if tarikh_pergi and tarikh_balik and tarikh_pergi == tarikh_balik:
            raw_price = jumlah_harga * 1.5
        else:
            raw_price = jumlah_harga * 2.0
    else:
        raw_price = jumlah_harga

    final_price = bundar_ke_puluhan_atas(raw_price)
    
    peratus_deposit = 1.0 if pilihan_deposit == 100 else 0.5
    raw_deposit = final_price * peratus_deposit
    deposit = bundar_ke_puluhan_atas(raw_deposit) if raw_deposit % 10 != 0 else int(raw_deposit)
    
    return {
        "status": "jaya",
        "harga": int(final_price),
        "deposit": int(deposit),
        "label_deposit": f"{int(peratus_deposit * 100)}%"
    }

def respon_zulfa(hasil_kiraan):
    if hasil_kiraan["status"] in ["rujuk_sales", "salah_kawasan"]:
        return hasil_kiraan["mesej"]
    
    return (f"Anggaran harga untuk sewaan ini adalah **RM {hasil_kiraan['harga']}** (harga ini adalah *all-in* termasuk tol). "
            f"Adakah anda bersetuju dengan harga ini?")