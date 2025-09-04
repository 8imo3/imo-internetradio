import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import time

class OledDisplay:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
        self.oled.fill(0)
        self.oled.show()
        self.font = ImageFont.load_default()

    def display_text(self, text):
        self.oled.fill(0)
        image = Image.new("1", (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)
        # Többsoros megjelenítéshez itt lehet sorokra bontani, de egyszerű verzió
        draw.text((0, 0), text, font=self.font, fill=255)
        self.oled.image(image)
        self.oled.show()
