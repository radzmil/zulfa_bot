from flask import Flask, request, jsonify
import requests
import os
import zulfa_brain
import sop_payment

app = Flask(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_ID")

def send_whatsapp_message(to_phone, message_text):
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        print("WhatsApp token atau Phone Number ID tidak dijumpai dalam environment variables.")
        return
        
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message_text}
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Gagal menghantar mesej WhatsApp: {response.text}")
    else:
        print(f"Mesej berjaya dihantar kepada {to_phone}")

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    verify_token = os.getenv("VERIFY_TOKEN", "sbleisure_token")
    
    if mode and token:
        if mode == "subscribe" and token == verify_token:
            return challenge, 200
        else:
            return "Verification failed", 403
    return "Hello World", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print(f"Webhook received: {data}")
        
        entry = data.get("entry", [])
        if entry:
            changes = entry[0].get("changes", [])
            if changes:
                value = changes[0].get("value", [])
                messages = value.get("messages", [])
                if messages:
                    msg = messages[0]
                    phone_number = msg.get("from")
                    # Ralat sintaks dibetulkan di sini (dibuang rujukan luaran)
                    msg_body = msg.get("text", {}).get("body", "")
                    
                    if msg_body:
                        # 1. Dapatkan respons jawapan daripada Zulfa
                        balasan = zulfa_brain.proses_mesej(msg_body, phone_number)
                        print(f"Zulfa Response: {balasan}")
                        
                        # 2. Hantar balasan kepada pelanggan
                        send_whatsapp_message(phone_number, balasan)
                        
                        # 3. Ambil nombor admin terkini daripada sop_payment
                        admin_phone = sop_payment.get_group_admin_number()
                        
                        # 4. Semak jika mesej berkaitan pembayaran / resit / slip / borang lengkap
                        keywords_bayar = ["resit", "slip", "dah bayar", "payment", "toyyibpay", "qr", "transfer", "bankin"]
                        is_payment_message = any(k in msg_body.lower() for k in keywords_bayar)
                        is_booking_form = "BORANG MAKLUMAT SEWAAN" in msg_body.upper() or ("PICK-UP POINT" in msg_body.upper() and "TARIKH" in msg_body.upper())
                        
                        if admin_phone and (is_payment_message or is_booking_form):
                            # Bina data lengkap untuk dihantar kepada admin menggunakan fungsi dari sop_payment
                            booking_data = {
                                "ref_id": f"REF-{phone_number[-4:]}",
                                "nama": f"Pelanggan ({phone_number})",
                                "tarikh": "Rujuk teks di bawah / perbualan",
                                "transfer_type": msg_body[:200], 
                                "masa": "-",
                                "destinasi": "-",
                                "status_bayaran": "MENUNGGU SAHAN ADMIN (Resit/Borang Diterima)"
                            }
                            
                            # Formatkan mesej notifikasi rasmi untuk admin
                            notif_admin = sop_payment.format_admin_notification(booking_data)
                            
                            # Tambah teks asal pelanggan supaya admin dapat lihat butiran borang/resit secara tepat
                            notif_admin += f"\n\n📝 *MAKLUMAT / MESEJ TERKINI DARI PELANGGAN:*\n{msg_body}"
                            
                            # Hantar terus ke nombor admin
                            send_whatsapp_message(admin_phone, notif_admin)
                            print(f"Notifikasi terperinci berjaya dihantar kepada Admin: {admin_phone}")
                        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)