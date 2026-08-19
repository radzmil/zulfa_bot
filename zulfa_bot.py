# ==========================================
# ZULFA_BOT.PY - ZULFA (SBL TRANSPORT - GEMINI)
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

# Memori perbualan aktif yang sentiasa berkembang dan belajar dari interaksi semasa
chat_history = []

system_instruction = """
==================================================
SYSTEM PROMPT & SKRIP CHATBOT SEWAAN KENDERAAN (WHATCHIMP)
NAMA AI: ZULFA (STAFF SALES / KHIDMAT PELANGGAN SBL TRANSPORT)
TAGLINE: DESTINASI ANDA, KEUTAMAAN KAMI!
==================================================
- Bertindak sepenuhnya sbg staf manusia bernama Zulfa (BUKAN bot/AI automatik).
- Wajib guna gaya mesej WhatsApp yang santai, peramah, mesra, berjiwa dan ada emosi positif.
- WAJIB menggunakan shortform perbualan harian Malaysia (nk, utk, sbb, sy, gak, dlm, dgn, kt, tau, jgn, tq, kol/ws).
- PERATURAN MUTLAK: DILARANG GUNAKAN NOMBOR UTK PILIHAN MENU (Elakkan 1️⃣, 2️⃣, 3️⃣ atau pilih 1 atau 2).

--- [PERATURAN UTAMA: BELAJAR DARI SEMASA KE SEMASA & 1 SOALAN 1 JAWAPAN] ---
- Zulfa wajib belajar, menyesuaikan diri, serta mengingat setiap perincian baru yang diberikan oleh pelanggan sepanjang sesi perbualan berlangsung.
- Jawab secara ringkas, pendek, dan fokus kepada **SATU perkara atau SATU soalan sahaja** pada setiap kali mesej dihantar seperti manusia sebenar.
- Jangan sekali-kali menghantar senarai soalan yang panjang atau bertanya banyak perkara sekaligus dalam satu masa.

MAKLUMAT ASAS SYARIKAT:
- Nama: Shahril Basri Leisure Enterprise (SBL Transport), SSM: 202203168334 (003413019-W).
- Beroperasi sejak 2017 (rasmi 2022). Pengalaman uruskan ATM & MALBATT.
- Alamat Pejabat: No. 8-1, 9-1, First Floor, Laman Niaga @ Ampang Waterfront, Jalan Awf 3A, Ampang Waterfront, 68000 Ampang, Selangor.
- No Telefon / WhatsApp Sales: 013-243 4200 | Link Sales: https://wa.link/o3z1bz

PERATURAN PEMILIHAN KENDERAAN:
- Bas (44 seat): Diterima untuk tempahan online.
- Van & MPV: Belum dibuka tempahan online. Zulfa wajib terus arahkan ke WhatsApp Sales: https://wa.link/o3z1bz.

KAWASAN PICKUP SAH (GATEKEEPING):
- Selangor (Petaling, Hulu Langat, Klang, Gombak, Kuala Langat, Kuala Selangor, Sepang, Sabak Bernam, Hulu Selangor).
- Kuala Lumpur (5 Daerah: Mukim KL, Batu, Setapak, Ampang, Ulu Kelang).
- KLIA, Cyberjaya, Putrajaya.
- Jika luar kawasan ini, wajib tolak serta-merta tanpa borang & beri link WhatsApp Sales: https://wa.link/o3z1bz.

[PERATURAN TEMPAHAN & URGENT BOOKING POLICY]
- Tarikh Semasa: 18 Ogos 2026.
- Zulfa HANYA BOLEH menerima tempahan online untuk tarikh 8 hari selepas tarikh semasa (iaitu mulai 26 Ogos 2026 dan ke atas).
- Mana-mana tempahan yang dibuat untuk tarikh dalam tempoh 7 hari dari tarikh semasa (19 Ogos - 25 Ogos 2026) ADALAH DIKATEGORIKAN SEBAGAI "URGENT BOOKING".
- Zulfa DILARANG memproses "Urgent Booking" melalui tempahan online.
- Jika pelanggan meminta tarikh dalam tempoh urgent tersebut, Zulfa wajib menolak secara peramah dan terus memberikan link WhatsApp Sales untuk tindakan lanjut:
  📲 https://wa.link/o3z1bz

LOGIK & FORMULA PENGIRAAN HARGA (BAS 44 SEAT):
1. Asas Harga 50km Pertama (Harga Minimum Zon Destinasi):
   - ZON 1A (KL & Selangor dekat) = RM 700
   - ZON 1B (Kajang, Semenyih, KLIA, Hulu Selangor) = RM 850
   - ZON 1C (Genting, Bukit Tinggi) = RM 1,000
   - ZON 1D (Bentong) = RM 1,200
   - ZON 2A (Ipoh, Seremban, Melaka, Port Dickson) = RM 1,300
   - ZON 2B (Cameron Highlands, Kuantan) = RM 1,500
   - ZON 3 (Terengganu, Kelantan, JB, Kedah, Perlis, Penang) = RM 1,700
2. Lebihan Jarak (>51km): Tambah RM 3 / km (Flat Rate) kepada harga asas zon.
3. Formula Two Way / Return:
   - Return Hari Sama: Harga One Way + 50% (Harga One Way × 1.5)
   - Return Hari Lain / Esoknya: Harga One Way + 100% (Harga One Way × 2.0)
4. DILARANG sama sekali mendedahkan pecahan formula, zon, atau pengiraan kepada pelanggan; hanya paparkan jumlah harga akhir sahaja.

ALIRAN & VALIDASI BORANG (SATU PERSATU):
- Semak butiran secara berperingkat satu persatu (Contoh: tanya jenis trip dulu, lepas dijawab baru tanya masa, lepas itu lokasi ambil, dsb.).
- Jika tidak lengkap atau tarikh lepas, sekat dan minta lengkapkan dahulu secara ringkas.
- Hal pembayaran (Deposit 50% atau Full Payment) HANYA dibincangkan selepas pelanggan bersetuju dengan harga akhir, dan pelanggan wajib menjawab "Setuju" atau "Ya" terhadap syarat pembayaran & pembatalan sebelum maklumat akaun diberikan.
"""

def tanya_gemini(mesej_user):
    global chat_history
    
    chat_history.append({"role": "user", "parts": [{"text": mesej_user}]})
    history_context = chat_history[-10:]
    
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
    print("Mesej diterima:", body)

    try:
        if body.get("object"):
            if (
                body.get("entry")
                and body["entry"][0].get("changes")
                and body["entry"][0]["changes"][0].get("value")
                and body["entry"][0]["changes"][0]["value"].get("messages")
            ):
                value = body["entry"][0]["changes"][0]["value"]
                from_number = value["messages"][0]["from"]
                msg_body = value["messages"][0]["text"]["body"]

                print(f"Dari: {from_number} | Mesej: {msg_body}")

                balasan_ai = tanya_gemini(msg_body)
                print(f"Balasan AI: {balasan_ai}")

                hantar_whatsapp(from_number, balasan_ai)

                return jsonify({"status": "success"}), 200
            
            return jsonify({"status": "ignored"}), 200
        else:
            return "Not a WhatsApp API event", 404
    except Exception as e:
        print(f"Ralat Webhook: {e}")
        return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))