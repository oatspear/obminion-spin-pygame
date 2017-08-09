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


class Spritesheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pg.image.load(filename).convert_alpha()
        except pg.error, message:
            print "Unable to load spritesheet image: " + filename
            raise SystemExit, message

    def image_at(self, rectangle, colorkey = None):
        rect = pg.Rect(rectangle)
        image = pg.Surface(rect.size, pg.SRCALPHA, 32).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        if not colorkey is None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pg.RLEACCEL)
        return image

    def images_at(self, rectangles, colorkey = None):
        return [self.image_at(rect, colorkey) for rect in rectangles]

    def load_strip(self, rect, image_count, margin = 0, colorkey = None):
        tups = [(rect[0] + (rect[2] + margin) * x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)



class ImageSequence(object):
    def __init__(self, spritesheet, rectangle, image_count, delays,
                 margin = 0, colorkey = None):
        if isinstance(delays, (int, long, float)):
            delays = [delays for n in xrange(image_count)]
        elif len(delays) < image_count:
            last = delays[-1]
            delays.extend([last for n in xrange(image_count - len(delays))])
        self.images = spritesheet.load_strip(rectangle, image_count,
                                        margin = margin, colorkey = colorkey)
        self.delays = delays
        self.elapsed = 0
        self.changed = False
        self.loops = 0
        self._i = 0

    @property
    def sprite(self):
        return self.images[self._i]

    @property
    def duration(self):
        return sum(self.delays)

    def reset(self):
        self.changed = False
        self.elapsed = 0
        self.loops = 0
        self._i = 0

    def update(self, dt):
        self.changed = False
        self.elapsed += dt
        while self.elapsed >= self.delays[self._i]:
            i = self._i
            self.changed = True
            self.elapsed -= self.delays[self._i]
            self._i = (self._i + 1) % len(self.delays)
            if i > self._i:
                self.loops += 1



class MultiPoseSprite(object):
    def __init__(self):
        self.sprites = {}
        self.current = None
        self._sprite = None

    @property
    def sprite(self):
        return self._sprite.sprite

    @property
    def image_sequence(self):
        return self._sprite

    def add_sprite(self, name, sprite):
        self.sprites[name] = sprite

    def set_sprite(self, name):
        assert name in self.sprites
        if name != self.current:
            self.current = name
            self._sprite = self.sprites[name]
            self._sprite.reset()

    def update(self, dt):
        self._sprite.update(dt)
