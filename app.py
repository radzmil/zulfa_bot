# ==========================================
# APP.PY - ZULFA (SBL TRANSPORT - MANUAL QR + ADMIN VERIFICATION)
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
GROUP_ADMIN_NUMBER = os.getenv("GROUP_ADMIN_NUMBER")

# Simpan status tempahan pelanggan (Menunggu bayaran / Selesai)
pending_payments = {}
user_sessions = {}

system_instruction = """
==================================================
SYSTEM PROMPT & SKRIP CHATBOT (ZULFA - SBL TRANSPORT)
==================================================
- PERANAN: Zulfa, staf sales mesra, ringkas, bersahaja (Guna: awk, sy, tq, blh).
- TUGAS UTAMA: Bantu pelanggan sewa MPV/Van/Bas.
- TARIKH SEMASA: 19 Ogos 2026.
- FLOW TEMPAHAN:
    1. Selepas pelanggan isi borang, Zulfa WAJIB tanya untuk PENGESAHAN: 
       "Awk pasti dengan maklumat ni? Kalau setuju, taip 'Submit Booking' untuk kami proses."
    2. Jika pelanggan taip 'Submit Booking':
       a. Zulfa sahkan tempahan, berikan arahan bayar guna QR, dan minta jadikan nombor telefon sebagai rujukan.
"""

def hantar_whatsapp(nombor_penerima, mesej_balasan):
    url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": nombor_penerima, "type": "text", "text": {"body": mesej_balasan}}
    requests.post(url, json=payload, headers=headers)

def hantar_ke_admin(detail_booking):
    if GROUP_ADMIN_NUMBER:
        url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_ID}/messages"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": GROUP_ADMIN_NUMBER,
            "type": "text",
            "text": {"body": detail_booking},
        }
        requests.post(url, json=payload, headers=headers)

def tanya_gemini(user_id, mesej_user):
    global user_sessions, pending_payments
    if user_id not in user_sessions: user_sessions[user_id] = []
    
    chat_history = user_sessions[user_id]
    chat_history.append({"role": "user", "parts": [{"text": mesej_user}]})
    
    # Jika pelanggan ketik Submit Booking
    if "submit booking" in mesej_user.lower():
        detail_sewaan = "".join([m["parts"][0]["text"] for m in chat_history if m["role"]=="user"][-3:])
        pending_payments[user_id] = {"detail": detail_sewaan, "status": "menunggu_bayaran"}
        
        # Hantar maklumat awal ke group admin dengan rujukan nombor telefon
        hantar_ke_admin(f"--- TEMPAHAN BARU (MENUNGGU BAYARAN) ---\nNo Rujukan / Tel: {user_id}\n\n{detail_sewaan}")
        
        return (
            "Booking diterima! Sila buat pembayaran deposit/penuh ke akaun syarikat kami.\n\n"
            "📱 *Sila jadikan nombor telefon awk sebagai rujukan pembayaran.*\n\n"
            "Selepas selesai bayar, sila beritahu saya (cth: 'dah bayar') dan hantar resit di sini ya."
        )

    # Jika pelanggan cakap dah bayar
    if "dah bayar" in mesej_user.lower() or "sudah bayar" in mesej_user.lower():
        pending_payments[user_id] = pending_payments.get(user_id, {})
        pending_payments[user_id]["status"] = "semak_admin"
        
        # Maklumkan kepada group admin untuk semak pembayaran
        hantar_ke_admin(
            f"🔔 SEMAKAN PEMBAYARAN DIPERLUKAN!\n"
            f"Pelanggan dengan No Tel / Rujukan: {user_id} mendakwa sudah membuat pembayaran.\n"
            f"Sila semak akaun bank.\n\n"
            f"Balas 'done {user_id}' dalam group ni jika duit sudah masuk."
        )
        return "Baik awk! Terima kasih. Saya sedang semak dengan pihak admin kami. Sila tunggu sebentar ya."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": chat_history[-10:], "system_instruction": {"parts": [{"text": system_instruction}]}}
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        jawapan_ai = response.json()['candidates'][0]['content']['parts'][0]['text']
        chat_history.append({"role": "model", "parts": [{"text": jawapan_ai}]})
        return jawapan_ai
    except:
        return "Maaf, sistem sedang sibuk."

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Forbidden", 403
    
    body = request.get_json()
    try:
        msg = body["entry"][0]["changes"][0]["value"]["messages"][0]
        from_number = msg["from"]
        msg_body = msg["text"]["body"]
        
        # Semak adakah mesej ini datang dari GROUP ADMIN
        if GROUP_ADMIN_NUMBER and from_number == GROUP_ADMIN_NUMBER:
            # Jika admin balas dengan format "done [nombor_telefon]"
            if msg_body.lower().startswith("done"):
                parts = msg_body.split()
                if len(parts) > 1:
                    target_customer = parts[1]
                    # Hantar mesej pengesahan kepada pelanggan tersebut
                    hantar_whatsapp(
                        target_customer, 
                        "Alhamdulillah! Pembayaran anda telah disahkan oleh admin. Tempahan anda kini sah dan berjaya diproses! 🎉"
                    )
                    hantar_ke_admin(f"✅ Sistem berjaya memaklumkan kepada pelanggan {target_customer} bahawa bayaran telah diterima.")
            return jsonify({"status": "success"}), 200

        # Jika mesej dari pelanggan biasa
        balasan = tanya_gemini(from_number, msg_body)
        hantar_whatsapp(from_number, balasan)
        
    except Exception as e:
        print(f"Ralat webhook: {e}")
        pass
        
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))