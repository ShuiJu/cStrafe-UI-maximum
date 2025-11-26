# main.py
import sys
import argparse
import threading
import os
import signal
from input_events import InputListener
from overlay import Overlay

# 导入托盘图标相关库
try:
    import pystray
    from PIL import Image
except ImportError:
    print("警告: 未安装 pystray 或 Pillow，托盘图标功能不可用。")
    pystray = None
    Image = None

# main.py (修改 resource_path 函数)
def resource_path(relative_path):
    """获取资源绝对路径，用于 Nuitka 打包"""
    try:
        # 对于 Nuitka 打包，使用模块目录
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def create_tray_icon():
    """创建托盘图标"""
    if pystray is None:
        return None
    
    icon_path = resource_path("cs-icon.png")
    try:
        image = Image.open(icon_path)
        print(f"成功加载图标: {icon_path}")
    except Exception as e:
        print(f"加载图标失败: {e}，使用默认图标")
        # 生成一个简单的默认图标
        image = Image.new('RGB', (16, 16), color='red')
    
    menu = pystray.Menu(pystray.MenuItem("退出", lambda icon, item: os.kill(os.getpid(), signal.SIGINT)))
    icon = pystray.Icon("cStrafe", image, "cStrafe - 按右键退出", menu)
    return icon

def run_tray_icon():
    """在后台线程中运行托盘图标"""
    if pystray is None:
        return
    icon = create_tray_icon()
    if icon:
        icon.run()

def run_local_mode():
    overlay = Overlay()
    
    def on_shot(result):
        overlay.update_result(result)

    listener = InputListener(on_shot_callback=on_shot)
    listener.start()
    
    try:
        overlay.run()
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()

def run_server_mode():
    import server 
    
    print("Running Server Mode for OBS/Web.")
    print("Add 'Browser Source' in OBS: http://127.0.0.1:8000")
    print("Or open browser on another device: http://<PC_IP>:8000")
    server.start_server()

if __name__ == "__main__":
    # 启动托盘图标（后台线程）
    tray_thread = threading.Thread(target=run_tray_icon, daemon=True)
    tray_thread.start()

    parser = argparse.ArgumentParser()
    parser.add_argument("--server", action="store_true")
    args = parser.parse_args()

    exe_name = sys.argv[0].lower()
    
    if args.server or "server" in exe_name:
        run_server_mode()
    else:
        run_local_mode()
