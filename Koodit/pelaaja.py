from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from Koodit.vakiot import ruutu_leveys, ruutu_korkeus, pelaajan_nopeus, alku


class Pelaaja(QGraphicsEllipseItem):
    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.painovoima = 0
        # luodaan muutuja jonka avulla voidaan pitää kirjaa tason aikana kerätyistä pisteistä
        self.score = 0
        self.init_pelaaja()  # luodaan pelaaja ensin kohtaan 0, 0 jotta se käyttää samaa koordinaatistoa kuin scene
        self.hyppy = False  # muuttuja jonka avulla tarkastellaan onko pelaaja hyppäämässä
        self.setPos(alku[0], alku[1])  # siirretään pelaaja oikeaan paikkaan.

        self.setBrush(QColor(255, 100, 60))
        self.setPen(QColor(70, 100, 60))

    def init_pelaaja(self):  # lisätään pelaaja sceneen
        self.scene.addItem(self)
        self.setRect(0, 0, ruutu_leveys - 5, ruutu_korkeus - 5)  # tehdään pelaajasta hieman pienempi kuin ruuduista

    def update_pelaaja(self, painallukset, game_state):

        # tämä funktio hoitaa pelaajan liikuttamisen ja collision detectionin
        # pelaajaa päivitetään vain jos game_state = 0, eli peli on käynnissä

        if game_state == 0:

            # käytetään dx ja dy muuttujia jotta ennen pelaajan paikan muuttamista voidaan tehdä tarkistuksia ilman että
            # pelaajan paikkaa muutetaan välittömästi

            dx = 0
            dy = 0

            # ylöspäin nuolella saadaan pelaaja hyppäämään

            if Qt.Key_Up in painallukset and not self.hyppy and self.painovoima == 0:
                self.painovoima = -15  # muutetaan painovoima hetkellisesti negatiiviseksi
                self.hyppy = True

            # Pelaajan siirtely vaakatasossa nuolinäppäimillä

            if Qt.Key_Left in painallukset:
                dx -= pelaajan_nopeus

            if Qt.Key_Right in painallukset:
                dx += pelaajan_nopeus

            self.painovoima += 1  # painovoima lisääntyy jatkuvasti jotta pelaaja tippuu alaspäin ollessaan ilmassa
            if self.painovoima >= 10:  # asetetaan raja painovoiman maksimille
                self.painovoima = 10
            dy += self.painovoima

            '''Törmäyksen tunnistus: katsotaan jokaista sceneen lisättyä tason osaa erikseen ja verrataan törmäisikö 
            pelaaja siihen jos pelaaja liikkuisi. Luodaan väliaikainen QGraphicsRectItem jonka sijaintia verratan 
            tason osaan. jos törmäystä ei tapahdu voi pelaaja liikkua normaalisti. Pallon todellinen "hitbox" on siis 
            neliö, koska se tekee törmäyksen tunnistamisesta sulavampaa '''

            item_list = self.scene.taso.objects
            for item in item_list:
                if item.collidesWithItem(QGraphicsRectItem(self.x() + dx, self.y(), ruutu_korkeus - 6, ruutu_leveys - 6)):
                    dx = 0  # koska törmäys tapahtuu, ei x-kordinaattia muuteta

                elif item.collidesWithItem(QGraphicsRectItem(self.x(), self.y() + dy, ruutu_korkeus - 5, ruutu_leveys - 5)):
                    dy = 0  # koska törmäys tapahtuu, ei y-kordinaattia muuteta

                    #  jos pelaaja on hyppäämässä kun törmäys tapahtuu, asetetaan painovoimaksi 0,
                    #  jotta pelaaja ei hetkellisesti jää ilmaan leijumaan

                    if self.painovoima < 0:
                        self.painovoima = 0

                    #  jos pelaaja on tippumassa tai maassa kun törmäys tapahtuu
                    elif self.painovoima >= 0:
                        self.hyppy = False
                        self.painovoima = 0

            self.setPos(self.x() + dx, self.y() + dy)  # muutetaan pelaajaan paikkaa

            # käydään läpi tason viholliset (piikit)

            viholliset = self.scene.taso.viholliset
            for vihollinen in viholliset:
                if vihollinen.collidesWithItem(self):
                    #  jos törmäys viholliseen tapahtuu, game stateksi asetetaan -1
                    game_state = -1

            # käydään läpi kaikki tason kolikot

            kolikot = self.scene.taso.kolikot
            if len(kolikot) != 0:  # tarkistetaan onko tasolla kolikoita
                for kolikko in kolikot:
                    if kolikko.collidesWithItem(self):

                        # törmäyksen sattuessa, poistetaan kolikko listasta ja scenestä

                        self.scene.removeItem(kolikko)
                        kolikot.remove(kolikko)

                        # tämä osa täytyi sisällyttää jotta scoren määrä ei olisi riippuvainen kolikon ja pelajaan
                        # törmäyksen pituudesta

                        if kolikko not in kolikot:
                            self.score += 1  # lisätään scoreen 1

                            # asetetaan score counteriin oikea arvo

                            self.scene.score_counter.setText(f"{self.scene.score + self.score}")

            # Tarkistetaan onko pelaaja maalissa

            if self.scene.taso.maali.collidesWithItem(self):
                self.scene.score += self.score  # kun pelaaja saavuttaa maalin, kolikot lisätään scoreen
                self.score = 0  # nollataan tasokohtainen score
                game_state = 1

        return game_state  # palautetaan game state joka kertoo onko pelaaja maalissa tai hävinnyt



