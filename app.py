import os
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS  # Penting untuk benarkan LEEA Portal berhubung dengan Flask
from dotenv import load_dotenv

# Muat turun pembolehubah persekitaran daripada fail .env
load_dotenv()

# Import modul projek Zulfa Bot
import zulfa_brain
import sbleisure_engine
import sop_payment

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
CORS(app)  # Aktifkan CORS supaya Vercel frontend boleh akses API Flask di Railway

# Senarai kata kunci untuk mengesan permintaan QR Code daripada pelanggan
KEYWORDS_QR = ["qr", "qr code", "qrcode", "duitnow", "cimb qr", "nak qr", "gambar qr"]

# Senarai kata kunci untuk mengesan penghantaran resit / bayaran selesai
KEYWORDS_BAYARAN = ["resit", "dah bayar", "selesai bayar", "payment done", "bukti bayar", "bank in"]

# Simulasi database memori sementara untuk Live Chat & Kawalan Bot di LEEA Portal
# Anda boleh tukar sambungkan ke database sebenar (cth: SQLite/PostgreSQL) nanti
live_chats_db = [
    {
        "id": 1,
        "customerName": "Ahmad bin Ali",
        "phone": "+60123456789",
        "lastMessage": "Berapa harga pakej sebulan?",
        "time": "11:02 AM",
        "mode": "ai", # Pilihan: 'ai' atau 'human'
        "messages": [
            {"sender": "customer", "text": "Hi, selamat tengah hari.", "time": "11:00 AM"},
            {"sender": "client", "text": "Hi Ahmad, ada apa yang boleh saya bantu?", "time": "11:01 AM"},
            {"sender": "customer", "text": "Berapa harga pakej sebulan?", "time": "11:02 AM"}
        ]
    }
]

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "bot_name": "Zulfa - Shahril Basri Leisure Enterprise Bot",
        "version": "2.2"
    }), 200

# ==========================================
# LALUAN API UNTUK LEEA PORTAL (VERCEL)
# ==========================================

