import os
import logging
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

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "bot_name": "Zulfa - Shahril Basri Leisure Enterprise Bot",
        "version": "2.0"
    }), 200

# 1. TAMBAHKAN LALUAN GET UNTUK PENGESAHAN META (WEBHOOK VERIFICATION)
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
    """
    Titik laluan (webhook) untuk menerima mesej daripada platform pemesejan (WhatsApp).
    """
    data = request.json
    logging.info(f"Mesej diterima: {data}")

    try:
        # Sesuaikan struktur data ini mengikut API provider WhatsApp anda
        sender_phone = data.get("from", "60123456789")
        message_text = data.get("message", "").strip()

        if not message_text:
            return jsonify({"status": "ignored", "reason": "empty message"}), 200

        message_lower = message_text.lower()

        # 1. SEMAKAN PERMINTAAN QR CODE
        if any(keyword in message_lower for keyword in KEYWORDS_QR):
            caption_teks = (
                "Berikut adalah QR Code DuitNow CIMB rasmi **SHAHRIL BASRI LEISURE ENTERPRISE**.\n\n"
                "Sila imbas untuk membuat bayaran **50% deposit** atau **Bayaran Penuh (Full Payment)**.\n\n"
                f"Pautan ToyyibPay alternatif: {sop_payment.TOYYIBPAY_LINK}\n\n"
                "Selepas bayaran dibuat, sila hantar resit di sini ya. Terima kasih!"
            )
            
            hantar_imej_whatsapp(
                phone=sender_phone, 
                image_url=sop_payment.QR_CODE_DIRECT_LINK, 
                caption=caption_teks
            )
            return jsonify({"status": "success", "action": "sent_qr_image"}), 200

        # 2. PROSES BIASA MELALUI OTAK ZULFA (AI GEMINI)
        jawapan_ai = zulfa_brain.proses_mesej(sender_phone, message_text)
        
        # Hantar jawapan teks AI kepada pelanggan
        hantar_teks_whatsapp(sender_phone, jawapan_ai)

        return jsonify({"status": "success", "action": "sent_ai_response"}), 200

    except Exception as e:
        logging.error(f"Ralat pada webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def hantar_teks_whatsapp(phone, text):
    """
    Fungsi pembantu untuk menghantar mesej teks. 
    (Gantikan bahagian ini dengan kod requests.post ke API WhatsApp anda).
    """
    logging.info(f"Menghantar teks ke {phone}: {text}")


def hantar_imej_whatsapp(phone, image_url, caption):
    """
    Fungsi pembantu untuk menghantar imej bersama kapsyen. 
    (Gantikan bahagian ini dengan kod requests.post ke API WhatsApp anda).
    """
    logging.info(f"Menghantar imej QR ke {phone} (URL: {image_url})")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)