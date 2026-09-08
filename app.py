import os
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

import zulfa_brain
import sbleisure_engine
import sop_payment

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
CORS(app)

KEYWORDS_QR = ["qr", "qr code", "qrcode", "duitnow", "cimb qr", "nak qr", "gambar qr"]
KEYWORDS_BAYARAN = ["resit", "dah bayar", "selesai bayar", "payment done", "bukti bayar", "bank in"]

# Pangkalan data memori dibersihkan sepenuhnya tanpa sebarang mesej dummy
live_chats_db = {
    "sbltransport": [],
    "aluzlia": []
}

def push_chat_to_sheets(client_name, phone_number, sender_type, message_text):
    apps_script_url = "https://script.google.com/macros/s/AKfycbR5k9eQY0lW0jjLBD-SZ14aeckCWG0363YAwFttwW4gFt5Exq1hjioFlQHt4OSe6Za/exec"
    payload = {
        "timestamp": datetime.now().isoformat(),
        "client": client_name,
        "phone": phone_number,
        "sender": sender_type,
        "message": message_text,
    }
    try:
        response = requests.post(apps_script_url, json=payload, timeout=10)
        print(f"DEBUG SHEET SYNC: Status {response.status_code} - {response.text}")
        logging.info(f"DEBUG SHEET SYNC: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"DEBUG SHEET ERROR: {e}")
        logging.error(f"Ralat hantar ke Google Sheet pusat: {e}")

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "bot_name": "Zulfa - Shahril Basri Leisure Enterprise Bot",
        "version": "2.10"
    }), 200

