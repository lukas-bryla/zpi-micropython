from machine import Pin
import time

class Keypad:
    def __init__(self):
        self.rows = [Pin(26, Pin.OUT), Pin(27, Pin.OUT), Pin(14, Pin.OUT), Pin(12, Pin.OUT)]
        self.cols = [Pin(25, Pin.IN, Pin.PULL_DOWN), Pin(33, Pin.IN, Pin.PULL_DOWN), Pin(32, Pin.IN, Pin.PULL_DOWN), Pin(15, Pin.IN, Pin.PULL_DOWN)]

        self.key_map = [
            ['S1', 'S2', 'S3', 'S4'],
            ['S5', 'S6', 'S7', 'S8'],
            ['S9', 'S10', 'S11', 'S12'],
            ['S13', 'S14', 'S15', 'S16'],
        ]

    def scan(self):
        """
        Prohledává klávesnici a vrací stisknutou klávesu.
        """
        for row_idx, row_pin in enumerate(self.rows):
            row_pin.value(1)  # Activate row
            for col_idx, col_pin in enumerate(self.cols):
                if col_pin.value() == 1:  # Detect press
                    time.sleep(0.3)  # Debounce
                    return self.key_map[row_idx][col_idx]
            row_pin.value(0)  # Deactivate row
        return None
