# app.py - Enjin Zulfa Bot & API Real-Time Portal SBLEisure (Zon Masa Malaysia UTC+8)
import os
import json
import logging
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

import zulfa_brain
import sbleisure_engine
import sop_payment

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
CORS(app)  # Membenarkan portal berhubung secara bebas tanpa sekatan CORS

KEYWORDS_QR = ["qr", "qr code", "qrcode", "duitnow", "cimb qr", "nak qr", "gambar qr"]
KEYWORDS_BAYARAN = ["resit", "dah bayar", "selesai bayar", "payment done", "bukti bayar", "bank in"]

# Fail pangkalan data JSON klien
CHAT_LOGS_FILE = "chat_history_logs.json"
CLIENT_PROFILE_FILE = "client_profile.json"

# Konfigurasi Pangkalan Data PostgreSQL (Supabase / Railway DB)
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logging.error(f"Ralat menyambung ke pangkalan data PostgreSQL: {e}")
        return None

def save_message_to_postgres(client_id, sender_name, message_text):
    """Fungsi selamat merekodkan mesej WhatsApp terus ke jadual messages"""
    conn = get_db_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (client_id, sender, message)
            VALUES (%s, %s, %s);
        """, (client_id, sender_name, message_text))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Ralat amaran simpan mesej ke PostgreSQL (diabaikan agar bot tidak terhenti): {e}")

def get_malaysia_time():
    # Menyelaraskan masa pelayan UTC kepada zon masa Malaysia (UTC +8)
    return datetime.utcnow() + timedelta(hours=8)

def load_json_db(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except Exception as e:
            logging.error(f"Ralat membaca fail {filename}: {e}")
            return []
    return []

def save_json_db(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Ralat menyimpan fail {filename}: {e}")

def push_chat_to_sheets(client_name, phone_number, sender_type, message_text):
    apps_script_url = "https://script.google.com/macros/s/AKfycbyv6mxISC-5OJ_Cli3RcPAxQaMJvUSQx5wlyBvg7N2nSh4BBVle7UXimJp7jy94mEB_/exec" 
    payload = {
        "timestamp": get_malaysia_time().isoformat(),
        "client": client_name,
        "phone": phone_number,
        "sender": sender_type,
        "message": message_text,
    }
    try:
        response = requests.post(apps_script_url, json=payload, timeout=10)
        logging.info(f"DEBUG SHEET SYNC: Status {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Ralat hantar ke Google Sheet DB_sbleisure: {e}")

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "bot_name": "Zulfa - Shahril Basri Leisure Enterprise Bot",
        "version": "2.12"
    }), 200

@app.route("/test-sheet", methods=["GET"])
def test_sheet_sync():
    push_chat_to_sheets("sbltransport", "+60132434200", "customer", "Ujian manual sinkronisasi DB_sbleisure")
    return jsonify({"status": "sent test data to DB_sbleisure sheet"}), 200

@app.route("/api/clients", methods=["GET"])
def get_clients_data():
    try:
        profile_data = load_json_db(CLIENT_PROFILE_FILE)
        return jsonify({"status": "success", "data": profile_data}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ==========================================
# LALUAN API REALTIME CHAT & ANALITIK PORTAL
# ==========================================
@app.route("/api/get-leads", methods=["GET"])
def get_leads_portal():
    try:
        chats = load_json_db(CHAT_LOGS_FILE)
        leads_summary = []
        for chat in chats:
            leads_summary.append({
                "phone": str(chat.get("phone", "")).replace("+", ""),
                "name": chat.get("customerName", "Pelanggan"),
                "status": "Aktif 🟢" if chat.get("mode") == "ai" else "Human Touch ⚡"
            })
        
        if not leads_summary:
            leads_summary = [
                {"phone": "601123687357", "name": "Zulfa Sementara", "status": "Aktif 🟢"}
            ]
            
        return jsonify(leads_summary), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/get-chat-history", methods=["GET"])
def get_chat_history_portal():
    try:
        phone = request.args.get("phone", "")
        clean_target = phone.replace("+", "").strip()
        
        chats = load_json_db(CHAT_LOGS_FILE)
        for chat in chats:
            db_phone = str(chat.get("phone", "")).replace("+", "").strip()
            if db_phone == clean_target:
                return jsonify(chat.get("messages", [])), 200
                
        return jsonify([], 200)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/get-analytics", methods=["GET"])
def get_analytics_portal():
    try:
        chats = load_json_db(CHAT_LOGS_FILE)
        total_messages = sum(len(c.get("messages", [])) for c in chats)
        total_leads = len(chats)
        human_interventions = sum(1 for c in chats if c.get("mode") == "human")
        
        return jsonify({
            "daily_chats": total_messages if total_messages > 0 else 0,
            "weekly_chats": total_messages * 7 if total_messages > 0 else 0,
            "monthly_chats": total_messages * 30 if total_messages > 0 else 0,
            "total_leads": total_leads if total_leads > 0 else 0,
            "human_interventions": human_interventions
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/update-prompt", methods=["POST"])
def update_bot_prompt():
    try:
        data = request.json or {}
        prompt_text = data.get("prompt", "")
        logging.info(f"Prompt baharu diterima: {prompt_text}")
        return jsonify({"success": True, "message": "Prompt berjaya dikemaskini!"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/update-client-profile", methods=["POST"])
def update_client_profile():
    try:
        data = request.json or {}
        username = data.get("username", "")
        bot_name = data.get("bot_name", "")
        admin_number = data.get("admin_number", "")
        fb_link = data.get("fb_link", "")
        ig_link = data.get("ig_link", "")
        tiktok_link = data.get("tiktok_link", "")
        logo_base64 = data.get("logo_base64", "")
        
        profiles = load_json_db(CLIENT_PROFILE_FILE)
        found = False
        
        for profile in profiles:
            if profile.get("username") == username:
                if bot_name: profile["bot_name"] = bot_name
                if admin_number: profile["admin_number"] = admin_number
                profile["fb_link"] = fb_link
                profile["ig_link"] = ig_link
                profile["tiktok_link"] = tiktok_link
                if logo_base64:
                    profile["logo"] = logo_base64
                found = True
                break
                
        if not found:
            profiles.append({
                "username": username,
                "bot_name": bot_name or f"bot-{username}",
                "admin_number": admin_number,
                "fb_link": fb_link,
                "ig_link": ig_link,
                "tiktok_link": tiktok_link,
                "logo": logo_base64
            })
            
        save_json_db(CLIENT_PROFILE_FILE, profiles)
        return jsonify({"success": True, "message": "Profil klien berjaya disimpan secara kekal!"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/send-whatsapp", methods=["POST"])
def send_whatsapp_portal():
    try:
        data = request.json or {}
        phone = data.get("phone", "")
        message = data.get("message", "")
        client_name = data.get("client", "sbltransport")
        
        if phone and message:
            clean_phone = str(phone).replace("+", "").strip()
            hantar_teks_whatsapp(clean_phone, message)
            push_chat_to_sheets(client_name, clean_phone, "human", message)
            
            # Simpan ke PostgreSQL (ID Klien 1 untuk sbltransport)
            save_message_to_postgres(1, "Admin", message)
            
            waktu_malaysia_str = get_malaysia_time().strftime('%I:%M %p')
            chats = load_json_db(CHAT_LOGS_FILE)
            for chat in chats:
                if str(chat.get("phone", "")).replace("+", "") == clean_phone:
                    chat.setdefault('messages', []).append({
                        "sender": "human", 
                        "name": "Anda", 
                        "text": message, 
                        "time": waktu_malaysia_str
                    })
                    chat['lastMessage'] = message
                    break
            save_json_db(CHAT_LOGS_FILE, chats)
            
            return jsonify({"success": True, "message": "Mesej berjaya dihantar!"}), 200
        return jsonify({"success": False, "error": "Maklumat tidak lengkap"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
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
    data = request.json or {}

    try:
        entry = data.get("entry", [])
        if not entry:
            return jsonify({"status": "ignored"}), 200
            
        changes = entry[0].get("changes", [])
        if not changes:
            return jsonify({"status": "ignored"}), 200
            
        value = changes[0].get("value", {})
        
        if "statuses" in value and "messages" not in value:
            return jsonify({"status": "ignored_status_update"}), 200

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

        # Simpan mesej masuk pelanggan ke DB utama (ID Klien 1: sbltransport)
        save_message_to_postgres(1, f"+{sender_phone}", message_text)

        message_lower = message_text.lower()
        waktu_sebenar = get_malaysia_time().strftime('%I:%M %p')
        
        sbl_chats = load_json_db(CHAT_LOGS_FILE)
        
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
                    "time": waktu_sebenar,
                    "mode": "ai",
                    "messages": []
                }
                sbl_chats.append(found_chat)

        if found_chat:
            found_chat.setdefault('messages', []).append({
                "sender": "user", 
                "name": found_chat.get("customerName", "Prospek"), 
                "text": message_text, 
                "time": waktu_sebenar
            })
            found_chat['lastMessage'] = message_text
            current_chat_mode = found_chat.get("mode", "ai")
        else:
            current_chat_mode = "ai"

        save_json_db(CHAT_LOGS_FILE, sbl_chats)
        push_chat_to_sheets("sbltransport", sender_phone, "customer", message_text)

        admin_phone = "60132434200"
        if sender_phone == admin_phone and message_lower.startswith(("#nota", "#ingat")):
            nota_baru = message_text.replace("#nota", "").replace("#NOTA", "").replace("#ingat", "").replace("#INGAT", "").strip()
            with open("admin_memory.txt", "a", encoding="utf-8") as f:
                f.write(f"- [{get_malaysia_time().strftime('%Y-%m-%d %H:%M')}] {nota_baru}\n")
            
            teks_balasan_admin = f"✅ Nota berjaya disimpan untuk ingatan Zulfa:\n\n\"{nota_baru}\""
            hantar_teks_whatsapp(sender_phone, teks_balasan_admin)
            save_message_to_postgres(1, "Zulfa (Bot)", teks_balasan_admin)
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
                f"Pautan ToyyibPay alternatif: {toyyib_link}\n\n"
                "Selepas bayaran dibuat, sila hantar resit di sini ya. Terima kasih!"
            )
            qr_link = getattr(sop_payment, "QR_CODE_DIRECT_LINK", "")
            if qr_link:
                hantar_imej_whatsapp(phone=sender_phone, image_url=qr_link, caption=caption_teks)
            else:
                hantar_teks_whatsapp(sender_phone, caption_teks)
            
            save_message_to_postgres(1, "Zulfa (Bot)", caption_teks)
            push_chat_to_sheets("sbltransport", sender_phone, "bot", caption_teks)
            return jsonify({"status": "success", "action": "sent_qr_image"}), 200

        if any(keyword in message_lower for keyword in KEYWORDS_BAYARAN) or msg_type == "image":
            data_tempahan_baru = {
                "ref_id": f"SB-{sender_phone[-4:]}",
                "nama": f"Pelanggan ({sender_phone})",
                "no_tel": sender_phone,
                "tarikh": "Disemak melalui WhatsApp",
                "status_bayaran": "Resit/Bayaran Dihantar oleh Pelanggan"
            }

            sop_payment.hantar_emel_admin(data_tempahan_baru)
            admin_phone_target = "60132434200"
            teks_admin = sop_payment.format_admin_notification(data_tempahan_baru)
            hantar_teks_whatsapp(admin_phone_target, teks_admin)

            balasan_pelanggan = "Terima kasih! Resit/makluman bayaran anda telah diterima dan disemak oleh pihak pengurusan."
            hantar_teks_whatsapp(sender_phone, balasan_pelanggan)
            save_message_to_postgres(1, "Zulfa (Bot)", balasan_pelanggan)
            push_chat_to_sheets("sbltransport", sender_phone, "bot", balasan_pelanggan)
            return jsonify({"status": "success", "action": "payment_notification_sent"}), 200

        if message_text and message_text != "[Gambar / Resit Dihantar]":
            jawapan_ai = zulfa_brain.proses_mesej(sender_phone, message_text)
            hantar_teks_whatsapp(sender_phone, jawapan_ai)
            
            # Simpan jawapan bot ke DB utama
            save_message_to_postgres(1, "Zulfa (Bot)", jawapan_ai)
            
            waktu_balasan_ai = get_malaysia_time().strftime('%I:%M %p')
            if found_chat:
                found_chat.setdefault('messages', []).append({
                    "sender": "bot", 
                    "name": "Zulfa (Bot)", 
                    "text": jawapan_ai, 
                    "time": waktu_balasan_ai
                })
                found_chat['lastMessage'] = jawapan_ai
                save_json_db(CHAT_LOGS_FILE, sbl_chats)

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