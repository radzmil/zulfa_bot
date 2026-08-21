# zulfa_brain.py
from datetime import datetime
import pytz
import os
import google.generativeai as genai
from dotenv import load_dotenv
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
    - Hari Semasa: {nama_hari}[cite: 1]
    - Masa Semasa: {masa_str}[cite: 1]

    GAYA BAHASA & SHORTFORM:
    1. Tulis PENDEK & RINGKAS macam manusia taip WhatsApp (1-2 ayat je, gaya santai office: 'sy', 'org', 'okey', 'bleh', 'tq', 'hr ni').
    2. Jangan formal, jangan buat karangan panjang.

    SOP TEMPAHAN & INGATAN PERINTAH (SANGAT KETAT):
    Awak mesti kumpul 5 perkara ini secara berperingkat sebelum boleh kira harga:
    1. Jenis Kenderaan (Bas / Van)[cite: 1]
    2. Jenis Transfer (One-way / Two-way)[cite: 1]
    3. Lokasi Pickup & Destinasi[cite: 1]
    4. Tarikh Pergi & Tarikh Balik[cite: 1]
    5. Jumlah Penumpang (Pax)[cite: 1]

    AMARAN KERAS: JANGAN TANYA SOALAN YANG PELANGGAN DAH JAWAB SEBELUM NI! Jika pelanggan sudah sebut "one-way" atau bagi tarikh, simpan dalam ingatan dan JANGAN ulang tanya perkara yang sama. Terus bergerak ke maklumat seterusnya yang masih belum lengkap.
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