from machine import Pin, PWM
import time

class Buzzer:
    def __init__(self):
        self.buzzer = PWM(Pin(13))
        self.tones = [262, 294, 330, 349, 392, 440, 494]  # C4, D4, E4, F4, G4, A4, B4
        self.buzzer.duty(0)

    def play_tone(self, frequency, duration=0.5):
        self.buzzer.freq(frequency)
        self.buzzer.duty(100)
        time.sleep(duration)
        self.buzzer.duty(0)
        time.sleep(0.3)

    def play_sequence(self, sequence):
        for frequency in sequence:
            self.play_tone(frequency)
