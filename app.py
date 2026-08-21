from flask import Flask, request, jsonify
import zulfa_brain

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print(f"Webhook received: {data}")
        
        # Ekstrak mesej dan nombor telefon daripada payload WhatsApp
        # (Sesuaikan laluan JSON ini mengikut struktur webhook WhatsApp anda)
        entry = data.get("entry", [])
        if entry:
            changes = entry[0].get("changes", [])
            if changes:
                value = changes[0].get("value", [])
                messages = value.get("messages", [])
                if messages:
                    msg = messages[0]
                    phone_number = msg.get("from")
                    msg_body = msg.get("text", {}).get("body", "")
                    
                    if msg_body:
                        # Panggil fungsi dari zulfa_brain.py
                        balasan = zulfa_brain.proses_mesej(msg_body, phone_number)
                        print(f"Zulfa Response: {balasan}")
                        # Masukkan kod untuk hantar semula ke WhatsApp API di sini jika perlu
                        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)