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


###############################################################################
#   Basic UI Widgets
###############################################################################

class UIWidget(pg.sprite.Sprite):
    def __init__(self, x, y, image, name = "widget", border = (0, 0, 0, 0)):
        pg.sprite.Sprite.__init__(self)
        self.name   = name
        self.x      = x
        self.y      = y
        self.set_image(image)
        self.on_click = None
        self.border_top     = border[0]
        self.border_left    = border[1]
        self.border_bottom  = border[2]
        self.border_right   = border[3]

    def update(self, dt):
        pass

    def draw(self, screen):
        self.rect.x = self.x
        self.rect.y = self.y
        screen.blit(self.image, self.rect)

    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                if not self.on_click is None:
                    self.on_click(self)
                    return True
        return False

    @property
    def cx(self):
        return self.rect.centerx

    @property
    def cy(self):
        return self.rect.centery

    @property
    def x2(self):
        return self.rect.right

    @property
    def y2(self):
        return self.rect.bottom

    @property
    def w(self):
        return self.rect.width

    @property
    def h(self):
        return self.rect.height

    def set_image(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


###############################################################################
#   Battle UI Unit Widgets
###############################################################################

class UnitPortrait(UIWidget):
    def __init__(self, x, y, name, frame, border, bar, bar_colour, picture):
        UIWidget.__init__(self, x, y, frame, name = name, border = border)
        self.bar_level = 0.0
        self.bar_pos = bar
        self.bar_colour = bar_colour
        self.bar_rect = pg.Rect(x + bar[0], y + bar[1], bar[2], bar[3])
        self.picture = None
        self.picture_pos = picture
        self.picture_rect = None

    def draw(self, screen):
        UIWidget.draw(self, screen)
        if not self.picture is None:
            self.picture_rect.x = self.x + self.picture_pos[0]
            self.picture_rect.y = self.y + self.picture_pos[1]
            screen.blit(self.picture, self.picture_rect)
        if self.bar_level > 0.0:
            self.bar_rect.x = self.x + self.bar_pos[0]
            self.bar_rect.h = int(self.bar_level * self.bar_pos[3])
            self.bar_rect.y = (self.y + self.bar_pos[1]
                               + self.bar_pos[3] - self.bar_rect.h)
            screen.fill(self.bar_colour, self.bar_rect)

    def set_picture(self, image):
        self.picture = image
        if not image is None:
            self.picture_rect = image.get_rect()
            self.picture_rect.x = self.x + self.picture_pos[0]
            self.picture_rect.y = self.y + self.picture_pos[1]
        else:
            self.picture_rect = None


class UnitPortraitL(UnitPortrait):
    def __init__(self, x = 0, y = 0, name = "portrait-L", frame = None,
                 border = (0, 0, 0, 0), bar = (0, 0, 8, 64),
                 picture = (8, 0, 64, 64), bar_colour = (0, 128, 0)):
        UnitPortrait.__init__(self, x, y, name, frame, border,
                              bar, bar_colour, picture)


class UnitPortraitR(UnitPortrait):
    def __init__(self, x = 0, y = 0, name = "portrait-R", frame = None,
                 border = (0, 0, 0, 0), bar = (64, 0, 8, 64),
                 picture = (0, 0, 64, 64), bar_colour = (0, 128, 0)):
        UnitPortrait.__init__(self, x, y, name, frame, border,
                              bar, bar_colour, picture)


class LargeUnitPortrait(UnitPortrait):
    def __init__(self, x, y, name, frame, border,
                 bar, bar_colour, picture, icon):
        UnitPortrait.__init__(self, x, y, name, frame, border,
                              bar, bar_colour, picture)
        self.icon = None
        self.icon_pos = icon
        self.icon_rect = None

    def draw(self, screen):
        UnitPortrait.draw(self, screen)
        if not self.icon is None:
            self.icon_rect.x = self.x + self.icon_pos[0]
            self.icon_rect.y = self.y + self.icon_pos[1]
            screen.blit(self.icon, self.icon_rect)

    def set_icon(self, image):
        self.icon = image
        if not image is None:
            self.icon_rect = image.get_rect()
            self.icon_rect.x = self.x + self.icon_pos[0]
            self.icon_rect.y = self.y + self.icon_pos[1]
        else:
            self.icon_rect = None


class LargeUnitPortraitL(LargeUnitPortrait):
    def __init__(self, x = 0, y = 0, name = "portrait-lg-L", frame = None,
                 border = (0, 0, 0, 0), bar = (24, 32, 8, 96),
                 bar_colour = (0, 128, 0), picture = (32, 0, 128, 128),
                 icon = (0, 0, 32, 32)):
        LargeUnitPortrait.__init__(self, x, y, name, frame, border, bar,
                                   bar_colour, picture, icon)


class LargeUnitPortraitR(LargeUnitPortrait):
    def __init__(self, x = 0, y = 0, name = "portrait-lg-R", frame = None,
                 border = (0, 0, 0, 0), bar = (128, 0, 8, 96),
                 bar_colour = (0, 128, 0), picture = (0, 0, 128, 128),
                 icon = (128, 96, 32, 32)):
        LargeUnitPortrait.__init__(self, x, y, name, frame, border, bar,
                                   bar_colour, picture, icon)


###############################################################################
#   Battle UI Team Widgets
###############################################################################

# active is a dict to pass down to LargeUnitPortrait
# team is a list of dict to pass down to UnitPortrait
class BattleTeamWidget(object):
    def __init__(self, active, team, upc, lupc):
        self.portraits = [lupc(**active)]
        for config in team:
            self.portraits.append(upc(**config))

    def draw(self, screen):
        for portrait in self.portraits:
            portrait.draw(screen)

    def get_event(self, event):
        for portrait in self.portraits:
            if portrait.get_event(event):
                return True
        return False


class BattleTeamWidgetL(BattleTeamWidget):
    def __init__(self, active = None, team = None):
        BattleTeamWidget.__init__(self, active, team,
                                  UnitPortraitL, LargeUnitPortraitL)

class BattleTeamWidgetR(BattleTeamWidget):
    def __init__(self, active = None, team = None):
        BattleTeamWidget.__init__(self, active, team,
                                  UnitPortraitR, LargeUnitPortraitR)


###############################################################################
#   Battle UI Scene
###############################################################################

class BattleScene(object):
    def __init__(self, gx_config):
        self.teams = [
            BattleTeamWidgetL(**gx_config["team_left"]),
            BattleTeamWidgetR(**gx_config["team_right"])
        ]
        for team in self.teams:
            for portrait in team.portraits:
                portrait.on_click = self.on_portrait_click

    def draw(self, screen):
        for team in self.teams:
            team.draw(screen)

    def get_event(self, event):
        for team in self.teams:
            if team.get_event(event):
                return True
        return False

    def on_portrait_click(self, portrait):
        print ">> Portrait clicked", portrait.name
