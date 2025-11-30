　　# cStrafe UI by CS2Kitchen

　　This is the second project in this domain. The goal is to provide a simplified, lightweight training tool to help players practice counter-strafing mechanics in CS2. It listens to your movement keys (W, A, S, D) and mouse clicks to classify your shooting behavior into states such as Run & Gun, Overlap, Early Release, or Static.  
　　Two modes are supported: **Local Overlay Mode** and **Server Mode** (for OBS).

　　![UI Preview](images/strafe_ui_2.gif)

　　---

　　## Features

　　- Real-time classification of CS2 movement + shooting behaviors.
　　- Two operation modes:
　　- **Local Mode**: Transparent overlay (Tkinter-based).
　　- **Server Mode**: Web HUD for OBS (FastAPI-based).
　　- Customizable overlay appearance and position.
　　- Compilable into standalone `.exe` files via Nuitka.
　　- Supports tray icon for quick exit (Local Mode).

　　---

　　## Installation

　　### Prerequisites

　　- **Python 3.7+**  
　　If you encounter issues, try Python 3.13 from the Microsoft Store.
　　- Python packages:
　　- `pynput`
　　- `tkinter` (bundled with most Python installations)
　　- `fastapi`, `uvicorn`, `websockets` (for Server Mode)
　　- `pystray`, `Pillow` (for system tray support)

　　### Install dependencies

　　```bash
　　pip install pynput fastapi uvicorn websockets pystray Pillow