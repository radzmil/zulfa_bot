import math
from datetime import datetime

def get_engine_rules_text():
    return """
    PANDUAN LOKASI PICKUP & ENJIN HARGA:
    - Semak JADUAL HARGA TETAP LALUAN terlebih dahulu. Jika laluan wujud, guna harga tersebut serta-merta.
    - STRICT GATEKEEPING PICKUP: Hanya terima lokasi pickup di Selangor, KL, Putrajaya/Cyberjaya/KLIA,Di luar kawasan, tolak dan beri link: https://wa.link/nrmesv.
    - NO URGENT BOOKINGS: Tempahan online HANYA untuk tarikh 8 HARI DAN KE ATAS. Jika 7 hari ke bawah, tolak dan beri link: https://wa.link/nrmesv.
    - PEMBAYARAN: Deposit 50% wajib ke akaun CIMB (SHAHRIL BASRI LEISURE ENTERPRISE) untuk lock tarikh.
    - FORMAT SEBUT HARGA: Jangan sebut harga asas atau formula. Hanya sebut laluan (pickup ke drop-off) dan harga sahaja. Balas pendek dan ringkas seperti manusia di WhatsApp
    - Jika tiada dalam jadual tetap, gunakan Harga Asas Mukim Pickup + Lebihan Jarak (>51km) mengikut Kadar Zon Wilayah masing-masing (Utara, Selatan, atau Pantai Timur).
    - LARANGAN KERAS: JANGAN SEKALI-KALI sebut harga asas, formula, kadar per km, atau pecahan kos kepada pelanggan.
    - FORMAT JAWAPAN HARGA: Terus sebut laluan (pickup ke drop-off) dan harga akhir sahaja dengan ringkas (Contoh: "Untuk sewaan dari Ampang ke Sungai Gabai, anggaran harga adalah RM900").
    """

def get_zulfa_persona():
    """Mengembalikan profil perwatakan dan arahan sistem rasmi untuk Zulfa AI"""
    return """
ANDA ADALAH ZULFA: Pembantu Khidmat Pelanggan & Perunding Tempahan Rasmi bagi SHAHRIL BASRI LEISURE ENTERPRISE.
PERWATAKAN: Mesra, profesional, sopan, sangat ringkas, dan mematuhi SOP.
- Jawab soalan secaran pendek dan ringkas.
- Sentiasa belajar dari semasa ke semasa untuk menambahbaik skill

"""

def validasi_pickup(lokasi):
    """Menyemak zon pickup yang dibenarkan berserta harga asas rasmi mengikut mukim"""
    lokasi = lokasi.strip().lower()
    
    zon_700 = ["ampang", "cheras", "hulu langat", "batu", "setapak", "ulu kelang", "kuala lumpur", "pusat bandar", "bukit bintang", "chow kit", "brickfields", "bangsar", "seputeh", "kepong", "segambut", "sentul", "jalan ipoh", "mont kiara", "sri hartamas", "batu caves", "wangsa maju", "danau kota", "taman melati", "semarak", "ampang hilir", "kampung pandan", "desa pandan", "maluri"]
    if any(z in lokasi for z in zon_700):
        return True, 700.00

    zon_800 = ["klia", "cyberjaya", "putrajaya", "airport", "damansara", "petaling", "kajang", "semenyih", "rawang", "dengkil", "sepang", "labu"]
    if any(z in lokasi for z in zon_800):
        return True, 800.00

    zon_900 = ["bukit raja", "sungai buloh", "sg buloh", "beranang", "kapar", "klang"]
    if any(z in lokasi for z in zon_900):
        return True, 900.00

    zon_1000 = ["bandar", "jugra", "kelanang", "morib", "tanjong duabelas", "telok panglima garang", "ampang pecah", "batang kali", "buloh telor", "kalumpang", "kerling", "kuala kalumpang", "peretak", "rasa", "serendah", "sungai gumut", "sungai tinggi", "ulu bernam", "ulu yam"]
    if any(z in lokasi for z in zon_1000):
        return True, 1000.00

    zon_1200 = ["api-api", "batang berjuntai", "bestari jaya", "ijok", "jeram", "kuala selangor", "pasangan", "tanjong karang", "ujong pematang", "ulu tinggi", "bagan nakhoda omar", "panchang bedena", "pasiran panjang", "sabak", "sungai panjang", "ampangan", "lenggeng", "pantai", "rantau", "rasah", "seremban", "setul", "jimah", "linggi", "pasir panjang", "port dickson", "si rusa"]
    if any(z in lokasi for z in zon_1200):
        return True, 1200.00

    zon_1400 = ["batu kikir", "chembong", "gadong", "kota", "kundor", "legong hilir", "legong hulu", "mambau", "nerasau", "pedas", "pilin", "seberang", "titian bintangor", "batu hampar", "gadong hilir", "rembau bandar", "ampang tinggi", "johol", "juasseh", "kepas", "kuala pilah", "langkap", "seri menanti", "ulu jempol", "terachi", "parit tinggi", "glami lemi", "hulu klawang", "klawang", "pertang", "peradong", "kenaboi", "triang hilir", "ulu triang"]
    if any(z in lokasi for z in zon_1400):
        return True, 1400.00

    zon_1600 = ["jelai", "serting ilir", "serting hulu", "palong", "ayer kuning", "gemencheh", "gemas", "kepis", "ladang", "tampin tengah", "tampin"]
    if any(z in lokasi for z in zon_1600):
        return True, 1600.00

    return False, 0.00

