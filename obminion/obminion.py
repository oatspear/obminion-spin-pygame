#Copyright (c) 2017 Andre Santos
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

import pygame as pg

from .engine.models import UnitTemplate, UnitInstance, UnitType, Ability, AbilityEffect
from .engine.mechanics import BattleEngine
from .view.battle import BattleScene


SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

###############################################################################
# Temporary hard-coded data

TYPES = {
    "dummy": UnitType("dummy", "Dummy Type"),
    "normal": UnitType("normal", "Normal"),
    "resistant": UnitType("resistant", "Resistant", resistances = ("dummy",)),
    "weak": UnitType("weak", "Weak", weaknesses = ("dummy",))
}

ABILITIES = {
    "none": Ability("none", "Do Nothing"),
    "log": Ability("log", "Log Ability",
                   effects = (AbilityEffect("log", "self", ("self attack", "opponent defend")),))
}

SPECIES = {
    "dummy": UnitTemplate("0000", "Target Dummy", TYPES["dummy"],
                          20, 10, 10, (ABILITIES["none"],), ""),
    "normal": UnitTemplate("0001", "Normal Tester", TYPES["normal"],
                          20, 10, 12, (), ""),
    "resistant": UnitTemplate("0002", "Resistant Tester", TYPES["resistant"],
                          20, 10, 12, (), ""),
    "weak": UnitTemplate("0003", "Weak Tester", TYPES["weak"],
                          20, 10, 12, (), ""),
    "logger": UnitTemplate("0004", "Logger", TYPES["normal"],
                          10, 10, 12, (ABILITIES["log"],), "")
}

PLAYER = (UnitInstance(SPECIES["normal"]), UnitInstance(SPECIES["normal"]))
DUMMY = (UnitInstance(SPECIES["dummy"]),)
###############################################################################


class GameEntity(pg.sprite.Sprite):
    def __init__(self, game, x, y, width, height, image = None):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.set_image(image)

    # def kill():
    #   remove the Sprite from all Groups

    # def alive():
    #   does the sprite belong to any groups

    def update(self, dt):
        pass

    def draw(self, screen):
        dw = (self.rect.width - self.width) / 2
        dh = (self.rect.height - self.height) / 2
        self.rect.x = int(self.x - dw)
        self.rect.y = int(self.y - dh)
        screen.blit(self.image, (self.rect.x, self.rect.y))

    @property
    def x2(self):
        return self.x + self.width

    @property
    def y2(self):
        return self.y + self.height

    @property
    def cx(self):
        return self.x + self.width / 2

    @property
    def cy(self):
        return self.y + self.height / 2

    def set_image(self, image):
    # Create an image of the block, and fill it with a color.
    # This could also be an image loaded from the disk.
        if image is None:
            self.image = pg.Surface([self.width, self.height])
            self.image.fill((0, 0, 0))
        else:
            self.image = image
    # Fetch the rectangle object that has the dimensions of the image
    # Update the position of this object with rect.x and rect.y
        self.rect = self.image.get_rect()
    # -----------------------------------------------------
        dw = (self.rect.width - self.width) / 2
        dh = (self.rect.height - self.height) / 2
        self.rect.x = int(self.x - dw)
        self.rect.y = int(self.y - dh)


class MovingObject(GameEntity):
    def __init__(self, game, position, dimension, direction, speed, image = None):
        GameEntity.__init__(self, game, position[0], position[1],
                            dimension[0], dimension[1], image = image)
        self.direction = direction
        self.speed = speed
        self.moving = False
        self._x = self.x    # previous x
        self._y = self.y    # previous y

    def update(self, dt):
        self._x = self.x
        self._y = self.y
        if self.moving:
            self.x += self.direction[0] * self.speed * dt
            self.y += self.direction[1] * self.speed * dt



class State(object):
    def __init__(self):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None

    def cleanup(self):
        pass

    def startup(self):
        pass

    def get_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass


class StartScreen(State):
    def __init__(self):
        State.__init__(self)
        self.next = "main_menu"

    def startup(self):
        print "> Start Screen"

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN or event.key == pg.K_SPACE:
                self.done = True
            elif event.key == pg.K_ESCAPE:
                self.quit = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.done = True

    def draw(self, screen):
        screen.fill((255, 51, 51))


class MainMenu(State):
    def __init__(self):
        State.__init__(self)
        self.next = "overworld"

    def startup(self):
        print "> Main Menu"

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN or event.key == pg.K_SPACE:
                self.done = True
            elif event.key == pg.K_ESCAPE:
                self.quit = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.done = True

    def draw(self, screen):
        screen.fill((192, 192, 192))


