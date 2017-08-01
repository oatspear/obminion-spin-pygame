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
    def __init__(self, cx, cy, image, name = "widget"):
        pg.sprite.Sprite.__init__(self)
        self.name   = name
        self.x      = cx
        self.y      = cy
        self.set_image(image)
        self.on_click = None

    def update(self, dt):
        pass

    def draw(self, screen):
        self.rect.centerx = self.x
        self.rect.centery = self.y
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                if not self.on_click is None:
                    self.on_click(self)
                    return True
        return False

    @property
    def x1(self):
        return self.rect.left

    @property
    def y1(self):
        return self.rect.top

    @property
    def x2(self):
        return self.rect.right

    @property
    def y2(self):
        return self.rect.bottom

    def set_image(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y


###############################################################################
#   Battle UI Widgets
###############################################################################

class UnitPortrait(UIWidget):
    def __init__(self, cx, cy, frame, name = "portrait"):
        UIWidget.__init__(self, cx, cy, frame, name)
        self.portrait = None
        self.rect_portrait = None

    def draw(self, screen):
        self.rect.centerx = self.x
        self.rect.centery = self.y
        if self.portrait:
            self.rect_portrait.centerx = self.x
            self.rect_portrait.centery = self.y
            screen.blit(self.portrait, (self.rect_portrait.x,
                                        self.rect_portrait.y))
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def set_portrait(self, image):
        self.portrait = image
        if not image is None:
            self.rect_portrait = image.get_rect()
            self.rect_portrait.centerx = self.x
            self.rect_portrait.centery = self.y
        else:
            self.rect_portrait = None


class BattleTeamWidget(object):
    def __init__(self, x, y, gx_defs, ltr = True):
        self.portraits = None
        if ltr:
            self._build_ltr_widgets(x, y, gx_defs)
        else:
            self._build_rtl_widgets(x, y, gx_defs)

    def draw(self, screen):
        for portrait in self.portraits:
            portrait.draw(screen)

    def get_event(self, event):
        for portrait in self.portraits:
            if portrait.get_event(event):
                return True
        return False


    def _build_ltr_widgets(self, x, y, gx_defs):
        ps = gx_defs["portrait_size"]
        ps_2 = ps // 2
        frame = gx_defs["portrait_frame_lr"]
        self.portraits = [
            UnitPortrait(x + 104 + ps, y + 104 + ps,
                         gx_defs["portrait_frame_lg_lr"], "portrait-l-0"),
            UnitPortrait(x + 72 + ps_2, y + 26 + ps_2, frame, "portrait-l-1"),
            UnitPortrait(x + 12 + ps_2, y + 103 + ps_2, frame, "portrait-l-2"),
            UnitPortrait(x + 28 + ps_2, y + 200 + ps_2, frame, "portrait-l-3")
        ]

    def _build_rtl_widgets(self, x, y, gx_defs):
        ps = gx_defs["portrait_size"]
        ps_2 = ps // 2
        frame = gx_defs["portrait_frame_rl"]
        self.portraits = [
            UnitPortrait(x - 104 - ps, y + 104 + ps,
                         gx_defs["portrait_frame_lg_rl"], "portrait-r-0"),
            UnitPortrait(x - 28 - ps_2, y + 200 + ps_2, frame, "portrait-r-1"),
            UnitPortrait(x - 12 - ps_2, y + 103 + ps_2, frame, "portrait-r-2"),
            UnitPortrait(x - 72 - ps_2, y + 26 + ps_2, frame, "portrait-r-3")
        ]


class BattleScene(object):
    def __init__(self, gx_defs):
        self.teams = [
            BattleTeamWidget(0, 0, gx_defs, ltr = True),
            BattleTeamWidget(gx_defs["screen_width"], 0, gx_defs, ltr = False)
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
