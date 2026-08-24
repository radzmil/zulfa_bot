import os
import requests
from flask import Flask, request, jsonify
import sbleisure_engine
import sop_payment

app = Flask(__name__)

<<<<<<< HEAD
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
=======
ADMIN_PHONE = "60132434200"

@app.route("/webhook", methods=["POST"])
def webhook():
>>>>>>> 002d667ef9161a34e9eaa187fab7ec7b6712108f
    data = request.json
    try:
<<<<<<< HEAD
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
=======
        message_data = data.get("message", {})
        phone_number = message_data.get("from", "")
        message_text = message_data.get("body", "").strip()
>>>>>>> 002d667ef9161a34e9eaa187fab7ec7b6712108f
        
        # Semak persetujuan Terma & Syarat
        if "setuju" in message_text.lower():
            reply_text = (
                "Terima kasih kerana bersetuju dengan Terma & Syarat kami.\n\n"
                "Sila pilih jenis perjalanan anda untuk meneruskan tempahan:\n"
                "1. Sehala (One-Way)\n"
                "2. Pergi-Balik (Two-Way)"
            )
            send_whatsapp_message(phone_number, reply_text)
            return jsonify({"status": "success"}), 200

        # Semak pembayaran / resit
        keywords_payment = ["bayar", "payment", "resit", "slip", "dah bayar", "bank in", "toyyibpay"]
        is_payment_message = any(k in message_text.lower() for k in keywords_payment)
        is_booking_form = "-" in message_text and ("nama" in message_text.lower() or "destinasi" in message_text.lower())

        if ADMIN_PHONE and (is_payment_message or is_booking_form):
            booking_data = {
                "ref_id": f"REF-{phone_number}",
                "nama": f"Pelanggan ({phone_number})",
                "tarikh": "Rujuk perbualan",
                "transfer_type": message_text[:200],
                "masa": "-",
                "destinasi": "-",
                "status_bayaran": "MENUNGGU PENGESAHAN ADMIN (Resit/Borang Diterima)"
            }
            
            notif_admin = sop_payment.format_admin_notification(booking_data)
            notif_admin += f"\n\n📝 **MAKLUMAT TERKINI DARI PELANGGAN:**\n{message_text}"
            
            send_whatsapp_message(ADMIN_PHONE, notif_admin)
            
            reply_pelanggan = (
                "Terima kasih! Maklumat dan resit anda telah diterima.\n"
                "Pihak admin kami akan menyemak transaksi pembayaran anda dalam masa terdekat."
            )
            send_whatsapp_message(phone_number, reply_pelanggan)
            return jsonify({"status": "success"}), 200

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"Ralat pada webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

<<<<<<< HEAD

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
=======
def send_whatsapp_message(to, message):
    # Masukkan endpoint API WhatsApp anda di sini
    pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
>>>>>>> 002d667ef9161a34e9eaa187fab7ec7b6712108f
