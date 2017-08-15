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

from .widgets import UIWidget, HighlightWidget, MissionPanel
from .animation import AnimationQueue, Animation


###############################################################################
#   Overworld UI Scene
###############################################################################

class OverworldScene(object):
    def __init__(self, gx_config, sprite_bank, animation_bank, image_bank):
        self.sprite_bank = sprite_bank
        self.animation_bank = animation_bank
        self.image_bank = image_bank
        self.selected_action = None
        self.map = UIWidget(0, 0, None, name = "map")
        self.nodes = []
        self._prepare_data(gx_config)
        self.mission_panel = MissionPanel(**gx_config["mission_panel"])
        self.mission_panel.visible = False
        self._animations = AnimationQueue()

    @property
    def busy(self):
        return self._animations.busy

    @property
    def waiting_mission_feedback(self):
        return self.mission_panel.visible

    def update(self, dt):
        if not self._animations.busy and not self.mission_panel.visible:
            pos = pg.mouse.get_pos()
            for node in self.nodes:
                node.update_mouse(pos)
        self._animations.update(dt)

    def draw(self, screen):
        self.map.draw(screen)
        for node in self.nodes:
            node.draw(screen)
        self.mission_panel.draw(screen)
        self._animations.draw(screen)

    def get_event(self, event):
        for node in self.nodes:
            if node.get_event(event):
                return True
        if self.mission_panel.get_event(event):
            return True
        return False

    def reset(self):
        self.nodes = []
        self.map.set_image(None)
        self.mission_panel.visible = False
        self._animations.cancel_all()
        self.selected_action = None
        for portrait in self.mission_panel.team:
            portrait.set_picture(None)
        for portrait in self.mission_panel.roster:
            portrait.set_picture(None)
        self.mission_panel.opponent.set_picture(None)

    def set_map(self, name, nodes):
        self.selected_action = None
        self.map.set_image(self.image_bank.get(name))
        self.map.visible = True
        for name, data in nodes.iteritems():
            node = HighlightWidget(data["x"], data["y"],
                                   data["highlight"], name = name)
            node.on_click = self.on_node_click
            self.nodes.append(node)

    def set_mission(self, title, team, roster, opponent):
        self.mission_panel.visible = True
        self.mission_panel.set_title(title)
        for i in xrange(len(self.mission_panel.team)):
            portrait = self.mission_panel.team[i]
            if i < len(team):
                portrait.visible = True
                portrait.set_picture(self.sprite_bank.get(team[i].template.id))
            else:
                portrait.visible = False
                portrait.set_picture(None)
        for i in xrange(len(self.mission_panel.roster)):
            portrait = self.mission_panel.roster[i]
            if i < len(roster):
                portrait.visible = True
                portrait.set_picture(self.sprite_bank.get(roster[i].id))
            else:
                portrait.visible = False
                portrait.set_picture(None)
        self.mission_panel.opponent.set_picture(self.sprite_bank.get(opponent.template.id))

    def get_player_input(self):
        action = self.selected_action
        self.selected_action = None
        return action


    def on_node_click(self, element):
        print ">> Selected level", element.name
        self.selected_action = element.name
        for node in self.nodes:
            node.active = False

    def on_accept_mission(self, portrait):
        self.mission_panel.visible = False
        self.selected_action = "battle"

    def on_cancel_mission(self, button):
        self.mission_panel.visible = False
        self.selected_action = "cancel"
        for node in self.nodes:
            node.active = True


    def _prepare_data(self, gx_config):
        mission_panel = gx_config["mission_panel"]
        mission_panel["opponent"]["name"] = "battle"
        for portrait in mission_panel["player_team"]:
            portrait["name"] = "team_unit"
        for portrait in mission_panel["roster"]:
            portrait["name"] = "roster"
        mission_panel["opponent"]["on_click"] = self.on_accept_mission
        actions = mission_panel["actions"]
        actions["cancel"]["on_click"] = self.on_cancel_mission
        # actions["swap_left"]["on_click"] = self.on_team_swap_left
        # actions["swap_right"]["on_click"] = self.on_team_swap_right
