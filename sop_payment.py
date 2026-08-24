# ==========================================
# FAIL: sop_payment.py
# MODUL SOP PAYMENT, TERMA SYARAT & NOTIFIKASI
# ==========================================
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Konstanta Admin Rasmi
GROUP_ADMIN_NUMBER = "60132434200"
ADMIN_EMAIL = "sbltransport.my@gmail.com"
TOYYIBPAY_LINK = "https://toyyibpay.com"  # Ganti dengan pautan ToyyibPay sebenar jika ada
QR_CODE_DIRECT_LINK = ""              # Masukkan pautan imej QR DuitNow jika ada

def get_sop_payment_text():
    return """
SOP & POLISI PEMBAYARAN (sbleisure_payment_sop):

1. STRUKTUR PEMBAYARAN:
- Deposit 50% ke CIMB (SHAHRIL BASRI LEISURE ENTERPRISE): Diperlukan untuk lock tarikh & bas selepas sebut harga dihantar.
- Baki 50% pengesahan: Mesti dijelaskan penuh sekurang-kurangnya 2 hari sebelum tarikh perjalanan.

2. POLISI PEMBATALAN OLEH PELANGGAN:
- Lebih 14 hari sebelum tarikh perjalanan: Refund 90% daripada jumlah deposit (tolak 10% yuran pentadbiran).
- 7 hingga 14 hari sebelum tarikh perjalanan: Refund 50% daripada jumlah deposit.
- Kurang daripada 2 hari (<2 hari): Hangus 100% daripada jumlah bayaran penuh.
- Gagal menjelaskan baki 2 hari sebelum tarikh: Tempahan dibatalkan secara automatik dan deposit hangus.

3. POLISI PENUNDAAN TARIKH (POSTPONEMENT):
- Dibenarkan 1 kali sahaja dengan syarat notis minimum 7 hari sebelum tarikh asal.
- Caj penundaan RM200 dikenakan jika notis kurang daripada 7 hari.

4. PEMBATALAN OLEH PIHAK SYARIKAT:
- Dikembalikan 100% penuh dalam tempoh 7 hari bekerja.
"""

def paparkan_terma_pembayaran_ringkas():
    return (
        "**RINGKASAN POLISI PEMBAYARAN & DEPOSIT**\n\n"
        "• **Deposit 50%**: Perlu dilunaskan ke akaun CIMB (SHAHRIL BASRI LEISURE ENTERPRISE) untuk *lock* tarikh bas[cite: 3].\n"
        "• **Baki 50%**: Perlu dijelaskan 2 hari sebelum tarikh perjalanan[cite: 3].\n\n"
        "Sila balas **'Setuju'** pada Terma & Syarat untuk meneruskan tempahan anda."
    )

def format_admin_notification(data):
    return (
        f"🚨 **NOTIFIKASI TEMPAHAN / PEMBAYARAN BAHARU** 🚨\n\n"
        f"• **ID Tempahan:** {data.get('ref_id', '-')}\n"
        f"• **Nama Pelanggan:** {data.get('nama', '-')}\n"
        f"• **No Telefon:** {data.get('no_tel', '-')}\n"
        f"• **Tarikh Perjalanan:** {data.get('tarikh', '-')}\n"
        f"• **Pick-up:** {data.get('pickup', '-')}\n"
        f"• **Drop-off:** {data.get('dropoff', '-')}\n"
        f"• **Jumlah Harga:** RM{data.get('harga', 0):.2f}\n"
        f"• **Status Bayaran:** {data.get('status_bayaran', 'Selesai/Deposit')}\n\n"
        f"Sila semak akaun bank rasmi (CIMB - SHAHRIL BASRI LEISURE ENTERPRISE) untuk pengesahan[cite: 3]."
    )

def hantar_emel_admin(data_tempahan):
    """Fungsi untuk menghantar notifikasi butiran tempahan ke emel rasmi syarikat"""
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "zulfa.sbltransport@gmail.com"
    sender_password = "H@$$ayang8683"
    admin_email = "sbltransport.my@gmail.com"

    subjek = f"🔔 Tempahan Baru Disahkan - ID: {data_tempahan.get('ref_id', 'SB-LEISURE')}"
    isi_mesej = format_admin_notification(data_tempahan)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = admin_email
    msg['Subject'] = subjek
    msg.attach(MIMEText(isi_mesej, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, admin_email, msg.as_string())
        server.quit()
        print(f"Emel berjaya dihantar ke {admin_email}")
        return True
    except Exception as e:
        print(f"Ralat menghantar emel: {e}")
        return False