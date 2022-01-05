# vakiot löytyvät yhdestä tiedostosta helppoa muokkausta varten

# ikkunan tiedot
leveys = 800
korkeus = 800

# ikkuna jaetaan ruutuihin
ruutu_maara = 20
ruutu_leveys = leveys // ruutu_maara
ruutu_korkeus = korkeus // ruutu_maara

ms_per_frame = 16  # 60fps

pelaajan_nopeus = 4
# pelaaja aloittaa tason aina kentän vasemmasta alakulmasta
alku = (ruutu_leveys + 2, korkeus - 2 * ruutu_leveys + 2)
