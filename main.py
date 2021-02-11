from math import cos, sin, pi
from datetime import *
from random import random
from kivy.core.text import Label as CoreLabel
from kivy.config import Config
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Rectangle, Ellipse
from kivy.properties import Clock, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
import serial

# fréquence d'acquisition de signal
from kivy.uix.widget import Widget

FREQ = .1


class Recepteur:
    """Capteur alimenté par la liaison série"""
    def __init__(self, nom=""):
        try:
            self.ser = serial.Serial('/dev/cu.usbmodem1411', 9600)
        except:
            print("no reception")
        self.nom = nom
        self.data = .0
        Clock.schedule_interval(self.recepteur_update, FREQ)

    def recepteur_update(self, dt):
        try:
            value = float(self.ser.readline().strip())
            print(value/1000)
            if value/1000 < 10:
                self.data = value/1000
        except:
            self.data = 0


class CapteurTest:
    """Classe de dévelopement de l'application
    A remplacer plus tard par l'acquisition des signaux réels du port série"""
    def __init__(self, nom="", coef=1.):
        self.nom = nom
        self.data = .0
        self.coef = coef
        Clock.schedule_interval(self.capteur_update, FREQ)

    def capteur_update(self, dt):
        if self.nom == "Altitude":
            self.data = self.data + random() * 2
        else:
            self.data = self.coef * (random() * 200 - 50) + 50
        # print(self.nom + " : " + str(self.data))


# ---- Capteurs de test ------
vitesse = CapteurTest("vitesse", 0.3)
altitude = CapteurTest("Altitude", 0.1)
gyro_x = CapteurTest("Inclinaison_x", 0.6)
gyro_y = CapteurTest("Inclinaison_y", 0.6)
gyro_z = CapteurTest("Inclinaison_z", 0.6)
gps_lat = CapteurTest("GPS_lat", 1)
gps_long = CapteurTest("GPS_long", 1)
vide = CapteurTest("vide", 0)
reception = Recepteur()
# ---- Capteurs de test ------


class ControleTir(GridLayout):
    """Affiche un pavé avec heure, temps depuis le lancement, etc."""
    heure = StringProperty("Heure")
    launched = BooleanProperty(False)
    since_launch = StringProperty("0.000 s")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_controle_tir, .1)
        self.launch_time = None

    def update_controle_tir(self, dt):
        self.heure = datetime.now().strftime('%H:%M:%S')
        if self.launch_time is not None:
            self.since_launch = str(datetime.now() - self.launch_time)

    def on_button_click(self):
        self.launch_time = datetime.now()
        print("La fusée est lancée à :" + self.launch_time.strftime('%H:%M:%S'))
        self.launched = True


#MainControleTir = ControleTir()


