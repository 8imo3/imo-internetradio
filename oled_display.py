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

    def display_status(self, channel, is_playing, volume=None):
       self.oled.fill(0)
       image = Image.new("1", (self.oled.width, self.oled.height))
       draw = ImageDraw.Draw(image)

       import os
       base_dir = os.path.dirname(os.path.abspath(__file__))
       font_path = os.path.join(base_dir, "DejaVuSans.ttf")

       large_font = ImageFont.truetype(font_path, 18)
       small_font = ImageFont.truetype(font_path, 12)

       # Csatorna név középre igazítása
       bbox = draw.textbbox((0, 0), channel, font=large_font)
       text_width = bbox[2] - bbox[0]
       x = (self.oled.width - text_width) // 2
       draw.text((x, 0), channel, font=large_font, fill=255)

       # Ha megadták a volume-t, akkor kiírjuk
       if volume is not None:
           vol_text = f"Vol: {volume}%"
           bbox_vol = draw.textbbox((0, 0), vol_text, font=small_font)
           vol_x = (self.oled.width - (bbox_vol[2] - bbox_vol[0])) // 2
           draw.text((vol_x, 20), vol_text, font=small_font, fill=255)

       # Állapot megjelenítése Play vagy Stop (mindig kiírjuk)
       status = "Play" if is_playing else "Stop"
       bbox_status = draw.textbbox((0, 0), status, font=small_font)
       status_x = (self.oled.width - (bbox_status[2] - bbox_status[0])) // 2
       y_status = 40 if volume is not None else 20  # Ha nincs volume, akkor magasabbra tesszük
       draw.text((status_x, y_status), status, font=small_font, fill=255)

       self.oled.image(image)
       self.oled.show()

    def display_error(self, message):
       self.oled.fill(0)
       image = Image.new("1", (self.oled.width, self.oled.height))
       draw = ImageDraw.Draw(image)

       import os
       base_dir = os.path.dirname(os.path.abspath(__file__))
       font_path = os.path.join(base_dir, "DejaVuSans.ttf")
       font = ImageFont.truetype(font_path, 16)

       bbox = draw.textbbox((0, 0), message, font=font)
       x = (self.oled.width - (bbox[2] - bbox[0])) // 2
       y = (self.oled.height - (bbox[3] - bbox[1])) // 2
       draw.text((x, y), message, font=font, fill=255)
       self.oled.image(image)
       self.oled.show()       

    def display_wifi_reconnecting(self, stop_event):
       # A villogást kezelő loop, stop_event jelzéssel áll le
       blink = True
       while not stop_event.is_set():
           image = Image.new("1", (self.oled.width, self.oled.height))
           draw = ImageDraw.Draw(image)

           # Megjelenítjük a jelenlegi státuszt (play/stop), ezt átveheted display_statusból is, de egyszerűsítve ideírjuk
           # Példa: Stop vagy Play a kijelzőn
           # Ha szükséges, paraméterként add át az aktuális állapotot és jelenítsd meg itt
           # Itt csak a WiFi reconnecting villog

           # Csak a "WiFi reconnecting" szöveg villogását megjelenítjük 40 ill 52 pont magasan, hogy a stop/play alatti terület maradjon szabadon
           if blink:
               font = self.font
               text = "WiFi reconnecting"
               bbox = draw.textbbox((0, 0), text, font=font)
               x = (self.oled.width - (bbox[2] - bbox[0])) // 2
               y = 52
               draw.text((x, y), text, font=font, fill=255)


       self.oled.image(image)
       self.oled.show()
       blink = not blink
       time.sleep(0.7)  # Villogási sebesség