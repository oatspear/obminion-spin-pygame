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
from .view.overworld import OverworldScene
from .view.sprites import Spritesheet, ImageSequence, MultiPoseSprite
from .view.widgets import HighlightWidget


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
                   effects = (AbilityEffect("log", "self", ("self attack", "opponent defend")),)),
    "recoil": Ability("recoil", "Recoil", effects = (
                      AbilityEffect("damage", "self", ("self attack",),
                                    parameters = {"amount": 3}),)),
    "lifesteal": Ability("lifesteal", "Lifesteal", effects = (
                         AbilityEffect("heal", "self", ("self post_attack",),
                                       parameters = {"relative": 0.5, "reference": "damage"}),)),
    "cleave": Ability("cleave", "Cleave", effects = (
                         AbilityEffect("damage", "opponent_adjacent", ("self post_attack",),
                                       parameters = {"relative": 0.2, "reference": "damage"}),)),
    "death_aoe": Ability("death_aoe", "Disease Cloud", effects = (
                         AbilityEffect("damage", "all", ("self death",),
                                       parameters = {"amount": 2}),)),
    "long_range": Ability("long_range", "Long Range", effects = (
                         AbilityEffect("damage", "opponent", ("friend_others post_attack",),
                                       parameters = {"amount": 2}),))
}

SPECIES = {
    "dummy": UnitTemplate("0000", "Target Dummy", TYPES["dummy"], 20, 10, 10, (ABILITIES["none"],)),
    "normal": UnitTemplate("0001", "Normal Tester", TYPES["normal"], 20, 10, 12, ()),
    "resistant": UnitTemplate("0002", "Resistant Tester", TYPES["resistant"], 20, 10, 12, ()),
    "weak": UnitTemplate("0003", "Weak Tester", TYPES["weak"], 20, 10, 12, ()),
    "logger": UnitTemplate("0004", "Logger", TYPES["normal"], 10, 10, 12,
                           (ABILITIES["log"],)),
    "double-edge": UnitTemplate("0005", "Double-Edge", TYPES["normal"], 16, 18, 12,
                                (ABILITIES["recoil"],)),
    "lifesteal": UnitTemplate("0006", "Vampire", TYPES["normal"], 16, 10, 8,
                                (ABILITIES["lifesteal"],)),
    "cleave": UnitTemplate("0007", "Brutal Warrior", TYPES["normal"], 20, 10, 8,
                                (ABILITIES["cleave"],)),
    "abomination": UnitTemplate("0008", "Abomination", TYPES["normal"], 16, 12, 8,
                                (ABILITIES["death_aoe"],)),
    "footman": UnitTemplate("0009", "Footman", TYPES["normal"], 20, 10, 10,
                                (ABILITIES["none"],)),
    "bowman": UnitTemplate("0010", "Bowman", TYPES["normal"], 14, 12, 10,
                                (ABILITIES["long_range"],))
}

PLAYER = (UnitInstance(SPECIES["lifesteal"]), UnitInstance(SPECIES["double-edge"]),
          UnitInstance(SPECIES["cleave"]), UnitInstance(SPECIES["abomination"]))
DUMMY = (UnitInstance(SPECIES["dummy"]), UnitInstance(SPECIES["dummy"]),
         UnitInstance(SPECIES["dummy"]), UnitInstance(SPECIES["dummy"]))
###############################################################################

class GameData(object):
    def __init__(self):
        self.player_team = PLAYER
        self.enemy_team = DUMMY


