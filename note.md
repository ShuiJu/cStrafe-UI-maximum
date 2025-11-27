python -m nuitka --standalone --onefile --windows-console-mode=disable --enable-plugin=tk-inter --include-package=pynput --include-package=pystray --include-package=PIL --include-package=PIL.Image --include-package=PIL.ImageDraw --include-data-files=./cs-icon.png=cs-icon.png --output-filename=cStrafe_Local.exe main.py

python -m nuitka --standalone --onefile --windows-console-mode=force --include-package=pynput --include-package=fastapi --include-package=uvicorn --include-package=websockets --output-filename=cStrafe_Server.exe main.py

For OBS

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
    background-color: rgba(0, 0, 0, 0) !important; /* 容器背景也设为透明 */
}
.line { 
    font-size: 32px; 
    white-space: pre; 
    line-height: 1.2;
}
.hidden { display: none; }

