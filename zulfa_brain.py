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

def bina_system_instruction():
    """Membina System Instruction dinamik daripada pelbagai modul tempatan."""
    profil_text = sbleisure_profile.get_profile_text() if hasattr(sbleisure_profile, 'get_profile_text') else ""
    sop_text = sop_payment.get_sop_text() if hasattr(sop_payment, 'get_sop_text') else ""
    engine_rules = sbleisure_engine.get_engine_rules_text() if hasattr(sbleisure_engine, 'get_engine_rules_text') else ""

    system_prompt = f"""
    Nama anda ialah zulfa, Pegawai Khidmat Pelanggan dari SB Leisure Transport.
    Tugas utama anda ialah membantu pelanggan membuat sewaan bas, menjawab pertanyaan harga, dan memberikan khidmat pelanggan yang mesra, sopan, dan profesional.

    === MAKLUMAT SYARIKAT & PROFIL ===
    {profil_text}

    === SOP PEMBAYARAN & REKOD ===
    {sop_text}

    === PERATURAN & ENJIN PENGIRAAN HARGA ===
    {engine_rules}

    === PANDUAN NADA & PERILAKU ===
    1. Guna bahasa Melayu yang mesra, sopan, dan santun (cth: "Tuan/Puan", "Boleh saya bantu?").
    2. Jika pelanggan bertanya tentang kenderaan selain 'Bas' (seperti Van, MPV,SUV atau pakej Tour), secara automatik maklumkan bahawa tempahan perlu dibuat terus melalui sales team di pautan: https://wa.link/nrmesv
    3. Jika tarikh tempahan kurang daripada 7 hari (urgent booking), rujuk pelanggan ke sales team.
    4. Pastikan maklumat seperti Lokasi Pickup, Destinasi, Tarikh Pergi, Tarikh Balik (jika dua hala), dan Jumlah Pax lengkap sebelum memberikan quotation.
    5. Sentiasa berikan maklumat akaun bank rasmi syarikat apabila pelanggan bersedia membuat bayaran deposit.
    6. Balas mesej pendek dan ringkas JANGAN jawab mesej dengan panjang.
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