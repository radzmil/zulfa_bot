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
        " - Deposit 50%: Diperlukan untuk lock tarikh & bas selepas quotation dihantar untuk pengesahan tempahan.\n"
        " - Baki 50%: Mesti dijelaskan penuh 2 hari sebelum tarikh perjalanan.\n\n"
        "**2. Pembatalan oleh Pelanggan**\n"
        " - >14 hari sebelum tarikh: Refund 90% dari jumlah deposit. Potong 10% untuk yuran admin.\n"
        " - 7-14 hari sebelum tarikh: Refund 50% dari jumlah deposit.\n"
        " - <2 hari sebelum tarikh: Burn 100% dari total payment.\n"
        " - Gagal bayar baki 2 hari sebelum: Tempahan terbatal. Deposit burn.\n\n"
        "**3. Penundaan Tarikh**\n"
        " Dibenarkan 1 kali sahaja dengan notis minima 7 hari.\n"
        " Deposit boleh dibawa ke tarikh baru.\n"
        " Kalau <7 hari, tambahan caj penundaan RM200.\n\n"
        "**4. Pembatalan oleh Syarikat**\n"
        " Deposit + Baki yang telah dibayar akan dikembalikan 100% dalam 7 hari bekerja.\n\n"
        "**5. Nota Penting**\n"
        " Deposit adalah untuk menahan tarikh.\n"
        " Jika tarikh dibatalkan, kami rugi peluang job lain.\n"
        " Oleh itu deposit tidak dikembalikan.\n\n"
        "**Adakah anda bersetuju dengan Terma & Syarat di atas?\n"
        "(Sila balas 'Setuju' untuk meneruskan tempahan)**"
    )

# ==========================================
# 2. PERATURAN & ENJIN PENGIRAAN HARGA UNTUK AI (ZULFA)
# ==========================================

def get_engine_rules_text():
    """Mengembalikan teks arahan formula harga untuk kegunaan Prompt Zulfa AI"""
    return """
PERATURAN PENGIRAAN HARGA (sbleisure_engine):

--------------------------------------------------
[PERATURAN KETAT VALIDASI KAWASAN PICKUP (STRICT GATEKEEPING PICKUP)]
--------------------------------------------------
Kawasan pickup HANYA TERHAD kepada senarai di bawah sahaja. Selain dari senarai ini, pickup ADALAH TIDAK DIBENARKAN.

SENARAI KAWASAN PICKUP YANG DIBENARKAN:
SELANGOR:
• Petaling: Bukit Raja, Damansara, Petaling, Sungai Buloh
• Hulu Langat: Ampang, Beranang, Cheras, Hulu Langat, Kajang, Semenyih
• Klang: Kapar, Klang
• Gombak: Ampang, Batu, Rawang, Setapak, Ulu Kelang
• Kuala Langat: Bandar, Batu, Jugra, Kelanang, Morib, Tanjong Duabelas, Telok Panglima Garang
• Kuala Selangor: Api-Api, Batang Berjuntai (Bestari Jaya), Ijok, Jeram, Kuala Selangor, Pasangan, Tanjong Karang, Ujong Permatang, Ulu Tinggi
• Sepang: Dengkil, Labu, Sepang
• Sabak Bernam: Bagan Nakhoda Omar, Panchang Bedena, Pasiran Panjang, Sabak, Sungai Panjang
• Hulu Selangor: Ampang Pecah, Batang Kali, Buloh Telor, Kalumpang, Kerling, Kuala Kalumpang, Peretak, Rasa, Serendah, Sungai Gumut, Sungai Tinggi, Ulu Bernam, Ulu Yam

KUALA LUMPUR (5 Daerah):
• Mukim Kuala Lumpur (Pusat bandaraya KL, Bukit Bintang, Chow Kit, Brickfields, Bangsar, Seputeh, dll)
• Mukim Batu (Kepong, Segambut, Sentul, Jalan Ipoh, Mont Kiara, Sri Hartamas, Batu Caves)
• Mukim Setapak (Setapak, Wangsa Maju, Danau Kota, Gombak Utara, Taman Melati, Semarak)
• Mukim Ampang (Ampang Hilir, Kampung Pandan, Desa Pandan, Maluri, dll)
• Mukim Ulu Kelang (Pinggir timur laut KL bersempadan Ulu Kelang)

KLIA, CYBERJAYA, PUTRAJAYA
--------------------------------------------------

1. Hanya kenderaan jenis 'Bas' sahaja dibenarkan untuk tempahan online. Kenderaan lain (Van, MPV, Tour) mesti dirujuk ke sales team (https://wa.link/nrmesv).

2. Harga Asas Kilometre Pertama Mengikut Zon Pickup:
- Ampang, Cheras, Hulu Langat, Batu, Setapak, Ulu Kelang, Kuala Lumpur: RM 700.00
- KLIA, Cyberjaya, Putrajaya, Damansara, Petaling, Kajang, Semenyih, Rawang, Dengkil, Sepang, Labu: RM 800.00
- Bukit Raja, Sg Buloh, Beranang, Kapar, Klang: RM 900.00
- Morib, Banting, Telok Panglima Garang, Bandar, Jugra, Kelanang, Tanjong Duabelas, Ampang Pecah, Serendah, Ulu Yam: RM 1,000.00
- Kuala Selangor, Tanjong Karang, Sabak Bernam, Seremban, Port Dickson: RM 1,200.00
- Rembau, Kuala Pilah, Jelebu: RM 1,400.00
- Tampin, Gemas: RM 1,600.00

3. Formula Kiraan Jarak (KM):
- 0 - 30 KM: Harga Asas Zon
- 31 - 35 KM: Harga Asas + ((Jarak - 30) * RM 30.00)
- 36 - 40 KM: Harga Asas + RM 150.00 + ((Jarak - 35) * RM 10.00)
- 41 - 60 KM: Harga Asas + RM 200.00 + ((Jarak - 40) * RM 7.50)
- 61 - 80 KM: Harga Asas + RM 350.00 + ((Jarak - 60) * RM 16.67)
- > 80 KM: Harga Asas + RM 500.00 + ((Jarak - 80) * RM 8.27)

4. Jenis Perjalanan:
- Sehala (One-Way): 1.0x harga asas kiraan
- Pergi-Balik (Two-Way pada hari sama): 1.5x harga asas kiraan
- Pergi-Balik (Two-Way pada hari berbeza): 2.0x harga asas kiraan

5. Semua jumlah harga dibundarkan ke RM10 teratas terdekat.
6. Deposit standard adalah 50% daripada jumlah harga penuh.
"""

