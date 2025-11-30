# cStrafe UI modified by ShuiJu, originally from CS2Kitchen

This is a lightweight training tool to help players practice counterstrafing mechanics in CS2. It listens to your movement keys (A/D for counter strafe detection, WASD for run & gun detection) and the left mouse button to classify your shooting behavior into states like Run & Gun, Overlap, Early Release, or Static. The tool supports two modes: **Local Overlay** (a transparent GUI overlay) and **Server Mode** (a web-based HUD for OBS and/or browser on phone).
Local:

![UI Preview](images/strafe_ui_1.avif)

OBS:
![UI Preview](images/strafe_ui_2.avif)


## Features

- Real-time analysis of movement and shooting inputs.
- Two operation modes:
  - **Local Mode**: Displays an overlay on your screen (uses Tkinter).
  - **Server Mode**: Provides a web interface for OBS Browser Source (uses FastAPI).
- Customizable overlay position and appearance.
- Compilable to standalone executables for easy distribution.

## Installation

### Prerequisites

- Python 3.7 or higher (if you encounter issues, try Python 3.13 from the Microsoft Store).
- Required Python packages:
  - `pynput` (for input listening)
  - `tkinter` (usually included with Python, for Local Mode GUI)
  - For Server Mode: `fastapi`, `uvicorn`, `websockets`
  - For tray icon (Local Mode): `pystray`, `Pillow` (PIL)

### Install Dependencies

Run the following command to install all required packages:

```bash
pip install -r requirements.txt
```

### Run from Source

- **Local Mode (Overlay)**:
  ```bash
  python main.py
  ```
  This starts the overlay GUI. You can drag it anywhere on the screen.

- **Server Mode (OBS HUD)**:
  ```bash
  python main.py --server
  ```
  This starts a web server at `http://127.0.0.1:8000`. Open this URL in OBS as a Browser Source.

### Compilation to Executable

You can compile the program to standalone executables using [Nuitka](https://nuitka.net/). This is optional but useful for distribution.

First, install Nuitka:
```bash
pip install nuitka
```

Then, compile for each mode:

- **Local Mode** (produces `cStrafe_Local.exe`):
  ```bash
  python -m nuitka --standalone --onefile --windows-console-mode=disable --enable-plugin=tk-inter --include-package=pynput --include-package=pystray --include-package=PIL --include-package=PIL.Image --include-package=PIL.ImageDraw --include-data-files=./cs-icon.png=cs-icon.png --output-filename=cStrafe_Local.exe main.py
  ```

- **Server Mode** (produces `cStrafe_Server.exe`):
  ```bash
  python -m nuitka --standalone --onefile --windows-console-mode=force --include-package=pynput --include-package=fastapi --include-package=uvicorn --include-package=websockets --output-filename=cStrafe_Server.exe main.py
  ```

Note: The `--include-data-files` flag ensures resources like `cs-icon.png` are bundled. Adjust file paths as needed.

## Usage

### Local Mode

When running in Local Mode, a transparent overlay window appears. It updates each time you fire the left mouse button. You can drag the overlay to reposition it. Make sure your game is in **fullscreen windowed mode** (it won’t work in exclusive fullscreen).

The overlay displays one of the following states after each shot:

- **Run & Gun**: You shot while moving. If a recent stop was detected, it shows the stop difference and shot delay.
- **Overlap**: You held both opposing movement keys (A and D) simultaneously before shooting. The overlap duration is shown.
- **Early Release**: You released one movement key and pressed the opposite key with a gap before shooting. The gap duration and shot delay are shown.
- **Static**: You shot without any recent movement change.

**Controls in Local Mode**:
- Drag the overlay to move it.
- Use the system tray icon (right-click) to exit the program.

### Server Mode (for OBS)

In Server Mode, the tool hosts a web-based HUD. To use it with OBS:

1. Run the server: `python main.py --server` or launch `cStrafe_Server.exe`.
2. In OBS, add a **Browser Source** with the URL: `http://127.0.0.1:8000`
3. Resize and position the source as needed, use following css style to overwrite.

For a transparent background in OBS, apply the following CSS to the Browser Source (right-click the source → Properties → Custom CSS):

```css
body { 
    background-color: rgba(0, 0, 0, 0) !important; 
    margin: 0; 
    overflow: hidden; 
    font-family: 'Courier New', monospace;
    font-weight: bold;
}
#container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    padding: 15px;
    text-shadow: 2px 2px 0px #000000;
    background-color: rgba(0, 0, 0, 0) !important;
}
.line { 
    font-size: 32px; 
    white-space: pre; 
    line-height: 1.2;
}
.hidden { display: none; }
```

## Classification Labels

| Label | Description |
|-------|-------------|
| **Run & Gun** | You fired while moving. It detects WASD for Run & Gun. If a stop occurred recently, the overlay shows timing data. |
| **Overlap** | You overlapped during A D key switching before shooting. Duration shown. |
| **Early Release** | You swapped movement keys with a gap before shooting. Gap and shot delay shown. |
| **Static** | No significant movement before the shot. You either is completely stopped for finishing counter strafe 500ms before shoot, or didn't swap A/D key press for counter strafe which it will not classify as a counter strafe. |

Colors: Green (good), Orange (acceptable), Red (poor/Run & Gun), Gray (static).

## Notes

- Designed for CS2; other games may behave differently.
- Fullscreen windowed mode required for overlay.
- Server mode can be accessed remotely using `http://<your_PC_IP>:8000`.
- It can not classify if when you shoot, your character model is actually stopped, so if you are fluent player, be assuming lots of Run & Gun shows on overlay. The mechanism is only defined by movement key and mouse key pressing. Fluent player will shoot when character movement speed is close enough to zero but at that point the movement key is not released yet. 
