import random

from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.app import App
from kivy.lang import Builder
from kivy.core.audio import SoundLoader
from kivy.uix.relativelayout import RelativeLayout
from kivy import platform
from kivy.core.window import Window
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty

Builder.load_file("menu.kv")

class MainWidget(RelativeLayout):
    from transforms import transform, transform_perspective, transform_2d
    from controls import _keyboard_closed, on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up
    score_txt = StringProperty("SCORE: 0")
    meniu = ObjectProperty(0)
    taskas_x = NumericProperty(0)
    taskas_y = NumericProperty(0)
    linijos_y = 16
    tarpai_y = 0.3
    vertikalios_linijos = []
    linijos_x = 15
    tarpai_x = 0.4
    horizontalios_linijos = []
    judejimas_y = 0
    judejimas_x = 0
    speed_y = 0.5
    speed_x = 1.5
    speed = 0
    skc_tile = 16
    tile = []
    tile_coordinates = []
    dabartinis_loop = 0
    ship = None
    ship_l = 0.1
    ship_h = 0.035
    ship_b = 0.04
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]
    game_over = False
    game_start = False
    menu_title = StringProperty("Katkus prieš Ateivius\n         Pabégimas")
    menu_title2 = StringProperty("2")
    menu_mygtukas = StringProperty("START")
    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    music1 = None
    restart1 = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_audio()
        self.vertikalios_linijos_y()
        self.horizontalios_linijos_x()
        self.tiles()
        self.prefill_coordinates()
        self.generate_tiles_coordinates()
        self.init_ship()
        self.music1.play()
        if self.is_dekstop():
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)
        self.sound_galaxy.play()
        Clock.schedule_interval(self.check_sound, 120)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.music1 = SoundLoader.load("audio/music1.wav")
        self.restart1 = SoundLoader.load("audio/restart.wav")

        self.sound_begin.volume = 0.25
        self.sound_galaxy.volume = 0.25
        self.sound_gameover_impact.volume = 0.6
        self.sound_gameover_voice.volume = 0.5
        self.music1.volume = 1
        self.restart1.volume = 0.25

    def is_dekstop(self):
        if platform in ("win"):
            return True
        return False

    def reset_game(self):
        self.score_txt = "SCORE: 0"
        self.judejimas_y = 0
        self.judejimas_x = 0
        self.dabartinis_loop = 0
        self.speed_y = 0.5
        self.tarpai_x = 0.4
        self.tile_coordinates = []
        self.prefill_coordinates()
        self.generate_tiles_coordinates()
        self.game_over = False

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        centras = self.width / 2
        base_y = self.ship_b * self.height
        base_h = (self.ship_b + self.ship_h) * self.height
        ship_width = self.ship_l * self.width / 2
        self.ship_coordinates[0] = ((centras - ship_width), base_y)
        self.ship_coordinates[1] = (centras, base_h)
        self.ship_coordinates[2] = ((centras + ship_width), base_y)
        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_collision(self):
        for i in range(0, len(self.tile_coordinates)):
            ti_x, ti_y = self.tile_coordinates[i]
            if ti_y > self.dabartinis_loop + 1:
                return False
            if self.check_collision_on_tile(ti_x, ti_y):
                return True
        return False

    def check_collision_on_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x+1, ti_y+1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def on_size(self, *args):
        self.taskas_x = self.width / 2
        self.taskas_y = self.height * 0.77

    def tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.skc_tile):
                self.tile.append(Quad())

    def generate_tiles_coordinates(self):
        last_y = 0
        last_x = 0
        for i in range(len(self.tile_coordinates)-1, -1, -1):
            if self.tile_coordinates[i][1] < self.dabartinis_loop:
                del self.tile_coordinates[i]

        if len(self.tile_coordinates) > 0:
            last_coordinate = self.tile_coordinates[-1]
            last_x = last_coordinate[0]
            last_y = last_coordinate[1] + 1

        for i in range(len(self.tile_coordinates), self.skc_tile):
            r = random.randint(0, 2)
            start_index = -int(self.linijos_y / 2) + 1
            end_index = start_index + self.linijos_y - 1
            if last_x <= start_index:
                r = 1
            if last_x >= end_index-1:
                r = 2
            self.tile_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tile_coordinates.append((last_x, last_y))
                last_y += 1
                self.tile_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tile_coordinates.append((last_x, last_y))
                last_y += 1
                self.tile_coordinates.append((last_x, last_y))
            last_y += 1

    def prefill_coordinates(self):
        for i in range(0, 5):
            self.tile_coordinates.append((0, i))

    def vertikalios_linijos_y(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.linijos_y):
                self.vertikalios_linijos.append(Line())

    def horizontalios_linijos_x(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.linijos_x):
                self.horizontalios_linijos.append(Line())

    def get_line_x_from_index(self, index):
        centrine_linija_x = self.taskas_x
        spacing = self.tarpai_y * self.width
        offset = index - 0.5
        line_x = centrine_linija_x + offset * spacing + self.judejimas_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.tarpai_x * self.height
        line_y = index * spacing_y - self.judejimas_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.dabartinis_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for i in range(0, self.skc_tile):
            tile = self.tile[i]
            tile_coordinates = self.tile_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0] + 1, tile_coordinates[1] + 1)
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertikalios_linijos_y(self):
        start_index = -int(self.linijos_y / 2) + 1
        for i in range(start_index, start_index + self.linijos_y):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertikalios_linijos[i].points = [x1, y1, x2, y2]


    def update_horizontalios_linijos_x(self):
        start_index = -int(self.linijos_y / 2) + 1
        end_index = start_index + self.linijos_y-1
        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(0, self.linijos_x):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontalios_linijos[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        laiko_faktorius = dt*60
        self.update_ship()
        self.update_vertikalios_linijos_y()
        self.update_horizontalios_linijos_x()
        self.update_tiles()
        self.score_txt = f"SCORE: {self.dabartinis_loop}"
        sunkumas = self.dabartinis_loop/200
        if sunkumas >= 0.8:
            sunkumas = 0.8
        if not self.game_over and self.game_start:
            greitis_y = (self.speed_y + sunkumas) * self.height / 100
            self.judejimas_y += greitis_y * laiko_faktorius
            if self.tarpai_x > 0.1:
                self.tarpai_x -= 0.00001
            else:
                self.tarpai_x = 0.1
            spacing_y = self.tarpai_x * self.height
            while self.judejimas_y >= spacing_y:
                self.judejimas_y -= spacing_y
                self.dabartinis_loop += 1
                self.generate_tiles_coordinates()
            greitis_x = self.speed * self.width / 100
            self.judejimas_x += greitis_x * laiko_faktorius
        if not self.check_collision() and not self.game_over:
            self.game_over = True
            self.menu_title = "G A M E    O V E R"
            self.menu_title2 = ""
            self.menu_mygtukas = "RESTART"
            self.meniu.opacity = 1
            self.music1.stop()
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.game_over_voice, 3)

    def game_over_voice(self, dt):
        if self.game_over:
            self.sound_gameover_voice.play()

    def on_menu_button(self):
        if self.game_over:
            self.restart1.play()
            self.music1.play()
        else:
            self.sound_begin.play()
        self.reset_game()
        self.game_start = True
        self.meniu.opacity = 0

    def check_sound(self, dt=None):
        self.music1.play()

class GalaxyApp(App):
    pass

GalaxyApp().run()
