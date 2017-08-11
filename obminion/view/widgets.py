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
        self.on_click       = None
        self.on_right_click = None
        self.border_top     = border[0]
        self.border_left    = border[1]
        self.border_bottom  = border[2]
        self.border_right   = border[3]
        self.visible        = True

    def update(self, dt):
        pass

    def draw(self, screen):
        if self.visible:
            self.rect.x = self.x
            self.rect.y = self.y
            screen.blit(self.image, self.rect)

    def get_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pg.mouse.get_pos()):
                if event.button == 1 and not self.on_click is None:
                    self.on_click(self)
                    return True
                if event.button == 3 and not self.on_right_click is None:
                    self.on_right_click(self)
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


class TextLabel(object):
    def __init__(self, x, y, text = "", font = None, font_name = "monospace",
                 font_size = 12, font_colour = (0, 0, 0), font_bg = None):
        self.x           = x
        self.y           = y
        self.label       = None
        self.rect        = None
        self.font_colour = font_colour
        self.font_bg     = font_bg
        if font is None:
            self.font = pg.font.SysFont(font_name, font_size)
        else:
            self.font = font
        self.set_text(text)

    def draw(self, screen):
        if not self.label is None:
            self.rect.x = self.x
            self.rect.y = self.y
            screen.blit(self.label, self.rect)

    def set_text(self, text):
        self.text = text
        if text:
            self.label = self.font.render(text, True, self.font_colour,
                                          self.font_bg)
            self.rect = self.label.get_rect()
            self.rect.x = self.x
            self.rect.y = self.y
        else:
            self.label = None
            self.rect = None


###############################################################################
#   Battle UI Unit Widgets
###############################################################################

class UnitPortrait(UIWidget):
    def __init__(self, x, y, name, frame, border, bar, bar_colour, bar_bg,
                 picture, bg_colour, font, font_colour,
                 health_label, power_label, speed_label):
        UIWidget.__init__(self, x, y, frame, name = name, border = border)
        self.bar_level = 0.0
        self.bar_pos = bar
        self.bar_colour = bar_colour
        self.bar_bg = bar_bg
        self.bar_rect = pg.Rect(x + bar[0], y + bar[1], bar[2], bar[3])
        self.picture = None
        self.picture_pos = picture
        self.picture_rect = None
        self.bg_colour = bg_colour
        self.display_picture = True
        self.display_labels = True
        self.health_pos = health_label
        self.health = TextLabel(health_label[0], health_label[1],
                                font = font, font_colour = font_colour,
                                font_bg = bg_colour)
        self.power_pos = power_label
        self.power = TextLabel(power_label[0], power_label[1],
                               font = font, font_colour = font_colour,
                               font_bg = bg_colour)
        self.speed_pos = speed_label
        self.speed = TextLabel(speed_label[0], speed_label[1],
                               font = font, font_colour = font_colour,
                               font_bg = bg_colour)

    def draw(self, screen):
        if not self.visible:
            return False
        if self.picture is None or not self.display_picture:
            screen.fill(self.bg_colour, self.picture_pos)
        else:
            self.picture_rect.x = self.x + self.picture_pos[0]
            self.picture_rect.y = self.y + self.picture_pos[1]
            screen.blit(self.picture, self.picture_rect)
    # -- health bar -----------------------------------------------------------
        self.bar_rect.x = self.x + self.bar_pos[0]
        if not self.bar_bg is None:
            self.bar_rect.h = self.bar_pos[3]
            self.bar_rect.y = self.y + self.bar_pos[1]
            screen.fill(self.bar_bg, self.bar_rect)
        if self.bar_level > 0.0:
            self.bar_rect.h = int(self.bar_level * self.bar_pos[3])
            self.bar_rect.y = (self.y + self.bar_pos[1]
                               + self.bar_pos[3] - self.bar_rect.h)
            screen.fill(self.bar_colour, self.bar_rect)
        UIWidget.draw(self, screen)
    # -- labels ---------------------------------------------------------------
        if self.display_labels:
            self.health.x = self.x + self.health_pos[0]
            self.health.y = self.y + self.health_pos[1]
            self.health.draw(screen)
            self.power.x = self.x + self.power_pos[0]
            self.power.y = self.y + self.power_pos[1]
            self.power.draw(screen)
            self.speed.x = self.x + self.speed_pos[0]
            self.speed.y = self.y + self.speed_pos[1]
            self.speed.draw(screen)

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
                 picture = (8, 0, 64, 64), bar_colour = (0, 128, 0),
                 bar_bg = (0, 0, 0), bg_colour = (0, 0, 0), font = None,
                 font_name = "monospace", font_size = 12,
                 font_colour = (0, 0, 0), font_bg = None,
                 health_label = (8, 0), power_label = (8, 18),
                 speed_label = (8, 36)):
        if font is None:
            font = pg.font.SysFont(font_name, font_size)
        UnitPortrait.__init__(self, x, y, name, frame, border,
                              bar, bar_colour, bar_bg, picture,
                              bg_colour, font, font_colour,
                              health_label, power_label, speed_label)


