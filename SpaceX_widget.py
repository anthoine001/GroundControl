from datetime import datetime
from math import cos, sin, pi
from kivy.core.text import Label as CoreLabel
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Rectangle
from kivy.properties import StringProperty, BooleanProperty, Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout

FREQ = 0.1


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