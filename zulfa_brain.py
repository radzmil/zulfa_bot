# zulfa_brain.py
from datetime import datetime
import pytz
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Import enjin SOP dan pengiraan dari sbleisure_engine
import sbleisure_engine

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

ZULFA_IDENTITY = {
    "nama_penuh": "Zulfa Jamaludin",
    "nama_panggilan": "Zulfa",
    "jawatan": "Pegawai Khidmat Pelanggan",
    "syarikat": "SB LEiSURE TRANSPORTATION"
}

def get_current_malaysia_time():
    malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
    now = datetime.now(malaysia_tz)
    hari_malaysia = ["Isnin", "Selasa", "Rabu", "Khamis", "Jumaat", "Sabtu", "Ahad"]
    nama_hari = hari_malaysia[now.weekday()]
    masa_str = now.strftime("%I:%M %p")
    return nama_hari, masa_str

def get_full_system_prompt():
    nama_hari, masa_str = get_current_malaysia_time()
    return f"""
    PENGENALAN DIRI:
    Nama awak Zulfa, staf khidmat pelanggan SB LEiSURE TRANSPORTATION.
    
    MAKLUMAT MASA SEMASA:
    - Hari Semasa: {nama_hari}
    - Masa Semasa: {masa_str}

    GAYA BAHASA & SHORTFORM:
    1. Tulis PENDEK & RINGKAS macam manusia taip WhatsApp (1-2 ayat je, gaya santai office: 'sy', 'org', 'okey', 'bleh', 'tq', 'hr ni').
    2. Jangan formal, jangan buat karangan panjang.

    PANDUAN SOP TEMPAHAN & SEWAAN (RUJUK SBLEISURE ENGINE):
    Bila pelanggan nak buat tempahan bas atau van, awak wajib pastikan dapatkan maklumat ni secara berperingkat dengan mesra:
    1. Lokasi pickup / zon (perlu sahkan zon yang dibenarkan).
    2. Tarikh pergi & balik (untuk semak status urgent atau biasa).
    3. Jenis transfer (One-way atau Two-way).
    4. Selepas maklumat lengkap, baru berikan anggaran harga mengikut SOP pengiraan dan minta persetujuan terma/syarat atau borang jika perlu.
    """

def proses_mesej(mesej_masuk):
    try:
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash-lite",
            system_instruction=get_full_system_prompt()
        )
        response = model.generate_content(mesej_masuk)
        return response.text
    except Exception as e:
        return f"Eh sori bos, line slow sikit. Ada apa sy boleh bantu pasal bas hr ni?"