@app.route("/api/clients", methods=["GET"])
def get_clients_data():
    try:
        senarai_client = [
            {
                "ref_id": "SB-4200",
                "nama": "Shahril Basri Leisure Enterprise (SBL Transport)",
                "no_tel": "+60132434200",
                "tarikh": "2026-08-27",
                "status": "Aktif / Selesai"
            }
        ]
        return jsonify({"status": "success", "data": senarai_client}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/<username>/chats", methods=["GET"])
def get_chats_multitenant(username):
    try:
        chats = live_chats_db.get(username, live_chats_db.get("sbltransport", []))
        return jsonify({"success": True, "chats": chats}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/chats", methods=["GET"])
def get_chats():
    try:
        client_name = request.args.get("client", "sbltransport")
        chats = live_chats_db.get(client_name, live_chats_db.get("sbltransport", []))
        return jsonify({"success": True, "chats": chats}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/<username>/chats/reply", methods=["POST"])
def reply_chat_multitenant(username):
    return proses_balasan_chat_logik(username)

@app.route("/api/chats/reply", methods=["POST"])
def reply_chat():
    return proses_balasan_chat_logik("sbltransport")

def proses_balasan_chat_logik(target_db_key):
    try:
        data = request.json or {}
        chat_id = str(data.get('chat_id', ''))
        reply_text = data.get('text', '')
        target_phone = data.get('phone')

        if not target_phone or target_phone == "None":
            target_phone = chat_id

        if target_phone and reply_text:
            clean_phone = str(target_phone).replace("+", "").strip()
            hantar_teks_whatsapp(clean_phone, reply_text)
            push_chat_to_sheets(target_db_key, clean_phone, "agent", reply_text)
        else:
            logging.warning(f"Gagal hantar WhatsApp: Nombor telefon tidak dijumpai untuk chat_id {chat_id}")

        dijumpai = False
        db_to_use = live_chats_db.get(target_db_key, live_chats_db["sbltransport"])
        
        for chat in db_to_use:
            if str(chat['id']) == str(chat_id) or str(chat['phone']).replace("+", "") == str(chat_id).replace("+", ""):
                chat['messages'].append({"sender": "client", "text": reply_text, "time": datetime.now().strftime('%I:%M %p')})
                chat['lastMessage'] = reply_text
                dijumpai = True
                break

        if not dijumpai:
            for client_key in live_chats_db:
                for chat in live_chats_db[client_key]:
                    if str(chat['id']) == str(chat_id) or str(chat['phone']).replace("+", "") == str(chat_id).replace("+", ""):
                        chat['messages'].append({"sender": "client", "text": reply_text, "time": datetime.now().strftime('%I:%M %p')})
                        chat['lastMessage'] = reply_text
                        dijumpai = True
                        break
                if dijumpai:
                    break

        if dijumpai:
            return jsonify({"success": True, "message": "Mesej berjaya dihantar ke WhatsApp!"}), 200
        else:
            return jsonify({"success": False, "error": "Chat tidak dijumpai dalam database"}), 404

    except Exception as e:
        logging.error(f"Ralat pada proses balasan chat: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/<username>/chats/toggle-mode", methods=["POST"])
def toggle_mode_multitenant(username):
    return proses_toggle_mode_logik(username)

@app.route("/api/chats/toggle-mode", methods=["POST"])
def toggle_mode():
    return proses_toggle_mode_logik("sbltransport")

def proses_toggle_mode_logik(target_db_key):
    try:
        data = request.json or {}
        chat_id = str(data.get('chat_id', ''))
        
        db_to_use = live_chats_db.get(target_db_key, live_chats_db["sbltransport"])
        for chat in db_to_use:
            if str(chat['id']) == str(chat_id):
                chat['mode'] = "human" if chat['mode'] == "ai" else "ai"
                return jsonify({"success": True, "mode": chat['mode']}), 200
                
        for client_key in live_chats_db:
            for chat in live_chats_db[client_key]:
                if str(chat['id']) == str(chat_id):
                    chat['mode'] = "human" if chat['mode'] == "ai" else "ai"
                    return jsonify({"success": True, "mode": chat['mode']}), 200

        return jsonify({"success": False, "error": "Chat tidak dijumpai"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/admin/clients", methods=["POST"])
def register_client_from_admin():
    try:
        data = request.json or {}
        username = data.get("username")
        if username and username not in live_chats_db:
            live_chats_db[username] = []
        return jsonify({"success": True, "message": f"Klien {username} berjaya didaftarkan di pelayan bot!"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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
    data = request.json or {}
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
        
        sender_phone = str(
            msg_obj.get("from") 
            or value.get("contacts", [{}])[0].get("wa_id", "") 
            or msg_obj.get("sender", "")
        ).replace("+", "").strip()

        if not sender_phone or sender_phone == "None":
            return jsonify({"status": "ignored", "reason": "no sender phone"}), 200
        
        message_text = ""
        msg_type = msg_obj.get("type")
        if msg_type == "text":
            message_text = msg_obj.get("text", {}).get("body", "").strip()
        elif msg_type == "image":
            message_text = "[Gambar / Resit Dihantar]"

        message_lower = message_text.lower()
        
        if "sbltransport" not in live_chats_db:
            live_chats_db["sbltransport"] = []
        sbl_chats = live_chats_db["sbltransport"]
        
        found_chat = None
        for chat in sbl_chats:
            db_phone = str(chat.get("phone", "")).replace("+", "").strip()
            if db_phone == sender_phone:
                found_chat = chat
                break

        if not found_chat:
            admin_phone = "60132434200"
            if sender_phone != admin_phone:
                found_chat = {
                    "id": sender_phone,
                    "customerName": f"Pelanggan ({sender_phone})",
                    "phone": f"+{sender_phone}",
                    "lastMessage": message_text,
                    "time": datetime.now().strftime('%I:%M %p'),
                    "mode": "ai",
                    "messages": []
                }
                sbl_chats.append(found_chat)

        if found_chat:
            found_chat['messages'].append({"sender": "customer", "text": message_text, "time": datetime.now().strftime('%I:%M %p')})
            found_chat['lastMessage'] = message_text
            current_chat_mode = found_chat.get("mode", "ai")
        else:
            current_chat_mode = "ai"

        # Hantar mesej masuk pelanggan ke Google Sheet pusat secara real-time
        push_chat_to_sheets("sbltransport", sender_phone, "customer", message_text)

        admin_phone = "60132434200"
        if sender_phone == admin_phone and message_lower.startswith(("#nota", "#ingat")):
            nota_baru = message_text.replace("#nota", "").replace("#NOTA", "").replace("#ingat", "").replace("#INGAT", "").strip()
            with open("admin_memory.txt", "a", encoding="utf-8") as f:
                f.write(f"- [{datetime.now().strftime('%Y-%m-%d %H:%M')}] {nota_baru}\n")
            
            teks_balasan_admin = f"✅ Nota berjaya disimpan untuk ingatan Zulfa:\n\n\"{nota_baru}\""
            hantar_teks_whatsapp(sender_phone, teks_balasan_admin)
            push_chat_to_sheets("sbltransport", sender_phone, "bot", teks_balasan_admin)
            return jsonify({"status": "success", "action": "admin_memory_saved"}), 200

        if current_chat_mode == "human":
            logging.info(f"Mesej daripada {sender_phone} diabaikan oleh AI kerana mod semasa adalah Human Touch.")
            return jsonify({"status": "success", "action": "ignored_human_mode"}), 200

        if any(keyword in message_lower for keyword in KEYWORDS_QR):
            toyyib_link = getattr(sop_payment, 'TOYYIBPAY_LINK', 'https://toyyibpay.com/sbl-online')
            caption_teks = (
                "Berikut adalah QR Code DuitNow CIMB rasmi **SHAHRIL BASRI LEISURE ENTERPRISE**.\n\n"
                "Sila imbas untuk membuat bayaran **50% deposit** atau **Bayaran Penuh (Full Payment)**.\n"
                "*(PENTING: Sila letakkan nombor telefon anda pada bahagian rujukan/reference pemindahan)*\n\n"
                f"Pautan ToyyibPay alternatif: {toyyib_link}\n\n"
                "Selepas bayaran dibuat, sila hantar resit di sini ya. Terima kasih!"
            )
            qr_link = getattr(sop_payment, "QR_CODE_DIRECT_LINK", "")
            if qr_link:
                hantar_imej_whatsapp(phone=sender_phone, image_url=qr_link, caption=caption_teks)
            else:
                hantar_teks_whatsapp(sender_phone, caption_teks)
            
            push_chat_to_sheets("sbltransport", sender_phone, "bot", caption_teks)
            return jsonify({"status": "success", "action": "sent_qr_image"}), 200

        if any(keyword in message_lower for keyword in KEYWORDS_BAYARAN) or msg_type == "image":
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
            push_chat_to_sheets("sbltransport", sender_phone, "bot", balasan_pelanggan)
            return jsonify({"status": "success", "action": "payment_notification_sent"}), 200

        if message_text and message_text != "[Gambar / Resit Dihantar]":
            jawapan_ai = zulfa_brain.proses_mesej(sender_phone, message_text)
            hantar_teks_whatsapp(sender_phone, jawapan_ai)
            
            if found_chat:
                found_chat['messages'].append({"sender": "ai", "text": jawapan_ai, "time": datetime.now().strftime('%I:%M %p')})
                found_chat['lastMessage'] = jawapan_ai

            push_chat_to_sheets("sbltransport", sender_phone, "bot", jawapan_ai)

        return jsonify({"status": "success", "action": "sent_ai_response"}), 200

    except Exception as e:
        logging.error(f"Ralat pada webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def hantar_teks_whatsapp(phone, text):
    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID", "1274341599093050")
    clean_phone = str(phone).replace("+", "").strip()
    
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": clean_phone,
        "type": "text",
        "text": {"body": text},
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        logging.info(f"Respons hantar WhatsApp ke {clean_phone}: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Ralat sambungan Meta API (teks): {e}")

def hantar_imej_whatsapp(phone, image_url, caption):
    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("PHONE_NUMBER_ID", "1274341599093050")
    clean_phone = str(phone).replace("+", "").strip()
    
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": clean_phone,
        "type": "image",
        "image": {
            "link": image_url,
            "caption": caption
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        logging.info(f"Respons hantar Imej QR ke {clean_phone}: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Ralat sambungan Meta API (imej): {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)