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

from random import randint

from .events import Event
from .models import BattleUnit, BattleTeam

###############################################################################
#   Battle Mechanics
###############################################################################

class BattleMechanics(object):
    def __init__(self):
        self.teams = []
        self.turn = 0
        self.round = 1
        self.abilities = []
        self.events = MechanicsEventChannel()
        self.unit_events = UnitEventChannel()
        self.team_events = TeamEventChannel()
        self.team_events.remove.sub(self._on_unit_remove)

    @property
    def battle_over(self):
        return len([t for t in self.teams if t.alive]) < 2

    @property
    def next(self):
        return (self.turn + 1) % len(self.teams)

    @property
    def active(self):
        return self.teams[self.turn]

    @property
    def next_active(self):
        return self.teams[self.next]

    @property
    def attacker(self):
        return self.teams[self.turn].active

    @property
    def defender(self):
        return self.teams[self.next].active

    def make_team(self, unit_listing):
        team = BattleTeam(4, self.team_events)
        for instance in unit_listing:
            unit = BattleUnit(instance, self.unit_events)
            team.add_unit(unit)
        team.index = len(self.teams)
        self.teams.append(team)

    def flip_turn(self):
        self.turn = self.next

    def calculate_turn(self):
        ms = 0
        s = 0
        for i, team in enumerate(self.teams):
            s = team.active.speed.value
            if s > ms:
                ms = s
                self.turn = i
            elif s == ms and randint(0, 1):
                self.turn = i

    def attack(self):
        unit    = self.attacker
        damage  = unit.power.value
        type    = unit.type
        target  = self.defender
        self.unit_events.attack(unit, target = target)
        self.unit_events.defend(target, target = unit)
        damage = target.damage(damage, type)
        if damage > 0:
            self.unit_events.post_attack(unit, target = target, damage = damage)
        # self.events.attack(self, unit = unit, target = target, damage = damage)

    def cleanup(self):
        for team in self.teams:
            team.cleanup()

    def tick(self):
        pass

    def next_round(self):
        self.round += 1
        self.events.round(self)

    def create_handlers(self):
        for team in self.teams:
            for unit in team.units:
                if unit.ability:
                    for effect in unit.ability.effects:
                        h = EffectHandler(self, unit, effect)
                        h.bind()
                        self.abilities.append(h)

    def target(self, unit, target):
        return getattr(self, "_target_" + target)(unit)

    def _target_all(self, unit):
        targets = [FixTarget(team, unit, range(team.capacity),
                             inclusive = True) for team in self.teams]
        return CompoundTarget(targets)

    def _target_self(self, unit):
        return RelativeTarget(unit.team, unit, (0,), inclusive = True)

    def _target_self_left(self, unit):
        return RelativeTarget(unit.team, unit, (-1,))

    def _target_self_right(self, unit):
        return RelativeTarget(unit.team, unit, (1,))

    def _target_self_adjacent(self, unit):
        return RelativeTarget(unit.team, unit, (1, -1))

    # def _target_friend_team(self, unit):
        # return unit.team

    def _target_friend_active(self, unit):
        return FixTarget(unit.team, unit, (0,), inclusive = True)

    def _target_friend_all(self, unit):
        return FixTarget(unit.team, unit, range(team.capacity),
                         inclusive = True)

    def _target_friend_left(self, unit):
        return FixTarget(unit.team, unit, (-1,), inclusive = True)

    def _target_friend_right(self, unit):
        return FixTarget(unit.team, unit, (1,), inclusive = True)

    def _target_friend_adjacent(self, unit):
        return FixTarget(unit.team, unit, (1, -1), inclusive = True)

    def _target_friend_front(self, unit):
        return FixTarget(unit.team, unit, (0, 1, -1), inclusive = True)

    def _target_friend_others(self, unit):
        return FixTarget(unit.team, unit, range(team.capacity))

    def _target_friend_standby(self, unit):
        return FixTarget(unit.team, unit, range(1, team.capacity),
                         inclusive = True)

    def _target_opponent(self, unit):
        return FixTarget(self._opposing(unit), unit, (0,))

    # def _target_opponent_team(self, unit):
        # return self._opposing(unit)

    def _target_opponent_all(self, unit):
        team = self._opposing(unit)
        return FixTarget(team, unit, range(team.capacity))

    def _target_opponent_left(self, unit):
        return FixTarget(self._opposing(unit), unit, (-1,))

    def _target_opponent_right(self, unit):
        return FixTarget(self._opposing(unit), unit, (1,))

    def _target_opponent_adjacent(self, unit):
        return FixTarget(self._opposing(unit), unit, (1, -1))

    def _target_opponent_front(self, unit):
        return FixTarget(self._opposing(unit), unit, (0, 1, -1))

    def _target_opponent_standby(self, unit):
        team = self._opposing(unit)
        return FixTarget(team, unit, range(1, team.capacity))

    def _opposing(self, unit):
        return self.teams[(unit.team.index + 1) % len(self.teams)]

    def _on_unit_remove(self, team, **args):
        i = 0
        unit = args["unit"]
        while i < len(self.abilities):
            effect = self.abilities[i]
            if effect.unit is unit:
                del self.abilities[i]
                effect.remove()
                print "removed ability effect"
            else:
                i += 1



