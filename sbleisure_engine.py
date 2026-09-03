import math
import requests
from datetime import datetime

def get_engine_rules_text():
    return """
    PANDUAN LOKASI PICKUP & ENJIN HARGA:
    - Semak JADUAL HARGA TETAP LALUAN di bawah terlebih dahulu. Jika laluan wujud, GUNA HARGA TERSEBUT SEBULAT-BULATNYA DAN JANGAN UBAH:
      * Ampang ke Kajang: RM850
      * KLIA ke Kajang: RM850
      * Ampang ke Semenyih: RM850
      * KLIA ke Semenyih: RM970
      * Ampang ke Seremban: RM1,354
      * KLIA ke Seremban: RM1,300
      * Ampang ke Port Dickson: RM1,420
      * Ampang ke Rawang: RM850
      * KLIA ke Rawang: RM990
      * Ampang ke Bukit Beruntung: RM850
      * KLIA ke Bukit Beruntung: RM1,024
      * Ampang ke Kalumpang: RM989
      * KLIA ke Kalumpang: RM1,225
      * Ampang ke Tanjung Malim: RM1,010
      * KLIA ke Tanjung Malim: RM1,250
      * Ampang ke Kuala Klawang: RM1,250
      * KLIA ke Kuala Klawang: RM1,450
      * Ampang ke Sungai Gabai: RM900
      * Ampang ke Janda Baik: RM1,000
      * KLIA ke Janda Baik: RM1,470
      * Ampang ke Bukit Tinggi: RM1,000
      * KLIA ke Bukit Tinggi: RM1,470
      * Ampang ke Genting: RM1,000
      * KLIA ke Genting: RM1,219
      * Ampang ke Bentong: RM1,220
      * KLIA ke Bentong: RM1,480
      * Ampang ke Raub: RM1,310
      * KLIA ke Raub: RM1,850
    - DESTINASI DALAM PULAU (PULAU PINANG): Tambahan surcaj RM200 bagi destinasi dalam pulau (seperti Georgetown, Batu Ferringhi, Bayan Lepas, dll) untuk caj tol jambatan dan logistik pulau.
    - STRICT GATEKEEPING PICKUP: Hanya terima lokasi pickup di Selangor, KL, Putrajaya/Cyberjaya/KLIA. Di luar kawasan, tolak dan beri link: https://wa.link/nrmesv.
    - NO URGENT BOOKINGS: Tempahan online HANYA untuk tarikh 8 HARI DAN KE ATAS. Jika 7 hari ke bawah, tolak dan beri link: https://wa.link/nrmesv.
    - FORMULA TWO-WAY:
      * Return pada HARI YANG SAMA: Tambah 50% dari harga One-Way (x1.5).
      * Return pada HARI BERBEZA (Bermalam): Tambah 100% dari harga One-Way (x2.0).
    - PEMBAYARAN: Deposit 50% wajib ke akaun CIMB (SHAHRIL BASRI LEISURE ENTERPRISE) untuk lock tarikh.
    - LARANGAN KERAS: JANGAN SEKALI-KALI sebut harga asas, formula, kadar per km, atau pecahan kos kepada pelanggan.
    - FORMAT JAWAPAN HARGA: Terus sebut laluan (pickup ke drop-off) dan harga akhir sahaja dengan ringkas (Contoh: "Untuk sewaan dari Ampang ke Tanjung Malim, anggaran harga adalah RM1,010").
    - WAJIB isi borang dulu SEBELUM bagi harga dan wajib isi semua detail untuk one way atau two way.
    """

def get_zulfa_persona():
    """Mengembalikan profil perwatakan dan arahan sistem rasmi untuk Zulfa AI"""
    return """
ANDA ADALAH ZULFA: Pembantu Khidmat Pelanggan & Perunding Tempahan Rasmi bagi SHAHRIL BASRI LEISURE ENTERPRISE.
PERWATAKAN: Mesra, profesional, sopan, sangat ringkas, dan mematuhi SOP.
- Jawab soalan secara pendek dan ringkas.
- Sentiasa belajar dari semasa ke semasa untuk menambahbaik skill.
- JANGAN pandai-pandai buat harga sendiri, ikot pada sbleisure.engine dan sop.
"""

