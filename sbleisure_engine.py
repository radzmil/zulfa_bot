import math
from datetime import datetime

def get_zulfa_persona():
    """Mengembalikan profil perwatakan dan arahan sistem rasmi untuk Zulfa AI"""
    return """
ANDA ADALAH ZULFA: Pembantu Khidmat Pelanggan & Perunding Tempahan Rasmi bagi SHAHRIL BASRI LEISURE ENTERPRISE.
PERWATAKAN: Mesra, profesional, sopan, namun SANGAT TEGAS dalam mematuhi SOP syarikat.

GARIS PANDUAN UTAMA:
1. STRICT GATEKEEPING PICKUP: Hanya terima lokasi pickup yang tersenarai di Selangor & KL sahaja. Jika di luar senarai, tolak dengan sopan dan beri link sales team: https://wa.link/nrmesv.
2. KETEGASAN TARIKH BOOKING (NO URGENT BOOKINGS): Tempahan online HANYA dibenarkan untuk tarikh 8 HARI DAN KE ATAS dari hari ini. Jika pelanggan cuba buat tempahan dalam masa 7 hari atau kurang (<= 7 hari), TOLAK dan arahkan terus ke sales team: https://wa.link/nrmesv.
3. PEMBAYARAN: Deposit 50% wajib ke akaun CIMB (SHAHRIL BASRI LEISURE ENTERPRISE) untuk lock tarikh.
"""

def validasi_pickup(lokasi):
    """Menyemak zon pickup yang dibenarkan berserta harga asas rasmi"""
    lokasi = lokasi.strip().lower()
    
    zon_700 = [
        "ampang", "cheras", "hulu langat", "batu", "setapak", "ulu kelang",
        "kuala lumpur", "pusat bandar", "bukit bintang", "chow kit", "brickfields",
        "bangsar", "seputeh", "kepong", "segambut", "sentul", "jalan ipoh",
        "mont kiara", "sri hartamas", "batu caves", "wangsa maju", "danau kota",
        "taman melati", "semarak", "ampang hilir", "kampung pandan", "desa pandan", "maluri"
    ]
    if any(z in lokasi for z in zon_700):
        return True, 700.00

    zon_800 = [
        "klia", "cyberjaya", "putrajaya", "airport", "damansara", "petaling",
        "kajang", "semenyih", "rawang", "dengkil", "sepang", "labu"
    ]
    if any(z in lokasi for z in zon_800):
        return True, 800.00

    zon_900 = [
        "bukit raja", "sungai buloh", "sg buloh", "beranang", "kapar", "klang"
    ]
    if any(z in lokasi for z in zon_900):
        return True, 900.00

    zon_1000 = [
        "morib", "banting", "telok panglima garang", "bandar", "jugra", "kelanang",
        "tanjong duabelas", "ampang pecah", "batang kali", "buloh telor", "kalumpang",
        "kerling", "kuala kalumpang", "peretak", "rasa", "serendah", "sungai gumut",
        "sungai tinggi", "ulu bernam", "ulu yam"
    ]
    if any(z in lokasi for z in zon_1000):
        return True, 1000.00

    zon_1200 = [
        "kuala selangor", "tanjong karang", "sabak bernam", "seremban", "port dickson",
        "api-api", "batang berjuntai", "bestari jaya", "ijok", "jeram", "pasangan",
        "ujong pematang", "ulu tinggi", "bagan nakhoda omar", "panchang bedena",
        "pasiran panjang", "sabak", "sungai panjang", "ampangangan", "lenggeng",
        "pantai", "rantau", "rasah", "setul", "jimah", "linggi", "si rusa"
    ]
    if any(z in lokasi for z in zon_1200):
        return True, 1200.00

    return False, 0.00

def semak_tarikh_booking(tarikh_str):
    """Menyemak sama ada tarikh lepas atau tergolong dalam urgent booking (<= 7 hari)"""
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
            return "boleh", "Tarikh disahkan lulus untuk tempahan online."
    except ValueError:
        return "ralat", "Format tarikh tidak sah. Sila guna format YYYY-MM-DD atau DD-MM-YYYY."

def bundar_ke_puluhan_atas(nilai):
    return math.ceil(nilai / 10.0) * 10