import math
from datetime import datetime

# ==========================================
# 1. MODUL TERMA & SYARAT
# ==========================================

def paparkan_terma_dan_syarat():
    """Memaparkan terma dan syarat rasmi syarikat untuk dibaca pelanggan"""
    return (
        "**SYARAT PEMBAYARAN & PEMBATALAN - DEPOSIT 50%**\n\n"
        "**1. Pembayaran**\n"
        "   - Deposit 50%: Diperlukan untuk lock tarikh & bas selepas quotation dihantar untuk pengesahan tempahan.\n"
        "   - Baki 50%: Mesti dijelaskan penuh 2 hari sebelum tarikh perjalanan.\n\n"
        "**2. Pembatalan oleh Pelanggan**\n"
        "   - >14 hari sebelum tarikh: Refund 90% dari jumlah deposit. Potong 10% untuk yuran admin.\n"
        "   - 7-14 hari sebelum tarikh: Refund 50% dari jumlah deposit.\n"
        "   - <2 hari sebelum tarikh: Burn 100% dari total payment.\n"
        "   - Gagal bayar baki 2 hari sebelum: Tempahan terbatal. Deposit burn.\n\n"
        "**3. Penundaan Tarikh**\n"
        "   Dibenarkan 1 kali sahaja dengan notis minima 7 hari. Deposit boleh dibawa ke tarikh baru. Kalau <7 hari, tambahan caj penundaan RM200.\n\n"
        "**4. Pembatalan oleh Syarikat**\n"
        "   Deposit + Baki yang telah dibayar akan dikembalikan 100% dalam 7 hari bekerja.\n\n"
        "**5. Nota Penting**\n"
        "   Deposit adalah untuk menahan tarikh. Jika tarikh dibatalkan, kami rugi peluang job lain. Oleh itu deposit tidak dikembalikan.\n\n"
        "*Adakah anda bersetuju dengan Terma & Syarat di atas? (Sila balas 'Setuju' untuk meneruskan tempahan)*"
    )


# ==========================================
# 2. MODUL VALIDASI & HARGA ASAS MENGIKUT ZON
# ==========================================

def validasi_pickup(lokasi):
    """Menyemak zon pickup mukim Selangor & Negeri Sembilan berserta harga asas rasmi"""
    lokasi = lokasi.strip().lower()
    
    if any(z in lokasi for z in ["klia", "cyberjaya", "putrajaya", "airport"]):
        return True, 800.00
    if any(z in lokasi for z in ["bukit raja", "sungai buloh"]):
        return True, 900.00
    if any(z in lokasi for z in ["damansara", "petaling"]):
        return True, 800.00
    if any(z in lokasi for z in ["ampang", "cheras", "hulu langat"]):
        return True, 700.00
    if "beranang" in lokasi:
        return True, 900.00
    if any(z in lokasi for z in ["kajang", "semenyih"]):
        return True, 800.00
    if any(z in lokasi for z in ["kapar", "klang"]):
        return True, 900.00
    if any(z in lokasi for z in ["batu", "setapak", "ulu kelang"]):
        return True, 700.00
    if "rawang" in lokasi:
        return True, 800.00
    if any(z in lokasi for z in ["bandar", "jugra", "kelanang", "morib", "tanjong duabelas", "telok panglima garang"]):
        return True, 1000.00
    if any(z in lokasi for z in ["api-api", "batang berjuntai", "bestari jaya", "ijok", "jeram", "kuala selangor", "pasangan", "tanjong karang", "ujong permatang", "ulu tinggi"]):
        return True, 1200.00
    if any(z in lokasi for z in ["dengkil", "labu", "sepang"]):
        return True, 800.00
    if any(z in lokasi for z in ["bagan nakhoda omar", "panchang bedena", "pasiran panjang", "sabak", "sungai panjang"]):
        return True, 1200.00
    if any(z in lokasi for z in ["ampang pecah", "batang kali", "buloh telor", "kalumpang", "kerling", "kuala kalumpang", "peretak", "rasa", "serendah", "sungai gumut", "sungai tinggi", "ulu bernam", "ulu yam"]):
        return True, 1000.00

    if any(z in lokasi for z in ["ampangan", "lenggeng", "pantai", "rantau", "rasah", "seremban", "setul"]):
        return True, 1200.00
    if any(z in lokasi for z in ["jimah", "linggi", "pasir panjang", "port dickson", "si rusa"]):
        return True, 1200.00
    if any(z in lokasi for z in ["batu kikir", "chembong", "gadong", "kota", "kundor", "legong hilir", "legong hulu", "mambau", "nerasau", "pedas", "pilin", "seberang", "titian bintangor", "batu hampar", "gadong hilir", "rembau"]):
        return True, 1400.00
    if any(z in lokasi for z in ["ampang tinggi", "johol", "juasseh", "kepas", "kuala pilah", "langkap", "seri menanti", "ulu jempol", "terachi", "parit tinggi"]):
        return True, 1400.00
    if any(z in lokasi for z in ["glami lemi", "hulu klawang", "klawang", "pertang", "peradong", "kenaboi", "triang hilir", "ulu triang"]):
        return True, 1400.00
    if any(z in lokasi for z in ["jelai", "serting ilir", "serting hulu", "palong"]):
        return True, 1600.00
    if any(z in lokasi for z in ["ayer kuning", "gemencheh", "gemas", "kepis", "ladang", "tampin tengah"]):
        return True, 1600.00

    if any(z in lokasi for z in ["kuala lumpur", "pusat bandar", "bukit bintang", "chow kit", "brickfields", "bangsar", "seputehe", "kepong", "segambut", "sentul", "jalan ipoh", "mont kiara", "sri hartamas", "batu caves", "wangsa maju", "danau kota", "taman melati", "semarak", "ampang hilir", "kampung pandan", "desa pandan", "maluri"]):
        return True, 700.00
        
    return False, 0.00

