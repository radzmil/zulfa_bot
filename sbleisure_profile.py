# ==========================================
# FILE: sbleisure_profile.py
# Modul Profil Syarikat SBLEISURE
# ==========================================
def get_profile_text():
    """Mengembalikan teks profil lengkap untuk system instruction."""
    p = get_company_identity()
    return f"""
    Nama Syarikat: {p['nama_syarikat']}
    No. SSM: {p['ssm_no']}
    Alamat: {p['alamat']}
    Google Maps: {p['google_maps']}
    Emel: {p['emel']}
    Telefon: {', '.join(p['telefon'])}
    Facebook: {p['facebook']}
    """
def get_company_identity():
    """Mengembalikan maklumat rasmi identiti dan pendaftaran syarikat SBLEISURE."""
    profile = {
        "nama_syarikat": "Shahril Basri Leisure Enterprise (SBLEISURE)",
        "ssm_no": "202203168334 (003413019-W)",
        "tahun_mula_operasi": 2017,
        "tahun_daftar_ssm": 2017,
        "alamat": "No. 8-1, 9-1, First Floor, Laman Niaga@Ampang Waterfront, Jalan AWF 3A, Ampang Waterfront, 68000, Ampang, Selangor",
        "google_maps": "https://maps.app.goo.gl/jSJHUNXjZdhiLDRbA",
        "emel": "sbltransport.my@gmail.com",
        "telefon": ["013-243 4200", "016-260 1885"],
        "facebook": "https://www.facebook.com/sewabaspersiaranmurah"
    }
    return profile

def get_payment_link():
    """Mengembalikan maklumat akaun bank rasmi untuk urusan deposit/pembayaran."""
    payment_info = {
        "bank": "CIMB Bank Berhad",
        "no_akaun": "860 5247 780",
        "nama_pemegang_akaun": "Shahril Basri Leisure Enterprise"
    }
    return payment_info

def get_fleet_and_services():
    """Senarai kenderaan dan perkhidmatan pengangkutan yang ditawarkan."""
    services = {
        "kenderaan": [
            "Bas Persiaran",
            "Van Persiaran",
            "MPV Mewah (Toyota Vellfire, Innova)",
            "Van Bagasi & Lori Logistik"
        ],
        "cakupan": "Seluruh Malaysia serta rentas sempadan ke Singapura dan Thailand",
        "kategori_pelanggan": [
            "Sektor Korporat",
            "Agensi Kerajaan",
            "Institusi Pendidikan (Sekolah/Universiti)",
            "Pelanggan Individu / Rombongan"
        ]
    }
    return services

def get_experience_and_clients():
    """Rekod pengalaman dan senarai klien utama syarikat."""
    experience = {
        "klien_kerajaan": [
            "Jabatan Muzium Malaysia",
            "Kementerian Pendidikan Malaysia (KPM)",
            "Kementerian Dalam Negeri (KDN)",
            "Akademi Binaan Malaysia (ABM)"
        ],
        "pengkhususan_khas": [
            "Sokongan logistik ketenteraan (Operasi MALBATT)",
            "Pengangkutan seminar, kursus, dan pelancongan rasmi"
        ]
    }
    return experience