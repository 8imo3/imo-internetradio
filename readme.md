# Additional Programs Installed

This document lists the extra system packages and Python libraries installed to support the Raspberry Pi Internet Radio project and its OLED display functionality.

## System Packages

These packages were installed via `apt` to support hardware interaction, audio playing, and font management:

- **python3-pip**, **python3-dev**, **python3-venv**  
  Essential Python tools for virtual environments, development headers, and package management.

- **fonts-dejavu**  
  Provides the DejaVuSans TrueType font used for rendering accented characters on the OLED display.

- **amixer (alsa-utils)**  
  Command-line audio mixer to adjust hardware volume levels.

- **mpg123**  
  Command-line MP3 player used for streaming internet radio channels.

## Python Packages (installed via pip)

Installed in a virtual environment to keep dependencies isolated:

- **adafruit-blinka**  
  Provides the CircuitPython hardware compatibility layer for accessing Raspberry Pi GPIO pins and buses.

- **adafruit-circuitpython-ssd1306**  
  Driver library for SSD1306 OLED displays.

- **adafruit-circuitpython-busdevice**  
  Provides hardware bus device abstractions needed by OLED drivers.

- **adafruit-circuitpython-requests**  
  CircuitPython-compatible requests library for HTTP communication.

- **pillow**  
  Python Imaging Library fork used for drawing text and shapes onto the OLED display.

## Notes

- The `fonts-dejavu` package is specifically needed to handle accented/multilingual characters on the OLED, as the default font only supports ASCII.

- The audio player `mpg123` is used via subprocess calls to stream radio URLs.

- Virtual environments are recommended to avoid polluting the global Python installation with project-specific packages.

---

This list ensures the project has all necessary dependencies and makes it straightforward for new setups or future maintenance.