class State(object):
    def __init__(self, shared_data):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None
        self.shared_data = shared_data

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
    def __init__(self, shared_data):
        State.__init__(self, shared_data)
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
    def __init__(self, shared_data):
        State.__init__(self, shared_data)
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
    def __init__(self, shared_data):
        State.__init__(self, shared_data)
        self.next = None
        self._waiting_for_mission = False

        image_bank = {
            "durotar": pg.image.load("images/overworld_map.jpg").convert()
        }
        animation_bank = MultiPoseSprite()
        dummy_pic = pg.image.load("images/dummy.png").convert()
        sprite_bank = {
            "0000": dummy_pic,
            "0001": dummy_pic,
            "0002": dummy_pic,
            "0003": dummy_pic,
            "0004": dummy_pic,
            "0005": pg.image.load("images/pyro.png").convert(),
            "0006": pg.image.load("images/vampire.png").convert(),
            "0007": pg.image.load("images/pitlord.png").convert(),
            "0008": pg.image.load("images/abomination.png").convert(),
            "0009": pg.image.load("images/footman.png").convert(),
            "0010": pg.image.load("images/bowman.png").convert()
        }

        common_font = pg.font.Font("OxygenMono-Regular.ttf", 12)
        highlight = pg.image.load("images/highlight_circle.png").convert_alpha()
        icon_combat = pg.image.load("images/overworld_button_combat.png").convert_alpha()
        portrait_frame = pg.image.load("images/portrait_simple.png").convert_alpha()
        self.missions = {
            "hold": (UnitInstance(SPECIES["footman"]),
                     UnitInstance(SPECIES["footman"]),
                     UnitInstance(SPECIES["footman"]),
                     UnitInstance(SPECIES["bowman"]))
        }
        self.level_data = {
            "senjin": {
                "name": "Sen'jin Village",
                "x": 330, # 346,
                "y": 330, # 338,
                # "icon": icon_combat
                "highlight": highlight
            },
            "echo": {
                "name": "Echo Isles",
                "x": 407, # 420,
                "y": 373, # 387,
                # "icon": icon_combat
                "highlight": highlight
            },
            "barrens": {
                "name": "The Barrens",
                "x": 175, # 187,
                "y": 171, # 185,
                # "icon": pg.image.load("images/overworld_button_travel.png").convert_alpha()
                "highlight": highlight
            },
            "hold": {
                "name": "Northwatch Hold",
                "x": 345, # 361,
                "y": 240, # 257,
                # "icon": pg.image.load("images/overworld_button_boss.png").convert_alpha()
                "highlight": highlight
            },
            "razor": {
                "name": "Razor Hill",
                "x": 315, # 333,
                "y": 176, # 187,
                # "icon": pg.image.load("images/overworld_button_home.png").convert_alpha()
                "highlight": highlight
            },
            "orgrimmar": {
                "name": "Orgrimmar",
                "x": 256, # 270,
                "y": 16, # 35,
                # "icon": pg.image.load("images/overworld_button_trade.png").convert_alpha()
                "highlight": highlight
            },
            "trials": {
                "name": "Valley of Trials",
                "x": 244,
                "y": 265,
                "highlight": highlight
            },
            "thunder": {
                "name": "Thunder Ridge",
                "x": 221,
                "y": 96,
                "highlight": highlight
            }
        }
        gx_config = {
            "screen_width": SCREEN_WIDTH,
            "screen_height": SCREEN_HEIGHT,
            "overworld_scene": {
                "mission_panel": {
                    "x": 0,
                    "y": 0,
                    "frame": pg.image.load("images/mission_panel.png").convert_alpha(),
                    "title": {
                        "x": 75,
                        "y": 36,
                        "font": common_font,
                        "font_colour": (255, 255, 255)
                    },
                    "actions": {
                        "cancel": {
                            "x": 353,
                            "y": 20,
                            "icon": pg.image.load("images/button_close.png").convert_alpha()
                        }
                    },
                    "opponent": {
                        "x": 77,
                        "y": 314,
                        "frame": pg.image.load("images/battle_button_frame.png").convert_alpha(),
                        "picture": (98, 33, 64, 64),
                        "bg_colour": (24, 24, 24)
                    },
                    "player_team": [{
                        "x": 43,
                        "y": 96,
                        "frame": portrait_frame,
                        "border": (3, 3, 4, 4),
                        "picture": (3, 2, 64, 64),
                        "bg_colour": (24, 24, 24)
                    }, {
                        "x": 126,
                        "y": 96,
                        "frame": portrait_frame,
                        "border": (3, 3, 4, 4),
                        "picture": (3, 2, 64, 64),
                        "bg_colour": (24, 24, 24)
                    }, {
                        "x": 209,
                        "y": 96,
                        "frame": portrait_frame,
                        "border": (3, 3, 4, 4),
                        "picture": (3, 2, 64, 64),
                        "bg_colour": (24, 24, 24)
                    }, {
                        "x": 292,
                        "y": 96,
                        "frame": portrait_frame,
                        "border": (3, 3, 4, 4),
                        "picture": (3, 2, 64, 64),
                        "bg_colour": (24, 24, 24)
                    }],
                    "roster": [{
                        "x": 43,
                        "y": 202,
                        "frame": portrait_frame,
                        "border": (3, 3, 4, 4),
                        "picture": (3, 2, 64, 64),
                        "bg_colour": (24, 24, 24)
                    }, {
                        "x": 126,
                        "y": 202,
                        "frame": portrait_frame,
                        "border": (3, 3, 4, 4),
                        "picture": (3, 2, 64, 64),
                        "bg_colour": (24, 24, 24)
                    }, {
                        "x": 209,
                        "y": 202,
                        "frame": portrait_frame,
                        "border": (3, 3, 4, 4),
                        "picture": (3, 2, 64, 64),
                        "bg_colour": (24, 24, 24)
                    }, {
                        "x": 292,
                        "y": 202,
                        "frame": portrait_frame,
                        "border": (3, 3, 4, 4),
                        "picture": (3, 2, 64, 64),
                        "bg_colour": (24, 24, 24)
                    }]
                }
            }
        }

        self.scene = OverworldScene(gx_config["overworld_scene"], sprite_bank,
                                    animation_bank, image_bank)

    def startup(self):
        print "> Overworld / Level Selection"
        self.next = None
        self._waiting_for_mission = False
        self.scene.set_map("durotar", self.level_data)

    def cleanup(self):
        self.scene.reset()

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN or event.key == pg.K_SPACE:
                self.next = "battle"
                self.done = True
            elif event.key == pg.K_ESCAPE:
                self.next = "main_menu"
                self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.scene.get_event(event)

    def update(self, dt):
        self.scene.update(dt)
        if not self.scene.busy and self.next:
            self.done = True
            return
        action = self.scene.get_player_input()
        if self._waiting_for_mission:
            if action == "battle":
                self.next = "battle"
            elif action == "cancel":
                self._waiting_for_mission = False
        else:
            if action:
                self.shared_data.enemy_team = self.missions.get(action, DUMMY)
                self._waiting_for_mission = True
                self.scene.set_mission(self.level_data[action]["name"],
                                       self.shared_data.player_team,
                                       [],
                                       self.shared_data.enemy_team[0])

    def draw(self, screen):
        self.scene.draw(screen)


