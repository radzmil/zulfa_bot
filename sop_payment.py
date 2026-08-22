import logging

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ==========================================
# 1. MAKLUMAT AKAUN BANK, TOYYIBPAY & QR CODE
# ==========================================
COMPANY_NAME = "SHAHRIL BASRI LEISURE ENTERPRISE"
BANK_NAME = "CIMB Bank"
ACCOUNT_NAME = "SHAHRIL BASRI LEISURE ENTERPRISE"
ACCOUNT_NUMBER = "MASUKKAN_NOMBOR_AKAUN_CIMB_DI_SINI"  # Sila kemaskini nombor akaun CIMB rasmi syarikat

# Pautan Rasmi ToyyibPay & Direct Image Link QR Code DuitNow
TOYYIBPAY_LINK = "https://toyyibpay.com/sbl-online"
QR_CODE_DIRECT_LINK = "https://i.ibb.co/YTP80GLk/Whats-App-Image-2026-08-19-at-9-27-28-PM.jpg"

KADAR_DEPOSIT = "50% deposit atau bayaran penuh (Full Payment)"

# ==========================================
# 2. FUNGSI SOKONGAN & SOP PEMBAYARAN
# ==========================================

def get_payment_details():
    """
    Memulangkan maklumat lengkap pilihan pembayaran rasmi syarikat.
    """
    return (
        f"**Pilihan Pembayaran Rasmi ({COMPANY_NAME}):**\n\n"
        f"1. **Imbas QR Code DuitNow ({BANK_NAME}):**\n"
        f"   Pautan Imej QR: {QR_CODE_DIRECT_LINK}\n"
        f"   Imbas QR Code atas nama **{ACCOUNT_NAME}** untuk bayaran menerusi aplikasi perbankan anda.\n\n"
        f"2. **Bayaran Dalam Talian (ToyyibPay):**\n"
        f"   Pautan Rasmi: {TOYYIBPAY_LINK}\n\n"
        f"3. **Pindahan Bank Direct (FPX / Online Transfer):**\n"
        f"   Bank: {BANK_NAME}\n"
        f"   Nama Akaun: **{ACCOUNT_NAME}**\n"
        f"   Nombor Akaun: **{ACCOUNT_NUMBER}**\n\n"
        f"Syarat Pembayaran: **{KADAR_DEPOSIT}**\n"
        f"Sila kemukakan resit/bukti pembayaran rasmi selepas transaksi dibuat untuk pengesahan tempahan."
    )


def get_sop_text():
    """
    Memulangkan teks SOP Pembayaran untuk dimasukkan ke dalam System Instruction Zulfa.
    """
    return f"""
    - **Kaedah Pembayaran**: Pelanggan boleh membuat bayaran melalui:
      1. Imbasan QR Code DuitNow CIMB Bank Syarikat ({ACCOUNT_NAME}). Pautan imej QR rasmi: {QR_CODE_DIRECT_LINK}
      2. Pautan ToyyibPay rasmi ({TOYYIBPAY_LINK}).
      3. Pindahan bank terus ke akaun {BANK_NAME}: **{ACCOUNT_NAME}** ({ACCOUNT_NUMBER}).
    - **Syarat Deposit**: Pelanggan perlu membayar **50% deposit** atau **Bayaran Penuh (Full Payment)** untuk mengesahkan tempahan bas.
    - **Baki Pembayaran**: Jika membayar deposit 50%, baki bayaran perlu dijelaskan sekurang-kurangnya **3 hari sebelum** tarikh perjalanan.
    - **Pengesahan Bayaran**: Pelanggan WAJIB menghantar resit rasmi transaksi bank, tangkap layar ToyyibPay, atau resit imbasan QR untuk tujuan rekod sistem.
    - **Pembatalan / Polisi Pemulangan**: Bayaran deposit tidak akan dipulangkan jika pembatalan dibuat kurang daripada 7 hari dari tarikh perlepasan.
    """