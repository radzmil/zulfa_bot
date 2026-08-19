# ==========================================
# APP.PY - ZULFA (SBL TRANSPORT - GEMINI + TOYYIBPAY API DYNAMIC)
# ==========================================

import os
import requests
import hashlib
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GROUP_ADMIN_NUMBER = os.getenv("GROUP_ADMIN_NUMBER")

# Maklumat ToyyibPay Bos (Secret Key & Category Code rasmi)
TOYYIBPAY_SECRET_KEY = "ct48pm53-ijta-7aq5-h0bc-hy1w37c9s4h2"
TOYYIBPAY_CATEGORY_CODE = "2iao5hzg" 
TOYYIBPAY_API_URL = "https://toyyibpay.com/index.php/api/createBill"

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
       a. Zulfa sahkan tempahan dan sediakan link pembayaran automatik.
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

def create_toyyibpay_bill(nama_pelanggan, telefon_pelanggan, detail_tempahan):
    """Fungsi untuk memanggil API Create Bill ToyyibPay secara dinamik"""
    try:
        payload = {
            'userSecretKey': TOYYIBPAY_SECRET_KEY,
            'categoryCode': TOYYIBPAY_CATEGORY_CODE,
            'billName': 'Tempahan SBL Transport',
            'billDescription': detail_tempahan[:200],
            'billPriceSetting': 1, # 1 = Fixed amount, 0 = Open amount
            'billPayorInfo': 1,
            'billAmount': 10000, # Contoh nilai dalam sen (RM100.00). Boleh ubah ikut harga sebenar.
            'billReturnURL': 'https://wa.link/o3z1bz',
            'billCallbackURL': 'https://hospitable-energy-production.up.railway.app/toyyibpay-callback',
            'billExternalReferenceNo': telefon_pelanggan,
            'billTo': nama_pelanggan,
            'billPhone': telefon_pelanggan,
            'billEmail': 'customer@sbltransport.com'
        }
        
        response = requests.post(TOYYIBPAY_API_URL, data=payload)
        result = response.json()
        
        if result and isinstance(result, list) and 'BillCode' in result[0]:
            bill_code = result[0]['BillCode']
            return f"https://toyyibpay.com/{bill_code}"
    except Exception as e:
        print(f"Ralat Create Bill ToyyibPay: {e}")
    
    return "https://toyyibpay.com/sbl-online"

def tanya_gemini(user_id, mesej_user):
    global user_sessions
    if user_id not in user_sessions: user_sessions[user_id] = []
    
    chat_history = user_sessions[user_id]
    chat_history.append({"role": "user", "parts": [{"text": mesej_user}]})
    
    if "submit booking" in mesej_user.lower():
        detail_sewaan = "".join([m["parts"][0]["text"] for m in chat_history if m["role"]=="user"][-3:])
        
        link_bayaran = create_toyyibpay_bill(nama_pelanggan="Pelanggan SBL", telefon_pelanggan=user_id, detail_tempahan=detail_sewaan)
        
        hantar_ke_admin(f"--- TEMPAHAN BARU (MENUNGGU BAYARAN) ---\nNo Tel: {user_id}\n{detail_sewaan}")
        
        return f"Booking diterima! Sila buat pembayaran melalui link rasmi ini: {link_bayaran}. Selepas pembayaran berjaya, sistem akan terus sahkan dan maklumkan kepada admin kami."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": chat_history[-10:], "system_instruction": {"parts": [{"text": system_instruction}]}}
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        jawapan_ai = response.json()['candidates'][0]['content']['parts'][0]['text']
        chat_history.append({"role": "model", "parts": [{"text": jawapan_ai}]})
        return jawapan_ai
    except:
        return "Maaf, sistem sedang sibuk."

@app.route("/toyyibpay-callback", methods=["POST"])
def toyyibpay_callback():
    data = request.form.to_dict()
    status = data.get("status")
    refno = data.get("refno")
    order_id = data.get("order_id", "")
    received_hash = data.get("hash")
    billcode = data.get("billcode")
    telefon_pelanggan = data.get("customerPhone") or data.get("billExternalReferenceNo")
    
    raw_string = f"{TOYYIBPAY_SECRET_KEY}{status}{order_id}{refno}ok"
    expected_hash = hashlib.md5(raw_string.encode()).hexdigest()
    
    if received_hash == expected_hash and status == '1':
        if telefon_pelanggan:
            hantar_whatsapp(telefon_pelanggan, "Alhamdulillah! Pembayaran anda telah berjaya disahkan. Tempahan anda kini dalam proses pihak admin.")
        
        pesan_admin = f"🎉 PEMBAYARAN BERJAYA DISAHKAN!\n\nNo Rujukan: {refno}\nBillCode: {billcode}\nNo Telefon Pelanggan: {telefon_pelanggan}\nStatus: Berjaya (Paid)"
        hantar_ke_admin(pesan_admin)
        
        return jsonify({"status": "ok"}), 200
    
    return jsonify({"status": "invalid"}), 200

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
        balasan = tanya_gemini(from_number, msg_body)
        hantar_whatsapp(from_number, balasan)
    except:
        pass
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))