# ==========================================
# FILE: sbleisure_profile.py
# Modul Profil Syarikat SBLEISURE
# ==========================================

def get_company_identity():
    """Mengembalikan maklumat rasmi identiti dan pendaftaran syarikat SBLEISURE."""
    profile = {
        "nama_syarikat": "Shahril Basri Leisure Enterprise (SBLEISURE)",[cite: 2]
        "ssm_no": "202203168334 (003413019-W)",[cite: 2]
        "tahun_mula_operasi": 2017,[cite: 2]
        "tahun_daftar_ssm": 2022,[cite: 2]
        "alamat": "No. 8-1, 9-1, First Floor, Laman Niaga@Ampang Waterfront, Jalan AWF 3A, Ampang Waterfront, 68000, Ampang, Selangor",[cite: 2]
        "google_maps": "https://maps.app.goo.gl/jSJHUNXjZdhiLDRbA",
        "emel": "sbltransport.my@gmail.com",[cite: 2]
        "telefon": ["013-243 4200", "016-260 1885"],[cite: 2]
        "facebook": "https://www.facebook.com/sewabaspersiaranmurah"[cite: 2]
    }
    return profile

def get_payment_link():
    """Mengembalikan maklumat akaun bank rasmi untuk urusan deposit/pembayaran."""
    payment_info = {
        "bank": "CIMB Bank Berhad",[cite: 2]
        "no_akaun": "860 5247 780",[cite: 2]
        "nama_pemegang_akaun": "Shahril Basri Leisure Enterprise"[cite: 2]
    }
    return payment_info

def get_fleet_and_services():
    """Senarai kenderaan dan perkhidmatan pengangkutan yang ditawarkan."""
    services = {
        "kenderaan": [
            "Bas Persiaran",[cite: 2]
            "Van Persiaran",[cite: 2]
            "MPV Mewah (Toyota Vellfire, Innova)",[cite: 2]
            "Van Bagasi & Lori Logistik"[cite: 2]
        ],
        "cakupan": "Seluruh Malaysia serta rentas sempadan ke Singapura dan Thailand",[cite: 2]
        "kategori_pelanggan": [
            "Sektor Korporat",[cite: 2]
            "Agensi Kerajaan",[cite: 2]
            "Institusi Pendidikan (Sekolah/Universiti)",[cite: 2]
            "Pelanggan Individu / Rombongan"[cite: 2]
        ]
    }
    return services

def get_experience_and_clients():
    """Rekod pengalaman dan senarai klien utama syarikat."""
    experience = {
        "klien_kerajaan": [
            "Jabatan Muzium Malaysia",[cite: 2]
            "Kementerian Pendidikan Malaysia (KPM)",[cite: 2]
            "Kementerian Dalam Negeri (KDN)",[cite: 2]
            "Akademi Binaan Malaysia (ABM)"[cite: 2]
        ],
        "pengkhususan_khas": [
            "Sokongan logistik ketenteraan (Operasi MALBATT)",[cite: 2]
            "Pengangkutan seminar, kursus, dan pelancongan rasmi"[cite: 2]
        ]
    }
    return experience