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


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


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
        gx_defs = {
            "screen_width": SCREEN_WIDTH,
            "screen_height": SCREEN_HEIGHT,
            "portrait_size": 64,
            "portrait_frame_lr": pg.image.load("images/portrait_frame_lr.png").convert_alpha(),
            "portrait_frame_rl": pg.image.load("images/portrait_frame_rl.png").convert_alpha(),
            "portrait_frame_lg_lr": pg.image.load("images/portrait_frame_lg_lr.png").convert_alpha(),
            "portrait_frame_lg_rl": pg.image.load("images/portrait_frame_lg_rl.png").convert_alpha()
        }
        self.scene = BattleScene(gx_defs)

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
        bk = (0,0,0)
        screen.fill((228,255,255))
        self.scene.draw(screen)
        # # pg.draw.circle(screen, bk, (168, 168), 128, 2)
        # pg.draw.circle(screen, bk, (104, 58), 32, 2)
        # pg.draw.circle(screen, bk, (44, 135), 32, 2)
        # pg.draw.circle(screen, bk, (60, 232), 32, 2)
        # pg.draw.circle(screen, bk, (168, 168), 64, 2)
        # pg.draw.circle(screen, bk, (230, 185), 16, 2)
        # pg.draw.circle(screen, bk, (185, 230), 16, 2)
        # pg.draw.rect(screen, bk, (168, 64, 128, 24), 2)

        # # pg.draw.circle(screen, bk, (632, 168), 128, 2)
        # pg.draw.circle(screen, bk, (696, 58), 32, 2)
        # pg.draw.circle(screen, bk, (756, 135), 32, 2)
        # pg.draw.circle(screen, bk, (740, 232), 32, 2)
        # pg.draw.circle(screen, bk, (632, 168), 64, 2)
        # pg.draw.circle(screen, bk, (570, 185), 16, 2)
        # pg.draw.circle(screen, bk, (615, 230), 16, 2)
        # pg.draw.rect(screen, bk, (632 - 128, 64, 128, 24), 2)

        pg.draw.rect(screen, bk, (400-64, 8, 128, 96), 2)
        pg.draw.rect(screen, bk, (16, 600-16-192, 800-256-16-4, 192), 2)
        pg.draw.rect(screen, bk, (800-256+4, 600-16-192, 256-4-16, 192), 2)


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
        "fps" : 60
    }

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
