#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from math import sin, cos, pi
from random import random
from kivy.core.text import Label as CoreLabel
from kivy.config import Config
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Rectangle
from kivy.properties import Clock, StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
import serial
from kivy.uix.screenmanager import ScreenManager
# from SpaceX_widget import SpaceXWidget, ControleTir


# fréquence d'acquisition de signal
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
            print(value / 1000)
            if value / 1000 < 10:
                self.data = value / 1000
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


# ---- Capteurs de test ------
vitesse = CapteurTest("vitesse", 0.3)
altitude = CapteurTest("Altitude", 0.1)
gyro_x = CapteurTest("Inclinaison_x", 0.6)
gyro_y = CapteurTest("Inclinaison_y", 0.6)
gyro_z = CapteurTest("Inclinaison_z", 0.6)
gps_lat = CapteurTest("GPS_lat", 1)
gps_long = CapteurTest("GPS_long", 1)
reception = Recepteur()


# ---- Capteurs de test ------


class Graphique(RelativeLayout):
    courbe = []

    def __init__(self, capteur, titre="", **kvargs):
        super().__init__(**kvargs)
        self.g = []
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
        pas = int(300 / 10 * FREQ)
        # pas = 3
        self.max_graph = int(10 / FREQ)
        # max_graph = 90

        if self.capteur.nom == "Altitude":
            self.graphY = [0] * self.max_graph
            for i in range(0, self.max_graph):
                self.graphX.append(pas * i)
        else:
            self.graphY = [self.y_mid] * self.max_graph
            for i in range(0, self.max_graph):
                self.graphX.append(pas * i)
        self.N = 0

        for i in range(0, 10):
            mylabel = CoreLabel(text=str(i - 9), font_size=15, color=(1, 1, 1, 1))
            # Force refresh to compute things and generate the texture
            mylabel.refresh()
            # Get the texture and the texture size
            texture = mylabel.texture
            texture_size = list(texture.size)
            self.g.append(Rectangle(pos=(17 + i * 30, 100), texture=texture, size=texture_size))

    def update(self, dt):
        self.canvas.clear()
        # Dessin du cadre
        with self.canvas:
            Color(1, 1, 1)
            Line(rectangle=(0, 0, self.L, self.H), width=2)
        self.remove_widget(self.label_titre)
        self.add_widget(self.label_titre)
        self.chart_unit()
        # Trace la courbe
        """essayer d'implémenter un buffer circulaire"""
        for i in range(0, self.max_graph - self.N-1):
            x1 = self.graphX[i]
            y1 = self.graphY[i+self.N]
            x2 = self.graphX[i + 1]
            y2 = self.graphY[i+self.N + 1]
            with self.canvas:
                Color(0, 1, 1)
                Line(points=(x1, y1, x2, y2))
        for i in range(self.max_graph - self.N-1, self.max_graph-1):
            x1 = self.graphX[i]
            y1 = self.graphY[i-(self.max_graph-self.N)]
            x2 = self.graphX[i + 1]
            y2 = self.graphY[i-(self.max_graph-self.N) + 1]
            with self.canvas:
                Color(0, 1, 1)
                Line(points=(x1, y1, x2, y2))
        # mise à jour des points avec intégration de la nouvelle valeur
        # à la fin
        """for i in range(0, self.max_graph - 1):
            self.graphY[i] = self.graphY[i + 1]
        # Mise à jour de de la valeur du capteur
        self.graphY[self.max_graph - 1] = self.capteur.data"""
        self.graphY[self.N] = self.capteur.data
        if self.N < self.max_graph-1:
            self.N += 1
        else:
            self.N = 0

    def chart_unit(self):
        for i in range(0, 10):
            self.g[i].pos = (17 + i * 30, 100)
            with self.canvas:
                Line(points=(30 + i * 30, 100, 30 + i * 30, 105))
            # Draw the texture on any widget canvas
            self.canvas.add(self.g[i])