def validasi_pickup(lokasi):
    """
    Menyemak kelayakan zon pickup (Gatekeeping).
    Memulangkan tuple (sah: bool, harga_asas: float).
    """
    if not lokasi:
        return False, 0.0

    lokasi_clean = str(lokasi).strip().lower()
    kawasan_dibenarkan = [
        "selangor", "kuala lumpur", "kl", "putrajaya", "cyberjaya", "klia",
        "ampang", "cheras", "hulu langat", "batu", "setapak", "ulu kelang", "pusat bandar",
        "bukit bintang", "chow kit", "brickfields", "bangsar", "seputeh", "kepong", "segambut",
        "sentul", "jalan ipoh", "mont kiara", "sri hartamas", "batu caves", "wangsa maju",
        "danau kota", "taman melati", "semarak", "ampang hilir", "kampung pandan", "desa pandan",
        "maluri", "airport", "damansara", "petaling", "kajang", "semenyih", "rawang", "dengkil",
        "sepang", "labu", "bukit raja", "sungai buloh", "sg buloh", "beranang", "kapar", "klang",
        "bandar", "jugra", "kelanang", "morib", "tanjong duabelas", "telok panglima garang",
        "ampang pecah", "batang kali", "buloh telor", "kalumpang", "kerling", "kuala kalumpang",
        "peretak", "rasa", "serendah", "sungai gumut", "sungai tinggi", "ulu bernam", "ulu yam",
        "api-api", "batang berjuntai", "bestari jaya", "ijok", "jeram", "kuala selangor",
        "pasangan", "tanjong karang", "ujong pematang", "ulu tinggi", "bagan nakhoda omar",
        "panchang bedena", "pasiran panjang", "sabak", "sungai panjang"
    ]
    
    sah = any(k in lokasi_clean for k in kawasan_dibenarkan)
    harga_asas = dapatkan_harga_asas_destinasi(lokasi_clean) if sah else 0.0
    return sah, harga_asas

def dapatkan_harga_asas_destinasi(destinasi):
    """Menentukan harga asas (50 km pertama) berdasarkan zon mukim destinasi"""
    dest = str(destinasi).strip().lower()
    
    zon_700 = ["ampang", "cheras", "hulu langat", "batu", "setapak", "ulu kelang", "kuala lumpur", "pusat bandar", "bukit bintang", "chow kit", "brickfields", "bangsar", "seputeh", "kepong", "segambut", "sentul", "jalan ipoh", "mont kiara", "sri hartamas", "batu caves", "wangsa maju", "danau kota", "taman melati", "semarak", "ampang hilir", "kampung pandan", "desa pandan", "maluri"]
    if any(z in dest for z in zon_700):
        return 700.00

    zon_800 = ["klia", "cyberjaya", "putrajaya", "airport", "damansara", "petaling", "kajang", "semenyih", "rawang", "dengkil", "sepang", "labu"]
    if any(z in dest for z in zon_800):
        return 800.00

    zon_900 = ["bukit raja", "sungai buloh", "sg buloh", "beranang", "kapar", "klang"]
    if any(z in dest for z in zon_900):
        return 900.00

    zon_1000 = ["bandar", "jugra", "kelanang", "morib", "tanjong duabelas", "telok panglima garang", "ampang pecah", "batang kali", "buloh telor", "kalumpang", "kerling", "kuala kalumpang", "peretak", "rasa", "serendah", "sungai gumut", "sungai tinggi", "ulu bernam", "ulu yam"]
    if any(z in dest for z in zon_1000):
        return 1000.00

    zon_1200 = ["api-api", "batang berjuntai", "bestari jaya", "ijok", "jeram", "kuala selangor", "pasangan", "tanjong karang", "ujong pematang", "ulu tinggi", "bagan nakhoda omar", "panchang bedena", "pasiran panjang", "sabak", "sungai panjang", "ampangan", "lenggeng", "pantai", "rantau", "rasah", "seremban", "setul", "jimah", "linggi", "pasir panjang", "port dickson", "si rusa", "tapah"]
    if any(z in dest for z in zon_1200):
        return 1200.00

    zon_1400 = ["batu kikir", "chembong", "gadong", "kota", "kundor", "legong hilir", "legong hulu", "mambau", "nerasau", "pedas", "pilin", "seberang", "titian bintangor", "batu hampar", "gadong hilir", "rembau bandar", "ampang tinggi", "johol", "juasseh", "kepas", "kuala pilah", "langkap", "seri menanti", "ulu jempol", "terachi", "parit tinggi", "glami lemi", "hulu klawang", "klawang", "kuala klawang", "pertang", "peradong", "kenaboi", "triang hilir", "ulu triang"]
    if any(z in dest for z in zon_1400):
        return 1400.00

    zon_1600 = ["jelai", "serting ilir", "serting hulu", "palong", "ayer kuning", "gemencheh", "gemas", "kepis", "ladang", "tampin tengah", "tampin", "ipoh", "taiping", "melaka", "kuantan", "johor bahru"]
    if any(z in dest for z in zon_1600):
        return 1600.00

    return 700.00

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
    ("ampang", "kuala klawang"): 1250,
    ("klia", "kuala klawang"): 1450,
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

