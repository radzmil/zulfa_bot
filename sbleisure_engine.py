import math
from datetime import datetime

# ==========================================
# 1. MODUL TERMA & SYARAT
# ==========================================

def paparkan_terma_dan_syarat():
    """Memaparkan terma dan syarat rasmi syarikat untuk dibaca pelanggan"""
    return (
        "糖 **SYARAT PEMBAYARAN & PEMBATALAN - DEPOSIT 50%**\n\n"
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
        "痩 *Adakah bos bersetuju dengan Terma & Syarat di atas? (Sila balas 'Setuju' untuk meneruskan tempahan)*"
    )


# ==========================================
# 2. MODUL VALIDASI & BORANG (GATEKEEPING KETAT)
# ==========================================

def validasi_pickup(lokasi):
    """Menyemak zon pickup mengikut senarai kawasan yang dibenarkan sahaja"""
    lokasi = lokasi.strip().lower()
    
    # Senarai zon yang dibenarkan (Selangor, KL, KLIA, Cyberjaya, Putrajaya)
    senarai_dibenarkan = [
        # Selangor - Petaling
        "bukit raja", "damansara", "petaling", "sungai buloh",
        # Selangor - Hulu Langat
        "ampang", "beranang", "cheras", "hulu langat", "kajang", "semenyih",
        # Selangor - Klang
        "kapar", "klang",
        # Selangor - Gombak
        "batu", "rawang", "setapak", "ulu kelang",
        # Selangor - Kuala Langat
        "bandar", "jugra", "kelanang", "morib", "tanjong duabelas", "telok panglima garang",
        # Selangor - Kuala Selangor
        "api-api", "batang berjuntai", "bestari jaya", "ijok", "jeram", "kuala selangor", "pasangan", "tanjong karang", "ujong permatang", "ulu tinggi",
        # Selangor - Sepang
        "dengkil", "labu", "sepang",
        # Selangor - Sabak Bernam
        "bagan nakhoda omar", "panchang bedena", "pasiran panjang", "sabak", "sungai panjang",
        # Selangor - Hulu Selangor
        "ampang pecah", "batang kali", "buloh telor", "kalumpang", "kerling", "kuala kalumpang", "peretak", "rasa", "serendah", "sungai gumut", "sungai tinggi", "ulu bernam", "ulu yam",
        # Kuala Lumpur (5 Daerah & Mukim)
        "kuala lumpur", "pusat bandar", "bukit bintang", "chow kit", "brickfields", "bangsar", "seputehe",
        "kepong", "segambut", "sentul", "jalan ipoh", "mont kiara", "sri hartamas", "batu caves",
        "wangsa maju", "danau kota", "taman melati", "semarak",
        "ampang hilir", "kampung pandan", "desa pandan", "maluri",
        # Tambahan Utama
        "klia", "cyberjaya", "putrajaya", "airport"
    ]
    
    ditemui = any(zon in lokasi for zon in senarai_dibenarkan)
    
    if ditemui:
        if any(z in lokasi for z in ["klia", "cyberjaya", "putrajaya", "airport"]):
            return True, 800.00
        else:
            return True, 700.00
            
    return False, 0.00

def respon_salah_kawasan():
    return "Maaf bos, lokasi pickup tersebut di luar zon operasi utama kitorang. Sila rujuk sales team untuk bantuan lanjut: https://wa.link/nrmesv"

def semak_tarikh_booking(tarikh_str):
    try:
        if '-' in tarikh_str and len(tarikh_str.split('-')[0]) == 4:
            tarikh_booking = datetime.strptime(tarikh_str, "%Y-%m-%d").date()
        else:
            tarikh_booking = datetime.strptime(tarikh_str, "%d-%m-%Y").date()
            
        tarikh_semasa = datetime.now().date()
        selisih_hari = (tarikh_booking - tarikh_semasa).days
        
        if selisih_hari < 0:
            return "tidak_sah", "Tarikh yang dipilih sudah lepas, bos."
        elif selisih_hari <= 7:
            return "urgent", f"Perhatian: Tarikh ni (dalam masa 7 hari) dikategorikan sebagai Urgent Booking. Sila sahkan dengan pihak kami."
        else:
            return "boleh", "Tarikh disahkan lulus untuk tempahan."
    except ValueError:
        return "ralat", "Format tarikh tidak sah. Sila guna format YYYY-MM-DD atau DD-MM-YYYY."

def paparkan_borang(jenis_transfer):
    jenis_transfer = jenis_transfer.strip().lower()
    
    if "two" in jenis_transfer or "2" in jenis_transfer:
        return (
            "統 **BORANG MAKLUMAT SEWAAN ( TWO WAY )**\n\n"
            "Syarikat : \n"
            "Alamat : \n\n"
            "Nama : \n"
            "No. tel : \n"
            "Tarikh : \n"
            "Masa : \n"
            "Pick-up point : \n"
            "Drop-off point : \n"
            "Pax : \n\n"
            "売 **Maklumat untuk RETURN trip :-**\n\n"
            "Tarikh : \n"
            "Masa : \n"
            "Pick-up point : \n"
            "Drop-off point : \n"
            "Pax : "
        )
    else:
        return (
            "統 **BORANG MAKLUMAT SEWAAN ( ONE WAY )**\n\n"
            "Syarikat : \n"
            "Alamat : \n\n"
            "Nama : \n"
            "No. tel : \n"
            "Tarikh : \n"
            "Masa : \n"
            "Pick-up point : \n"
            "Drop-off point : \n"
            "Pax : "
        )


# ==========================================
# 3. MODUL KALKULATOR SEWAAN & ZON
# ==========================================

def bundar_ke_puluhan_atas(nilai):
    return math.ceil(nilai / 10.0) * 10

def kira_harga_kenderaan_sbleisure(jenis_kenderaan="bas", jenis_transfer="one_way", lokasi_ambil="ampang", jarak_km=0, tarikh_pergi=None, tarikh_balik=None, pilihan_deposit=50):
    jenis_kenderaan = jenis_kenderaan.strip().lower()
    
    if jenis_kenderaan == "tour":
        return {
            "status": "rujuk_sales",
            "mesej": "Eh, utk trip jenis Tour ni kita tak terima booking online, bosku. Sila direct roger sales team kitorang kat sini eh: https://wa.link/nrmesv"
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
    
    return (f"Ok bos, anggaran harga untuk sewaan ni adalah **RM {hasil_kiraan['harga']}** (harga ni dah *all-in* termasuk tol semua skali ya). "
            f"Bos setuju tak dengan harga ni?")