def respon_salah_kawasan():
    return "Maaf, lokasi pickup tersebut di luar zon operasi utama kami. Sila rujuk sales team untuk bantuan lanjut: https://wa.link/nrmesv"

def semak_tarikh_booking(tarikh_str):
    try:
        if '-' in tarikh_str and len(tarikh_str.split('-')[0]) == 4:
            tarikh_booking = datetime.strptime(tarikh_str, "%Y-%m-%d").date()
        else:
            tarikh_booking = datetime.strptime(tarikh_str, "%d-%m-%Y").date()
            
        tarikh_semasa = datetime.now().date()
        selisih_hari = (tarikh_booking - tarikh_semasa).days
        
        if selisih_hari < 0:
            return "tidak_sah", "Tarikh yang dipilih sudah lepas."
        elif selisih_hari <= 7:
            return "urgent", "Maaf, untuk tempahan dalam masa 7 hari atau kurang (urgent booking), sistem tidak boleh terima. Sila berhubung terus dengan sales team kami di pautan ini: https://wa.link/nrmesv"
        else:
            return "boleh", "Tarikh disahkan lulus untuk tempahan."
    except ValueError:
        return "ralat", "Format tarikh tidak sah. Sila guna format YYYY-MM-DD atau DD-MM-YYYY."

def paparkan_borang(jenis_transfer):
    jenis_transfer = jenis_transfer.strip().lower()
    
    if "two" in jenis_transfer or "2" in jenis_transfer:
        return (
            "**BORANG MAKLUMAT SEWAAN ( TWO WAY )**\n\n"
            "- Syarikat/agensi :\n"
            "- Nama :\n"
            "- Destinasi: \n"
            "- Tarikh Pergi: \n"
            "- Mase pickup pergi : \n"
            "- Tarikh Balik: \n"
            "- Masa Pickup balik : \n"
            "- Jumlah Pax (Penumpang): "
        )
    else:
        return (
            "**BORANG MAKLUMAT SEWAAN ( ONE WAY )**\n\n"
            "- Syarikat/agensi :\n"
            "- Nama :\n"
            "- Destinasi: \n"
            "- Tarikh Pergi: \n"
            "- Mase pickup pergi : \n"
            "- Tarikh Balik: \n"
            "- Jumlah Pax (Penumpang): "
        )


