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

from .view.widgets import BattleScene


SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480


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
        bar_colour = (0, 204, 0)
        frame_l = pg.image.load("images/portrait_frame_lr.png").convert_alpha()
        frame_r = pg.image.load("images/portrait_frame_rl.png").convert_alpha()
        dummy_pic = pg.image.load("images/dummy.png").convert()
        dummy_pic_lg = pg.image.load("images/dummy_lg.png").convert()
        type_icon = pg.image.load("images/type.png").convert_alpha()
        gx_config = {
            "screen_width": SCREEN_WIDTH,
            "screen_height": SCREEN_HEIGHT,
            "battle_scene": {
                "team_left": {
                    "active": {
                        "name": "portrait-0-0",
                        "x": 16 + 68,
                        "y": SCREEN_HEIGHT - 16 - 72 - 8 - 136,
                        "frame": pg.image.load("images/portrait_frame_lg_lr.png").convert_alpha(),
                        "border": (4, 4, 4, 4),
                        "picture": (40, 4, 128, 128),
                        "icon": (4, 4, 32, 32),
                        "bar": (28, 40, 8, 92),
                        "bar_colour": bar_colour
                    },
                    "team": [{
                        "name": "portrait-0-1",
                        "x": 16,
                        "y": SCREEN_HEIGHT - 16 - 72 - 8 - 72,
                        "frame": frame_l,
                        "border": (4, 4, 4, 4),
                        "picture": (16, 4, 64, 64),
                        "bar": (4, 4, 8, 64),
                        "bar_colour": bar_colour
                    }, {
                        "name": "portrait-0-2",
                        "x": 16,
                        "y": SCREEN_HEIGHT - 16 - 72,
                        "frame": frame_l,
                        "border": (4, 4, 4, 4),
                        "picture": (16, 4, 64, 64),
                        "bar": (4, 4, 8, 64),
                        "bar_colour": bar_colour
                    }, {
                        "name": "portrait-0-3",
                        "x": 16 + 84 + 8,
                        "y": SCREEN_HEIGHT - 16 - 72,
                        "frame": frame_l,
                        "border": (4, 4, 4, 4),
                        "picture": (16, 4, 64, 64),
                        "bar": (4, 4, 8, 64),
                        "bar_colour": bar_colour
                    }]
                },
                "team_right": {
                    "active": {
                        "name": "portrait-1-0",
                        "x": SCREEN_WIDTH - 16 - 68 - 172,
                        "y": 16 + 72 + 8,
                        "frame": pg.image.load("images/portrait_frame_lg_rl.png").convert_alpha(),
                        "border": (4, 4, 4, 4),
                        "picture": (4, 4, 128, 128),
                        "icon": (136, 100, 32, 32),
                        "bar": (136, 4, 8, 92),
                        "bar_colour": bar_colour
                    },
                    "team": [{
                        "name": "portrait-1-1",
                        "x": SCREEN_WIDTH - 16 - 84,
                        "y": 16 + 72 + 8,
                        "frame": frame_r,
                        "border": (4, 4, 4, 4),
                        "picture": (4, 4, 64, 64),
                        "bar": (72, 4, 8, 64),
                        "bar_colour": bar_colour
                    }, {
                        "name": "portrait-1-2",
                        "x": SCREEN_WIDTH - 16 - 84,
                        "y": 16,
                        "frame": frame_r,
                        "border": (4, 4, 4, 4),
                        "picture": (4, 4, 64, 64),
                        "bar": (72, 4, 8, 64),
                        "bar_colour": bar_colour
                    }, {
                        "name": "portrait-1-3",
                        "x": SCREEN_WIDTH - 16 - 84 - 8 - 84,
                        "y": 16,
                        "frame": frame_r,
                        "border": (4, 4, 4, 4),
                        "picture": (4, 4, 64, 64),
                        "bar": (72, 4, 8, 64),
                        "bar_colour": bar_colour
                    }]
                },
                "action_panel": {
                    "name": "action-panel",
                    "x": SCREEN_WIDTH - 338,
                    "y": SCREEN_HEIGHT - 144,
                    "frame": pg.image.load("images/panel_frame.png").convert_alpha(),
                    "border": (16, 16, 16, 16),
                    "label": (32, 144 - 32),
                    "font_size": 14,
                    "font_colour": (255, 255, 255),
                    "actions": {
                        # "attack": {},
                        # "rotate_counter": {},
                        # "rotate_clock": {},
                        # "surrender": {}
                    }
                }
            }
        }
        self.scene = BattleScene(gx_config["battle_scene"])
        self.scene.teams[0].portraits[0].bar_level = 0.25
        self.scene.teams[0].portraits[1].bar_level = 0.75
        self.scene.teams[0].portraits[2].bar_level = 0.5
        self.scene.teams[0].portraits[3].bar_level = 1.0
        self.scene.teams[1].portraits[0].bar_level = 0.2
        self.scene.teams[1].portraits[1].bar_level = 0.8
        self.scene.teams[1].portraits[2].bar_level = 0.4
        self.scene.teams[1].portraits[3].bar_level = 0.6

        self.scene.teams[0].portraits[0].set_icon(type_icon)
        self.scene.teams[0].portraits[0].set_picture(dummy_pic_lg)
        self.scene.teams[0].portraits[1].set_picture(dummy_pic)
        self.scene.teams[0].portraits[2].set_picture(dummy_pic)
        self.scene.teams[0].portraits[3].set_picture(dummy_pic)
        self.scene.teams[1].portraits[0].set_icon(type_icon)
        self.scene.teams[1].portraits[0].set_picture(dummy_pic_lg)
        self.scene.teams[1].portraits[1].set_picture(dummy_pic)
        self.scene.teams[1].portraits[2].set_picture(dummy_pic)
        self.scene.teams[1].portraits[3].set_picture(dummy_pic)

        self.scene.action_panel.active = True
        self.scene.action_panel.set_text_label("Lorem ipsum dolor sit amet")

    def startup(self):
        print "> Battle"

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN or event.key == pg.K_SPACE:
                self.done = True
            elif event.key == pg.K_ESCAPE:
                self.done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if not self.scene.get_event(event):
                self.done = True

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((0,0,0))
        self.scene.draw(screen)


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