###############################################################################
#   Effect Handlers
###############################################################################

class EffectHandler(object):
    def __init__(self, mechanics, unit, template):
        self.mechanics  = mechanics
        self.unit       = unit
        self.template   = template
        self.targets    = mechanics.target(unit, template.target)
        self.mechanic   = getattr(self, "_mechanic_" + template.mechanic)
        self.callbacks  = []

    def bind(self):
        for event in self.template.events:
            event = event.split()
            source = event[0]
            event = event[1]
            if source == "mechanics":
                cb = EffectCallback(self.template.ability, self.unit,
                                    self.mechanics.events, event,
                                    (self.mechanics,), self.mechanic)
            elif "team" in source:
                cb = EffectCallback(self.template.ability, self.unit,
                                    self.mechanics.team_events, event,
                                    self.mechanics.target(self.unit, source),
                                    self.mechanic)
            else:
                cb = EffectCallback(self.template.ability, self.unit,
                                    self.mechanics.unit_events, event,
                                    self.mechanics.target(self.unit, source),
                                    self.mechanic)
            self.callbacks.append(cb)

    def remove(self):
        while self.callbacks:
            callback = self.callbacks.pop()
            callback.remove()

    def _mechanic_log(self, emitter, **args):
        print self.template.ability.name, "triggered with", args
        return True

    def _mechanic_damage(self, emitter, **args):
        param = self.template.parameters
        type = param.get("type")
        if "amount" in param:
            amount = param["amount"]
        else:
            assert "relative" in param and "reference" in param
            amount = int(param["relative"] * args[param["reference"]])
        for target in self.targets.get():
            target.damage(amount, type = type, source = self)
        return True

    def _mechanic_heal(self, emitter, **args):
        param = self.template.parameters
        if "amount" in param:
            amount = param["amount"]
        else:
            assert "relative" in param and "reference" in param
            amount = int(param["relative"] * args[param["reference"]])
        for target in self.targets.get():
            target.heal(amount)
        return True


class EffectCallback(object):
    def __init__(self, ability, unit, channel, event, sources, function):
        self.ability = ability
        self.unit = unit
        self.channel = channel
        self.topic = getattr(channel, event)
        self.sources = sources
        self.function = function
        self.topic.sub(self.callback)

    def callback(self, emitter, **args):
        if emitter in self.sources:
            if self.function(emitter, **args):
                self.channel.ability(self.ability, unit = self.unit)

    def remove(self):
        self.topic.unsub(self.callback)



###############################################################################
#   Event Channels
###############################################################################

class UnitEventChannel(object):
    def __init__(self):
        self.spawn      = Event()
        self.death      = Event()
        self.damage     = Event()
        self.heal       = Event()
        self.attack     = Event()
        self.defend     = Event()
        self.rotate_in  = Event()
        self.rotate_out = Event()
        self.ability    = Event()
        self.post_attack = Event()  # successful attack

class TeamEventChannel(object):
    def __init__(self):
        self.add            = Event()
        self.remove         = Event()
        self.rotate         = Event()
        self.rotate_left    = Event()
        self.rotate_right   = Event()

class MechanicsEventChannel(object):
    def __init__(self):
        self.round  = Event()
        # self.attack = Event()

class EngineEventChannel(object):
    def __init__(self):
        self.battle_start           = Event()
        self.battle_select_action   = Event()
        self.battle_attack          = Event()
        self.battle_between_rounds  = Event()
        self.battle_end             = Event()
        self.request_input          = Event()
        self.end_phase              = Event()
        self.attack                 = Event()



