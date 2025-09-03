from flask import Flask, render_template_string, request, redirect, url_for
import subprocess
import threading
import time
import logging
import os
import RPi.GPIO as GPIO


APP_HOME = "/home/imo/git"
# 📂 Alkalmazás home mappa
APP_HOME = "/home/imo/git"

# 📂 Log könyvtár
LOG_DIR = os.path.join(APP_HOME, "log")
os.makedirs(LOG_DIR, exist_ok=True)

# 📄 Log fájl elérési út
LOG_FILE = os.path.join(LOG_DIR, "radio_buttons.log")


# 🔧 Logging beállítás
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)


app = Flask(__name__)

# 🔗 Csatornalista
channels = {
       "Petőfi Rádió": "https://icast.connectmedia.hu/4738/mr2.mp3",
       "Retró Rádió": "https://icast.connectmedia.hu/5001/live.mp3",
       "BDPST Rock": "https://bdpstrock.hu/live_320.mp3",
       "Rádió 1": "https://icast.connectmedia.hu/5201/live.mp3",
       "Rádio Szarvas": "http://91.82.85.44:1630/radioszarvas.mp3",
       "Dankó Rádió": "https://mr-stream.connectmedia.hu/4748/mr7.mp3",
       "Best FM": "http://stream.webthings.hu:8000/fm95-x-128.mp3",
       "Szakcsi Rádió": "https://mr-stream.connectmedia.hu/4691/mr9.mp3"
}

# 📦 Globális változók
current_channel = None
player_process = None
player_lock = threading.Lock()
volume_level = 32768  # érték: 0–32768,  kb.
DEFAULT_STREAM = "https://icast.connectmedia.hu/5001/live.mp3"


# ▶️ Lejátszó indítása hangerővel
def start_player(url, retries=5):
    global player_process
    attempt = 0
    while attempt < retries:
        try:
            with player_lock:
                if player_process:
                    player_process.terminate()
                    player_process.wait()
                player_process = subprocess.Popen(["mpg123", "-f", str(volume_level), url])
            break  # sikeres indítás
        except Exception as e:
            attempt += 1
            time.sleep(2)

# ⏹️ Lejátszó leállítása
def stop_player():
    global player_process
    with player_lock:
        if player_process:
            player_process.terminate()
            player_process.wait()
            player_process = None

def change_volume(direction):
    global volume_level
    if direction == "up":
        volume_level = min(volume_level + 2000, 32768)
    elif direction == "down":
        volume_level = max(volume_level - 2000, 0)

    # 💡 Hardveres hangerő (0–100%) állítása amixerrel
    percent = int(volume_level * 100 / 32768)
    subprocess.run(["amixer", "set", "PCM", f"{percent}%"], check=False)

    # újraindítjuk a lejátszót, hogy az új hangerő érvényesüljön szoftveresen is
    if current_channel:
        start_player(channels[current_channel])

def get_volume():
    return int(volume_level * 100 / 32768)

# 🌐 Főoldal
@app.route("/")
def index():
    vol = get_volume()
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Imó Internet Rádió</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: sans-serif;
            background: #222;
            color: #fff;
            text-align: center;
            padding: 1rem;
            font-size: 1.5rem;
        }
        h1 {
            font-size: 2.2rem;
            margin-bottom: 1rem;
        }
        select, button {
            font-size: 1.2rem;
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            border: none;
        }
        select {
            min-width: 60%;
        }
        button {
            background-color: #0af;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background-color: #08c;
        }
        form {
            margin: 1rem 0;
        }
        .channel-row {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.5rem;
        }
        @media(min-width: 500px) {
            .channel-row {
                flex-direction: row;
                justify-content: center;
            }
        }
        .vol-control {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 1rem;
            margin-top: 1rem;
        }
        .vol-control span {
            font-size: 1.5rem;
            min-width: 60px;
        }
    </style>
</head>
<body>
    <h1>Imó Internet Rádió</h1>

    <form method="post" action="/play" class="channel-row">
        <label for="channel">Jelenlegi csatorna:</label>
        <select id="channel" name="channel">
            {% for name in channels %}
                <option value="{{ name }}" {% if name == current %}selected{% endif %}>{{ name }}</option>
            {% endfor %}
        </select>
        <button type="submit">Lejátszás</button>
    </form>

    <form method="post" action="/stop" style="display: inline;">
        <button type="submit">Stop</button>
    </form>
    <form method="post" action="/next" style="display: inline; margin-left: 10px;">
        <button type="submit">Következő csatorna</button>
    </form>

    <h3>Hangerő</h3>
    <form method="post" action="/volume" class="vol-control">
        <button type="submit" name="dir" value="down">-</button>
        <span>{{ vol }}%</span>
        <button type="submit" name="dir" value="up">+</button>
    </form>
</body>
</html>
""", channels=channels.keys(), current=current_channel or "Nincs lejátszva", vol=vol)

# ▶️ Lejátszás csatorna szerint
@app.route("/play", methods=["POST"])
def play():
    global current_channel
    channel_name = request.form.get("channel")
    if channel_name in channels:
        start_player(channels[channel_name])
        current_channel = channel_name
    return redirect(url_for("index"))

# ⏹️ Stop gomb
@app.route("/stop", methods=["POST"])
def stop():
    stop_player()
    global current_channel
    current_channel = None
    return redirect(url_for("index"))

# 🔀 Következő csatorna
@app.route("/next", methods=["POST"])
def next_channel():
    global current_channel
    names = list(channels.keys())
    if current_channel and current_channel in names:
        idx = names.index(current_channel)
        next_idx = (idx + 1) % len(names)
    else:
        next_idx = 0
    current_channel = names[next_idx]
    start_player(channels[current_channel])
    return redirect(url_for("index"))

# 🔊 Volume +/- route
@app.route("/volume", methods=["POST"])
def volume():
    direction = request.form.get("dir")
    change_volume(direction)
    return redirect(url_for("index"))

def button_loop():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # belső felhúzó
    while True:
        if GPIO.input(17) == GPIO.LOW:  # gomb lenyomva
            logging.info("Gombnyomás: következő csatorna")

            # csatornaváltás
            global current_channel
            names = list(channels.keys())
            if current_channel and current_channel in names:
                idx = names.index(current_channel)
                next_idx = (idx + 1) % len(names)
            else:
                next_idx = 0
            current_channel = names[next_idx]
            start_player(channels[current_channel])
            logging.info(f"Csatorna váltva: {current_channel}")

            # várjunk, amíg elengeded a gombot (debounce)
            while GPIO.input(17) == GPIO.LOW:
                time.sleep(0.1)

        time.sleep(0.1)


if __name__ == "__main__":
    import time

    # Kis késleltetés, hogy biztos legyen, minden inicializálva
    def start_default():
        global current_channel
        time.sleep(1)
        # 💡 Hardveres hangerő beállítása induláskor is
        percent = int(volume_level * 100 / 32768)
        subprocess.run(["amixer", "set", "PCM", f"{percent}%"], check=False)

        start_player(DEFAULT_STREAM)
        current_channel = "Retró Rádió"

    threading.Thread(target=start_default, daemon=True).start()
    threading.Thread(target=button_loop, daemon=True).start()

    # Majd indítsuk el a web UI-t
    app.run(host="0.0.0.0", port=8080)