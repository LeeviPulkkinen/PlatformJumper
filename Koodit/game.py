import sys
from PyQt5.QtCore import Qt, QBasicTimer
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QMainWindow, QPushButton, QLabel, QShortcut
from PyQt5.QtGui import QColor, QFont, QKeySequence
from Koodit.vakiot import leveys, korkeus, ms_per_frame
from Koodit.Taso import Taso
from Koodit.pelaaja import Pelaaja


class Scene(QGraphicsScene):

    def __init__(self):
        super().__init__()
        self.init_scene()

    # tehdään erillinen init funktio jota voidaan kutsua myös luokan ulkopuolelta

    def init_scene(self):
        self.ikkuna = Ikkuna(self)
        self.view = QGraphicsView(self, self.ikkuna)  # luodaan grapichsview
        self.painallukset = set()  # säilötään havaitut painallukset
        self.kello = QBasicTimer()  # luodaan kello jonka avulla pelinäkymään voidaan päivittää

        self.taso_nro = 0  # pidetään kirjaa missä tasossa ollaan menossa
        self.game_state = 0  # -1 : pelaaja häviää tason, 0 : peli jatkuu normaalisti, 1 : pelaaja on voittanut tason
        self.score = 0  # pelaajan kokonaispisteet
        self.score_counter = self.luo_score()

        self.taso = Taso(taso_data[self.taso_nro], self)  # luodaan taso
        self.pelaaja = Pelaaja(self)  # luodaan pelaaja
        self.init_view()
        self.kello.start(ms_per_frame, self)

    def init_view(self):
        self.setBackgroundBrush(QColor(150, 150, 150))
        self.setSceneRect(0, 0, leveys, korkeus)
        self.view.setGeometry(0, 0, leveys + 3,
                              korkeus + 3)  # kokoon oli lisättävä kolme pikseliä tilan puutteen vuoksi
        self.view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)  # Poistetaan mahdollisuus scrollbarin esiintymiselle
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.show()

    def keyPressEvent(self, e):  # havaitsee pelaajan painamat napit ja lisää ne listaan
        self.painallukset.add(e.key())

    def keyReleaseEvent(self, e):  # havaitsee kun pelaaja lopettaa napin painamisen ja poistaan sen listasta
        if e.key() in self.painallukset:
            self.painallukset.remove(e.key())

    def timerEvent(self, e):  # päivittää pelaajan sijainnin aina kun havaitaan kello tapahtuma

        #  pelaajan päivitys palauttaa aina päivitetyn game staten

        self.game_state = self.pelaaja.update_pelaaja(self.painallukset, self.game_state)

        if self.game_state == -1:  # jos pelaaja on osunut viholliseen, aloitetaan taso alusta
            self.restart_level()

        elif self.game_state == 1:  # jos pelaaja on maalissa, luodaan uusi taso
            self.uusi_taso()

    def uusi_taso(self):
        self.taso_nro += 1
        if self.taso_nro >= len(taso_data):  # jos kyseessä on viimeinen taso, pelaaja voittaa pelin
            self.voitto()
            with open('scores', 'r+') as data:  # avataan tiedosto jossa säilötään pelaajien tulokset
                self.top_scores(data)
                data.write(f"{self.score}\n")  # lisätään viimeisin tulos tiedostoon

        else:
            self.clear()  # tyhjennetään scene jotta tällä funktiolla voidaan luoda uusia tasoja
            self.game_state = 0
            self.taso = Taso(taso_data[self.taso_nro], self)  # luodaan seuraava taso
            self.pelaaja = Pelaaja(self)  # luodaan pelaaja

    def luo_score(self):

        # luodaan ruudun vasempaan yläkulmaan laskuri joka näyttää scoren

        label = QLabel(self.ikkuna)
        label.setText(f"{self.score}")
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # muutetaan fonttia
        font = label.font()
        font.setBold(True)
        font.setStyle(3)
        label.setFont(font)

        label.show()

        return label

    def restart_level(self):

        # funktio jonka avulla tason voi aloittaa helposti alusta
        if self.game_state != 1:
            self.clear()  # tyhjennetään scene
            self.taso = Taso(taso_data[self.taso_nro], self)  # luodaan sama taso uudestaan
            self.pelaaja = Pelaaja(self)  # luodaan pelaaja uudestaan
            self.score_counter.setText(f"{self.score}")  # poistetaan tason aikana saadut pisteet
            self.game_state = 0

    def voitto(self):

        # kun pelaaja voittaa pelin, pysäytetään kello, luodaan voittonäkymä ja kaksi nappia

        self.kello.stop()
        self.clear()
        self.setBackgroundBrush(QColor(200, 220, 200))

        text = self.addText("Voitit Pelin!")
        text.setScale(5)
        text.setPos(leveys // 5, 150)

        # luodaan kaksi nappia
        self.ikkuna.exit_button()
        self.ikkuna.replay_button()

    def top_scores(self, data):
        scoret = [self.score]  # uusin score on valmiina listassa

        for line in data:  # käydään tiedosto läpi ja lisätään tulokset listaan
            try:

                # tarkastetaan että line voidaan muuttaa numeroksi ja että se on >= 0

                line = int(line)
                if line >= 0:
                    scoret.append(line)

            except ValueError:  # jos score tiedostossa on jotain ylimääräistä, se yksin kertaisesti jätetään huomiotta
                pass

        scoret.sort(reverse=True)

        # jos peliä ei ole läpäisty vielä viittä kertaa, lisätään top scores taulukkoon tarvittava määrä nollia

        if len(scoret) < 5:

            if len(scoret) == 0:
                score1, score2, score3, score4, score5 = 0, 0, 0, 0, 0

            elif len(scoret) == 1:
                score1 = scoret[0]
                score2, score3, score4, score5 = 0, 0, 0, 0

            elif len(scoret) == 2:
                score1, score2 = scoret[0], scoret[1]
                score3, score4, score5 = 0, 0, 0

            elif len(scoret) == 3:
                score1, score2, score3 = scoret[0], scoret[1], scoret[2]
                score4, score5 = 0, 0

            elif len(scoret) == 4:
                score1, score2, score3, score4 = scoret[0], scoret[1], scoret[2], scoret[3]
                score5 = 0

        # valitaan viisi parasta tulosta listasta
        else:
            score1, score2, score3, score4, score5 = scoret[0], scoret[1], scoret[2], scoret[3], scoret[4]

        # luodaan scoreboard
        label = QLabel(self.ikkuna)
        label.setText(f"Top Scores:\n{score1}\n{score2}\n{score3}\n{score4}\n{score5}\n")
        label.setGeometry(leveys // 2 - 50, korkeus // 2, 200, 300)
        label.setFont(QFont('Arial', 15))

        #  muutetaan fonttia
        font = label.font()
        font.setBold(True)

        label.setFont(font)
        label.show()


class Ikkuna(QMainWindow):
    def __init__(self, scene):
        super(Ikkuna, self).__init__()
        self.scene = scene
        self.init_ikkuna()  # luodaan ikkuna
        self.luo_pikanappaimet()

    def init_ikkuna(self):
        self.setGeometry(560, 100, korkeus, leveys)
        self.setWindowTitle("Tasohyppelypeli")
        self.show()

    def exit_button(self):  # luo napin jolla voidaan sulkea peli
        exit_button = QPushButton("Quit", self)
        exit_button.setGeometry(leveys // 2 - exit_button.width(), korkeus // 2 - 100, 100, 50)
        exit_button.clicked.connect(self.exit_on_click)
        exit_button.show()

    def exit_on_click(self):  # exit_buttonin toiminta klikattaessa
        self.close()

    def replay_button(self):  # luo napin jolla voi aloittaa tason alusta
        replay_button = QPushButton("Replay", self)
        replay_button.setGeometry(leveys // 2, korkeus // 2 - 100, 100, 50)
        replay_button.clicked.connect(self.replay_on_click)
        replay_button.show()

    def replay_on_click(self):  # replay_buttonin toiminta klikattaessa
        self.scene.clear()
        self.scene.init_scene()

    def luo_pikanappaimet(self):  # luo pikanäppäimet joilla voidaan sulkea peli tai aloittaa taso alusta
        self.sulje_pikanappain = QShortcut(QKeySequence("Ctrl+q"), self)
        self.sulje_pikanappain.activated.connect(self.exit_on_click)

        self.restart_pikanappain = QShortcut(QKeySequence("Ctrl+r"), self)
        self.restart_pikanappain.activated.connect(self.scene.restart_level)


"""
0 : tyhjä
1 : maa
2 : piikki
3 : maali
4 : kolikko

jos ruudussa on mitä tahansa muuta kuin nämä viisi numeroa, se tulkitaan tyhjäksi
"""

taso1 = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 3, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 2, 2, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 4, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

taso2 = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
    [1, 4, 0, 0, 1, 0, 1, 2, 0, 2, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
    [1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1]]

taso3 = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 2, 0, 1, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 2, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 4, 0, 1, 0, 0, 0, 2, 2, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1],
    [1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1],
    [1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 2, 2, 1, 3, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1]]

taso_data = [taso1, taso2, taso3]  # lista joka sisältää kaikki tasot

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = Scene()
    sys.exit(app.exec_())
