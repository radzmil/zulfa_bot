import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Import Google GenAI SDK
from google import genai
from google.genai import types

# Import modul-modul tempatan
import sbleisure_profile
import sop_payment
import sbleisure_engine

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()

# Setup Client Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Pangkalan Data Memori Pelanggan (JSON)
MEMORY_FILE = "zulfa_customers_memory.json"

# ==========================================
# 1. PENGURUSAN MEMORI PELANGGAN
# ==========================================

def muat_memori():
    """Membaca rekod memori pelanggan dari fail JSON."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Ralat membaca fail memori: {e}")
            return {}
    return {}

def simpan_memori(data):
    """Menyimpan rekod memori pelanggan ke fail JSON."""
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Ralat menyimpan fail memori: {e}")

def dapatkan_konteks_pelanggan(no_telefon):
    """Mengambil konteks atau sejarah perbualan pelanggan berdasarkan nombor telefon."""
    memori = muat_memori()
    return memori.get(no_telefon, {
        "nama": "",
        "status_tempahan": "baru",
        "sejarah_mesej": []
    })

def kemaskini_konteks_pelanggan(no_telefon, mesej_user, mesej_zulfa, nama=None):
    """Menyimpan perbualan baharu ke dalam memori pelanggan."""
    memori = muat_memori()
    if no_telefon not in memori:
        memori[no_telefon] = {
            "nama": nama or "",
            "status_tempahan": "baru",
            "sejarah_mesej": []
        }
    
    if nama:
        memori[no_telefon]["nama"] = nama

    # Simpan perbualan (Hadkan 10 perbualan terakhir untuk jimatkan token)
    sejarah = memori[no_telefon]["sejarah_mesej"]
    sejarah.append({"role": "user", "content": mesej_user, "timestamp": datetime.now().isoformat()})
    sejarah.append({"role": "assistant", "content": mesej_zulfa, "timestamp": datetime.now().isoformat()})
    
    if len(sejarah) > 20:  # 10 pasang perbualan
        sejarah = sejarah[-20:]
        
    memori[no_telefon]["sejarah_mesej"] = sejarah
    simpan_memori(memori)

# ==========================================
# 2. SYSTEM INSTRUCTION & INTEGRASI GEMINI
# ==========================================

def get_zulfa_persona():
    return "ANDA ADALAH ZULFA: Pembantu Khidmat Pelanggan & Perunding Tempahan Rasmi bagi SHAHRIL BASRI LEISURE ENTERPRISE. PERWATAKAN: Mesra, profesional, sopan, namun SANGAT TEGAS dalam mematuhi SOP syarikat. PANDUAN PENILAIAN INFRASTRUKTUR & TIER JALAN: Apabila pelanggan memberikan destinasi, nilai bentuk mukabumi dan laluan secara bijak (JALAN BERBUKIT: kawasan tinggi/pendakian; JALAN SEMPIT: perkampungan pedalaman/chalet tepi sungai; JALAN NORMAL: lebuh raya/bandar). Caj tambahan 15% hanya untuk Berbukit & Sempit. Jangan beritahu formula kepada pelanggan."

def bina_system_instruction():
    """Membina System Instruction dinamik daripada pelbagai modul tempatan."""
    profil_text = sbleisure_profile.get_profile_text() if hasattr(sbleisure_profile, 'get_profile_text') else ""
    sop_text = sop_payment.get_sop_text() if hasattr(sop_payment, 'get_sop_text') else ""
    engine_rules = sbleisure_engine.get_engine_rules_text() if hasattr(sbleisure_engine, 'get_engine_rules_text') else ""
    persona_text = get_zulfa_persona()

    system_prompt = f"""
    Nama anda ialah zulfa, Pegawai Khidmat Pelanggan dari SB Leisure Transport.
    Tugas utama anda ialah membantu pelanggan membuat sewaan bas, menjawab pertanyaan harga, dan memberikan khidmat pelanggan yang mesra, sopan, dan profesional.

    === MAKLUMAT SYARIKAT & PROFIL ===
    {profil_text}

    === SOP PEMBAYARAN & REKOD ===
    {sop_text}

    === PERATURAN & ENJIN PENGIRAAN HARGA ===
    {engine_rules}

    === PERSONA & PANDUAN PENILAIAN ===
    {persona_text}
    
    === PANDUAN NADA & PERILAKU ===
    1. Guna bahasa Melayu yang mesra, sopan, dan santun (cth: "Tuan/Puan", "Boleh saya bantu?").
    2. Jika pelanggan bertanya tentang kenderaan selain 'Bas' (seperti Van, MPV, SUV atau pakej Tour), secara automatik maklumkan bahawa tempahan perlu dibuat terus melalui sales team di pautan: https://wa.link/nrmesv
    3. Jika tarikh tempahan kurang daripada 7 hari (urgent booking), rujuk pelanggan ke sales team.
    4. Pastikan maklumat seperti Lokasi Pickup, Destinasi, Tarikh Pergi, Tarikh Balik (jika dua hala), dan Jumlah Pax lengkap sebelum memberikan quotation.
    5. Apabila pelanggan bersedia membuat bayaran, tanya dahulu pilihan mereka: Adakah ingin membayar melalui (1) Imbasan QR Code DuitNow atau (2) Pautan Online Banking ToyyibPay (`https://toyyibpay.com/sbl-online`), serta ingatkan mereka boleh pilih sama ada Deposit 50% atau Bayaran Penuh (Full Payment). Selepas mereka pilih, barulah berikan pilihan tersebut.
    6. Balas mesej pendek dan ringkas JANGAN jawab mesej dengan panjang.
    7. Selepas dapat mesej pertama dari pelanggan, terus tanya nak sewa bas, van, mpv atau suv, selepas customer jawab tanya untuk one way atau two way.
    8. One way terus bagi borang one way, two way terus bagi borang two way.
    9. Borang wajib diisi sebelum soalan seterusnya.
    10. Mesej seperti manusia yang natural.
    11. Mesej shortform seperti manusia contoh (nk, x, dkt, nnti, bz, sori, lg).
    12. Elakkan ulang soalan: Beritahu semak memori perbualan sebelumnya. Jika pelanggan sudah sebut jenis kenderaan (contoh: "bas") atau jenis trip, jangan tanya soalan itu lagi.
    13. Guna bahasa Melayu santai, mesra, dan pandai ambil hati pelanggan (cth: "Baik bos", "Boleh je, tak ada masalah").
    14. **PENTING (JANGAN ULANG SOALAN):** Sentiasa baca sejarah perbualan sebelum membalas. Jika pelanggan sudah beritahu jenis kenderaan (bas/mpv) atau jenis trip (one-way/two-way), JANGAN TANYA SOALAN YANG SAMA SEMULA. Terus ke langkah seterusnya (seperti minta butiran lokasi pickup/borang).
    15. Jika pelanggan tanya soalan luar jangkaan, layan dengan cerdik dan berhemah, jangan terus ulang skrip.
    16. Sentiasa pastikan respons pendek, padat, dan mesra WhatsApp.
    17. Jika pelanggan ingin menyemak status tempahan sedia ada, semak memori perbualan mereka dan beritahu status terkini tempahan mereka secara ringkas dan jelas (contoh: status sebut harga, menunggu bayaran deposit, atau telah dihantar kepada admin).
    17. **SOALAN DI LUAR KAWALAN / BUNTU:** Jika anda tidak tahu menjawab soalan pelanggan:
        - Jika status semasa adalah **DALAM WAKTU PEJABAT**, beritahu: "Baik, saya rujuk soalan ni pada pihak admin sebentar ye. Mohon tunggu sekejap."
        - Jika status semasa adalah **DI LUAR WAKTU PEJABAT / CUTI**, beritahu: "Maaf bos, sekarang di luar waktu pejabat (Isnin-Jumaat 8pg-5ptg). Pihak admin akan semak mesej Tuan/Puan esok/pada hari bekerja."

    === BORANG ONE WAY ===
    Terima kasih kerana berminat dengan perkhidmatan sewaan Mpv/Van/Bas persiaran   
    *SB Leisure *🚎

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

    ➡️Jenis sewaan (Mpv/Van/Bas) : BAS

    📌HARGA SEWAAN TERTAKLUK KEPADA JARAK DAN MASA PERJALANAN YANG DIBERIKAN📍

    T.KASIH😊

    === BORANG TWO WAY ===

    Terima kasih kerana berminat dengan perkhidmatan sewaan Mpv/Van/Bas persiaran
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

    ➡️Jenis sewaan (Mpv/Van/Bas) : 

    🔄Maklumat untuk RETURN trip :-

    Tarikh : 
    Masa : 
    Pick-up point : 
    Drop-off point : 
    Pax : 

    📌HARGA SEWAAN TERTAKLUK KEPADA JARAK DAN MASA PERJALANAN YANG DIBERIKAN📍

    T.KASIH😊
    """
    return system_prompt

def proses_mesej(no_telefon, mesej_user, nama_pelanggan=None):
    """Menerima mesej daripada pelanggan dan memulangkan respons Zulfa menggunakan Gemini 3.5 Flash Lite."""
    if not client:
        return "Ralat: GEMINI_API_KEY tidak dikonfigurasikan dengan betul."

    # 1. Dapatkan sejarah perbualan pelanggan
    data_pelanggan = dapatkan_konteks_pelanggan(no_telefon)
    sejarah = data_pelanggan.get("sejarah_mesej", [])

    # 2. Bina pesanan perbualan untuk Gemini API
    contents = []
    for h in sejarah:
        contents.append(types.Content(
            role=h["role"],
            parts=[types.Part.from_text(text=h["content"])]
        ))
    
    # Tambah mesej terkini daripada pengguna
    contents.append(types.Content(
        role="user",
        parts=[types.Part.from_text(text=mesej_user)]
    ))

    # 3. Tetapkan Konfigurasi LLM
    system_instruction = bina_system_instruction()
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.3,
        max_output_tokens=1000
    )

    try:
        # 4. Panggil model Gemini 3.5 Flash Lite
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents,
            config=config
        )
        
        jawapan_zulfa = response.text.strip()

        # 5. Kemaskini memori perbualan
        kemaskini_konteks_pelanggan(no_telefon, mesej_user, jawapan_zulfa, nama=nama_pelanggan)

        return jawapan_zulfa

    except Exception as e:
        logging.error(f"Ralat semasa memproses mesej Gemini: {e}")
        return "Maaf, sistem mengalami sedikit gangguan teknikal. Sila cuba sebentar lagi atau hubungi pegawai kami."

    from datetime import datetime
import pytz  # Pastikan pytz ada atau guna masa tempatan Malaysia

def bina_system_instruction():
    """Membina System Instruction dinamik daripada pelbagai modul tempatan."""
    profil_text = sbleisure_profile.get_profile_text() if hasattr(sbleisure_profile, 'get_profile_text') else ""
    sop_text = sop_payment.get_sop_text() if hasattr(sop_payment, 'get_sop_text') else ""
    engine_rules = sbleisure_engine.get_engine_rules_text() if hasattr(sbleisure_engine, 'get_engine_rules_text') else ""
    persona_text = get_zulfa_persona()

    # Baca nota tambahan daripada admin jika ada
    admin_notes = ""
    if os.path.exists("admin_memory.txt"):
        with open("admin_memory.txt", "r", encoding="utf-8") as f:
            admin_notes = f.read()

    # SEMAKAN MASA REAL-TIME MALAYSIA
    tz_malaysia = pytz.timezone('Asia/Kuala_Lumpur')
    sekarang = datetime.now(tz_malaysia)
    hari_ini = sekarang.strftime('%A') # Contoh: Monday, Tuesday, etc.
    jam_semasa = sekarang.strftime('%H:%M')
    angka_hari = sekarang.weekday() # 0=Isnin hingga 4=Jumaat, 5=Sabtu, 6=Ahad
    jam_angka = sekarang.hour

    # Tentukan status waktu pejabat (Isnin-Jumaat, 8 pagi - 5 petang)
    is_waktu_pejabat = True
    if angka_hari >= 5: # Sabtu atau Ahad
        is_waktu_pejabat = False
    elif jam_angka < 8 or jam_angka >= 17: # Sebelum 8 pagi atau selepas 5 petang
        is_waktu_pejabat = False

    status_waktu = "DALAM WAKTU PEJABAT (Isnin-Jumaat, 8pg-5ptg)" if is_waktu_pejabat else "DI LUAR WAKTU PEJABAT / CUTI (Sabtu/Ahad atau selepas 5ptg)"

    system_prompt = f"""
    Nama anda ialah zulfa, Pegawai Khidmat Pelanggan dari SB Leisure Transport.
    Tugas utama anda ialah membantu pelanggan membuat sewaan bas, menjawab pertanyaan harga, dan memberikan khidmat pelanggan yang mesra, sopan, dan profesional.

    === STATUS MASA SEMASA (REAL-TIME) ===
    - Hari & Masa: {hari_ini}, {jam_semasa} (Waktu Malaysia)
    - Status: {status_waktu}

    === NOTA KAS & ARAHAN TERKINI DARIPADA ADMIN ===
    {admin_notes}
    ...