# ==========================================
# 3. MODUL KALKULATOR SEWAAN & ZON
# ==========================================

def bundar_ke_puluhan_atas(nilai):
    return math.ceil(nilai / 10.0) * 10

def kira_harga_kenderaan_sbleisure(jenis_kenderaan="bas", jenis_transfer="one_way", lokasi_ambil="ampang", jarak_km=0, tarikh_pergi=None, tarikh_balik=None, pilihan_deposit=50):
    jenis_kenderaan = jenis_kenderaan.strip().lower()
    
    # KEMASKINI: Hanya Bas sahaja dibenarkan untuk tempahan online
    if jenis_kenderaan != "bas":
        return {
            "status": "rujuk_sales",
            "mesej": f"Maaf, untuk tempahan {jenis_kenderaan.upper()}, sistem tidak boleh ambil tempahan terus. Sila berhubung terus dengan team sales kami untuk tempahan kenderaan ini: https://wa.link/nrmesv"
        }
    
    if jenis_kenderaan == "tour":
        return {
            "status": "rujuk_sales",
            "mesej": "Untuk trip jenis Tour, tempahan tidak diambil secara atas talian. Sila berhubung terus dengan sales team kami di sini: https://wa.link/nrmesv"
        }
    
    lokasi_ambil = lokasi_ambil.strip().lower()
    is_valid, harga_asas = validasi_pickup(lokasi_ambil)
    
    if not is_valid:
        return {
            "status": "salah_kawasan",
            "mesej": respon_salah_kawasan()
        }
    
    jenis_transfer = jenis_transfer.strip().lower()
    
    if jarak_km <= 30:
        jumlah_harga = harga_asas
    elif jarak_km <= 35:
        jumlah_harga = harga_asas + ((jarak_km - 30) * 30.00)
    elif jarak_km <= 40:
        jumlah_harga = harga_asas + (5 * 30.00) + ((jarak_km - 35) * 10.00)
    elif jarak_km <= 60:
        jumlah_harga = harga_asas + (5 * 30.00) + (5 * 10.00) + ((jarak_km - 40) * 7.50)
    elif jarak_km <= 80:
        jumlah_harga = harga_asas + (5 * 30.00) + (5 * 10.00) + (20 * 7.50) + ((jarak_km - 60) * 16.67)
    else:
        jarak_sederhana_max = 50
        kadar_sederhana = 10.00
        jarak_jauh = jarak_km - 80
        kadar_jauh = 8.27
        jumlah_harga = harga_asas + (jarak_sederhana_max * kadar_sederhana) + (jarak_jauh * kadar_jauh)
        
    if "two" in jenis_transfer or "2" in jenis_transfer:
        if tarikh_pergi and tarikh_balik and tarikh_pergi == tarikh_balik:
            raw_price = jumlah_harga * 1.5
        else:
            raw_price = jumlah_harga * 2.0
    else:
        raw_price = jumlah_harga

    final_price = bundar_ke_puluhan_atas(raw_price)
    
    peratus_deposit = 1.0 if pilihan_deposit == 100 else 0.5
    raw_deposit = final_price * peratus_deposit
    deposit = bundar_ke_puluhan_atas(raw_deposit) if raw_deposit % 10 != 0 else int(raw_deposit)
    
    return {
        "status": "jaya",
        "harga": int(final_price),
        "deposit": int(deposit),
        "label_deposit": f"{int(peratus_deposit * 100)}%"
    }

def respon_zulfa(hasil_kiraan):
    if hasil_kiraan["status"] in ["rujuk_sales", "salah_kawasan"]:
        return hasil_kiraan["mesej"]
    
    return (f"Anggaran harga untuk sewaan ini adalah **RM {hasil_kiraan['harga']}** (harga ini adalah *all-in* termasuk tol). "
            f"Adakah anda bersetuju dengan harga ini?")