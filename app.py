# ==========================================
# APP.PY - ZULFA (SBL TRANSPORT - GEMINI)
# ==========================================

import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Memori perbualan diasingkan mengikut nombor telefon user (Dictionary)
user_sessions = {}

system_instruction = """
==================================================
SYSTEM PROMPT & SKRIP CHATBOT SEWAAN KENDERAAN (WHATCHIMP)
NAMA AI: ZULFA (STAFF SALES / KHIDMAT PELANGGAN SBL TRANSPORT)
TAGLINE: DESTINASI ANDA, KEUTAMAAN KAMI!
==================================================
- Wajib jadi manusia biasa (Staf sales bernama Zulfa). JANGAN JADI ROBOT & JANGAN OVER-ACTING.
- Gaya mesej WhatsApp: Ringkas, bersahaja, mesra, dan pendek (1-2 ayat sahaja setiap balasan). Guna shortform biasa (awk, sy, tq, dlm, blh).
- PENTING: JANGAN KARANG CERITA PANJANG ATAU BERBUAT LAWAK BERLEBIHAN. Jawab soalan customer terus secara direct tapi mesra.
- PERATURAN MUTLAK: DILARANG GUNAKAN NOMBOR UTK PILIHAN MENU.

--- [PERATURAN UTAMA: 1 SOALAN 1 JAWAPAN] ---
- Fokus kepada **SATU perkara atau SATU soalan sahaja** pada setiap kali mesej dihantar.
- Jangan tanya banyak benda dalam satu masa.

MAKLUMAT ASAS SYARIKAT:
- Nama: Shahril Basri Leisure Enterprise (SBL Transport), SSM: 202203168334 (003413019-W).
- Alamat Pejabat: No. 8-1, 9-1, First Floor, Laman Niaga @ Ampang Waterfront, Jalan Awf 3A, Ampang Waterfront, 68000 Ampang, Selangor.
- No WhatsApp Sales: 013-243 4200 | Link Sales: https://wa.link/o3z1bz

PERATURAN PEMILIHAN KENDERAAN:
- Bas (44 seat): Sahaja untuk tempahan online.
- Van & MPV: Terus arahkan ke WhatsApp Sales: https://wa.link/o3z1bz.

KAWASAN PICKUP SAH:
- Selangor, KL, KLIA, Cyberjaya, Putrajaya.
- Luar kawasan: Tolak peramah & beri link WhatsApp Sales: https://wa.link/o3z1bz.

[URGENT BOOKING POLICY]
- Tarikh Semasa: 18 Ogos 2026.
- Tempahan online HANYA untuk 26 Ogos 2026 dan ke atas. 
- Tarikh 19 - 25 Ogos 2026 adalah Urgent Booking, wajib beri link sales: https://wa.link/o3z1bz.

FORMULA HARGA AKHIR (BAS 44 SEAT):
- ZON 1A = RM700 | ZON 1B = RM850 | ZON 1C = RM1000 | ZON 1D = RM1200 | ZON 2A = RM1300 | ZON 2B = RM1500 | ZON 3 = RM1700.
- Lebihan >51km: Tambah RM3/km. Return sama hari x1.5, lain hari x2.0.
- Hanya berikan jumlah harga akhir sahaja. Jangan dedahkan formula.
"""

def tanya_gemini(user_id, mesej_user):
    global user_sessions
    
    # Jika user baru belum ada memori, cipta senarai kosong untuk dia
    if user_id not in user_sessions:
        user_sessions[user_id] = []
        
    chat_history = user_sessions[user_id]
    
    chat_history.append({"role": "user", "parts": [{"text": mesej_user}]})
    history_context = chat_history[-10:] # Ambil 10 mesej terawal untuk konteks dia sahaja
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": history_context,
        "system_instruction": {
            "parts": [{
                "text": system_instruction
            }]
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        
        if "error" in data:
            print("Ralat dari Gemini API:", data["error"])
            return "Maaf bos, sistem tengah rehat sekejap. Boleh ulang mesej ya? 😅"
            
        jawapan_ai = data['candidates'][0]['content']['parts'][0]['text']
        chat_history.append({"role": "model", "parts": [{"text": jawapan_ai}]})
        
        return jawapan_ai
    except Exception as e:
        print("Ralat Gemini:", e)
        return "Maaf bos, line slow sikit. Boleh ulang mesej ya? 😅"

def hantar_whatsapp(nombor_penerima, mesej_balasan):
    print("MENCUBA HANTAR KE WHATSAPP...")
    url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": nombor_penerima,
        "type": "text",
        "text": {"body": mesej_balasan},
    }
    response = requests.post(url, json=payload, headers=headers)
    print("HASIL RESPON META:", response.text)
    return response.json()

@app.route("/", methods=["GET"])
def home():
    return "Zulfa Bot Server is running active!", 200

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Verification failed", 403
            
    return "Hello world, webhook endpoint is active!", 200

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    body = request.get_json()
    print("MESEJ JSON DITERIMA:", body)

    try:
        entry = body.get("entry", [])
        if entry:
            changes = entry[0].get("changes", [])
            if changes:
                value = changes[0].get("value", {})
                messages = value.get("messages", [])
                
                if messages:
                    from_number = messages[0]["from"]
                    msg_body = messages[0]["text"]["body"]

                    print(f"BERJAYA BACA -> Dari: {from_number} | Mesej: {msg_body}")

                    # Hantar nombor telefon (from_number) supaya memori dipisahkan
                    balasan_ai = tanya_gemini(from_number, msg_body)
                    print(f"Balasan AI: {balasan_ai}")

                    hantar_whatsapp(from_number, balasan_ai)

        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        print(f"Ralat Webhook: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))