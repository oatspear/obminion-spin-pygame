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
from .animation import AnimationQueue, Animation, BarLevelAnimation, \
                       WriteAnimation, GetActionAnimation, AnimatedSprite


###############################################################################
#   Battle UI Scene
###############################################################################

class BattleScene(object):
    def __init__(self, gx_config, sprite_bank, animation_bank):
        self.sprite_bank = sprite_bank
        self.animation_bank = animation_bank
        self.teams = [
            BattleTeamWidgetL(**gx_config["team_left"]),
            BattleTeamWidgetR(**gx_config["team_right"])
        ]
        for team in self.teams:
            for portrait in team.portraits:
                portrait.on_click = self.on_portrait_click
        self.selected_action = None
        self.action_panel = BattleActionPanel(**gx_config["action_panel"])
        self.combat_log = CombatLogWidget(**gx_config["combat_log"])
        self._animations = AnimationQueue()

    @property
    def busy(self):
        return self._animations.busy

    def update(self, dt):
        self._animations.update(dt)

    def draw(self, screen):
        for team in self.teams:
            team.draw(screen)
        self.combat_log.draw(screen)
        self.action_panel.draw(screen)
        self._animations.draw(screen)

    def get_event(self, event):
        for team in self.teams:
            if team.get_event(event):
                return True
        if self.action_panel.get_event(event):
            return True
        return False

    def reset(self):
        self.combat_log.clear()
        self.action_panel.set_active(False)
        self._animations.cancel_all()

    def set_battle(self, engine):
        team_index = 0
        for battle_team in engine.mechanics.teams:
            self._update_team_portraits(team_index, battle_team)
            team_index += 1
        engine.mechanics.team_events.rotate_left.sub(self.on_team_rotate_left)
        engine.mechanics.team_events.rotate_right.sub(self.on_team_rotate_right)
        engine.mechanics.team_events.add.sub(self.on_team_add)
        engine.mechanics.team_events.remove.sub(self.on_team_remove)
        engine.mechanics.unit_events.attack.sub(self.on_attack)
        engine.mechanics.unit_events.damage.sub(self.on_damage)
        engine.mechanics.unit_events.heal.sub(self.on_heal)
        engine.mechanics.unit_events.ability.sub(self.on_trigger_ability)

    def get_player_input(self):
        action = self.selected_action
        if action:
            self.selected_action = None
        return action

    def request_player_input(self):
        self.selected_action = None
        self._log("Selecting actions...")
        animation = GetActionAnimation(self.action_panel)
        animation.on_end = self._on_player_action
        self._animations.push(animation)

    def on_portrait_click(self, portrait):
        print ">> Portrait clicked", portrait.name
        self.combat_log.log("Clicked on " + portrait.name)

    def on_battle_start(self, engine):
        self._log("The battle has started!")

    def on_battle_attack(self, engine):
        self._log("Entering the attack phase.")

    def on_between_rounds(self, engine):
        self._log("Round {} has ended.".format(engine.mechanics.round))

    def on_attack(self, unit, target = None):
        if unit.team.index == 0:
            self._log("You attacked the enemy.")
        else:
            self._log("The enemy attacked you.")

    def on_damage(self, unit, amount = 0, type = None, source = None):
        team = self.teams[unit.team.index]
        portrait = team.get_portrait_for(unit.index, unit.team.size)
        if type is None:
            text = "{} took {} damage.".format(unit.template.name, amount)
        else:
            text = "{} took {} {} damage.".format(unit.template.name, amount,
                                                  type.name)
        self._log(text)
        level = unit.health / float(unit.max_health.value)
        self._animations.push(BarLevelAnimation(portrait, level, -0.5))
        self._animations.push(WriteAnimation(portrait.health,
                                             str(unit.health), 0))

    def on_heal(self, unit, amount = 0, source = None):
        team = self.teams[unit.team.index]
        portrait = team.get_portrait_for(unit.index, unit.team.size)
        self._log("{} restored {} health.".format(unit.template.name, amount))
        level = unit.health / float(unit.max_health.value)
        self._animations.push(BarLevelAnimation(portrait, level, 0.5))
        self._animations.push(WriteAnimation(portrait.health,
                                             str(unit.health), 0))

    def on_trigger_ability(self, ability, unit = None):
        self._log("{} triggered {}.".format(unit.template.name, ability.name))

    def on_team_rotate_left(self, team, active = None, previous = None):
        if team.index == 0:
            self._log("Your team rotated counter-clockwise.")
        else:
            self._log("The enemy team rotated counter-clockwise.")
        self.animation_bank.set_sprite("rotation_counter")
        portrait = self.teams[team.index].get_portrait_for(0, team.size)
        cx = portrait.picture_rect.centerx
        cy = portrait.picture_rect.centery
        animation = AnimatedSprite(self.animation_bank.image_sequence,
                                   cx, cy, repeats = 3)
        animation.on_end = lambda a: self._update_team_portraits(team.index, team)
        self._animations.push(animation)

    def on_team_rotate_right(self, team, active = None, previous = None):
        if team.index == 0:
            self._log("Your team rotated clockwise.")
        else:
            self._log("The enemy team rotated clockwise.")
        self.animation_bank.set_sprite("rotation_clock")
        portrait = self.teams[team.index].get_portrait_for(0, team.size)
        cx = portrait.picture_rect.centerx
        cy = portrait.picture_rect.centery
        animation = AnimatedSprite(self.animation_bank.image_sequence,
                                   cx, cy, repeats = 3)
        animation.on_end = lambda a: self._update_team_portraits(team.index, team)
        self._animations.push(animation)

    def on_team_add(self, team, unit = None):
        animation = Animation(1.0, 0.0)
        animation.on_end = lambda a: self._update_team_portraits(team.index, team)
        self._animations.push(animation)

    def on_team_remove(self, team, unit = None):
        if team.size:
            animation = Animation(1.0, 0.0)
            animation.on_end = lambda a: self._update_team_portraits(team.index, team)
            self._animations.push(animation)


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
            portrait.health.set_text(str(unit.health))
        unit = battle_team.units[0]
        portrait = team.get_portrait_for(0, n)
        portrait.visible = True
        portrait.set_picture(self.sprite_bank.get(unit.template.id + "_main"))
        portrait.set_icon(self.sprite_bank.get(unit.template.type.id))
        portrait.bar_level = unit.health / float(unit.max_health.value)
        portrait.health.set_text(str(unit.health))
        portrait.power.set_text(str(unit.power.value))
        portrait.speed.set_text(str(unit.speed.value))

    def _log(self, text):
        animation = WriteAnimation(None, text, 0, delay = 0.5)
        animation.on_start = self._on_log_start
        self._animations.push(animation)

    def _on_log_start(self, animation):
        self.combat_log.log("")
        animation.element = self.combat_log.entries[-1]

    def _on_player_action(self, animation):
        self.action_panel.set_active(False)
        self.selected_action = animation.action