# 1. Tarik senarai klien untuk tab Dashboard
@app.route("/api/clients", methods=["GET"])
def get_clients_data():
    try:
        senarai_client = [
            {
                "ref_id": "SB-4200",
                "nama": "Pelanggan Contoh",
                "no_tel": "+60132434200",
                "tarikh": "2026-08-27",
                "status": "Aktif / Selesai"
            }
        ]
        return jsonify({"status": "success", "data": senarai_client}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 2. Tarik senarai Live Chats & Mesej untuk Tab Live Chat & Kawalan Bot
@app.route("/api/chats", methods=["GET"])
def get_chats():
    try:
        return jsonify({"success": True, "chats": live_chats_db}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 3. Hantar Mesej Balasan Manual daripada Ejen Portal ke WhatsApp Pelanggan
@app.route("/api/chats/reply", methods=["POST"])
def reply_chat():
    try:
        data = request.json
        chat_id = data.get('chat_id')
        reply_text = data.get('text')
        target_phone = data.get('phone') # Nombor WhatsApp penerima

        # Hantar mesej sebenar melalui WhatsApp Cloud API
        if target_phone and reply_text:
            hantar_teks_whatsapp(target_phone, reply_text)

        # Kemaskini simpanan data live_chats_db
        for chat in live_chats_db:
            if chat['id'] == chat_id:
                chat['messages'].append({"sender": "client", "text": reply_text, "time": datetime.now().strftime('%I:%M %p')})
                chat['lastMessage'] = reply_text
                return jsonify({"success": True, "message": "Mesej berjaya dihantar ke WhatsApp!"}), 200
                
        return jsonify({"success": False, "error": "Chat tidak dijumpai"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# 4. Tukar Mod Bot (AI Bot <-> Human Touch) melalui Portal
@app.route("/api/chats/toggle-mode", methods=["POST"])
def toggle_mode():
    try:
        data = request.json
        chat_id = data.get('chat_id')
        
        for chat in live_chats_db:
            if chat['id'] == chat_id:
                chat['mode'] = "human" if chat['mode'] == "ai" else "ai"
                return jsonify({"success": True, "mode": chat['mode']}), 200
                
        return jsonify({"success": False, "error": "Chat tidak dijumpai"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==========================================
# WHATSAPP WEBHOOK (META)
# ==========================================

@app.route("/webhook", methods=["GET"])
def verify_whatsapp_webhook():
    verify_token_env = os.getenv("VERIFY_TOKEN", "token_rahsia_anda")
    
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode and token:
        if mode == "subscribe" and token == verify_token_env:
            logging.info("Webhook berjaya disahkan oleh Meta!")
            return challenge, 200
        else:
            return "Verification token mismatch", 403
    return "Hello, this is WhatsApp webhook endpoint", 200


@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    data = request.json
    logging.info(f"Mesej diterima: {data}")

    try:
        entry = data.get("entry", [])
        if not entry:
            return jsonify({"status": "ignored"}), 200
            
        changes = entry[0].get("changes", [])
        if not changes:
            return jsonify({"status": "ignored"}), 200
            
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return jsonify({"status": "ignored", "reason": "no messages array"}), 200

        msg_obj = messages[0]
        sender_phone = msg_obj.get("from")
        
        message_text = ""
        if msg_obj.get("type") == "text":
            message_text = msg_obj.get("text", {}).get("body", "").strip()

        message_lower = message_text.lower()

        # Semak sama ada nombor ini dalam mod 'human' di live chat portal
        current_chat_mode = "ai"
        for chat in live_chats_db:
            if chat.get("phone") == sender_phone or chat.get("phone") == f"+{sender_phone}":
                current_chat_mode = chat.get("mode", "ai")
                # Kemaskini mesej masuk ke dalam live chat db untuk paparan portal
                chat['messages'].append({"sender": "customer", "text": message_text, "time": datetime.now().strftime('%I:%M %p')})
                chat['lastMessage'] = message_text
                break

        # 0. KAWALAN KHAS ADMIN UNTUK NOTA (#nota / #ingat)
        admin_phone = "60132434200"
        if sender_phone == admin_phone and message_lower.startswith(("#nota", "#ingat")):
            nota_baru = message_text.replace("#nota", "").replace("#NOTA", "").replace("#ingat", "").replace("#INGAT", "").strip()
            with open("admin_memory.txt", "a", encoding="utf-8") as f:
                f.write(f"- [{datetime.now().strftime('%Y-%m-%d %H:%M')}] {nota_baru}\n")
            
            teks_balasan_admin = f"✅ Nota berjaya disimpan untuk ingatan Zulfa:\n\n\"{nota_baru}\""
            hantar_teks_whatsapp(sender_phone, teks_balasan_admin)
            return jsonify({"status": "success", "action": "admin_memory_saved"}), 200

        # JIKA MOD ADALAH 'HUMAN', AI JANGAN BALAS AUTOMATIK (Biar ejen balas di portal)
        if current_chat_mode == "human":
            logging.info(f"Mesej daripada {sender_phone} diabaikan oleh AI kerana mod semasa adalah Human Touch.")
            return jsonify({"status": "success", "action": "ignored_human_mode"}), 200

        # 1. SEMAKAN PERMINTAAN QR CODE
        if any(keyword in message_lower for keyword in KEYWORDS_QR):
            caption_teks = (
                "Berikut adalah QR Code DuitNow CIMB rasmi **SHAHRIL BASRI LEISURE ENTERPRISE**.\n\n"
                "Sila imbas untuk membuat bayaran **50% deposit** atau **Bayaran Penuh (Full Payment)**.\n"
                "*(PENTING: Sila letakkan nombor telefon anda pada bahagian rujukan/reference pemindahan)*\n\n"
                f"Pautan ToyyibPay alternatif: {getattr(sop_payment, 'TOYYIBPAY_LINK', 'https://toyyibpay.com')}\n\n"
                "Selepas bayaran dibuat, sila hantar resit di sini ya. Terima kasih!"
            )
            qr_link = getattr(sop_payment, "QR_CODE_DIRECT_LINK", "")
            hantar_imej_whatsapp(phone=sender_phone, image_url=qr_link, caption=caption_teks)
            return jsonify({"status": "success", "action": "sent_qr_image"}), 200

        # 2. SEMAKAN JIKA PELANGGAN HANTAR RESIT / BAYARAN
        if any(keyword in message_lower for keyword in KEYWORDS_BAYARAN) or msg_obj.get("type") == "image":
            data_tempahan_baru = {
                "ref_id": f"SB-{sender_phone[-4:]}",
                "nama": f"Pelanggan ({sender_phone})",
                "no_tel": sender_phone,
                "tarikh": "Disemak melalui WhatsApp",
                "pickup": "Mengikut Sesi Sembang",
                "dropoff": "Mengikut Sesi Sembang",
                "harga": 0.00,
                "status_bayaran": "Resit/Bayaran Dihantar oleh Pelanggan"
            }

            sop_payment.hantar_emel_admin(data_tempahan_baru)
            admin_phone_target = "60132434200"
            teks_admin = sop_payment.format_admin_notification(data_tempahan_baru)
            hantar_teks_whatsapp(admin_phone_target, teks_admin)

            balasan_pelanggan = "Terima kasih! Resit/makluman bayaran anda telah diterima dan dihantar kepada pihak pengurusan (Admin) untuk disemak. Kami akan sahkan sebentar lagi."
            hantar_teks_whatsapp(sender_phone, balasan_pelanggan)
            return jsonify({"status": "success", "action": "payment_notification_sent"}), 200

        # 3. PROSES BIASA MELALUI OTAK ZULFA (AI GEMINI)
        if message_text:
            jawapan_ai = zulfa_brain.proses_mesej(sender_phone, message_text)
            hantar_teks_whatsapp(sender_phone, jawapan_ai)

        return jsonify({"status": "success", "action": "sent_ai_response"}), 200

    except Exception as e:
        logging.error(f"Ralat pada webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def hantar_teks_whatsapp(phone, text):
    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID", "1274341599093050")
    
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": text},
    }
    
    response = requests.post(url, json=payload, headers=headers)
    logging.info(f"Respons hantar WhatsApp ke {phone}: {response.status_code} - {response.text}")


def hantar_imej_whatsapp(phone, image_url, caption):
    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID", "1274341599093050")
    
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": caption
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    logging.info(f"Respons hantar Imej QR: {response.status_code} - {response.text}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)