class UnitPortraitR(UnitPortrait):
    def __init__(self, x = 0, y = 0, name = "portrait-R", frame = None,
                 border = (0, 0, 0, 0), bar = (64, 0, 8, 64),
                 picture = (0, 0, 64, 64), bar_colour = (0, 128, 0),
                 bar_bg = (0, 0, 0), bg_colour = (0, 0, 0), font = None,
                 font_name = "monospace", font_size = 12,
                 font_colour = (0, 0, 0), font_bg = None,
                 health_label = (0, 0), power_label = (0, 18),
                 speed_label = (0, 36)):
        if font is None:
            font = pg.font.SysFont(font_name, font_size)
        UnitPortrait.__init__(self, x, y, name, frame, border,
                              bar, bar_colour, bar_bg, picture,
                              bg_colour, font, font_colour,
                              health_label, power_label, speed_label)


class LargeUnitPortrait(UnitPortrait):
    def __init__(self, x, y, name, frame, border,
                 bar, bar_colour, bar_bg, picture, icon,
                 bg_colour, font, font_colour,
                 health_label, power_label, speed_label):
        UnitPortrait.__init__(self, x, y, name, frame, border,
                              bar, bar_colour, bar_bg, picture,
                              bg_colour, font, font_colour,
                              health_label, power_label, speed_label)
        self.icon = None
        self.icon_pos = icon
        self.icon_rect = None

    def draw(self, screen):
        if not self.visible:
            return False
        if not self.icon is None:
            self.icon_rect.x = self.x + self.icon_pos[0]
            self.icon_rect.y = self.y + self.icon_pos[1]
            screen.blit(self.icon, self.icon_rect)
        UnitPortrait.draw(self, screen)

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
                 bar_colour = (0, 128, 0), bar_bg = (0, 0, 0),
                 picture = (32, 0, 128, 128), icon = (0, 0, 32, 32),
                 bg_colour = (0, 0, 0), font = None, font_name = "monospace",
                 font_size = 12, font_colour = (0, 0, 0), font_bg = None,
                 health_label = (0, 0), power_label = (0, 18),
                 speed_label = (0, 36)):
        if font is None:
            font = pg.font.SysFont(font_name, font_size)
        LargeUnitPortrait.__init__(self, x, y, name, frame, border, bar,
                                   bar_colour, bar_bg, picture, icon,
                                   bg_colour, font, font_colour,
                                   health_label, power_label, speed_label)


class LargeUnitPortraitR(LargeUnitPortrait):
    def __init__(self, x = 0, y = 0, name = "portrait-lg-R", frame = None,
                 border = (0, 0, 0, 0), bar = (128, 0, 8, 96),
                 bar_colour = (0, 128, 0), bar_bg = (0, 0, 0),
                 picture = (0, 0, 128, 128), icon = (128, 96, 32, 32),
                 bg_colour = (0, 0, 0), font = None, font_name = "monospace",
                 font_size = 12, font_colour = (0, 0, 0), font_bg = None,
                 health_label = (0, 0), power_label = (0, 18),
                 speed_label = (0, 36)):
        if font is None:
            font = pg.font.SysFont(font_name, font_size)
        LargeUnitPortrait.__init__(self, x, y, name, frame, border, bar,
                                   bar_colour, bar_bg, picture, icon,
                                   bg_colour, font, font_colour,
                                   health_label, power_label, speed_label)


###############################################################################
#   Battle UI Team Widgets
###############################################################################

# active is a dict to pass down to LargeUnitPortrait
# team is a list of dict to pass down to UnitPortrait
class BattleTeamWidget(object):
    def __init__(self, active, team, ordering, upc, lupc):
        self.portraits = [lupc(**active)]
        for config in team:
            self.portraits.append(upc(**config))
        if ordering:
            self.ordering = ordering
        else:
            self.ordering = [range(i) for i in xrange(len(self.portraits))]

    def draw(self, screen):
        for portrait in self.portraits:
            portrait.draw(screen)

    def get_event(self, event):
        for portrait in self.portraits:
            if portrait.get_event(event):
                return True
        return False

    def get_portrait_for(self, i, n):
        assert i >= -n and i < n and n <= len(self.portraits)
        return self.portraits[self.ordering[n][i]]


class BattleTeamWidgetL(BattleTeamWidget):
    def __init__(self, active = None, team = None, ordering = None):
        BattleTeamWidget.__init__(self, active, team, ordering,
                                  UnitPortraitL, LargeUnitPortraitL)

