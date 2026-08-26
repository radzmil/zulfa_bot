import sbleisure_engine

# Senarai test laluan untuk disemak
laluan_test = [
    ("klia", "raub"),
    ("ampang", "raub"),
    ("klia", "janda baik"),
    ("ampang", "kajang")
]

print("=== KEPUTUSAN TEST ENJIN HARGA SBLEISURE ===")
for pickup, destinasi in laluan_test:
    # Cuba semak terus dari jadual tetap atau pengiraan
    harga = sbleisure_engine.kira_harga_bas(pickup, destinasi, jarak_km=100)
    print(f"Trip dari [{pickup.upper()}] ke [{destinasi.upper()}] -> RM{harga:.2f}")

# Test fungsi validasi mukim pickup
print("\n=== TEST VALIDASI PICKUP ===")
sah, asas = sbleisure_engine.validasi_pickup("klia")
print(f"Pickup 'klia' sah? {sah}, Harga Asas: RM{asas}")