###############################################################################
#   Target System
###############################################################################

class RelativeTarget(object):
    def __init__(self, team, unit, offsets, inclusive = False):
        self.team = team
        self.unit = unit
        self.offsets = offsets
        self.inclusive = inclusive

    def get(self):
        units = []
        for offset in self.offsets:
            u = self.team.units[(self.unit.index + offset) % self.team.size]
            if self.inclusive or not u is self.unit:
                if not u in units:
                    units.append(u)
        return units

    def __contains__(self, unit):
        for offset in self.offsets:
            u = self.team.units[(self.unit.index + offset) % self.team.size]
            if self.inclusive or not u is self.unit:
                if u is unit:
                    return True
        return False


class FixTarget(object):
    def __init__(self, team, unit, indices, inclusive = False):
        self.team = team
        self.unit = unit
        self.indices = indices
        self.inclusive = inclusive

    def get(self):
        units = []
        for index in self.indices:
            if index < self.team.size and index > -self.team.size:
                u = self.team.units[index]
                if self.inclusive or not u is self.unit:
                    if not u in units:
                        units.append(u)
        return units

    def __contains__(self, unit):
        for index in self.indices:
            if index < self.team.size and index > -self.team.size:
                u = self.team.units[index]
                if self.inclusive or not u is self.unit:
                    if u is unit:
                        return True
        return False


class CompoundTarget(object):
    def __init__(self, targets):
        self.targets = targets

    def get(self):
        units = set()
        for target in self.targets:
            units.update(target.get())
        return list(units)

    def __contains__(self, unit):
        for target in self.targets:
            if unit in target:
                return True
        return False



###############################################################################
#   Battle Engine
###############################################################################

class BattleEngine(object):
    def __init__(self):
        self.mechanics  = None
        self.on         = EngineEventChannel()
        self.state      = None
        self._handler   = None

    def set_battle(self, unit_listings):
        self.mechanics = BattleMechanics()
        for unit_listing in unit_listings:
            self.mechanics.make_team(unit_listing)
        self.state = "start"
        self._handler = self._state_start

    def set_action(self, action, i):
        team = self.mechanics.teams[i]
        if action == "surrender":
            self.state = "end"
            self._handler = self._state_end
            return
        if action == "rotate_counter":
            if team.can_rotate:
                print "rotating left"
                team.rotate_left()
        elif action == "rotate_clock":
            if team.can_rotate:
                print "rotating right"
                team.rotate_right()
        elif action == "attack":
            print "no rotation"
        else:
            print "invalid action"
            return
        self.state = "attack"
        self._handler = self._state_attack
        self.on.end_phase(self)

    def step(self):
        next = self._handler()
        if next:
            self.state = next
            self._handler = getattr(self, "_state_" + next)

    def _state_start(self):
        self.on.battle_start(self)
        self.mechanics.create_handlers()
        self.on.end_phase(self)
        return "select_action"

    def _state_select_action(self):
        self.on.battle_select_action(self)
        self.on.request_input(self)
        return None

    def _state_attack(self):
        self.on.battle_attack(self)
        self.mechanics.calculate_turn()
        self.mechanics.attack()
        self.on.attack(self, unit = self.mechanics.attacker,
                       target = self.mechanics.defender)
        self.mechanics.cleanup()
        if self.mechanics.battle_over:
            self.on.end_phase(self)
            return "end"
        # If the defender dies here, the guy that steps in automatically attacks.
        # cleanup() places another guy into position, if there's one available.
        # Revenge!
        self.mechanics.flip_turn()
        self.mechanics.attack()
        self.on.attack(self, unit = self.mechanics.attacker,
                       target = self.mechanics.defender)
        self.mechanics.cleanup()
        self.on.end_phase(self)
        if self.mechanics.battle_over:
            return "end"
        return "between_rounds"

    def _state_between_rounds(self):
        self.on.battle_between_rounds(self)
        self.mechanics.tick()
        self.mechanics.cleanup()
        if self.mechanics.battle_over:
            self.on.end_phase(self)
            return "end"
        self.mechanics.next_round()
        self.on.end_phase(self)
        return "select_action"

    def _state_end(self):
        self.on.battle_end(self)
        self.on.end_phase(self)
