# ==========================================
# FAIL: zulfa_brain.py (DIKEMASKINI)
# MODUL UTAMA OTAK AI ZULFA (GEMINI)
# ==========================================
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

import tempat_menarik
import info_jalan
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

    sejarah = memori[no_telefon]["sejarah_mesej"]
    sejarah.append({"role": "user", "content": mesej_user, "timestamp": datetime.now().isoformat()})
    sejarah.append({"role": "assistant", "content": mesej_zulfa, "timestamp": datetime.now().isoformat()})
    
    if len(sejarah) > 20:  
        sejarah = sejarah[-20:]
        
    memori[no_telefon]["sejarah_mesej"] = sejarah
    simpan_memori(memori)

# ==========================================
# 2. SYSTEM INSTRUCTION & INTEGRASI GEMINI
# ==========================================

def get_zulfa_persona():
    return "ANDA ADALAH ZULFA: Pembantu Khidmat Pelanggan & Perunding Tempahan Rasmi bagi SHAHRIL BASRI LEISURE ENTERPRISE. PERWATAKAN: Mesra, profesional, sopan, tegas, dan ULTRA-RINGKAS (fokus jimat kos API Meta)."

def bina_system_instruction():
    """Membina System Instruction dinamik daripada pelbagai modul tempatan."""
    profil_text = sbleisure_profile.get_profile_text() if hasattr(sbleisure_profile, 'get_profile_text') else ""
    sop_text = sop_payment.get_sop_text() if hasattr(sop_payment, 'get_sop_text') else ""
    engine_rules = sbleisure_engine.get_engine_rules_text() if hasattr(sbleisure_engine, 'get_engine_rules_text') else ""
    persona_text = get_zulfa_persona()

    admin_notes = ""
    if os.path.exists("admin_memory.txt"):
        with open("admin_memory.txt", "r", encoding="utf-8") as f:
            admin_notes = f.read()

    try:
        import pytz
        tz_malaysia = pytz.timezone('Asia/Kuala_Lumpur')
        sekarang = datetime.now(tz_malaysia)
    except Exception:
        sekarang = datetime.now()

    hari_ini = sekarang.strftime('%A') 
    jam_semasa = sekarang.strftime('%H:%M')
    angka_hari = sekarang.weekday() 
    jam_angka = sekarang.hour

    is_waktu_pejabat = True
    if angka_hari >= 5: 
        is_waktu_pejabat = False
    elif jam_angka < 8 or jam_angka >= 17: 
        is_waktu_pejabat = False

    status_waktu = "DALAM WAKTU PEJABAT" if is_waktu_pejabat else "DI LUAR WAKTU PEJABAT"

    system_prompt = f"""
    Nama anda ialah zulfa, Pegawai Khidmat Pelanggan SB Leisure Transport.
    
    === STATUS MASA SEMASA ===
    - Masa: {hari_ini}, {jam_semasa} ({status_waktu})

    === MAKLUMAT & SOP ===
    {profil_text}
    {sop_text}
    {engine_rules}
    {persona_text}
    
    === PERATURAN MUTLAK KOS META & KELAJUAN (WAJIB PATUH) ===
    1. **JAWAP ULTRAPENDEK & PADAT:** Mesej WhatsApp caj dikira per hantaran. Dilarang meleret-leret atau melalut. Jawab dalam 1 hingga 2 ayat sahaja jika boleh.
    2. **HANYA HARGA AKHIR SAHAJA:** Berikan terus harga muktamad (cth: "Harga sewaan ke Ipoh ialah RM1,780"). Jangan sebut formula, jarak, kos asas, atau pecahan langsung.
    3. **TIADA TAWAR-MENAWAR:** Jika pelanggan minta kurang harga atau tawar-menawar, terus balas ringkas: "Maaf bos, harga fixed. Nak proceed boleh hubungi team sales kami di https://wa.link/nrmesv".
    4. **GATEKEEPING PICKUP:** Pickup hanya Selangor, KL, Putrajaya, Cyberjaya, KLIA sahaja. Luar kawasan, terus tolak dan beri link: https://wa.link/nrmesv.
    5. **HANYA BAS SAJA ONLINE:** Van, MPV, SUV tidak diterima online, terus beri link: https://wa.link/nrmesv.
    6. **ALIRAN BORANG PANTAS:** Mesej pertama tanya sewa apa (bas/lain), terus tanya one-way atau two-way, terus berikan borang ringkas yang berkaitan. Jangan ulang soalan jika info sudah ada dalam memori.
    7. Gunakan bahasa Melayu santai ringkas (cth: "baik bos", "ok", "nk", "x").
    
    === NOTA ADMIN ===
    {admin_notes}

    === BORANG ONE WAY ===
    📝 *BORANG SEWAAN ONE WAY*
    Syarikat: 
    Nama: 
    No. tel: 
    Tarikh & Masa: 
    Pick-up: 
    Drop-off: 
    Pax: 
    Jenis: BAS
    T.KASIH 😊

    === BORANG TWO WAY ===
    📝 *BORANG SEWAAN TWO WAY*
    Syarikat/Nama: 
    No. tel: 
    Trip Pergi (Tarikh/Masa/Pick/Drop/Pax): 
    Trip Balik (Tarikh/Masa/Pick/Drop/Pax): 
    Jenis: BAS
    T.KASIH 😊
    """
    return system_prompt

def proses_mesej(no_telefon, mesej_user, nama_pelanggan=None):
    """Menerima mesej daripada pelanggan dan memulangkan respons Zulfa menggunakan Gemini."""
    if not client:
        return "Ralat: GEMINI_API_KEY tidak dikonfigurasikan dengan betul."

    message_lower = mesej_user.lower()
    
    if any(kunci in message_lower for kunci in ["bukit", "sempit", "sungai", "riadah", "rekreasi"]):
        info_jalan_khas = info_jalan.semak_struktur_jalan_khas(mesej_user)
        if info_jalan_khas:
            return f"🚌 Info Laluan ({info_jalan_khas['kategori']}): {info_jalan_khas['panduan_bas']}. Teruskan dengan jumlah pax?"

    data_pelanggan = dapatkan_konteks_pelanggan(no_telefon)
    sejarah = data_pelanggan.get("sejarah_mesej", [])

    contents = []
    for h in sejarah:
        contents.append(types.Content(
            role=h["role"],
            parts=[types.Part.from_text(text=h["content"])]
        ))
    
    contents.append(types.Content(
        role="user",
        parts=[types.Part.from_text(text=mesej_user)]
    ))

    system_instruction = bina_system_instruction()
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,
        max_output_tokens=300
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents,
            config=config
        )
        
        jawapan_zulfa = response.text.strip()
        kemaskini_konteks_pelanggan(no_telefon, mesej_user, jawapan_zulfa, nama=nama_pelanggan)
        return jawapan_zulfa

    except Exception as e:
        logging.error(f"Ralat semasa memproses mesej Gemini: {e}")
        return "Maaf, sistem tergendala sebentar. Sila cuba lagi."