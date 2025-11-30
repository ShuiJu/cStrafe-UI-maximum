# classifier.py
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Set

@dataclass
class KeyState:
    press_time: float = 0.0
    release_time: float = 0.0
    is_held: bool = False

@dataclass
class ShotResult:
    # 状态类型: "Run&Gun", "Overlap", "EarlyRelease", "Static"
    state_type: str
    # 颜色代码
    color_hex: str
    # 数据
    time_diff: Optional[float] = None # Overlap 或 Gap 的时间
    shot_delay: Optional[float] = None # 停稳到开枪的时间
    
    def to_display_data(self) -> dict:
        """转换为前端/UI易读的字典格式"""
        return {
            "type": self.state_type,
            "color": self.color_hex,
            "diff": int(self.time_diff) if self.time_diff is not None else None,
            "delay": int(self.shot_delay) if self.shot_delay is not None else None
        }

class MovementClassifier:
    def __init__(self) -> None:
        self.keys: Dict[str, KeyState] = {
            "W": KeyState(), "A": KeyState(), "S": KeyState(), "D": KeyState()
        }
        # 记录最近的一次反向操作 (Key, Time)
        self.last_transition_time: float = 0.0
        self.last_transition_type: str = "None" # "Overlap" or "Gap"
        self.last_transition_diff: float = 0.0 # 具体的毫秒数

    def on_press(self, key: str, timestamp: float) -> None:
        if key not in self.keys: return
        
        # 记录按下
        self.keys[key].press_time = timestamp
        self.keys[key].is_held = True

        # 检测水平方向的急停逻辑 (A/D)
        if key in ("A", "D"):
            opposite = "D" if key == "A" else "A"
            opp_state = self.keys[opposite]
            
            # 场景1：按下新键时，旧键还没松开 -> Overlap 开始
            # 真正的 Overlap 结算要在旧键松开时计算，但这里标记状态
            pass 
            
            # 场景2：按下新键时，旧键已经松开 -> Gap (Early Release) 结束
            if not opp_state.is_held and (timestamp - opp_state.release_time) < 300: # 300ms内的操作视为急停意图
                self.last_transition_type = "EarlyRelease"
                self.last_transition_diff = timestamp - opp_state.release_time # Gap duration
                self.last_transition_time = timestamp # 以按下的时间为“完成急停”的时间点

    def on_release(self, key: str, timestamp: float) -> None:
        if key not in self.keys: return
        
        self.keys[key].release_time = timestamp
        self.keys[key].is_held = False

        # 检测水平方向的 Overlap 结算
        if key in ("A", "D"):
            opposite = "D" if key == "A" else "A"
            opp_state = self.keys[opposite]
            
            # 场景：松开旧键时，新键已经按下了 -> Overlap 结束
            if opp_state.is_held:
                # Overlap duration = Release Time - Opp Press Time
                # 注意：如果一直按着两个键，这里也会触发，但 shot 逻辑会判定为跑打
                overlap = timestamp - opp_state.press_time
                if overlap > 0: # 正常的重叠
                    self.last_transition_type = "Overlap"
                    self.last_transition_diff = overlap
                    self.last_transition_time = timestamp # 以松开的时间为“完成急停”的时间点

    def classify_shot(self, shot_time: float) -> ShotResult:
        is_run_gun = self.keys["A"].is_held or self.keys["D"].is_held
        has_recent_stop = (shot_time - self.last_transition_time) < 500

        if is_run_gun:
            # 跑打状态
            if has_recent_stop:
                # 有近期急停，显示急停数据
                shot_delay = shot_time - self.last_transition_time
                return ShotResult("Run&Gun", "#ff4444", self.last_transition_diff, shot_delay)
            else:
                # 没有近期急停，只显示跑打
                return ShotResult("Run&Gun", "#ff4444")
        else:
            # 非跑打状态
            if has_recent_stop:
                shot_delay = shot_time - self.last_transition_time
                time_diff_abs = abs(self.last_transition_diff)
                if time_diff_abs <= 20:
                    color = "#228b22"  # 绿色
                else:
                    color = "#ff8c00"  # 橙色
                return ShotResult(self.last_transition_type, color, self.last_transition_diff, shot_delay)
            else:
                # 静态射击
                return ShotResult("Static", "#888888")
