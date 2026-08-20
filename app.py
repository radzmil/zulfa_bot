from flask import Flask, request, jsonify
from sbleisure_engine import kira_harga_kenderaan_sbleisure, respon_zulfa, paparkan_terma_dan_syarat, paparkan_borang

app = Flask(__name__)

@app.route("/")
def home():
    return "SBLEISURE Bot Server is running smoothly, bosku!"

@app.route("/kira", methods=["POST"])
def kira_harga():
    data = request.json
    # Terima data dari user/bot
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