# Jadual Harga Tetap Laluan Popular (Override)
JADUAL_HARGA_BAS_TETAP = {
    ("ampang", "kajang"): 850,
    ("klia", "kajang"): 850,
    ("ampang", "semenyih"): 850,
    ("klia", "semenyih"): 970,
    ("ampang", "seremban"): 1354,
    ("klia", "seremban"): 1300,
    ("ampang", "port dickson"): 1420,
    ("ampang", "rawang"): 850,
    ("klia", "rawang"): 990,
    ("ampang", "bukit beruntung"): 850,
    ("klia", "bukit beruntung"): 1024,
    ("ampang", "kalumpang"): 989,
    ("klia", "kalumpang"): 1225,
    ("ampang", "tanjung malim"): 1010,
    ("klia", "tanjung malim"): 1250,
    ("ampang", "sungai gabai"): 900,
    ("ampang", "janda baik"): 1000,
    ("klia", "janda baik"): 1470,
    ("ampang", "bukit tinggi"): 1000,
    ("klia", "bukit tinggi"): 1470,
    ("ampang", "genting"): 1000,
    ("klia", "genting"): 1219,
    ("ampang", "bentong"): 1220,
    ("klia", "bentong"): 1480,
    ("ampang", "raub"): 1310,
    ("klia", "raub"): 1850,
}

def tentukan_zon_wilayah(destinasi):
    """Menentukan zon wilayah destinasi berdasarkan nama tempat"""
    dest = destinasi.lower()
    
    zon_utara = ["rawang", "bukit beruntung", "kalumpang", "tanjung malim", "tapah", "ipoh", "taiping", "teluk intan", "parit buntar", "gerik", "kuala kangsar", "sungai buloh", "serendah", "batang kali", "rasa", "hulu bernam"]
    zon_selatan = ["kajang", "semenyih", "seremban", "port dickson", "nilai", "sepang", "dengkil", "bangi", "mantin", "rembau", "tampin", "melaka", "muar", "batu pahat", "johor bahru"]
    zon_timur = ["janda baik", "bukit tinggi", "genting", "bentong", "raub", "temerloh", "kuantan", "jeram", "cameron highlands", "kuala lipis"]
    
    if any(k in dest for k in zon_utara):
        return "utara"
    elif any(k in dest for k in zon_selatan):
        return "selatan"
    elif any(k in dest for k in zon_timur):
        return "timur"
    else:
        return "standard"

def kira_harga_bas(lokasi_pickup, destinasi, jarak_km=0, tier_jalan="normal"):
    """
    Mengira harga bas: semak jadual tetap dulu, jika tiada guna harga asas mukim + lebihan jarak mengikut kadar zon wilayah.
    """
    pickup = lokasi_pickup.strip().lower()
    dest = destinasi.strip().lower()
    
    kunci = (pickup, dest)
    if kunci in JADUAL_HARGA_BAS_TETAP:
        jumlah_harga = JADUAL_HARGA_BAS_TETAP[kunci]
    else:
        sah, harga_asas = validasi_pickup(pickup)
        if not sah:
            harga_asas = 700.00
            
        # Kadar lebihan km mengikut zon wilayah
        zon = tentukan_zon_wilayah(dest)
        if zon == "utara":
            kadar_km = 3.50
        elif zon == "selatan":
            kadar_km = 4.00
        elif zon == "timur":
            kadar_km = 6.50
        else:
            kadar_km = 3.50
            
        caj_jarak = (jarak_km - 51) * kadar_km if jarak_km > 51 else 0
        jumlah_harga = harga_asas + caj_jarak
            
    return round(jumlah_harga, 2)

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
            return "boleh", "Tarikh disahkan lulus untuk tempahan online."
    except ValueError:
        return "ralat", "Format tarikh tidak sah. Sila guna format YYYY-MM-DD atau DD-MM-YYYY."

def bundar_ke_puluhan_atas(nilai):
    return math.ceil(nilai / 10.0) * 10

def dapatkan_harga_automatik(pickup, destinasi):
    """Mencari harga tetap laluan atau mengembalikan ralat jika tiada."""
    p = pickup.strip().lower()
    d = destinasi.strip().lower()
    
    # Semak padanan dalam jadual tetap
    if (p, d) in JADUAL_HARGA_BAS_TETAP:
        return JADUAL_HARGA_BAS_TETAP[(p, d)]
    
    # Jika tiada, guna fungsi pengiraan asas
    return kira_harga_bas(p, d, jarak_km=100)