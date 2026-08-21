from flask import Flask, request, jsonify
import os
import requests
import hashlib
from dotenv import load_dotenv
import sbleisure_profile
import sbleisure_engine
import zulfa_brain
import sop_payment
from sbleisure_engine import kira_harga_kenderaan_sbleisure, respon_zulfa, paparkan_terma_dan_syarat, paparkan_borang

load_dotenv()
app = Flask(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "sbleisure_secure_token")
TOYYIBPAY_SECRET_KEY = "ct48pm53-ijta-7aq5-h0bc-hy1w37c9s4h2"

@app.route("/")
def home():
    return "SBLEISURE Bot Server is running smoothly, bosku! Zulfa is ready."

# 1. Pengesahan Webhook untuk Meta (WhatsApp Cloud API)
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403
    return "Hello, this is SBLEISURE Webhook endpoint", 200

# 2. Penerima Mesej Masuk & Hantar Balik ke WhatsApp
@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json
    try:
        if "entry" in body:
            for entry in body["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    if "messages" in value:
                        msg = value["messages"][0]
                        nombor_sender = msg["from"]
                        teks_mesej = msg["text"]["body"]
                        
                        jawapan_zulfa = zulfa_brain.proses_mesej(teks_mesej)
                        kirim_whatsapp(nombor_sender, jawapan_zulfa)
                        
        return jsonify({"status": "received"}), 200
    except Exception as e:
        print(f"Error webhook: {e}")
        return jsonify({"status": "error"}), 500

# 3. ToyyibPay Callback Webhook (Auto-Ping bila customer bayar)
@app.route("/toyyibpay-callback", methods=["POST"])
def toyyibpay_callback():
    try:
        data = request.form.to_dict() or request.json or {}
        
        status = str(data.get('status') or data.get('status_id') or '')
        order_id = str(data.get('order_id') or '')
        refno = str(data.get('refno') or '')
        received_hash = str(data.get('hash') or '')
        nama_customer = data.get('name') or data.get('customer_name', 'Pelanggan')
        billcode = data.get('billcode') or order_id
        
        # Validasi Hash ToyyibPay
        raw_string = TOYYIBPAY_SECRET_KEY + status + order_id + refno + "ok"
        expected_hash = hashlib.md5(raw_string.encode('utf-8')).hexdigest()
        
        if received_hash == expected_hash and (status == '1' or status.lower() == 'success'):
            booking_info = {
                "ref_id": billcode,
                "nama": nama_customer,
                "status_bayaran": "PAID ONLINE (ToyyibPay Secure Verified)"
            }
            
            pesanan_admin = sop_payment.format_admin_notification(booking_info)
            kirim_whatsapp(sop_payment.get_group_admin_number(), pesanan_admin)
            
            return jsonify({"status": "success", "message": "Hash valid, admin telah di-ping."}), 200
        else:
            return jsonify({"status": "invalid_hash_or_failed", "message": "Hash tidak sepadan atau bayaran belum berjaya."}), 400
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def kirim_whatsapp(nombor_tujuan, mesej_teks):
    url = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": nombor_tujuan,
        "type": "text",
        "text": {"body": mesej_teks}
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Gagal hantar WhatsApp: {e}")

@app.route("/kira", methods=["POST"])
def kira_harga():
    data = request.json
    hasil = kira_harga_kenderaan_sbleisure(
        jenis_kenderaan=data.get("kenderaan", "bas"),
        jenis_transfer=data.get("transfer", "one_way"),
        lokasi_ambil=data.get("lokasi", "ampang"),
        jarak_km=data.get("jarak", 0),
        tarikh_pergi=data.get("tarikh_pergi"),
        tarikh_balik=data.get("tarikh_balik")
    )
    respon = respon_zulfa(hasil)
    return jsonify({"status": hasil["status"], "mesej": respon, "data_harga": hasil})

@app.route("/terma", methods=["GET"])
def get_terma():
    return jsonify({"terma": paparkan_terma_dan_syarat()})

@app.route("/borang", methods=["POST"])
def get_borang():
    data = request.json
    transfer = data.get("transfer", "one_way")
    return jsonify({"borang": paparkan_borang(transfer)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)