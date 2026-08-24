import os
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify
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

# Senarai kata kunci untuk mengesan permintaan QR Code daripada pelanggan
KEYWORDS_QR = ["qr", "qr code", "qrcode", "duitnow", "cimb qr", "nak qr", "gambar qr"]

# Senarai kata kunci untuk mengesan penghantaran resit / bayaran selesai
KEYWORDS_BAYARAN = ["resit", "dah bayar", "selesai bayar", "payment done", "bukti bayar", "bank in"]

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "bot_name": "Zulfa - Shahril Basri Leisure Enterprise Bot",
        "version": "2.2"
    }), 200

# Laluan GET untuk pengesahan Meta Webhook
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

# Laluan POST untuk terima mesej masuk
@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    data = request.json
    logging.info(f"Mesej diterima: {data}")

    try:
        # Ekstrak mesej masuk daripada struktur payload WhatsApp Cloud API
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
        
        # Sokongan teks biasa
        message_text = ""
        if msg_obj.get("type") == "text":
            message_text = msg_obj.get("text", {}).get("body", "").strip()

        message_lower = message_text.lower()

        # 0. KAWALAN KHAS ADMIN UNTUK TAMBAH NOTA / INGATAN BARU (#nota / #ingat)
        admin_phone = "60132434200"
        if sender_phone == admin_phone and message_lower.startswith(("#nota", "#ingat")):
            nota_baru = message_text.replace("#nota", "").replace("#NOTA", "").replace("#ingat", "").replace("#INGAT", "").strip()
            
            # Simpan ke dalam fail teks ingatan admin
            with open("admin_memory.txt", "a", encoding="utf-8") as f:
                f.write(f"- [{datetime.now().strftime('%Y-%m-%d %H:%M')}] {nota_baru}\n")
            
            # Balas pengesahan kepada admin
            teks_balasan_admin = f"✅ Nota berjaya disimpan untuk ingatan Zulfa:\n\n\"{nota_baru}\""
            hantar_teks_whatsapp(sender_phone, teks_balasan_admin)
            return jsonify({"status": "success", "action": "admin_memory_saved"}), 200

        # 1. SEMAKAN PERMINTAAN QR CODE
        if any(keyword in message_lower for keyword in KEYWORDS_QR):
            caption_teks = (
                "Berikut adalah QR Code DuitNow CIMB rasmi **SHAHRIL BASRI LEISURE ENTERPRISE**.\n\n"
                "Sila imbas untuk membuat bayaran **50% deposit** atau **Bayaran Penuh (Full Payment)**.\n"
                "*(PENTING: Sila letakkan nombor telefon anda pada bahagian rujukan/reference pemindahan)*\n\n"
                f"Pautan ToyyibPay alternatif: {getattr(sop_payment, 'TOYYIBPAY_LINK', 'https://toyyibpay.com')}\n\n"
                "Selepas bayaran dibuat, sila hantar resit di sini ya. Terima kasih!"
            )
            
            # Semak sama ada pembolehubah imej wujud dalam sop_payment, jika tidak guna string kosong/default
            qr_link = getattr(sop_payment, "QR_CODE_DIRECT_LINK", "")
            hantar_imej_whatsapp(
                phone=sender_phone, 
                image_url=qr_link, 
                caption=caption_teks
            )
            return jsonify({"status": "success", "action": "sent_qr_image"}), 200

        # 2. SEMAKAN JIKA PELANGGAN HANTAR RESIT / MAKLUMAT BAYARAN SELESAI
        if any(keyword in message_lower for keyword in KEYWORDS_BAYARAN) or msg_obj.get("type") == "image":
            # Data contoh tempahan dikumpul daripada sesi pelanggan (boleh diubah mengikut database memori anda)
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

            # A. Hantar Emel ke sbleisuretranspot.my@gmail.com
            sop_payment.hantar_emel_admin(data_tempahan_baru)

            # B. Hantar Notifikasi WhatsApp ke Nombor Admin Rasmi: 60132434200
            admin_phone_target = "60132434200"
            teks_admin = sop_payment.format_admin_notification(data_tempahan_baru)
            hantar_teks_whatsapp(admin_phone_target, teks_admin)

            # Balas kepada pelanggan
            balasan_pelanggan = "Terima kasih! Resit/makluman bayaran anda telah diterima dan dihantar kepada pihak pengurusan (Admin) untuk disemak menggunakan rujukan nombor telefon anda. Kami akan sahkan sebentar lagi."
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