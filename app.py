from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
import sbleisure_profile
import sbleisure_engine
import zulfa_brain
from sbleisure_engine import kira_harga_kenderaan_sbleisure, respon_zulfa, paparkan_terma_dan_syarat, paparkan_borang

load_dotenv()
app = Flask(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "sbleisure_secure_token")

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
                        nombor_sender = msg["from"] # Nombor telefon penerima
                        teks_mesej = msg["text"]["body"] # Teks mesej masuk
                        
                        # Dapatkan jawapan pintar daripada Zulfa Brain (Gemini)
                        jawapan_zulfa = zulfa_brain.proses_mesej(teks_mesej)
                        
                        # Hantar semula jawapan ke WhatsApp melalui Meta Cloud API
                        kirim_whatsapp(nombor_sender, jawapan_zulfa)
                        
        return jsonify({"status": "received"}), 200
    except Exception as e:
        print(f"Error webhook: {e}")
        return jsonify({"status": "error"}), 500

def kirim_whatsapp(nombor_tujuan, mesej_teks):
    """Fungsi untuk menghantar mesej teks kembali ke WhatsApp pengguna"""
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
    kenderaan = data.get("kenderaan", "bas")
    transfer = data.get("transfer", "one_way")
    lokasi = data.get("lokasi", "ampang")
    jarak = data.get("jarak", 0)
    t_pergi = data.get("tarikh_pergi")
    t_balik = data.get("tarikh_balik")
    
    hasil = kira_harga_kenderaan_sbleisure(
        jenis_kenderaan=kenderaan,
        jenis_transfer=transfer,
        lokasi_ambil=lokasi,
        jarak_km=jarak,
        tarikh_pergi=t_pergi,
        tarikh_balik=t_balik
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