class ControleTir(GridLayout):
    """Affiche un pavé avec heure, temps depuis le lancement, etc."""
    heure = StringProperty("Heure")
    launched = BooleanProperty(False)
    since_launch = StringProperty("0.000 s")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_controle_tir, .1)
        self.launch_time = None
        self.date_since_launch = None

    def update_controle_tir(self, dt):
        self.heure = datetime.now().strftime('%H:%M:%S')
        if self.launch_time is not None:
            self.date_since_launch = datetime.now()-self.launch_time
            self.since_launch = str(datetime.now() - self.launch_time)

    def on_button_click(self):
        self.launch_time = datetime.now()
        print("La fusée est lancée à :" + self.launch_time.strftime('%H:%M:%S.%f'))
        self.launched = True


class SpaceXWidget(RelativeLayout):
    """un cercle de rayon 700, centre à 500,-600"""
    def __init__(self, CtrlTir, **kwargs):
        super().__init__(**kwargs)
        self.CtrlTir = CtrlTir
        self.angles = []
        self.phases = []

        Clock.schedule_interval(self.update, FREQ)
        """Paramètres de la mission à passer plus tard par une fenetre de parametres"""
        self.phases.append("Launch")
        self.phases.append("Separation")
        self.phases.append("Landing")
        self.angles.append(90)
        self.angles.append(76)
        self.angles.append(38)

        self.affiche_timer("T+00:00:00", 26, 430, 30)
        for i in range(0, len(self.phases)):
            a = 700 * cos(self.angles[i] / 180 * pi)
            b = 700 * sin(self.angles[i] / 180 * pi)
            with self.canvas:
                Color(1, 1, 1)
                Line(circle=(500 + a, b - 600, 7))
            self.affiche_timer(self.phases[i], 13, 485 + a, b - 590)

    def update(self, dt):
        if self.CtrlTir.launched:
            self.canvas.clear()
            for i in range(0, len(self.phases)):
                self.angles[i] += FREQ
                a = 700*cos(self.angles[i]/180*pi)
                b = 700*sin(self.angles[i]/180*pi)
                with self.canvas:
                    Color(1, 1, 1)
                    Line(circle=(500+a, b-600, 7))
                self.affiche_timer(self.phases[i], 13, 485 + a, b - 590)
            """ compteur """
            self.affiche_timer("T+"+str(self.CtrlTir.date_since_launch), 26, 430, 30)
            with self.canvas:
                Color(1, 1, 1)
                Line(circle=(500, -600, 700, -30, 30))
                Line(circle=(500, -600, 700, -30, 0), width=2)

    def affiche_timer(self, texte, size, a, b):
        mylabel = CoreLabel(text=texte, font_size=size,
                            color=(1, 1, 1, 1))
        mylabel.refresh()
        texture = mylabel.texture
        texture_size = list(texture.size)
        with self.canvas:
            Rectangle(pos=(a, b), texture=texture, size=texture_size)


class MainWidget(BoxLayout):
    def __init__(self, **kvargs):
        super().__init__(**kvargs)
        box = BoxLayout(orientation="vertical")
        layout = GridLayout(cols=3)
        my_controle_tir = ControleTir()
        layout.add_widget(my_controle_tir)
        layout.add_widget(Graphique(vitesse, "Vitesse"))
        layout.add_widget(Graphique(altitude, "Altitude"))
        layout.add_widget(Graphique(gyro_x, "inclinaison_x"))
        layout.add_widget(Graphique(gyro_y, "inclinaison_y"))
        layout.add_widget(Graphique(gyro_z, "inclinaison_z"))
        layout.add_widget(Graphique(gps_lat, "GPS_L"))
        layout.add_widget(Graphique(gps_long, "GPS_l"))
        layout.add_widget(Graphique(reception, "Recepteur"))
        box.add_widget(layout)
        box.add_widget(SpaceXWidget(my_controle_tir))
        self.add_widget(box)


class NavigationScreenManager(ScreenManager):
    screen_stack = []

    def push(self, screen_name):
        if screen_name not in self.screen_stack:
            self.screen_stack.append(self.current)
            self.transition.direction = "left"
            self.current = screen_name

    def pop(self):
        if len(self.screen_stack) > 0:
            screen_name = self.screen_stack[-1]
            del self.screen_stack[-1]
            self.transition.direction = "right"
            self.current = screen_name


class MyScreenManager(NavigationScreenManager):
    pass


class ParameterScreen(BoxLayout):
    pass


class GroundControlStationApp(App):
    manager = ObjectProperty(None)

    def build(self):
        self.manager = MyScreenManager()
        return self.manager


Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '800')

GroundControlStationApp().run()
