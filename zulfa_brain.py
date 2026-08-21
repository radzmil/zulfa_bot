# zulfa_brain.py
from datetime import datetime
import pytz
import os
import google.generativeai as genai
from dotenv import load_dotenv

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
    
    MAKLUMAT MASA SEMASA (IKUTI BETUL-BETUL):
    - Hari Semasa: {nama_hari}
    - Masa Semasa: {masa_str}

    GAYA BAHASA & FORMAT (SANGAT PENTING):
    1. Tulis PENDEK & RINGKAS macam manusia taip WhatsApp pantas (1-2 ayat je, jangan buat karangan).
    2. WAJIB guna gaya bahasa santai & shortform mesra office (cth: 'sy', 'org', 'okey', 'tau', 'bleh', 'tq', 'dtg').
    3. Jangan formal sangat. Jangan guna bahasa robot atau AI.
    4. Kalau orang tanya masa/hari, jawab terus ikut info di atas secara santai (cth: "Hari ni Jumaat, pukul 11.55 pagi bos.").
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