class Overworld(State):
    def __init__(self):
        State.__init__(self)
        self.next = "battle"
        self.nodes = [GameEntity(self, 100, 100, 32, 32),
                      GameEntity(self, 200, 240, 32, 32),
                      GameEntity(self, 470, 300, 32, 32)]

    def startup(self):
        print "> Overworld / Level Selection"

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN or event.key == pg.K_SPACE:
                self.next = "battle"
                self.done = True
            elif event.key == pg.K_ESCAPE:
                self.next = "main_menu"
                self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            i = 0
            for node in self.nodes:
                if node.rect.collidepoint(pg.mouse.get_pos()):
                    print ">> Selected level", i
                    self.next = "battle"
                    self.done = True
                    break
                i += 1

    def draw(self, screen):
        screen.fill((32, 92, 228))
        for node in self.nodes:
            node.draw(screen)


class Battle(State):
    def __init__(self):
        State.__init__(self)
        self.next = "overworld"
        self.engine = BattleEngine()

        bar_colour = (0, 204, 0)
        frame_l = pg.image.load("images/portrait_frame3_lr.png").convert_alpha()
        frame_r = pg.image.load("images/portrait_frame3_rl.png").convert_alpha()
        dummy_pic = pg.image.load("images/dummy.png").convert()
        dummy_pic_lg = pg.image.load("images/dummy_lg.png").convert()
        type_icon = pg.image.load("images/type.png").convert_alpha()
        panel_frame = pg.image.load("images/panel_frame.png").convert_alpha()
        action_panel = pg.image.load("images/action_panel.png").convert_alpha()
        common_font = pg.font.SysFont("monospace", 12)
        sprite_bank = {
            "0000": dummy_pic,
            "0000-main": dummy_pic_lg,
            "0001": dummy_pic,
            "0001-main": dummy_pic_lg,
            "0002": dummy_pic,
            "0002-main": dummy_pic_lg,
            "0003": dummy_pic,
            "0003-main": dummy_pic_lg,
            "0004": dummy_pic,
            "0004-main": dummy_pic_lg,
            "dummy": type_icon,
            "normal": type_icon,
            "resistant": type_icon,
            "weak": type_icon
        }
        gx_config = {
            "screen_width": SCREEN_WIDTH,
            "screen_height": SCREEN_HEIGHT,
            "battle_scene": {
                "team_left": {
                    "active": {
                        "name": "portrait-0-0",
                        "x": 16 + 82 - 16,
                        "y": SCREEN_HEIGHT - 16 - 69 - 8 - 133,
                        "frame": pg.image.load("images/portrait_frame_lg3_lr.png").convert_alpha(),
                        "border": (5, 4, 4, 4),
                        "picture": (39, 2, 128, 128),
                        "icon": (4, 11, 32, 32),
                        "bar": (27, 46, 8, 78),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24)
                    },
                    "team": [{
                        "name": "portrait-0-1",
                        "x": 16,
                        "y": SCREEN_HEIGHT - 16 - 69 - 8 - 69,
                        "frame": frame_l,
                        "border": (3, 3, 4, 4),
                        "picture": (15, 2, 64, 64),
                        "bar": (3, 8, 8, 52),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24)
                    }, {
                        "name": "portrait-0-2",
                        "x": 16,
                        "y": SCREEN_HEIGHT - 16 - 69,
                        "frame": frame_l,
                        "border": (3, 3, 4, 4),
                        "picture": (15, 2, 64, 64),
                        "bar": (3, 8, 8, 52),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24)
                    }, {
                        "name": "portrait-0-3",
                        "x": 16 + 82 + 8,
                        "y": SCREEN_HEIGHT - 16 - 69,
                        "frame": frame_l,
                        "border": (3, 3, 4, 4),
                        "picture": (15, 2, 64, 64),
                        "bar": (3, 8, 8, 52),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24)
                    }],
                    "ordering": [
                        (),
                        (0,),
                        (0, 2),
                        (0, 1, 3),
                        (0, 1, 2, 3)
                    ]
                },
                "team_right": {
                    "active": {
                        "name": "portrait-1-0",
                        "x": SCREEN_WIDTH - 16 - 82 - (170 - 16),
                        "y": 16 + 69 + 8,
                        "frame": pg.image.load("images/portrait_frame_lg3_rl.png").convert_alpha(),
                        "border": (3, 4, 4, 4),
                        "picture": (3, 2, 128, 128),
                        "icon": (135, 87, 32, 32),
                        "bar": (135, 8, 8, 78),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24)
                    },
                    "team": [{
                        "name": "portrait-1-1",
                        "x": SCREEN_WIDTH - 16 - 82,
                        "y": 16 + 69 + 8,
                        "frame": frame_r,
                        "border": (3, 5, 4, 3),
                        "picture": (3, 2, 64, 64),
                        "bar": (71, 8, 8, 52),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24)
                    }, {
                        "name": "portrait-1-2",
                        "x": SCREEN_WIDTH - 16 - 82,
                        "y": 16,
                        "frame": frame_r,
                        "border": (3, 5, 4, 3),
                        "picture": (3, 2, 64, 64),
                        "bar": (71, 8, 8, 52),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24)
                    }, {
                        "name": "portrait-1-3",
                        "x": SCREEN_WIDTH - 16 - 82 - 8 - 82,
                        "y": 16,
                        "frame": frame_r,
                        "border": (3, 5, 4, 3),
                        "picture": (3, 2, 64, 64),
                        "bar": (71, 8, 8, 52),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24)
                    }],
                    "ordering": [
                        (),
                        (0,),
                        (0, 2),
                        (0, 1, 3),
                        (0, 1, 2, 3)
                    ]
                },
                "action_panel": {
                    "name": "action-panel",
                    "x": SCREEN_WIDTH - 428,
                    "y": SCREEN_HEIGHT - 104,
                    "frame": action_panel,
                    "border": (8, 112, 16, 0),
                    "label": (118, 90),
                    "font": common_font,
                    "font_colour": (255, 255, 255),
                    "actions": {
                        "attack": {
                            "x": 206,
                            "y": 15,
                            "icon": pg.image.load("images/button_attack.png").convert_alpha(),
                            "border": (6, 9, 9, 9),
                            "description": "Attack the opponent"
                        },
                        "rotate_counter": {
                            "x": 132,
                            "y": 15,
                            "icon": pg.image.load("images/button_rotate_counter.png").convert_alpha(),
                            "border": (6, 9, 9, 9),
                            "description": "Rotate counter-clockwise"
                        },
                        "rotate_clock": {
                            "x": 280,
                            "y": 15,
                            "icon": pg.image.load("images/button_rotate_clock.png").convert_alpha(),
                            "border": (6, 9, 9, 9),
                            "description": "Rotate clockwise"
                        },
                        "surrender": {
                            "x": 354,
                            "y": 15,
                            "icon": pg.image.load("images/button_surrender.png").convert_alpha(),
                            "border": (6, 9, 9, 9),
                            "description": "Surrender to the opponent"
                        }
                    }
                },
                "combat_log": {
                    "name": "combat_log",
                    "x": 0,
                    "y": 0,
                    "frame": panel_frame,
                    "border": (16, 16, 16, 16),
                    "label": (24, 16),
                    "entries": 7,
                    "font": common_font,
                    "font_colour": (255, 255, 255)
                }
            }
        }
        self.scene = BattleScene(gx_config["battle_scene"], sprite_bank)

        self.engine.on.battle_start.sub(self.scene.on_battle_start)
        self.engine.on.battle_attack.sub(self.scene.on_battle_attack)
        self.engine.on.battle_between_rounds.sub(self.scene.on_between_rounds)

        self.engine.on.battle_end.sub(self._on_battle_end)
        self.engine.on.request_input.sub(self._on_input_request)
        self._waiting_for_input = False

    def startup(self):
        print "> Battle"
        self.scene.reset()
        self.engine.set_battle((PLAYER, DUMMY))
        self.scene.set_battle(self.engine)

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN or event.key == pg.K_SPACE:
                self.done = True
            elif event.key == pg.K_ESCAPE:
                self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.scene.get_event(event)

    def update(self, dt):
        self.scene.update(dt)
        if self._waiting_for_input:
            action = self.scene.get_player_input()
            if action:
                self.engine.set_action(action, 0)
                self._waiting_for_input = False
        if not self.scene.busy:
            self.engine.step()

    def draw(self, screen):
        screen.fill((0,0,0))
        self.scene.draw(screen)

    def _on_battle_end(self, engine):
        self.done = True

    def _on_input_request(self, engine):
        self._waiting_for_input = True
        self.scene.request_player_input()


class Control(object):
    def __init__(self, **settings):
        self.__dict__.update(settings)
        self.done = False
        self.screen = pg.display.set_mode(self.size)
        self.clock = pg.time.Clock()

    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]
        self.state.startup()

    def flip_state(self):
        self.state.done = False
        previous, self.state_name = self.state_name, self.state.next
        self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup()
        self.state.previous = previous

    def update(self, dt):
        if self.state.quit:
            self.done = True
        elif self.state.done:
            self.flip_state()
        self.state.update(dt)
        return self.state.draw(self.screen)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            self.state.get_event(event)

    def main_game_loop(self):
        while not self.done:
            delta_time = self.clock.tick(self.fps)/1000.0
            self.event_loop()
            dirty = self.update(delta_time)
            if dirty is None:
                pg.display.update()
            else:
                pg.display.update(dirty)



def main():
    settings = {
        "size": (SCREEN_WIDTH, SCREEN_HEIGHT),
        "fps" : 30
    }

    pg.init()
    app = Control(**settings)
    state_dict = {
        "start":        StartScreen(),
        "main_menu":    MainMenu(),
        "overworld":    Overworld(),
        "battle":       Battle()
    }
    app.setup_states(state_dict, "start")
    app.main_game_loop()
    pg.quit()
