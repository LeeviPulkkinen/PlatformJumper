from Koodit.vakiot import ruutu_leveys, ruutu_korkeus, korkeus, leveys
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsEllipseItem
from PyQt5.QtGui import QColor, QPolygonF, QBrush
from PyQt5.QtCore import QPointF


class Taso:

    def __init__(self, taso_data, scene):
        self.taso_data = taso_data
        self.scene = scene
        self.maali = None
        self.objects = []  # lista luoduista maa paloista
        self.viholliset = []  # lista johon laitetaan viholliset, eli asiat joiden takia peli voi päättyä
        self.kolikot = []  # lista jossa säilötään tason kolikot

        self.lue_data()

    def lue_data(self):  # käy läpi tason datan ja lisää tarvittavat esineet
        y = 0
        for row in self.taso_data:
            x = 0
            for col in row:

                if col == 1:  # jos ruudun arvo on 1, luodaan maa palanen
                    maa = Maa(x, y)
                    self.scene.addItem(maa)  # lisätään maa sceneen
                    self.objects.append(maa)  # lisätään maa listaan

                if col == 2:  # jos ruudun arvo on 2, luodaan piikki
                    piikki = Piikki(x, y)
                    self.scene.addItem(piikki)  # lisätään piikki sceneen
                    self.viholliset.append(piikki)  # lisätään piikki listaan

                if col == 3:  # jos ruudun arvo on 3, luodaan maali

                    # tarkistetaan etta maalia ei ole luotu, jos maali on jo olemassa ruutu jää tyhjäksi

                    if self.maali is None:
                        maali = Maali(x, y)
                        self.maali = maali
                        self.scene.addItem(self.maali)  # lisätään maali sceneen

                if col == 4:  # jos ruudun arvo on 4, luodaan kolikko
                    kolikko = Kolikko(x, y)
                    self.kolikot.append(kolikko)  # lisätään kolikko listaan
                    self.scene.addItem(kolikko)  # lisätään kolikko sceneen

                x += ruutu_leveys  # kasvatetaan x-kordinaattia yhden ruudun leveydellä

            # jos datassa ei ole tarpeeksi ruutuja tai maali puuttuu, heitetään poikkeus

            if x < leveys:
                raise ValueError("virheellinen taso")

            y += ruutu_korkeus

        if y < korkeus or self.maali is None:
            raise ValueError("virheellinen taso")


class Maa(QGraphicsRectItem):  # maa luokka
    def __init__(self, x, y):
        super().__init__()
        self.setBrush(QColor(70, 100, 80))
        self.setPen(QColor(70, 100, 60))
        self.setRect(x, y, ruutu_leveys, ruutu_korkeus)


class Piikki(QGraphicsPolygonItem):  # luokka piikeille
    def __init__(self, x, y):
        super().__init__()

        #  luodaan kolmio joka piirretään näytölle piikkinä
        kolmio = QPolygonF()
        kolmio.append(QPointF(ruutu_leveys / 2, ruutu_leveys / 6))
        kolmio.append(QPointF(ruutu_leveys / 6, ruutu_leveys))
        kolmio.append(QPointF(ruutu_leveys - ruutu_leveys / 6, ruutu_leveys))
        kolmio.append(QPointF(ruutu_leveys / 2, ruutu_leveys / 6))

        self.setPolygon(kolmio)
        self.setPos(x, y)
        self.setBrush(QColor(70, 70, 70))
        self.setPen(QColor(0, 0, 0))


class Maali(QGraphicsRectItem):  # Maali luokka
    def __init__(self, x, y):
        super().__init__()
        self.brush = QBrush()
        self.brush.setStyle(14)
        self.setBrush(self.brush)
        self.setRect(x, y - ruutu_leveys // 2, ruutu_leveys, ruutu_korkeus * 1.5)


class Kolikko(QGraphicsEllipseItem):  # kolikko luokka
    def __init__(self, x, y):
        super().__init__()
        self.setRect(x + ruutu_leveys // 4, y + ruutu_korkeus // 4, ruutu_leveys // 2, ruutu_korkeus // 2)
        self.setBrush(QColor(255, 255, 0))
