"""
Micropython MH-Z19 CO2 Sensor driver.
Source: https://github.com/overflo23/MH-Z19_MicroPython/blob/main/mhz19.py
Commit: 627bdc7d57e51582d7937f8465f1e0bf30cdb962
License:
MIT License
Copyright (c) 2020 der flo
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
from machine import UART
import time
import sys


class mhz19:
    def __init__(self,  uart_no):
        self.uart_no = uart_no
        self.start()
        self.ppm = 0
        self.temp = 0
        self.co2status = 0

    def start(self):
        self.uart = UART(self.uart_no, 9600)
        self.uart.init(9600, bits=8, parity=None, stop=1, timeout=10)

    def stop(self):
        while self.uart.any():
            self.uart.read(1)
        self.uart.deinit()

    def get_data(self):
        self.uart.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
        time.sleep(0.1)
        s = self.uart.read(9)
        try:
            z = bytearray(s)
        except:
            return 0
        # Calculate crc
        crc = self.crc8(s)
        if crc != z[8]:
            # we should restart the uart comm here..
            self.stop()
            time.sleep(1)
            self.start()

            print('CRC error calculated %d bytes= %d:%d:%d:%d:%d:%d:%d:%d crc= %dn' % (
                crc, z[0], z[1], z[2], z[3], z[4], z[5], z[6], z[7], z[8]))
            return 0
        else:
            self.ppm = ord(chr(s[2])) * 256 + ord(chr(s[3]))
            self.temp = ord(chr(s[4])) - 40
            self.co2status = ord(chr(s[5]))
            return 1

    def crc8(self, a):
        crc = 0x00
        count = 1
        b = bytearray(a)
        while count < 8:
            crc += b[count]
            count = count+1
        # Truncate to 8 bit
        crc %= 256
        # Invert number with xor
        crc = ~crc & 0xFF
        crc += 1
        return crc
