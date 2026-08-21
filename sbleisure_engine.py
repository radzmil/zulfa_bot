def semak_tarikh_booking(tarikh_str):
    """
    SOP KETAT TARIKH:
    - 7 hari atau kurang dari tarikh semasa = Urgent Booking (TIDAK BOLEH ambil tempahan, rujuk sales)
    - 8 hari dan seterusnya = Lulus untuk tempahan
    """
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
            return "urgent", "Maaf bos, untuk tempahan dalam masa 7 hari atau kurang (urgent booking), sistem tak boleh terima. Sila direct roger sales team kitorang ya: https://wa.link/nrmesv"
        else:
            return "boleh", "Tarikh disahkan lulus untuk tempahan."
    except ValueError:
        return "ralat", "Format tarikh tidak sah. Sila guna format YYYY-MM-DD atau DD-MM-YYYY."