def semak_jadual_tetap(pickup, dest):
    """Semakan fleksibel dua hala untuk jadual harga tetap."""
    p = pickup.strip().lower()
    d = dest.strip().lower()

    for (asal, tuju), harga in JADUAL_HARGA_BAS_TETAP.items():
        if (asal in p and tuju in d) or (tuju in p and asal in d):
            return float(harga)
    return None

def semak_kawasan_dalam_pulau_pinang(destinasi):
    """
    Mengesan sama ada destinasi berada di bahagian dalam pulau (Pulau Pinang)
    untuk caj tambahan tol jambatan / kesesakan bandar & logistik pulau (+RM200).
    """
    dest = str(destinasi).strip().lower()
    kawasan_pulau = [
        "georgetown", "george town", "batu ferringhi", "bayan lepas", 
        "bayan baru", "tanjung bungah", "tanjung tokoh", "teluk bahang", 
        "air itam", "ayer itam", "gelugor", "jelutong", "gurney", 
        "pulau pinang (pulau)", "penang island"
    ]
    return any(k in dest for k in kawasan_pulau)

def tentukan_zon_wilayah(destinasi):
    """Menentukan kadar caj per km melebihi 50 km mengikut zon wilayah destinasi"""
    dest = str(destinasi).lower()
    
    zon_utara = ["rawang", "bukit beruntung", "kalumpang", "tanjung malim", "tapah", "ipoh", "taiping", "teluk intan", "parit buntar", "gerik", "kuala kangsar", "sungai buloh", "serendah", "batang kali", "rasa", "hulu bernam", "butterworth", "georgetown", "george town", "batu ferringhi", "bayan lepas", "pulau pinang", "penang", "alor setar", "kangar"]
    zon_selatan = ["kajang", "semenyih", "seremban", "port dickson", "nilai", "sepang", "dengkil", "bangi", "mantin", "rembau", "tampin", "melaka", "muar", "batu pahat", "johor bahru", "kuala klawang", "klawang"]
    zon_timur = ["janda baik", "bukit tinggi", "genting", "bentong", "raub", "temerloh", "kuantan", "cameron highlands", "kuala lipis"]
    
    if any(k in dest for k in zon_utara):
        return "utara"
    elif any(k in dest for k in zon_selatan):
        return "selatan"
    elif any(k in dest for k in zon_timur):
        return "timur"
    else:
        return "standard"

def dapatkan_jarak_km(lokasi_asal, lokasi_tuju):
    """Mendapatkan jarak pemanduan sebenar (km) menggunakan OpenStreetMap / OSRM"""
    try:
        headers = {'User-Agent': 'SBLTransportApp/1.0'}
        url_asal = f"https://nominatim.openstreetmap.org/search?q={lokasi_asal},Malaysia&format=json&limit=1"
        url_tuju = f"https://nominatim.openstreetmap.org/search?q={lokasi_tuju},Malaysia&format=json&limit=1"
        
        res_asal = requests.get(url_asal, headers=headers, timeout=4).json()
        res_tuju = requests.get(url_tuju, headers=headers, timeout=4).json()
        
        if not res_asal or not res_tuju:
            return None
            
        lon1, lat1 = res_asal[0]['lon'], res_asal[0]['lat']
        lon2, lat2 = res_tuju[0]['lon'], res_tuju[0]['lat']
        
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
        osrm_res = requests.get(osrm_url, timeout=4).json()
        
        if osrm_res.get('routes'):
            jarak_meter = osrm_res['routes'][0]['distance']
            return round(jarak_meter / 1000.0, 1)
    except Exception:
        return None
    return None

