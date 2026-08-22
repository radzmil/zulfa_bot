# ==========================================
# FAIL: sop_payment.py
# MODUL SOP PAYMENT & TERMA SYARAT (RUJUKAN ZULFA)
# ==========================================

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
        "• **Deposit 50%**: Perlu dilunaskan ke akaun CIMB (SHAHRIL BASRI LEISURE ENTERPRISE) untuk *lock* tarikh bas.\n"
        "• **Baki 50%**: Perlu dijelaskan 2 hari sebelum tarikh perjalanan.\n\n"
        "Sila balas **'Setuju'** pada Terma & Syarat untuk meneruskan tempahan anda."
    )

def format_admin_notification(data):
    return (
        f"🚨 **NOTIFIKASI TEMPAHAN / PEMBAYARAN BAHARU** 🚨\n\n"
        f"• **ID Tempahan:** {data.get('ref_id')}\n"
        f"• **Nama Pelanggan:** {data.get('nama')}\n"
        f"• **Jenis / Mesej:** {data.get('transfer_type')}\n"
        f"• **Status Semasa:** {data.get('status_bayaran')}\n\n"
        f"Sila semak akaun bank rasmi (CIMB - SHAHRIL BASRI LEISURE ENTERPRISE) untuk pengesahan."
    )