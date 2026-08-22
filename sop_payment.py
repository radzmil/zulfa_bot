# ==========================================
# FAIL: sop_payment.py
# MODUL SOP PAYMENT & TERMA SYARAT (RUJUKAN ZULFA)
# ==========================================

def get_sop_payment_text():
    """Mengembalikan teks rasmi SOP pembayaran, polisi kewangan dan syarat untuk rujukan Zulfa AI"""
    return """
SOP & POLISI PEMBAYARAN (sbleisure_payment_sop):

1. STRUKTUR PEMBAYARAN:
- Deposit 50%: Diperlukan untuk lock tarikh & bas selepas sebut harga (quotation) dihantar kepada pelanggan.
- Baki 50%: Mesti dijelaskan penuh sekurang-kurangnya 2 hari sebelum tarikh perjalanan.

2. POLISI PEMBATALAN OLEH PELANGGAN:
- Lebih 14 hari sebelum tarikh perjalanan: Refund 90% daripada jumlah deposit (tolak 10% yuran pentadbiran).
- 7 hingga 14 hari sebelum tarikh perjalanan: Refund 50% daripada jumlah deposit.
- Kurang daripada 2 hari (<2 hari) sebelum tarikh perjalanan: Hangus 100% (burn 100%) daripada jumlah bayaran penuh.
- Gagal menjelaskan baki 2 hari sebelum tarikh: Tempahan dibatalkan secara automatik dan deposit hangus.

3. POLISI PENUNDAAN TARIKH (POSTPONEMENT):
- Dibenarkan sebanyak 1 kali sahaja dengan syarat notis diberikan minimum 7 hari sebelum tarikh asal.
- Deposit boleh dipindahkan ke tarikh baharu yang dipersetujui.
- Jika notis penundaan kurang daripada 7 hari (<7 hari), caj penundaan sebanyak RM200 akan dikenakan.

4. PEMBATALAN OLEH PIHAK SYARIKAT:
- Sekiranya pembatalan dibuat oleh pihak syarikat, deposit serta baki yang telah dibayar akan dikembalikan 100% penuh dalam tempoh 7 hari bekerja.
"""

def paparkan_terma_pembayaran_ringkas():
    """Paparan ringkas terma pembayaran untuk mesej bot mesra pelanggan"""
    return (
        "**RINGKASAN POLISI PEMBAYARAN & DEPOSIT**\n\n"
        "• **Deposit 50%**: Perlu dilunaskan untuk *lock* tarikh bas.\n"
        "• **Baki 50%**: Perlu dijelaskan 2 hari sebelum tarikh perjalanan.\n"
        "• **Pembatalan**: Bergantung pada terma notis (rujuk SOP penuh).\n"
        "• **Penundaan**: Dibenarkan 1x dengan notis minimum 7 hari.\n\n"
        "Sila balas **'Setuju'** pada Terma & Syarat untuk meneruskan tempahan anda."
    )