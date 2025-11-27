# overlay.py
import tkinter as tk
from typing import Optional
from classifier import ShotResult

class Overlay:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("cStrafe Local")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.85) #稍微透明一点
        
        self.frame = tk.Frame(self.root, bg="#202020", bd=0)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.font_name = "Courier New"
        self.font_size = 14
        self.font_weight = "bold"

        # 主显示标签 (多行)
        self.label = tk.Label(
            self.frame,
            text="Waiting...",
            fg="white",
            bg="#202020",
            font=(self.font_name, self.font_size, self.font_weight),
            justify=tk.LEFT,
            padx=10,
            pady=5
        )
        self.label.pack()

        # 拖动逻辑
        self.root.bind("<ButtonPress-1>", self._on_drag_start)
        self.root.bind("<B1-Motion>", self._on_drag_move)
        self._drag_data = {"x": 0, "y": 0}

    def _on_drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag_move(self, event):
        x = self.root.winfo_x() - self._drag_data["x"] + event.x
        y = self.root.winfo_y() - self._drag_data["y"] + event.y
        self.root.geometry(f"+{x}+{y}")

    def update_result(self, result: ShotResult) -> None:
        lines = []
        if result.state_type == "Run&Gun":
            lines.append("RUN & GUN")
            # 如果有急停数据，显示时间差和射击延迟
            if result.time_diff is not None and result.shot_delay is not None:
                lines.append(f"{'Stop Diff': <10} {int(result.time_diff)} ms")
                lines.append(f"{'Shot Delay': <10} {int(result.shot_delay)} ms")
        elif result.state_type == "Static":
            lines.append("STATIC / IDLE")
        else:
            # Overlap 或 EarlyRelease
            type_text = "Overlap" if result.state_type == "Overlap" else "Gap"
            lines.append(f"{type_text: <10} {int(result.time_diff)} ms")
            lines.append(f"{'Shot Delay': <10} {int(result.shot_delay)} ms")

        final_text = "\n".join(lines)
        
        # 更新颜色和文本
        self.root.after(0, lambda: self._apply_ui(final_text, result.color_hex))

    def _apply_ui(self, text, color):
        self.label.config(text=text, fg=color)
        # 边框颜色也可以跟着变，如果想更明显
        self.frame.config(bg="#202020") 

    def run(self) -> None:
        self.root.mainloop()
