import math
from datetime import datetime

def get_engine_rules_text():
    return """
    PANDUAN LOKASI PICKUP & ENJIN HARGA:
    - Lokasi pickup yang sah mesti disahkan mengikut senarai mukim Selangor & Negeri Sembilan.
    - Harga asas dikira secara automatik mengikut mukim pickup (bermula dari RM700 hingga RM1,600).
    - Jarak perjalanan akan dikira menggunakan kadar berperingkat (tiered rate) jika melebihi 30km.
    
    SENARAI KAWASAN PICKUP YANG DIBENARKAN & HARGA ASAS:
    1. SELANGOR:
       - Petaling (Bukit Raja, Sungai Buloh: RM900; Damansara, Petaling: RM800)
       - Hulu Langat (Ampang, Cheras, Hulu Langat: RM700; Beranang: RM900; Kajang, Semenyih: RM800)
       - Klang (Kapar, Klang: RM900)
       - Gombak (Ampang, Batu, Setapak, Ulu Kelang: RM700; Rawang: RM800)
       - Kuala Langat (Bandar, Batu, Jugra, Kelanang, Morib, Tanjong Duabelas, Telok Panglima Garang: RM1,000)
       - Kuala Selangor (Api-Api, Batang Berjuntai/Bestari Jaya, Ijok, Jeram, Kuala Selangor, Pasangan, Tanjong Karang, Ujong Permatang, Ulu Tinggi: RM1,200)
       - Sepang (Dengkil, Labu, Sepang: RM800)
       - Sabak Bernam (Bagan Nakhoda Omar, Panchang Bedena, Pasiran Panjang, Sabak, Sungai Panjang: RM1,200)
       - Hulu Selangor (Ampang Pecah, Batang Kali, Buloh Telor, Kalumpang, Kerling, Kuala Kalumpang, Peretak, Rasa, Serendah, Sungai Gumut, Sungai Tinggi, Ulu Bernam, Ulu Yam: RM1,000)
       
    2. KUALA LUMPUR & PUTRAJAYA/CYBERBERJAYA/KLIA:
       - KL (Pusat bandar, Bukit Bintang, Chow Kit, Brickfields, Bangsar, Seputeh, Kepong, Segambut, Sentul, Jalan Ipoh, Mont Kiara, Sri Hartamas, Batu Caves, Setapak, Wangsa Maju, Danau Kota, Gombak Utara, Taman Melati, Semarak, Ampang Hilir, Kampung Pandan, Desa Pandan, Maluri, Ulu Kelang): RM700
       - KLIA, Cyberjaya, Putrajaya: RM800

    3. NEGERI SEMBILAN:
       - Seremban & Port Dickson (Mukim-mukim berkaitan): RM1,200
       - Rembau, Kuala Pilah, Jelebu (Mukim-mukim berkaitan): RM1,400
       - Jempol & Tampin (Mukim-mukim berkaitan): RM1,600
    """

def get_zulfa_persona():
    """Mengembalikan profil perwatakan dan arahan sistem rasmi untuk Zulfa AI"""
    return """
ANDA ADALAH ZULFA: Pembantu Khidmat Pelanggan & Perunding Tempahan Rasmi bagi SHAHRIL BASRI LEISURE ENTERPRISE.
PERWATAKAN: Mesra, profesional, sopan, namun SANGAT TEGAS dalam mematuhi SOP syarikat.

GARIS PANDUAN UTAMA:
1. STRICT GATEKEEPING PICKUP: Hanya terima lokasi pickup yang tersenarai di Selangor, KL, Putrajaya/Cyberjaya/KLIA, & Negeri Sembilan sahaja. Jika di luar senarai, tolak dengan sopan dan beri link sales team: https://wa.link/nrmesv.
2. KETEGASAN TARIKH BOOKING (NO URGENT BOOKINGS): Tempahan online HANYA dibenarkan untuk tarikh 8 HARI DAN KE ATAS dari hari ini. Jika pelanggan cuba buat tempahan dalam masa 7 hari atau kurang (<= 7 hari), TOLAK dan arahkan terus ke sales team: https://wa.link/nrmesv.
3. PEMBAYARAN: Deposit 50% wajib ke akaun CIMB (SHAHRIL BASRI LEISURE ENTERPRISE) untuk lock tarikh atau full payment.
"""

