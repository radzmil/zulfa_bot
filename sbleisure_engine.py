import logging

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ==========================================
# 1. TETAPAN HARGA ASAS & PEMETAAN KAWASAN
# ==========================================
KADAR_ASAS_BAS = 1200
CAJ_LUAR_KAWASAN = 300
PERATUS_DEPOSIT_DEFAULT = 0.3

# Pemetaan Negeri & Zon Utama SB Leisure
SENARAI_NEGERI = [
    "Kuala Lumpur", "Selangor", "Putrajaya", "Johor", "Kedah", 
    "Kelantan", "Melaka", "Negeri Sembilan", "Pahang", "Perak", 
    "Perlis", "Pulau Pinang", "Terengganu"
]

ZON_LEMBAH_KLANG = [
    "kuala lumpur", "selangor", "putrajaya", "shah alam", "petaling jaya", 
    "subang jaya", "klang", "kajang", "bangi", "puchong", "cyberjaya"
]

# ==========================================
# 2. FUNGSI SOKONGAN & SEMAKAN KAWASAN
# ==========================================

def semak_dalam_lembah_klang(lokasi):
    """Memeriksa sama ada lokasi berada di dalam kawasan Lembah Klang."""
    if not lokasi:
        return False
    return any(zon in lokasi.lower() for zon in ZON_LEMBAH_KLANG)

def semak_rentas_negeri(negeri_pickup, negeri_destinasi):
    """Memeriksa sama ada perjalanan melibatkan pergerakan rentas negeri."""
    pickup = negeri_pickup.strip().lower() if negeri_pickup else ""
    destinasi = negeri_destinasi.strip().lower() if negeri_destinasi else ""
    
    if not pickup or not destinasi:
        return False
        
    return pickup != destinasi

# ==========================================
# 3. ENJIN UTAMA PENGIRAAN HARGA
# ==========================================

def kira_harga_kenderaan_sbleisure(
    jenis_kenderaan="bas",
    jenis_transfer="one_way",
    negeri_pickup="Kuala Lumpur",
    negeri_destinasi="Kuala Lumpur",
    bilangan_hari=1,
    peratus_deposit=PERATUS_DEPOSIT_DEFAULT
):
    """
    Mengira anggaran harga sewaan kenderaan dan deposit.
    Berdasarkan formula asal projek SB Leisure.
    """
    
    # 1. Semakan Kenderaan (Hanya Bas disokong oleh enjin)
    if jenis_kenderaan.lower() != "bas":
        return {
            "status": "rujuk_sales",
            "mesej": "Untuk tempahan kenderaan selain Bas (seperti Van, MPV, atau Pakej Tour), sila hubungi sales team kami di: https://wa.link/nrmesv"
        }

    # 2. Semakan Caj Rentas Negeri / Luar Kawasan
    caj_luar_kawasan = 0
    if semak_rentas_negeri(negeri_pickup, negeri_destinasi):
        caj_luar_kawasan = CAJ_LUAR_KAWASAN

    # 3. Logik Pengiraan mengikut Jenis Perjalanan
    if jenis_transfer == "one_way":
        harga_asas = (KADAR_ASAS_BAS * 0.7) + caj_luar_kawasan
    elif jenis_transfer == "two_way":
        harga_asas = (KADAR_ASAS_BAS * bilangan_hari) + caj_luar_kawasan
    elif jenis_transfer == "daily_charter":
        harga_asas = (KADAR_ASAS_BAS * bilangan_hari) + caj_luar_kawasan
    else:
        harga_asas = (KADAR_ASAS_BAS * bilangan_hari) + caj_luar_kawasan

    # 4. Pengiraan Ringgit & Deposit
    final_price = round(harga_asas, 2)
    deposit = round(final_price * peratus_deposit, 2)

    return {
        "status": "jaya",
        "jenis_kenderaan": jenis_kenderaan,
        "jenis_transfer": jenis_transfer,
        "bilangan_hari": bilangan_hari,
        "harga": int(final_price),
        "deposit": int(deposit),
        "label_deposit": f"{int(peratus_deposit * 100)}%"
    }

# ==========================================
# 4. RESPONS TEKS & INTEGRASI SYSTEM PROMPT
# ==========================================

def respon_zulfa(hasil_kiraan):
    """
    Memulangkan respons teks berasaskan hasil pengiraan untuk balasan Zulfa.
    """
    if hasil_kiraan["status"] in ["rujuk_sales", "salah_kawasan"]:
        return hasil_kiraan["mesej"]
    
    return (
        f"Anggaran harga untuk sewaan ini adalah **RM {hasil_kiraan['harga']}**\n"
        f"Deposit ({hasil_kiraan['label_deposit']}): **RM {hasil_kiraan['deposit']}**\n\n"
        f"Adakah anda bersetuju dengan harga ini?"
    )

def get_engine_rules_text():
    """
    Memulangkan arahan enjin pengiraan untuk dimasukkan ke dalam System Instruction `zulfa_brain.py`.
    """
    return f"""
    - **Kenderaan Dibenarkan**: Hanya 'Bas' sahaja. Kenderaan lain mesti dirujuk ke Sales Team (https://wa.link/nrmesv).
    - **Kadar Asas Bas**: RM {KADAR_ASAS_BAS} / hari.
    - **Kadar One Way**: (RM {KADAR_ASAS_BAS} x 0.7) + Caj Luar Kawasan (jika ada).
    - **Caj Luar Kawasan / Rentas Negeri**: RM {CAJ_LUAR_KAWASAN} jika negeri pickup dan destinasi berbeza.
    - **Deposit**: Standard deposit adalah {int(PERATUS_DEPOSIT_DEFAULT * 100)}% daripada harga keseluruhan.
    """