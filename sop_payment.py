# ==========================================
# FILE: sop_payment.py
# Modul SOP Pembayaran & Kewangan SBLEISURE
# ==========================================
import os

def get_bank_details():
    """Maklumat akaun bank rasmi syarikat untuk transaksi pembayaran."""
    return {
        "bank": "CIMB Bank Berhad",
        "no_akaun": "860 5247 780",
        "nama_pemegang_akaun": "Shahril Basri Leisure Enterprise"
    }

def get_toyyibpay_link():
    """Pautan ToyyibPay rasmi syarikat."""
    return os.getenv("TOYYIBPAY_LINK", "https://toyyibpay.com/sbl-online")

def get_qr_code_link():
    """Pautan QR Code DuitNow rasmi syarikat."""
    return "https://i.ibb.co/YTP80GLk/Whats-App-Image-2026-08-19-at-9-27-28-PM.jpg"

def get_group_admin_number():
    """Mendapatkan nombor WhatsApp group admin dari Environment Variables (Railway)."""
    return os.getenv("GROUP_ADMIN_NUMBER", "")

def get_payment_and_cancellation_sop_text():
    """Teks syarat rasmi pembayaran dan pembatalan mengikut SOP Jannah/Zulfa."""
    return (
        "SYARIKAT PEMBAYARAN & PEMBATALAN:\n"
        "1. Pembayaran: Deposit 50% untuk lock tarikh (baki 50% 2 hari sebelum) atau Full Payment.\n"
        "2. Pembatalan oleh Pelanggan:\n"
        "   - >14 hari sebelum tarikh: Refund 90% (potong 10% yuran admin).\n"
        "   - 7-14 hari sebelum tarikh: Refund 50%.\n"
        "   - <2 hari sebelum tarikh: Burn 100%.\n"
        "   - Gagal bayar baki 2 hari sebelum (jika deposit): Tempahan terbatal, deposit burn.\n"
        "3. Penundaan Tarikh: Dibenarkan 1 kali (notis 7 hari awal). Jika <7 hari, caj RM200.\n"
        "4. Pembatalan oleh Syarikat: Refund 100% dalam 7 hari bekerja.\n"
        "5. Nota Penting: Deposit adalah untuk menahan tarikh. Jika tarikh dibatalkan, deposit tidak dikembalikan."
    )

def get_payment_instructions_text():
    """Format teks pilihan cara bayar kepada pelanggan."""
    bank = get_bank_details()
    toyyib = get_toyyibpay_link()
    qr_link = get_qr_code_link()
    return (
        "Orite, tq bos! Ni cara bayar yang senang:\n\n"
        f"• ToyyibPay: {toyyib}\n"
        f"• QR DuitNow: {qr_link}\n"
        f"• Transfer/CDM: {bank['bank']} - {bank['no_akaun']} ({bank['nama_pemegang_akaun']})\n\n"
        "Dah setel nanti, rojer hantar gambar resit atau slip CDM kat Zulfa k."
    )

def format_admin_notification(booking_details):
    """Format mesej butiran tempahan yang siap dibayar untuk dihantar ke GROUP_ADMIN_NUMBER."""
    admin_no = get_group_admin_number()
    return (
        f"🚨 *UPDATE: NEW PAYMENT RECEIVED* 🚨\n\n"
        f"• *Reference ID / Bukti:* {booking_details.get('ref_id', '-')}\n"
        f"• *Nama Customer:* {booking_details.get('nama', '-')}\n"
        f"• *Tarikh Perjalanan:* {booking_details.get('tarikh', '-')}\n"
        f"• *Jenis Transfer:* {booking_details.get('transfer_type', '-')}\n"
        f"• *Masa Pickup & Return:* {booking_details.get('masa', '-')}\n"
        f"• *Destinasi/Lokasi:* {booking_details.get('destinasi', '-')}\n"
        f"• *Status Bayaran:* {booking_details.get('status_bayaran', 'PAID (Deposit 50% / Full)')}\n\n"
        f"Target Admin No: {admin_no}"
    )

def get_customer_completion_message(nama_pelanggan):
    """Ucapan terima kasih rasmi kepada pelanggan selepas admin sahkan pembayaran."""
    return (
        f"Yeay, terima kasih banyak {nama_pelanggan}! Bayaran dah berjaya direkodkan. "
        "Booking bas awk rasmi confirmed! 🚌✨ "
        "Nanti team kitorang akan contact awk untuk details driver dan perjalanan ya."
    )