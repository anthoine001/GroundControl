from datetime import *
from math import cos
from kivy.config import Config
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.metrics import dp
from kivy.properties import Clock, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout


FREQ = .1


class Capteur:
    def __init__(self):
        self.nom = ""
        self.data = []

""" A developper
vitesse = Capteur()
accel = Capteur()

for i in range(0,300):
    vitesse.data.append(2 * cos(i/10) + 1)
"""


class ControleTir(GridLayout):
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
            self.since_launch = str(datetime.now()-self.launch_time)

    def on_button_click(self):
        self.launch_time = datetime.now()
        print("La fusée est lancée à :" + self.launch_time.strftime('%H:%M:%S'))
        self.launched = True


class Graphique2(RelativeLayout):
    courbe = []
    def __init__(self, capteur=1, **kvargs):
        super().__init__(**kvargs)
        self.L = 300
        self.H = 200
        self.graphX = []
        self.graphY = []
        self.y_mid = self.H/2
        self.capteur = capteur
        self.add_widget(Label(text="TITRE"))
        Clock.schedule_interval(self.update, FREQ)
        self.temps = 0
        for i in range(0, 300):
            self.graphX.append(i)
            self.graphY.append(self.y_mid)

    def update(self, dt):
        self.temps += FREQ
        self.canvas.clear()
        # Dessin du cadre
        with self.canvas:
            Color(1, 1, 1)
            Line(rectangle=(0, 0, dp(self.L), dp(self.H)), width=2)
        for i in range(0, 299):
            x1 = self.graphX[i]
            y1 = self.graphY[i]
            x2 = self.graphX[i+1]
            y2 = self.graphY[i+1]
            self.canvas.remove()
            with self.canvas:
                Color(0, 1, 1)
                Line(points=(x1, y1, x2, y2))
        for i in range(0, 299):
            self.graphY[i] = self.graphY[i + 1]
        # Mise à jour de de la valeur du capteur
        #self.graphY[299] = 50 + 50 * cos(self.temps)
        self.graphY[299] = self.capteur

    def transform(self, dataX, dataY):
        transformx = 0
        transformy = 0
        return transformx, transformy


class MainWidget(BoxLayout):
    def __init__(self, **kvargs):
        super().__init__(**kvargs)
        pass


class GroundControlStationApp(App):
    def __init__(self, **kvargs):
        super().__init__(**kvargs)

    def build(self):
        self.title = 'Ground Control Station - Section Espace'
        layout = GridLayout(cols=3)
        layout.add_widget(ControleTir())
        layout.add_widget(Graphique2(30))
        layout.add_widget(Graphique2(50))
        layout.add_widget(Graphique2(10))
        layout.add_widget(Graphique2(100))
        layout.add_widget(Graphique2(30))
        return layout



Config.set('graphics', 'width', '1000')
Config.set('graphics', 'height', '600')

GroundControlStationApp().run()
