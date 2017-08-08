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

from .widgets import BattleTeamWidgetL, BattleTeamWidgetR, \
                     BattleActionPanel, CombatLogWidget


###############################################################################
#   Battle UI Scene
###############################################################################

class BattleScene(object):
    def __init__(self, gx_config, sprite_bank):
        self.busy = False
        self.sprite_bank = sprite_bank
        self.teams = [
            BattleTeamWidgetL(**gx_config["team_left"]),
            BattleTeamWidgetR(**gx_config["team_right"])
        ]
        for team in self.teams:
            for portrait in team.portraits:
                portrait.on_click = self.on_portrait_click
        self.action_panel = BattleActionPanel(**gx_config["action_panel"])
        self.combat_log = CombatLogWidget(**gx_config["combat_log"])
        self._timer = 0.0
        self._animations = 0

    def update(self, dt):
        if self.busy:
            if self._timer > 0.0:
                self._timer -= dt
                self.busy = self._timer >= 0.0
        if not self.busy and self._animations > 0:
            self.busy = True
            self._timer = 2.0
            self._animations -= 1

    def draw(self, screen):
        for team in self.teams:
            team.draw(screen)
        self.combat_log.draw(screen)
        self.action_panel.draw(screen)

    def get_event(self, event):
        for team in self.teams:
            if team.get_event(event):
                return True
        if self.action_panel.get_event(event):
            return True
        return False

    def reset(self):
        self.busy = False
        self.combat_log.clear()
        self.action_panel.set_active(False)

    def set_battle(self, engine):
        team_index = 0
        for battle_team in engine.mechanics.teams:
            self._update_team_portraits(team_index, battle_team)
            team_index += 1
        engine.mechanics.team_events.rotate_left.sub(self.on_team_rotate_left)
        engine.mechanics.team_events.rotate_right.sub(self.on_team_rotate_right)
        engine.mechanics.unit_events.damage.sub(self.on_damage)
        engine.mechanics.unit_events.heal.sub(self.on_heal)

    def get_player_input(self):
        self.busy = True
        action = self.action_panel.get_selected_action()
        if action:
            self.busy = False
            self.action_panel.set_active(False)
        return action

    def request_player_input(self):
        self.busy = True
        self._timer = -1.0
        self.action_panel.set_active(True)
        self.combat_log.log("Selecting round actions...")

    def on_portrait_click(self, portrait):
        print ">> Portrait clicked", portrait.name
        self.combat_log.log("Clicked on " + portrait.name)

    def on_battle_start(self, engine):
        self._animations += 1
        self.combat_log.log("The battle has started!")

    def on_battle_attack(self, engine):
        self._animations += 1
        self.combat_log.log("Entering the attack phase.")

    def on_between_rounds(self, engine):
        self._animations += 1
        self.combat_log.log("Round {} has ended.".format(engine.mechanics.round))

    def on_attack(self, engine, unit = None, target = None):
        self._animations += 1
        if unit.team.index == 0:
            self.combat_log.log("You attacked the enemy.")
        else:
            self.combat_log.log("The enemy attacked you.")

    def on_damage(self, unit, amount = 0, type = None):
        team = self.teams[unit.team.index]
        portrait = team.get_portrait_for(unit.index, unit.team.size)
        portrait.bar_level = unit.health / float(unit.max_health.value)
        if type is None:
            text = "{} took {} damage.".format(unit.template.name, amount)
        else:
            text = "{} took {} {} damage.".format(unit.template.name, amount,
                                                  type.name)
        self.combat_log.log(text)

    def on_heal(self, unit, amount = 0):
        team = self.teams[unit.team.index]
        portrait = team.get_portrait_for(unit.index, unit.team.size)
        portrait.bar_level = unit.health / float(unit.max_health.value)
        self.combat_log.log("{} restored {} health.".format(unit.template.name,
                                                            amount))

    def on_team_rotate_left(self, team, active = None, previous = None):
        self._update_team_portraits(team.index, team)
        if team.index == 0:
            self.combat_log.log("Your team rotated counter-clockwise.")
        else:
            self.combat_log.log("The enemy team rotated counter-clockwise.")

    def on_team_rotate_right(self, team, active = None, previous = None):
        self._update_team_portraits(team.index, team)
        if team.index == 0:
            self.combat_log.log("Your team rotated clockwise.")
        else:
            self.combat_log.log("The enemy team rotated clockwise.")


    def _update_team_portraits(self, team_index, battle_team):
        team = self.teams[team_index]
        for portrait in team.portraits:
            portrait.visible = False
            portrait.set_picture(None)
        n = battle_team.size
        for i in xrange(1, n):
            unit = battle_team.units[i]
            portrait = team.get_portrait_for(i, n)
            portrait.visible = True
            portrait.set_picture(self.sprite_bank.get(unit.template.id))
            portrait.bar_level = unit.health / float(unit.max_health.value)
        unit = battle_team.units[0]
        portrait = team.get_portrait_for(0, n)
        portrait.visible = True
        portrait.set_picture(self.sprite_bank.get(unit.template.id + "-main"))
        portrait.set_icon(self.sprite_bank.get(unit.template.type.id))
        portrait.bar_level = unit.health / float(unit.max_health.value)
