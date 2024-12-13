from machine import Pin, I2C
from sh1106 import SH1106_I2C

class OledDisplay:
    def __init__(self):
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        self.oled = SH1106_I2C(128, 64, self.i2c)

    def display_text(self, text, x=0, y=0):
        self.oled.text(text, x, y)
        self.oled.show()

    def clear_screen(self):
        self.oled.fill(0)
        self.oled.show()
        
    def clear_area(self, x, y, width, height):
        for i in range(x, x + width):
            for j in range(y, y + height):
                self.oled.pixel(i, j, 0)  # Nastav pixel na černou
        self.oled.show()
        

    def text(self, text, x, y, color=1):
        """Zobrazí text s danou barvou (1 = svítí, 0 = nesvítí)."""
        if color == 0:
            self.oled.fill_rect(x, y, len(text) * 8, 10, 0)  # Vymaž místo pro text
        self.oled.text(text, x, y, color)
        self.oled.show()
        
    def display_menu(self, menu_items, selected_index):
        """
        Zobrazuje menu na OLED displeji.
        """
        self.oled.fill(0)  # Vyčistí obrazovku
        for i, item in enumerate(menu_items):
            if i == selected_index:
                self.oled.text("> " + item, 0, i * 10)  # Označení vybraného
            else:
                self.oled.text(item, 10, i * 10)
        self.oled.show()
        
    def highlight_sequence(self, user_sequence, correct_sequence, color):
        """
        Zvýrazní sekvenci na displeji. Správné zeleně, špatné červeně.
        """
        x_pos = 0
        y_pos = 20
        for i, user_key in enumerate(user_sequence):
            correct = (user_key == correct_sequence[i])
            self.text(f"S{user_key}", x_pos, y_pos, color=1 if correct else 0)  # Zelená nebo červená
            x_pos += 16
            if x_pos > 128:
                x_pos = 0
                y_pos += 10
        
    def draw_heart(self, x, y):
        """
        Nakreslí jednoduché srdíčko na displej.
        """
        self.oled.pixel(x, y, 1)
        self.oled.pixel(x + 1, y - 1, 1)
        self.oled.pixel(x + 2, y - 1, 1)
        self.oled.pixel(x + 3, y, 1)
        self.oled.pixel(x + 3, y + 1, 1)
        self.oled.pixel(x + 2, y + 2, 1)
        self.oled.pixel(x + 1, y + 2, 1)
        self.oled.pixel(x, y + 1, 1)

