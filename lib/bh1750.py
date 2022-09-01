"""
Micropython BH1750 ambient light sensor driver.
Source: https://github.com/PinkInk/iocp/blob/master/sensor-bh1750-bme280-hygrometer/lib/bh1750/__init__.py
Commit: c8ecb818514fce7337b60f6d1e78e6449f3d602e
License: 
MIT License
Copyright (c) 2017 Tim Pelling (tim.pelling@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from utime import sleep_ms

class BH1750():
    """Micropython BH1750 ambient light sensor driver."""

    PWR_OFF = 0x00
    PWR_ON = 0x01
    RESET = 0x07

    # modes
    CONT_LOWRES = 0x13
    CONT_HIRES_1 = 0x10
    CONT_HIRES_2 = 0x11
    ONCE_HIRES_1 = 0x20
    ONCE_HIRES_2 = 0x21
    ONCE_LOWRES = 0x23

    # default addr=0x23 if addr pin floating or pulled to ground
    # addr=0x5c if addr pin pulled high
    def __init__(self, bus, addr=0x23):
        self.bus = bus
        self.addr = addr
        self.off()
        self.reset()

    def off(self):
        self.set_mode(self.PWR_OFF)

    def on(self):
        self.set_mode(self.PWR_ON)

    def reset(self):
        self.on()
        self.set_mode(self.RESET)

    def set_mode(self, mode):
        self.mode = mode
        self.bus.writeto(self.addr, bytes([self.mode]))

    def luminance(self, mode):
        # continuous modes
        if mode & 0x10 and mode != self.mode:
            self.set_mode(mode)
        # one shot modes
        if mode & 0x20:
            self.set_mode(mode)
        # earlier measurements return previous reading
        sleep_ms(24 if mode in (0x13, 0x23) else 180)
        data = self.bus.readfrom(self.addr, 2)
        factor = 2.0 if mode in (0x11, 0x21) else 1.0
        return (data[0]<<8 | data[1]) / 1.2 / factor
