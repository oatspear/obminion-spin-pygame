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

###############################################################################
#   Species Template
###############################################################################

class UnitTemplate(object):
    id_gen = 1

    def __init__(self, id, name, type, health, power, speed, abilities,
                 portrait):
        self.id         = id
        self.name       = name
        self.type       = type
        self.health     = health
        self.power      = power
        self.speed      = speed
        self.abilities  = abilities
        self.portrait   = portrait

    @classmethod
    def defaults(cls):
        id = "ut" + str(cls.id_gen)
        cls.id_gen += 1
        return cls(id, "<name>", None, 1, 1, 1, [], None)

    def random_ability(self):
        if self.abilities:
            return self.abilities[0]
        return None



###############################################################################
#   Species Instance
###############################################################################

class UnitInstance(object):
    def __init__(self, template, level = 1, experience = 0, health = None,
                 power = None, speed = None, ability = None):
        self.template   = template
        self.level      = level
        self.xp         = experience
        self.health     = health or self.get_health()
        self.power      = power or self.get_power()
        self.speed      = speed or self.get_speed()
        self.ability    = ability or self.template.random_ability()

    def get_health(self):
        return self.template.health + (self.level + 1) // 3

    def get_power(self):
        return self.template.power + self.level // 3

    def get_speed(self):
        return self.template.speed + (self.level - 1) // 3



###############################################################################
#   Battle Instance
###############################################################################

class BattleUnit(object):
    def __init__(self, instance, events, template = None, type = None,
                 health = None, max_health = None, power = None, speed = None,
                 ability = None):
        self.instance   = instance
        self.template   = template or instance.template
        self.type       = type or self.template.type
        self.max_health = Attribute(max_health or instance.get_health())
        self.health     = health or self.max_health.value
        self.power      = Attribute(power or instance.get_power())
        self.speed      = Attribute(speed or instance.get_speed())
        self.ability    = ability or instance.ability
        self.team       = None
        self.index      = -1
        self.on         = events

    @property
    def alive(self):
        return self.health > 0

    def plus_health(self, amount):
        self.max_health.plus(amount)
        if self.health > 0:
            self.health = min(self.health + amount, self.max_health.value)

    def minus_health(self, amount):
        self.max_health.minus(amount)
        self.health = min(self.max_health.value, self.health)

    def plus_power(self, amount):
        self.power.plus(amount)

    def minus_power(self, amount):
        self.power.minus(amount)

    def plus_speed(self, amount):
        self.speed.plus(amount)

    def minus_speed(self, amount):
        self.speed.minus(amount)

    def damage(self, amount, type = None):
        amount = self.type(type.id if type else None)(amount)
        self.health = max(0, self.health - amount)
        self.on.damage(self, amount = amount, type = type)
        if self.health == 0:
            self.on.death(self)

    def heal(self, amount):
        self.health = min(self.max_health.value, self.health + amount)
        self.on.heal(self, amount = amount)

    def kill(self):
        self.health = 0
        self.on.death(self)



###############################################################################
#   Battle Team
###############################################################################

class BattleTeam(object):
    def __init__(self, capacity, events):
        self.capacity = capacity
        self.units  = []
        self.grave  = []
        self.index  = -1
        self.on     = events
        for i in xrange(len(self.units)):
            self.units[i].team = self
            self.units[i].index = i

    @property
    def size(self):
        return len(self.units)

    @property
    def alive(self):
        return len(self.units) > 0

    @property
    def active(self):
        return self.units[0] if self.alive else None

    def at_left(self, unit = None, index = None):
        if len(self.units) < 2:
            return None
        unit = unit or self.units[0]
        index = self.units.index(unit) if index is None else index
        return self.units[index - 1]

    def at_right(self, unit = None, index = None):
        if len(self.units) < 2:
            return None
        unit = unit or self.units[0]
        index = self.units.index(unit) if index is None else index
        return self.units[(index + 1) % len(self.units)]

    @property
    def can_rotate(self):
        return len(self.units) > 1

    def rotate_left(self):
        u = self.units.pop(0)
        self.units.append(u)
        for i in xrange(len(self.units)):
            self.units[i].index = i
        self.on.rotate(self, active = self.active, previous = u)
        self.on.rotate_left(self, active = self.active, previous = u)

    def rotate_right(self):
        u = self.units.pop()
        self.units.insert(0, u)
        for i in xrange(len(self.units)):
            self.units[i].index = i
        self.on.rotate(self, active = self.active, previous = u)
        self.on.rotate_right(self, active = self.active, previous = u)

    def add_unit(self, unit):
        if len(self.units) < self.capacity:
            unit.index  = len(self.units)
            unit.team   = self
            self.units.append(unit)
            return True
        return False

    def kill(self, i):
        u = self.units.pop(i)
        self.grave.append(u)
        for j in xrange(i, len(self.units)):
            self.units[j].index = j
        u.kill()

    def cleanup(self):
        i = 0
        while i < len(self.units):
            if not self.units[i].alive:
                unit = self.units.pop(i)
                self.grave.append(unit)
                self.on.remove(self, unit = unit)
            else:
                self.units[i].index = i
                i += 1



###############################################################################
#   Battlefield
###############################################################################

class Battlefield(object):
    def __init__(self, teams = None):
        self.teams = teams or []
        self.terrain = "normal"



###############################################################################
#   Attribute
###############################################################################

class Attribute(object):
    def __init__(self, value):
        self.base = value
        self.bonus = 0

    @property
    def value(self):
        return max(1, self.base + self.bonus)

    def plus(self, amount):
        self.bonus += amount

    def minus(self, amount):
        self.bonus -= amount



###############################################################################
#   Species Type
###############################################################################

class UnitType(object):
    def __init__(self, id, name, resistances = None, weaknesses = None):
        self.id = id
        self.name = name
        self.resistances = resistances or []
        self.weaknesses = weaknesses or []

    def __call__(self, attacking_type):
        if attacking_type in self.resistances:
            return UnitType.multiplier_minus
        if attacking_type in self.weaknesses:
            return UnitType.multiplier_plus
        return UnitType.multiplier_normal

    @staticmethod
    def multiplier_plus(amount):
        return int(amount + amount / 2)

    @staticmethod
    def multiplier_minus(amount):
        return int(amount - amount / 3)

    @staticmethod
    def multiplier_normal(amount):
        return int(amount)



###############################################################################
#   Abilities
###############################################################################

class Ability(object):
    def __init__(self, id, name, description = "No description.",
                 effects = None):
        self.id             = id
        self.name           = name
        self.description    = description
        self.effects        = effects or []
        for effect in self.effects:
            effect.ability = self


class AbilityEffect(object):
    def __init__(self, mechanic, target, events, ability = None, parameters = None):
        self.ability    = ability
        self.mechanic   = mechanic
        self.target     = target
        self.events     = events
        self.parameters = parameters