def bundar_ke_puluhan_atas(nilai):
    return math.ceil(nilai / 10.0) * 10

def kira_harga_bas(lokasi_pickup, destinasi, jarak_km=None, tier_jalan="normal"):
    """
    Mengira harga One-Way:
    1. Semak jadual harga tetap laluan dahulu.
    2. Jika tiada, gunakan harga asas zon destinasi (50 km pertama) + lebihan jarak (51 km ke atas).
    3. Tambah surcaj khas RM200 jika destinasi masuk ke bahagian dalam pulau (Pulau Pinang).
    """
    pickup = str(lokasi_pickup).strip().lower()
    dest = str(destinasi).strip().lower()
    
    # 1. Semak Jadual Tetap
    harga_tetap = semak_jadual_tetap(pickup, dest)
    if harga_tetap is not None:
        jumlah_harga = harga_tetap
    else:
        # 2. Dapatkan Harga Asas daripada Zon Destinasi (50 km pertama)
        harga_asas = dapatkan_harga_asas_destinasi(dest)
            
        # 3. Dapatkan Jarak Sebenar jika tidak dibekalkan
        if jarak_km is None or jarak_km <= 0:
            jarak_dikesan = dapatkan_jarak_km(pickup, dest)
            jarak_km = jarak_dikesan if jarak_dikesan else 80.0
            
        # 4. Tentukan Kadar Lebihan KM Mengikut Zon Wilayah (51 km ke atas)
        zon = tentukan_zon_wilayah(dest)
        if zon == "utara":
            kadar_km = 3.50
        elif zon == "selatan":
            kadar_km = 4.00
        elif zon == "timur":
            kadar_km = 6.50
        else:
            kadar_km = 3.50
            
        caj_jarak = (jarak_km - 50) * kadar_km if jarak_km > 50 else 0
        jumlah_harga = harga_asas + caj_jarak

    # 5. Surcaj Khas Bahagian Dalam Pulau (Pulau Pinang) +RM200
    if semak_kawasan_dalam_pulau_pinang(dest):
        jumlah_harga += 200.00
    
    # 6. Surcaj Muka Bumi (Tier Jalan)
    if tier_jalan in ["berbukit", "sempit", "pedalaman"]:
        jumlah_harga *= 1.15
        
    return float(bundar_ke_puluhan_atas(jumlah_harga))

def kira_harga_trip(lokasi_pickup, destinasi, jenis_trip="one_way", return_hari_sama=True, jarak_km=None, tier_jalan="normal"):
    """
    Mengira harga trip penuh mengikut jenis sewaan:
    - One-Way: 100% harga sehala
    - Two-Way Return Hari Sama: +50% (x1.5)
    - Two-Way Return Hari Berbeza (Bermalam): +100% (x2.0)
    """
    harga_one_way = kira_harga_bas(lokasi_pickup, destinasi, jarak_km=jarak_km, tier_jalan=tier_jalan)
    
    trip = str(jenis_trip).strip().lower()
    if trip in ["two_way", "two way", "pergi balik", "return"]:
        if return_hari_sama:
            jumlah_two_way = harga_one_way * 1.5
        else:
            jumlah_two_way = harga_one_way * 2.0
        return float(bundar_ke_puluhan_atas(jumlah_two_way))
        
    return float(harga_one_way)

def semak_tarikh_booking(tarikh_str):
    """Menyemak sama ada tarikh tempahan melepasi sekatan tempahan tergesa-gesa (>= 8 hari)"""
    try:
        tarikh_bersih = tarikh_str.strip()
        if '-' in tarikh_bersih and len(tarikh_bersih.split('-')[0]) == 4:
            tarikh_booking = datetime.strptime(tarikh_bersih, "%Y-%m-%d").date()
        else:
            tarikh_booking = datetime.strptime(tarikh_bersih, "%d-%m-%Y").date()
        
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

def dapatkan_harga_automatik(pickup, destinasi, jenis_trip="one_way", return_hari_sama=True, tier_jalan="normal"):
    """Fungsi pembantu utama untuk mendapatkan harga automatik One-Way atau Two-Way"""
    return kira_harga_trip(pickup, destinasi, jenis_trip=jenis_trip, return_hari_sama=return_hari_sama, jarak_km=None, tier_jalan=tier_jalan)