def validasi_pickup(lokasi):
    """Menyemak zon pickup yang dibenarkan berserta harga asas rasmi mengikut mukim"""
    lokasi = lokasi.strip().lower()
    
    # Kumpulan Harga Asas RM700 (KL, Gombak terpilih, Hulu Langat terpilih)
    zon_700 = [
        "ampang", "cheras", "hulu langat", "batu", "setapak", "ulu kelang",
        "kuala lumpur", "pusat bandar", "bukit bintang", "chow kit", "brickfields",
        "bangsar", "seputeh", "kepong", "segambut", "sentul", "jalan ipoh",
        "mont kiara", "sri hartamas", "batu caves", "wangsa maju", "danau kota",
        "taman melati", "semarak", "ampang hilir", "kampung pandan", "desa pandan", "maluri"
    ]
    if any(z in lokasi for z in zon_700):
        return True, 700.00

    # Kumpulan Harga Asas RM800 (Petaling terpilih, Hulu Langat terpilih, Gombak Rawang, Sepang, KLIA/Cyber/Putrajaya)
    zon_800 = [
        "klia", "cyberjaya", "putrajaya", "airport", "damansara", "petaling",
        "kajang", "semenyih", "rawang", "dengkil", "sepang", "labu"
    ]
    if any(z in lokasi for z in zon_800):
        return True, 800.00

    # Kumpulan Harga Asas RM900 (Petaling Bukit Raja/Sungai Buloh, Hulu Langat Beranang, Klang)
    zon_900 = [
        "bukit raja", "sungai buloh", "sg buloh", "beranang", "kapar", "klang"
    ]
    if any(z in lokasi for z in zon_900):
        return True, 900.00

    # Kumpulan Harga Asas RM1,000 (Kuala Langat & Hulu Selangor)
    zon_1000 = [
        "morib", "banting", "telok panglima garang", "bandar", "jugra", "kelanang",
        "tanjong duabelas", "ampang pecah", "batang kali", "buloh telor", "kalumpang",
        "kerling", "kuala kalumpang", "peretak", "rasa", "serendah", "sungai gumut",
        "sungai tinggi", "ulu bernam", "ulu yam"
    ]
    if any(z in lokasi for z in zon_1000):
        return True, 1000.00

    # Kumpulan Harga Asas RM1,200 (Kuala Selangor, Sabak Bernam, Seremban, Port Dickson)
    zon_1200 = [
        "kuala selangor", "tanjong karang", "sabak bernam", "api-api", "batang berjuntai", 
        "bestari jaya", "ijok", "jeram", "pasangan", "ujong pematang", "ulu tinggi", 
        "bagan nakhoda omar", "panchang bedena", "pasiran panjang", "sabak", "sungai panjang", 
        "ampangan", "lenggeng", "pantai", "rantau", "rasah", "seremban", "setul",
        "jimah", "linggi", "pasir panjang", "port dickson", "si rusa"
    ]
    if any(z in lokasi for z in zon_1200):
        return True, 1200.00

    # Kumpulan Harga Asas RM1,400 (Rembau, Kuala Pilah, Jelebu)
    zon_1400 = [
        "batu kikir", "chembong", "gadong", "kota", "kundor", "legong hilir", "legong hulu", 
        "mambau", "nerasau", "pedas", "pilin", "seberang", "titian bintangor", "batu hampar", 
        "gadong hilir", "rembau bandar", "ampang tinggi", "johol", "juasseh", "kepas", 
        "kuala pilah", "langkap", "seri menanti", "ulu jempol", "terachi", "parit tinggi",
        "glami lemi", "hulu klawang", "klawang", "pertang", "peradong", "kenaboi", "triang hilir", "ulu triang"
    ]
    if any(z in lokasi for z in zon_1400):
        return True, 1400.00

    # Kumpulan Harga Asas RM1,600 (Jempol, Tampin)
    zon_1600 = [
        "jelai", "serting ilir", "serting hulu", "palong",
        "ayer kuning", "gemencheh", "gemas", "kepis", "ladang", "tampin tengah", "tampin"
    ]
    if any(z in lokasi for z in zon_1600):
        return True, 1600.00

    return False, 0.00

def kira_harga_bas(lokasi_ambil, jarak_km):
    """
    Kalkulator harga bas carter (44 seats) berasaskan jarak dan zon pickup.
    Menggunakan konsep kadar asas mukim + kadar lebihan berperingkat.
    """
    lokasi_ambil = lokasi_ambil.strip().lower()
    
    # Dapatkan harga asas mengikut mukim menggunakan fungsi validasi_pickup
    sah, harga_asas = validasi_pickup(lokasi_ambil)
    if not sah:
        harga_asas = 700.00  # Default fallback jika tidak dikesan
        
    # Logik Pengiraan Jarak Berperingkat (Tiered Rate)
    if jarak_km <= 30:
        # 30km pertama menggunakan harga asas sepenuhnya
        jumlah_harga = harga_asas
        
    elif jarak_km <= 80:
        # Peringkat Sederhana (31km hingga 80km)
        jarak_lebihan = jarak_km - 30
        kadar_sederhana = 12.00  # Kadar per-km untuk jarak sederhana
        jumlah_harga = harga_asas + (jarak_lebihan * kadar_sederhana)
        
    else:
        # Peringkat Jauh (> 80km)
        jarak_sederhana_max = 50  # dari 30km ke 80km (50km pertama selepas asas)
        kadar_sederhana = 12.00
        
        jarak_sangat_jauh = jarak_km - 80
        kadar_jauh = 5.50  # Kadar lebih murah untuk kilometer seterusnya
        
        jumlah_harga = harga_asas + (jarak_sederhana_max * kadar_sederhana) + (jarak_sangat_jauh * kadar_jauh)

    return round(jumlah_harga, 2)

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