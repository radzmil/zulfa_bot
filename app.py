import os
import requests
from flask import Flask, request, jsonify
import sbleisure_engine
import sop_payment

app = Flask(__name__)

ADMIN_PHONE = "60132434200"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    try:
        message_data = data.get("message", {})
        phone_number = message_data.get("from", "")
        message_text = message_data.get("body", "").strip()
        
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

def send_whatsapp_message(to, message):
    # Masukkan endpoint API WhatsApp anda di sini
    pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)