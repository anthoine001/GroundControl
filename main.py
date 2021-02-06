from datetime import *
from math import cos

from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.instructions import Canvas
from kivy.graphics.vertex_instructions import Line
from kivy.metrics import dp
from kivy.properties import Clock, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

FREQ = .1


class Capteur:
    def __init__(self):
        self.nom = ""
        self.data = []

vitesse = Capteur()
for i in range(0,300):
    vitesse.data.append(2 * cos(i/10) + 1)


class MainWidget(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ControleTir(GridLayout):
    heure = StringProperty("Heure")
    since_launch = StringProperty("0.000 s")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_controle_tir, 1)
        self.launch_time = None

    def update_controle_tir(self, dt):
        self.heure = datetime.now().strftime('%H:%M:%S')
        if self.launch_time is not None:
            self.since_launch = str(datetime.now()-self.launch_time)

    def on_button_click(self):
        self.launch_time = datetime.now()
        print("La fusée est lancée à :" + self.launch_time.strftime('%H:%M:%S'))





class Graphique(BoxLayout):
    def __init__(self, a=0, b=0, **kwargs):
        super().__init__(**kwargs)
        # a, b coordonnees du coin inferieur gauche de la fenetre graphique
        self.a = a
        self.b = b
        self.L = 300
        self.H = 200
        self.graphX = []
        self.graphY = []
        self.cadre = Canvas()

        Clock.schedule_interval(self.update, FREQ)
        self.temps = 0
        for i in range(0, 300):
            self.graphX.append(i)
            self.graphY.append(50)

    def update(self, dt):
        self.temps += FREQ
        self.canvas.clear()


        with self.canvas:
            Line(rectangle=(dp(self.a), dp(self.b), dp(self.L), dp(self.H)), width=1)
        for i in range(0, 299):
            x1 = self.a + self.graphX[i]
            y1 = self.b + self.graphY[i]
            x2 = self.a + self.graphX[i+1]
            y2 = self.b + self.graphY[i+1]
            with self.canvas:
                #Color(1, 1, 1)
                Line(points=(x1, y1, x2, y2))
        for i in range(0,299):
            self.graphY[i] = self.graphY[i + 1]
        self.graphY[299] = 50 + 50 * cos(self.temps)

    def transform(self, dataX, dataY):
        transformX = 0
        transformY = 0
        return transformX, transformY


class Graphique2(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.L = 300
        self.H = 200
        self.graphX = []
        self.graphY = []

        Clock.schedule_interval(self.update, FREQ)
        self.temps = 0
        for i in range(0, 300):
            self.graphX.append(i)
            self.graphY.append(50)

    def update(self, dt):
        self.temps += FREQ
        self.canvas.clear()

        with self.canvas:
            Line(rectangle=(0, 0, dp(self.L), dp(self.H)), width=1)
        for i in range(0, 299):
            x1 = self.graphX[i]
            y1 = self.graphY[i]
            x2 = self.graphX[i+1]
            y2 = self.graphY[i+1]
            with self.canvas:
                #Color(1, 1, 1)
                Line(points=(x1, y1, x2, y2))
        for i in range(0,299):
            self.graphY[i] = self.graphY[i + 1]
        self.graphY[299] = 50 + 50 * cos(self.temps)

    def transform(self, dataX, dataY):
        transformX = 0
        transformY = 0
        return transformX, transformY

class GroundControlStationApp(App):
    pass


GroundControlStationApp().run()
