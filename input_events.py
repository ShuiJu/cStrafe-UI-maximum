# input_events.py
import threading
import time
from typing import Optional, Callable
from pynput import keyboard, mouse
from classifier import MovementClassifier, ShotResult

class InputListener:
    def __init__(self, on_shot_callback: Callable[[ShotResult], None]) -> None:
        self.on_shot_callback = on_shot_callback
        self.classifier = MovementClassifier()
        self._lock = threading.Lock()
        self._keyboard_listener: Optional[keyboard.Listener] = None
        self._mouse_listener: Optional[mouse.Listener] = None
        self.running = False

    def start(self) -> None:
        self.running = True
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._keyboard_listener.start()
        self._mouse_listener = mouse.Listener(
            on_click=self._on_click,
        )
        self._mouse_listener.start()

    def stop(self) -> None:
        self.running = False
        if self._keyboard_listener:
            self._keyboard_listener.stop()
        if self._mouse_listener:
            self._mouse_listener.stop()

    def _on_key_press(self, key: keyboard.Key) -> None:
        timestamp = time.time() * 1000.0
        try:
            char = key.char.upper() if hasattr(key, 'char') and key.char else None
        except AttributeError:
            char = None

        if char in {"W", "A", "S", "D"}:
            with self._lock:
                self.classifier.on_press(char, timestamp)
        
        # 快捷键处理 (仅在 Local 模式下生效，通过回调扩展可以更灵活，这里简化处理)
        # 如果需要 F8 退出等功能，建议在 main 中处理，或者保留基本逻辑

    def _on_key_release(self, key: keyboard.Key) -> None:
        timestamp = time.time() * 1000.0
        try:
            char = key.char.upper() if hasattr(key, 'char') and key.char else None
        except AttributeError:
            char = None

        if char in {"W", "A", "S", "D"}:
            with self._lock:
                self.classifier.on_release(char, timestamp)

    def _on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        if button == mouse.Button.left and pressed:
            current_time = time.time() * 1000.0
            with self._lock:
                result = self.classifier.classify_shot(current_time)
            # 回调传出结果
            self.on_shot_callback(result)
