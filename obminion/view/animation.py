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
# General Purpose Animations
###############################################################################

class Animation(object):
    def __init__(self, duration, delay, loop = False):
        self.duration = duration
        self.delay = delay
        self.loop = loop
        self.elapsed = 0.0
        self.started = False
        self.on_start = None
        self.on_end = None

    @property
    def done(self):
        if self.loop:
            return False
        return self.started and self.elapsed >= self.delay + self.duration

    def update(self, dt):
        self.elapsed += dt

    def draw(self, screen):
        pass


class BarLevelAnimation(object):
    def __init__(self, element, goal, rate, delay = 0.0):
        self.element = element
        self.goal = goal
        self.rate = rate    # % per second (e.g. 0.5 per second)
        self.delay = delay
        self.elapsed = 0.0
        self.started = False
        self.on_start = None
        self.on_end = None

    @property
    def done(self):
        return self.started and self.element.bar_level == self.goal

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed > self.delay and self.element.bar_level != self.goal:
            d = dt * self.rate
            if d > 0:
                value = min(self.element.bar_level + d, self.goal)
            else:
                value = max(self.element.bar_level + d, self.goal)
            self.element.bar_level = value

    def draw(self, screen):
        pass


class WriteAnimation(object):
    def __init__(self, element, text, rate, delay = 0.0):
        self.element = element
        self.text = text
        self.rate = rate    # char per second
        self.displayed = ""
        self.delay = delay
        self.elapsed = 0.0
        self.started = False
        self.on_start = None
        self.on_end = None

    @property
    def done(self):
        return self.started and len(self.displayed) == len(self.text)

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed > self.delay and len(self.displayed) != len(self.text):
            if self.rate <= 0:
                self.displayed = self.text
            else:
                t = self.elapsed - self.delay
                n = int(t * self.rate)
                if n > len(self.displayed):
                    self.displayed = self.text[:n]
                    self.element.set_text(self.displayed)

    def draw(self, screen):
        pass


class GetActionAnimation(object):
    def __init__(self, element):
        self.element = element
        self.action = None
        self.started = False
        self.on_start = self._on_start
        self.on_end = self._on_end

    @property
    def done(self):
        return not self.action is None

    def update(self, dt):
        if self.action is None:
            self.action = self.element.get_selected_action()

    def draw(self, screen):
        pass

    def _on_start(self, animation):
        self.element.set_active(True)

    def _on_end(self, animation):
        self.element.set_active(False)


class AnimatedSprite(Animation):
    def __init__(self, image_sequence, cx, cy,
                 duration = 0.0, delay = 0.0, loop = False, repeats = 0):
        Animation.__init__(self, duration, delay, loop = loop)
        image_sequence.reset()
        self.image_sequence = image_sequence
        self.cx = cx
        self.cy = cy
        self.rect = image_sequence.sprite.get_rect()
        self.rect.centerx = cx
        self.rect.centery = cy
        if duration == 0.0 and not loop:
            self.duration += (repeats + 1) * image_sequence.duration

    def update(self, dt):
        self.elapsed += dt
        if self.delay > 0.0:
            self.delay -= dt
            if self.delay < 0.0:
                dt = -self.delay
            else:
                return
        self.image_sequence.update(dt)
        if self.image_sequence.changed:
            self.rect = self.image_sequence.sprite.get_rect()
            self.rect.centerx = self.cx
            self.rect.centery = self.cy

    def draw(self, screen):
        if self.delay > 0.0:
            return
        screen.blit(self.image_sequence.sprite, self.rect)
        


###############################################################################
# Animation Queue
###############################################################################

class AnimationQueue(object):
    def __init__(self):
        self.queue = []
        self.current = None

    @property
    def busy(self):
        return not self.current is None

    def push(self, animation):
        if self.current is None:
            self.current = animation
            self.current.started = True
            if self.current.on_start:
                self.current.on_start(self.current)
        else:
            self.queue.append(animation)

    def cancel(self):
        if self.current and self.current.on_end:
            self.current.on_end(self.current)
        self._next()

    def cancel_all(self):
        while self.current:
            if self.current.on_end:
                self.current.on_end(self.current)
            self._next()

    def update(self, dt):
        if self.current is None:
            return
        if self.current.done:
            if self.current.on_end:
                self.current.on_end(self.current)
            self._next()
            if self.current is None:
                return
        self.current.update(dt)

    def draw(self, screen):
        if not self.current is None:
            self.current.draw(screen)


    def _next(self):
        if self.queue:
            self.current = self.queue.pop(0)
            self.current.started = True
            if self.current.on_start:
                self.current.on_start(self.current)
        else:
            self.current = None
