from .models import UnitTemplate, UnitInstance, UnitType, Ability, AbilityEffect
from .mechanics import BattleEngine

###############################################################################
# Data creation

print "Creating engine..."

action = "attack"

engine = BattleEngine()

def action_callback(engine):
    print "> Engine requesting action."
    engine.set_action(action, 0)

engine.on.request_input.sub(action_callback)

print "> OK"
print "Creating data..."

types = {
    "dummy": UnitType("Dummy Type"),
    "normal": UnitType("Normal"),
    "resistant": UnitType("Resistant", resistances = ("Dummy Type",)),
    "weak": UnitType("Weak", weaknesses = ("Dummy Type",))
}

abilities = {
    "none": Ability("none", "Do Nothing"),
    "log": Ability("log", "Log Ability",
                   effects = (AbilityEffect("log", "self", ("self attack", "opponent defend")),))
}

species = {
    "dummy": UnitTemplate("dummy", "Target Dummy", types["dummy"],
                          20, 10, 10, (abilities["none"],), ""),
    "normal": UnitTemplate("normal", "Normal Tester", types["normal"],
                          20, 10, 12, (), ""),
    "resistant": UnitTemplate("resistant", "Resistant Tester", types["resistant"],
                          20, 10, 12, (), ""),
    "weak": UnitTemplate("weak", "Weak Tester", types["weak"],
                          20, 10, 12, (), ""),
    "logger": UnitTemplate("logger", "Logger", types["normal"],
                          10, 10, 12, (abilities["log"],), "")
}

dummy = (UnitInstance(species["dummy"]),)

print "> OK"

###############################################################################
# Normal damage test

print "Testing for normal damage..."

unit = (UnitInstance(species["normal"]),)

engine.set_battle((unit, dummy))

assert len(engine.mechanics.teams) == 2
assert engine.mechanics.teams[0].size == 1
assert engine.mechanics.teams[1].size == 1
assert engine.mechanics.teams[0].active.max_health.value == 20
assert engine.mechanics.teams[0].active.power.value == 10
assert engine.mechanics.teams[0].active.speed.value == 12

assert engine.state == "start"
engine.step()
assert engine.state == "select_action"
engine.step()
assert engine.state == "attack"
engine.step()
assert engine.state == "between_rounds"
assert engine.mechanics.teams[0].alive
assert engine.mechanics.teams[1].alive
assert engine.mechanics.teams[0].active.health == 10
assert engine.mechanics.teams[1].active.health == 10

print "> OK"

###############################################################################
# Reduced damage test

print "Testing for reduced damage..."

unit = (UnitInstance(species["resistant"]),)

engine.set_battle((unit, dummy))

assert len(engine.mechanics.teams) == 2
assert engine.mechanics.teams[0].size == 1
assert engine.mechanics.teams[1].size == 1

assert engine.state == "start"
engine.step()
assert engine.state == "select_action"
engine.step()
assert engine.state == "attack"
engine.step()
assert engine.state == "between_rounds"
assert engine.mechanics.teams[0].alive
assert engine.mechanics.teams[1].alive
assert engine.mechanics.teams[0].active.health == 20 - (10 - 10 // 3)
assert engine.mechanics.teams[1].active.health == 10

print "> OK"

###############################################################################
# Increased damage test

print "Testing for increased damage..."

unit = (UnitInstance(species["weak"]),)

engine.set_battle((unit, dummy))

assert len(engine.mechanics.teams) == 2
assert engine.mechanics.teams[0].size == 1
assert engine.mechanics.teams[1].size == 1

assert engine.state == "start"
engine.step()
assert engine.state == "select_action"
engine.step()
assert engine.state == "attack"
engine.step()
assert engine.state == "between_rounds"
assert engine.mechanics.teams[0].alive
assert engine.mechanics.teams[1].alive
assert engine.mechanics.teams[0].active.health == 20 - (10 + 10 // 2)
assert engine.mechanics.teams[1].active.health == 10

print "> OK"

###############################################################################
# Logging ability test

print "Testing logging ability..."

unit = (UnitInstance(species["logger"]),)

engine.set_battle((unit, dummy))

assert len(engine.mechanics.teams) == 2
assert engine.mechanics.teams[0].size == 1
assert engine.mechanics.teams[1].size == 1

assert engine.state == "start"
engine.step()
assert engine.state == "select_action"
engine.step()
assert engine.state == "attack"
engine.step()
assert engine.state == "end"
assert not engine.mechanics.teams[0].alive
assert engine.mechanics.teams[1].alive
assert engine.mechanics.teams[0].active is None
assert engine.mechanics.teams[1].active.health == 10
assert len(engine.mechanics.teams[0].grave) == 1
assert len(engine.mechanics.abilities) == 0

print "> OK"

###############################################################################
# Clockwise rotation test

print "Testing clockwise rotation..."

action = "rotate_clock"

unit = (UnitInstance(species["resistant"]), UnitInstance(species["weak"]),
        UnitInstance(species["normal"]))

engine.set_battle((unit, dummy))

assert len(engine.mechanics.teams) == 2
assert engine.mechanics.teams[0].size == 3
assert engine.mechanics.teams[1].size == 1
assert engine.mechanics.teams[0].active.template.id == "resistant"

assert engine.state == "start"
engine.step()
assert engine.state == "select_action"
engine.step()
assert engine.state == "attack"
assert engine.mechanics.teams[0].active.template.id == "normal"
engine.step()
assert engine.state == "between_rounds"
assert engine.mechanics.teams[0].alive
assert engine.mechanics.teams[1].alive
assert engine.mechanics.teams[0].active.health == 10
assert engine.mechanics.teams[1].active.health == 10

print "> OK"
action = "attack"

###############################################################################
# Counter-clockwise rotation test

print "Testing counter-clockwise rotation..."

action = "rotate_counter"

unit = (UnitInstance(species["resistant"]), UnitInstance(species["normal"]),
        UnitInstance(species["weak"]))

engine.set_battle((unit, dummy))

assert len(engine.mechanics.teams) == 2
assert engine.mechanics.teams[0].size == 3
assert engine.mechanics.teams[1].size == 1
assert engine.mechanics.teams[0].active.template.id == "resistant"

assert engine.state == "start"
engine.step()
assert engine.state == "select_action"
engine.step()
assert engine.state == "attack"
assert engine.mechanics.teams[0].active.template.id == "normal"
engine.step()
assert engine.state == "between_rounds"
assert engine.mechanics.teams[0].alive
assert engine.mechanics.teams[1].alive
assert engine.mechanics.teams[0].active.health == 10
assert engine.mechanics.teams[1].active.health == 10

print "> OK"
action = "attack"