class Battle(State):
    def __init__(self, shared_data):
        State.__init__(self, shared_data)
        self.next = "overworld"
        self.engine = BattleEngine()
        self.bg_image = pg.image.load("images/battle_bg2.jpg").convert()

        animation_bank = MultiPoseSprite()
        battle_animations = Spritesheet("images/rotation_sheet.png")
        animation_bank.add_sprite("rotation_clock", ImageSequence(battle_animations,
                                  (0, 0, 128, 128), 4, 0.1))
        animation_bank.add_sprite("rotation_counter", ImageSequence(battle_animations,
                                  (0, 128, 128, 128), 4, 0.1))

        bar_colour = (0, 204, 0)
        frame_l = pg.image.load("images/portrait_frame4_lr.png").convert_alpha()
        frame_r = pg.image.load("images/portrait_frame4_rl.png").convert_alpha()
        dummy_pic = pg.image.load("images/dummy.png").convert()
        dummy_pic_lg = pg.image.load("images/dummy_lg.png").convert()
        type_icon = pg.image.load("images/type.png").convert_alpha()
        panel_frame = pg.image.load("images/panel_frame.png").convert_alpha()
        action_panel = pg.image.load("images/action_panel.png").convert_alpha()
        common_font = pg.font.Font("OxygenMono-Regular.ttf", 12)
        sprite_bank = {
            "0000": dummy_pic,
            "0000_main": dummy_pic_lg,
            "0001": dummy_pic,
            "0001_main": dummy_pic_lg,
            "0002": dummy_pic,
            "0002_main": dummy_pic_lg,
            "0003": dummy_pic,
            "0003_main": dummy_pic_lg,
            "0004": dummy_pic,
            "0004_main": dummy_pic_lg,
            "0005": pg.image.load("images/pyro.png").convert(),
            "0005_main": pg.image.load("images/pyro_lg.png").convert(),
            "0006": pg.image.load("images/vampire.png").convert(),
            "0006_main": pg.image.load("images/vampire_lg.png").convert(),
            "0007": pg.image.load("images/pitlord.png").convert(),
            "0007_main": pg.image.load("images/pitlord_lg.png").convert(),
            "0008": pg.image.load("images/abomination.png").convert(),
            "0008_main": pg.image.load("images/abomination_lg.png").convert(),
            "0009": pg.image.load("images/footman.png").convert(),
            "0009_main": pg.image.load("images/footman_lg.png").convert(),
            "0010": pg.image.load("images/bowman.png").convert(),
            "0010_main": pg.image.load("images/bowman_lg.png").convert(),
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
                        "frame": pg.image.load("images/portrait_frame_lg4_lr.png").convert_alpha(),
                        "border": (5, 4, 4, 4),
                        "picture": (39, 2, 128, 128),
                        "icon": (4, 11, 32, 32),
                        "bar": (27, 46, 8, 78),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24),
                        "bg_colour": (24, 24, 24),
                        "health_label": (72, 114),
                        "power_label": (107, 114),
                        "speed_label": (137, 114),
                        "font": common_font,
                        "font_colour": (255, 255, 255)
                    },
                    "team": [{
                        "name": "portrait-0-1",
                        "x": 16 + 82 + 8,
                        "y": SCREEN_HEIGHT - 16 - 69,
                        "frame": frame_l,
                        "border": (3, 3, 4, 4),
                        "picture": (15, 2, 64, 64),
                        "bar": (3, 8, 8, 52),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24),
                        "bg_colour": (24, 24, 24),
                        "health_label": (44, 50),
                        "font": common_font,
                        "font_colour": (255, 255, 255)
                    }, {
                        "name": "portrait-0-2",
                        "x": 16,
                        "y": SCREEN_HEIGHT - 16 - 69,
                        "frame": frame_l,
                        "border": (3, 3, 4, 4),
                        "picture": (15, 2, 64, 64),
                        "bar": (3, 8, 8, 52),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24),
                        "bg_colour": (24, 24, 24),
                        "health_label": (44, 50),
                        "font": common_font,
                        "font_colour": (255, 255, 255)
                    }, {
                        "name": "portrait-0-3",
                        "x": 16,
                        "y": SCREEN_HEIGHT - 16 - 69 - 8 - 69,
                        "frame": frame_l,
                        "border": (3, 3, 4, 4),
                        "picture": (15, 2, 64, 64),
                        "bar": (3, 8, 8, 52),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24),
                        "bg_colour": (24, 24, 24),
                        "health_label": (44, 50),
                        "font": common_font,
                        "font_colour": (255, 255, 255)
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
                        "frame": pg.image.load("images/portrait_frame_lg4_rl.png").convert_alpha(),
                        "border": (3, 4, 4, 4),
                        "picture": (3, 2, 128, 128),
                        "icon": (135, 87, 32, 32),
                        "bar": (135, 8, 8, 78),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24),
                        "bg_colour": (24, 24, 24),
                        "health_label": (36, 114),
                        "power_label": (71, 114),
                        "speed_label": (99, 114),
                        "font": common_font,
                        "font_colour": (255, 255, 255)
                    },
                    "team": [{
                        "name": "portrait-1-1",
                        "x": SCREEN_WIDTH - 16 - 82 - 8 - 82,
                        "y": 16,
                        "frame": frame_r,
                        "border": (3, 5, 4, 3),
                        "picture": (3, 2, 64, 64),
                        "bar": (71, 8, 8, 52),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24),
                        "bg_colour": (24, 24, 24),
                        "health_label": (32, 50),
                        "font": common_font,
                        "font_colour": (255, 255, 255)
                    }, {
                        "name": "portrait-1-2",
                        "x": SCREEN_WIDTH - 16 - 82,
                        "y": 16,
                        "frame": frame_r,
                        "border": (3, 5, 4, 3),
                        "picture": (3, 2, 64, 64),
                        "bar": (71, 8, 8, 52),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24),
                        "bg_colour": (24, 24, 24),
                        "health_label": (32, 50),
                        "font": common_font,
                        "font_colour": (255, 255, 255)
                    }, {
                        "name": "portrait-1-3",
                        "x": SCREEN_WIDTH - 16 - 82,
                        "y": 16 + 69 + 8,
                        "frame": frame_r,
                        "border": (3, 5, 4, 3),
                        "picture": (3, 2, 64, 64),
                        "bar": (71, 8, 8, 52),
                        "bar_colour": bar_colour,
                        "bar_bg": (24, 24, 24),
                        "bg_colour": (24, 24, 24),
                        "health_label": (32, 50),
                        "font": common_font,
                        "font_colour": (255, 255, 255)
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
        self.scene = BattleScene(gx_config["battle_scene"], sprite_bank,
                                 animation_bank)

        self.engine.on.battle_start.sub(self.scene.on_battle_start)
        self.engine.on.battle_attack.sub(self.scene.on_battle_attack)
        self.engine.on.battle_between_rounds.sub(self.scene.on_between_rounds)

        self.engine.on.battle_end.sub(self._on_battle_end)
        self.engine.on.request_input.sub(self._on_input_request)
        self._waiting_for_input = False

    def startup(self):
        print "> Battle"
        self.scene.reset()
        self.engine.set_battle((self.shared_data.player_team,
                                self.shared_data.enemy_team))
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
        if self.bg_image:
            screen.blit(self.bg_image, (0, 0))
        else:
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
    shared_data = GameData()
    state_dict = {
        "start":        StartScreen(shared_data),
        "main_menu":    MainMenu(shared_data),
        "overworld":    Overworld(shared_data),
        "battle":       Battle(shared_data)
    }
    app.setup_states(state_dict, "start")
    app.main_game_loop()
    pg.quit()