class BattleTeamWidgetR(BattleTeamWidget):
    def __init__(self, active = None, team = None, ordering = None):
        BattleTeamWidget.__init__(self, active, team, ordering,
                                  UnitPortraitR, LargeUnitPortraitR)


###############################################################################
#   Battle UI Combat Log
###############################################################################

class CombatLogWidget(UIWidget):
    def __init__(self, x = 0, y = 0, name = "action_panel", frame = None,
                 border = (0, 0, 0, 0), entries = 1, label = (0, 0),
                 font = None, font_name = "monospace",
                 font_size = 12, font_colour = (0, 0, 0), font_bg = None):
        UIWidget.__init__(self, x, y, frame, name = name, border = border)
        if font is None:
            self.font = pg.font.SysFont(font_name, font_size)
        else:
            self.font = font
        self.spacing = self.font.get_linesize()
        self.label_pos = label
        self.entries = []
        for i in xrange(entries):
            lx = x + label[0]
            ly = y + label[1] + i * self.spacing
            self.entries.append(TextLabel(lx, ly, font = self.font,
                                          font_colour = font_colour,
                                          font_bg = font_bg))

    def draw(self, screen):
        UIWidget.draw(self, screen)
        i = 0
        for entry in self.entries:
            entry.x = self.x + self.label_pos[0]
            entry.y = self.y + self.label_pos[1] + i * self.spacing
            entry.draw(screen)
            i += 1

    def log(self, text):
        entry = self.entries.pop(0)
        self.entries.append(entry)
        entry.set_text(text)

    def clear(self):
        for entry in self.entries:
            entry.set_text("")


###############################################################################
#   Battle UI Action Widgets
###############################################################################

class ActionButton(UIWidget):
    def __init__(self, x = 0, y = 0, name = "button", icon = None,
                 border = (0, 0, 0, 0), description = ""):
        UIWidget.__init__(self, x, y, icon, name = name, border = border)
        self.description = description


# it is easier for 'actions' to be a dict instead of a list of things
class ActionPanel(UIWidget):
    def __init__(self, x = 0, y = 0, name = "action_panel", frame = None,
                 border = (0, 0, 0, 0), actions = None, label = (0, 0),
                 font = None, font_name = "monospace",
                 font_size = 12, font_colour = (0, 0, 0), font_bg = None):
        UIWidget.__init__(self, x, y, frame, name = name, border = border)
        self.active = False
        self.label_pos = label
        if font is None:
            self.font = pg.font.SysFont(font_name, font_size)
        else:
            self.font = font
        self.label = TextLabel(x + label[0], y + label[1], font = self.font,
                               font_colour = font_colour, font_bg = font_bg)
        self.actions    = []
        for name, config in actions.iteritems():
            button = ActionButton(name = name, **config)
            self.actions.append(button)
            button.x += x
            button.y += y

    def draw(self, screen):
        UIWidget.draw(self, screen)
        if self.active:
            for action in self.actions:
                action.draw(screen)
            self.label.x = self.x + self.label_pos[0]
            self.label.y = self.y + self.label_pos[1]
            self.label.draw(screen)

    def get_event(self, event):
        if self.active:
            for action in self.actions:
                if action.get_event(event):
                    return True
        return False

    def set_text_label(self, text):
        self.label.set_text(text)

    def set_active(self, active):
        self.active = active
        for action in self.actions:
            action.hovering = False


class BattleActionPanel(ActionPanel):
    DEFAULT_ACTIONS = ("attack", "rotate_counter", "rotate_clock", "surrender")

    def __init__(self, x = 0, y = 0, name = "action_panel", frame = None,
                 border = (0, 0, 0, 0), actions = None, label = (0, 0),
                 font = None, font_name = "monospace",
                 font_size = 12, font_colour = (0, 0, 0), font_bg = None):
        ActionPanel.__init__(self, x = x, y = y, name = name, frame = frame,
                             border = border, actions = {}, label = label,
                             font = font, font_name = font_name,
                             font_size = font_size, font_colour = font_colour,
                             font_bg = font_bg)
        self._selected_action = None
        for name in self.DEFAULT_ACTIONS:
            config = actions[name]
            button = ActionButton(name = name, **config)
            self.actions.append(button)
            button.x += x
            button.y += y
            button.on_click = self.on_action_button_click
            button.on_right_click = self.on_action_button_right_click

    def set_active(self, active):
        ActionPanel.set_active(self, active)
        self._selected_action = None

    def get_selected_action(self):
        action = self._selected_action
        self._selected_action = None
        return action

    def on_action_button_click(self, button):
        self._selected_action = button.name
        self.label.set_text("")

    def on_action_button_right_click(self, button):
        self.label.set_text(button.description)
