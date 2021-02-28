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
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
import serial
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
# from SpaceX_widget import SpaceXWidget, ControleTir


# fréquence d'acquisition de signal
from kivy.uix.textinput import TextInput

FREQ = .1
VAL = [90, 70, 60, 55, 40]
CHAMPS = ["Launch", "Propulsion End", "Apogee", "Parachute Deployment", "Landing"]
in_flight = False
Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '800')


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
vitesse = CapteurTest("Vitesse", 0.3)
altitude = CapteurTest("Altitude", 0.1)
gyro_x = CapteurTest("Inclinaison_x", 0.6)
gyro_y = CapteurTest("Inclinaison_y", 0.6)
gyro_z = CapteurTest("Inclinaison_z", 0.6)
gps_lat = CapteurTest("GPS_lat", 1)
gps_long = CapteurTest("GPS_long", 1)
reception = Recepteur("Recepteur")


# ---- Capteurs de test ------


class Graphique(RelativeLayout):
    courbe = []

    def __init__(self, capteur, **kvargs):
        super().__init__(**kvargs)
        self.g = []
        self.L = 300
        self.H = 200
        self.graphX = []
        self.graphY = []
        self.y_mid = self.H / 2
        self.capteur = capteur
        self.titre = self.capteur.nom
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
            Color(1, 1, 1, 0.8)
            Line(points=(0, self.H / 2, self.L, self.H / 2))
            Color(1, 1, 1)
            Line(rectangle=(0, 0, self.L, self.H), width=2)
        self.remove_widget(self.label_titre)
        self.add_widget(self.label_titre)
        self.chart_unit()
        # Trace la courbe
        """essayer d'implémenter un buffer circulaire"""
        for i in range(0, self.max_graph - self.N - 1):
            x1 = self.graphX[i]
            y1 = self.graphY[i + self.N]
            x2 = self.graphX[i + 1]
            y2 = self.graphY[i + self.N + 1]
            with self.canvas:
                Color(0, 1, 1)
                Line(points=(x1, y1, x2, y2))
        for i in range(self.max_graph - self.N - 1, self.max_graph - 1):
            x1 = self.graphX[i]
            y1 = self.graphY[i - (self.max_graph - self.N)]
            x2 = self.graphX[i + 1]
            y2 = self.graphY[i - (self.max_graph - self.N) + 1]
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
        if self.N < self.max_graph - 1:
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
    since_launch = StringProperty("0.00 s")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_controle_tir, .1)
        self.launch_time = None
        self.date_since_launch = None

    def update_controle_tir(self, dt):
        self.heure = datetime.now().strftime('%H:%M:%S')
        if self.launch_time is not None:
            if in_flight:
                self.date_since_launch = datetime.now() - self.launch_time
                self.since_launch = (str(datetime.now() - self.launch_time))[:-4]

    def on_button_click(self):
        self.launch_time = datetime.now()
        global in_flight
        in_flight = True
        print("La fusée est lancée à :" + self.launch_time.strftime('%H:%M:%S.%f'))
        self.launched = True


class SpaceXWidget(RelativeLayout):
    """un cercle de rayon 700, centre à 500,-600"""
    def set_mission(self):
        for i in range(0, len(CHAMPS)):
            self.phases.append(CHAMPS[i])
        for i in range(0, len(VAL)):
            self.angles.append(int(VAL[i]))

    def __init__(self, ctrl_tir, **kwargs):
        super().__init__(**kwargs)

        self.ctrl_tir = ctrl_tir
        self.angles = []
        self.phases = []

        Clock.schedule_interval(self.update, FREQ)
        """Paramètres de la mission par une fenetre de parametres"""
        self.set_mission()

        self.affiche_timer("T+00:00:00", 26, 430, 30)
        for i in range(0, len(self.phases)):
            a = 700 * cos(self.angles[i] / 180 * pi)
            b = 700 * sin(self.angles[i] / 180 * pi)
            with self.canvas:
                Color(1, 1, 1)
                Line(circle=(500 + a, b - 600, 7))
            self.affiche_timer(self.phases[i], 13, 485 + a, b - 590)
        with self.canvas:
            Color(1, 1, 1)
            Line(circle=(500, -600, 700, -30, 30))
            Line(circle=(500, -600, 700, -30, 0), width=2)

    def update_mission(self):
        for i in range(0, len(VAL)):
            self.angles[i] = int(VAL[i])
        #GroundControlStationApp().manager.pop()

    def update(self, dt):
        if self.ctrl_tir.launched and self.angles[len(self.angles)-1] <= 90:
            self.canvas.clear()
            for i in range(0, len(self.phases)):
                self.angles[i] += FREQ
                a = 700 * cos(self.angles[i] / 180 * pi)
                b = 700 * sin(self.angles[i] / 180 * pi)
                with self.canvas:
                    Color(1, 1, 1)
                    Line(circle=(500 + a, b - 600, 7))
                # Ecriture de la phase
                if a>0:
                    self.affiche_timer(self.phases[i], 13, 485 + a, b - 590)
                else:
                    self.affiche_timer(self.phases[i], 13, 485 + a, b - 620)
            """ compteur """
            self.affiche_timer("T+" + str(self.ctrl_tir.date_since_launch)[:-4], 26, 430, 30)
            with self.canvas:
                Color(1, 1, 1)
                Line(circle=(500, -600, 700, -30, 30))
                Line(circle=(500, -600, 700, -30, 0), width=2)
        elif self.angles[len(self.angles)-1] > 90:
            self.ctrl_tir.launched = False
            global in_flight
            in_flight = False
        else:
            self.update_mission()


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
        SpaceX = SpaceXWidget(my_controle_tir)
        layout.add_widget(my_controle_tir)
        layout.add_widget(Graphique(vitesse))
        layout.add_widget(Graphique(altitude))
        layout.add_widget(Graphique(gyro_x))
        layout.add_widget(Graphique(gyro_y))
        layout.add_widget(Graphique(gyro_z))
        layout.add_widget(Graphique(gps_lat))
        layout.add_widget(Graphique(reception))
        box.add_widget(layout)
        box.add_widget(SpaceX)
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


class ParameterScreen(GridLayout):
    def __init__(self, **kvargs):
        super().__init__(**kvargs)
        self.val = []
        self.add_widget(Label(text="Profil de mission", color=(1, 0.5, 0, 1), size_hint=(None, None), width=170,
                              height=30))
        self.add_widget(Label(text="", size_hint=(None, None), width=150, height=30))
        for i in range(0, len(CHAMPS)):
            self.add_widget(Label(text=CHAMPS[i], size_hint=(None, None), width=170, height=30))
            self.val.append(TextInput(text=str(VAL[i]), multiline=False, size_hint=(None, None), width=100, height=30))
            self.add_widget(self.val[i])

    def parameter_validation(self):
        for i in range(0, len(VAL)):
            VAL[i] = self.val[i].text
        print("Parameters changed")


class GroundControlStationApp(App):
    manager = ObjectProperty(None)

    def build(self):
        self.manager = MyScreenManager()
        Window.size = (1000, 800)
        return self.manager


GroundControlStationApp().run()