class SpaceXWidget(BoxLayout):
    """un cercle de rayon 700, centre à 500,-600"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angles = []
        self.phases = []
        a = 700*cos(80/180*3.14)
        b = 700*sin(80/180*3.14)
        with self.canvas:
            self.e = Line(circle=(500, 100, 7))
            self.f = Line(circle=(500+a, b-600, 7))
        Clock.schedule_interval(self.update, FREQ)
        self.phases.append("Launch")
        self.phases.append("Separation")
        self.angles.append(90)
        self.angles.append(76)
        self.compteur_cs = 0
        self.compteur_s =0

    def update(self, dt):
        self.canvas.clear()
        for i in range(0, len(self.phases)):
            self.angles[i] += FREQ
            self.compteur_cs += int(FREQ * 10)
            if self.compteur_cs == 10:
                self.compteur_cs = 0
                self.compteur_s += 1

            mylabel = CoreLabel(text=self.phases[i], font_size=13, color=(1, 1, 1, 1))
            # Force refresh to compute things and generate the texture
            mylabel.refresh()
            # Get the texture and the texture size
            texture = mylabel.texture
            texture_size = list(texture.size)
            a = 700*cos(self.angles[i]/180*pi)
            b = 700*sin(self.angles[i]/180*pi)
            with self.canvas:
                Color(1,1,1)
                Rectangle(pos=(485+a, b-590), texture=texture, size=texture_size)
                Line(circle=(500+a, b-600, 7))
        """ compteur """
        #mylabel = CoreLabel(text=GroundControlStationApp().MainControlTir.since_launch, font_size=26, color=(1, 1, 1, 1))
        mylabel = CoreLabel(text=('T+'+'00:'+str(self.compteur_s)+":"+str(self.compteur_cs)), font_size=26, color=(1, 1, 1, 1))
        # Force refresh to compute things and generate the texture
        mylabel.refresh()
        # Get the texture and the texture size
        texture = mylabel.texture
        texture_size = list(texture.size)
        with self.canvas:
            Color(1,1,1)
            Line(circle=(500, -600, 700, -30, 30))
            Line(circle=(500, -600, 700, -30, 0), width=2)
            Rectangle(pos=(430, 30), texture=texture, size=texture_size)



class Graphique2(RelativeLayout):
    courbe = []

    def __init__(self, capteur, titre="", **kvargs):
        super().__init__(**kvargs)
        self.titre = titre
        self.L = 300
        self.H = 200
        self.graphX = []
        self.graphY = []
        self.y_mid = self.H / 2
        self.capteur = capteur
        self.label_titre = Label(text=self.titre,
                                 color=(1, 0.5, 0),
                                 text_size=(self.width, self.height),
                                 size_hint=(1, 2),
                                 padding_y=0)
        self.add_widget(self.label_titre)
        Clock.schedule_interval(self.update, FREQ)
        self.temps = 0
        pas = int(300/10*FREQ)
        # pas = 3
        max_graph = int(10/FREQ)
        # max_graph = 90
        if self.capteur.nom == "Altitude":
            for i in range(0, max_graph):
                self.graphX.append(pas*i)
                self.graphY.append(0)
        else:
            for i in range(0, max_graph):
                self.graphX.append(pas*i)
                # pas*i = 89*3 =
                self.graphY.append(self.y_mid)

    def update(self, dt):
        self.temps += FREQ
        self.canvas.clear()
        # Dessin du cadre
        with self.canvas:
            Color(1, 1, 1)
            Line(rectangle=(0, 0, self.L, self.H), width=2)
        self.remove_widget(self.label_titre)
        self.add_widget(self.label_titre)
        self.chart_unit()
        # Trace la courbe
        pas = int(300/10*FREQ)
        max_graph = int(10 / FREQ)
        for i in range(0, max_graph-1):
            x1 = self.graphX[i]
            y1 = self.graphY[i]
            x2 = self.graphX[i + 1]
            y2 = self.graphY[i + 1]
            with self.canvas:
                Color(0, 1, 1)
                Line(points=(x1, y1, x2, y2))
        # mise à jour des points avec intégration de la nouvelle valeur
        # à la fin
        for i in range(0, max_graph-1):
            self.graphY[i] = self.graphY[i + 1]
        # Mise à jour de de la valeur du capteur
        self.graphY[max_graph-1] = self.capteur.data

    def chart_unit(self):
        self.g = []
        for i in range(0,10):
            mylabel = CoreLabel(text=str(i-9), font_size=15, color=(1, 1, 1, 1))
            # Force refresh to compute things and generate the texture
            mylabel.refresh()
            # Get the texture and the texture size
            texture = mylabel.texture
            texture_size = list(texture.size)
            self.g.append(Rectangle(pos=(17+i*30, 100), texture=texture, size=texture_size))
            with self.canvas:
                Line(points=(30+i*30, 100, 30+i*30, 105))
            # Draw the texture on any widget canvas
            self.canvas.add(self.g[i])


class MainWidget(BoxLayout):
    def __init__(self, **kvargs):
        super().__init__(**kvargs)
        pass


class GroundControlStationApp(App):
    def __init__(self, **kvargs):
        super().__init__(**kvargs)
        #self.MainControlTir = ControleTir()

    def build(self):
        self.title = 'Ground Control Station - Section Espace'
        box = BoxLayout(orientation="vertical")
        layout = GridLayout(cols=3)
        #layout.add_widget(self.MainControlTir)
        layout.add_widget(ControleTir())
        layout.add_widget(Graphique2(vitesse, "Vitesse"))
        layout.add_widget(Graphique2(altitude, "Altitude"))
        layout.add_widget(Graphique2(gyro_x, "inclinaison_x"))
        layout.add_widget(Graphique2(gyro_y, "inclinaison_y"))
        layout.add_widget(Graphique2(gyro_z, "inclinaison_z"))
        layout.add_widget(Graphique2(gps_lat, "GPS_L"))
        layout.add_widget(Graphique2(gps_long, "GPS_l"))
        layout.add_widget(Graphique2(reception, "Recepteur"))
        box.add_widget(layout)
        box.add_widget(SpaceXWidget())

        return box


Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '800')

GroundControlStationApp().run()