# ==========================================
# 3. MODUL VALIDASI & HARGA ASAS MENGIKUT ZON
# ==========================================

def validasi_pickup(lokasi):
    """Menyemak zon pickup yang dibenarkan berserta harga asas rasmi"""
    lokasi = lokasi.strip().lower()
    
    # Kumpulan RM 700
    zon_700 = [
        "ampang", "cheras", "hulu langat", "batu", "setapak", "ulu kelang",
        "kuala lumpur", "pusat bandar", "bukit bintang", "chow kit", "brickfields",
        "bangsar", "seputeh", "kepong", "segambut", "sentul", "jalan ipoh",
        "mont kiara", "sri hartamas", "batu caves", "wangsa maju", "danau kota",
        "taman melati", "semarak", "ampang hilir", "kampung pandan", "desa pandan", "maluri"
    ]
    if any(z in lokasi for z in zon_700):
        return True, 700.00

    # Kumpulan RM 800
    zon_800 = [
        "klia", "cyberjaya", "putrajaya", "airport", "damansara", "petaling",
        "kajang", "semenyih", "rawang", "dengkil", "sepang", "labu"
    ]
    if any(z in lokasi for z in zon_800):
        return True, 800.00

    # Kumpulan RM 900
    zon_900 = [
        "bukit raja", "sungai buloh", "sg buloh", "beranang", "kapar", "klang"
    ]
    if any(z in lokasi for z in zon_900):
        return True, 900.00

    # Kumpulan RM 1,000
    zon_1000 = [
        "morib", "banting", "telok panglima garang", "bandar", "jugra", "kelanang",
        "tanjong duabelas", "ampang pecah", "batang kali", "buloh telor", "kalumpang",
        "kerling", "kuala kalumpang", "peretak", "rasa", "serendah", "sungai gumut",
        "sungai tinggi", "ulu bernam", "ulu yam"
    ]
    if any(z in lokasi for z in zon_1000):
        return True, 1000.00

    # Kumpulan RM 1,200
    zon_1200 = [
        "kuala selangor", "tanjong karang", "sabak bernam", "seremban", "port dickson",
        "api-api", "batang berjuntai", "bestari jaya", "ijok", "jeram", "pasangan",
        "ujong pematang", "ulu tinggi", "bagan nakhoda omar", "panchang bedena",
        "pasiran panjang", "sabak", "sungai panjang", "ampangangan", "lenggeng",
        "pantai", "rantau", "rasah", "setul", "jimah", "linggi", "si rusa"
    ]
    if any(z in lokasi for z in zon_1200):
        return True, 1200.00

    # Jika tiada dalam senarai yang dibenarkan
    return False, 0.00

def respon_salah_kawasan():
    return "Maaf, lokasi pickup tersebut di luar senarai kawasan yang dibenarkan. Sila rujuk sales team untuk bantuan lanjut: https://wa.link/nrmesv"

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
            "- Masa pickup pergi : \n"
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
            "- Masa pickup pergi : \n"
            "- Tarikh Balik: \n"
            "- Jumlah Pax (Penumpang): "
        )

# ==========================================
# 4. MODUL KALKULATOR SEWAAN & ZON
# ==========================================

def bundar_ke_puluhan_atas(nilai):
    return math.ceil(nilai / 10.0) * 10