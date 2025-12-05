import obspython as obs
import subprocess
import platform
import ctypes
import time

# 全局变量
ip_address = "192.168.1.2"
source_name = "cstrafe"
online_interval = 10 * 60 * 1000  # 10分钟 (毫秒)
offline_interval = 60 * 1000  # 1分钟 (毫秒)
wait_before_refresh = 30000  # 30秒 (毫秒)
is_online = False  # 初始状态为离线
current_timer = None

# Windows虚拟键码
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt键
VK_NUMPAD0 = 0x60

def script_description():
    return """监控指定IP地址的在线状态。
    
功能:
- 初始状态为离线
- 在线状态时每10分钟检测一次IP地址
- 离线状态时每1分钟检测一次IP地址
- 当从离线变为在线时,等待30秒后刷新浏览器源
- 通过模拟热键 Ctrl+Alt+数字小键盘0 来刷新

配置:
- IP地址: 192.168.1.2
- 浏览器源名称: cstrafe
- 刷新热键: Ctrl+Alt+数字小键盘0"""

def check_ip_online():
    """检测IP是否在线"""
    try:
        system = platform.system()
        if system == "Windows":
            # 使用CREATE_NO_WINDOW标志隐藏CMD窗口
            CREATE_NO_WINDOW = 0x08000000
            result = subprocess.call(
                ["ping", "-n", "1", "-w", "1000", ip_address],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )
        else:
            result = subprocess.call(
                ["ping", "-c", "1", "-W", "1", ip_address],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        return result == 0
    except Exception as e:
        obs.script_log(obs.LOG_WARNING, f"Ping失败: {e}")
        return False

def send_hotkey():
    """发送Ctrl+Alt+数字小键盘0热键"""
    try:
        if platform.system() == "Windows":
            # 使用ctypes调用Windows API
            user32 = ctypes.windll.user32
            
            obs.script_log(obs.LOG_INFO, "模拟按下热键: Ctrl+Alt+Numpad0")
            
            # 按下Ctrl
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            time.sleep(0.05)
            
            # 按下Alt
            user32.keybd_event(VK_MENU, 0, 0, 0)
            time.sleep(0.05)
            
            # 按下数字小棋盘0
            user32.keybd_event(VK_NUMPAD0, 0, 0, 0)
            time.sleep(0.05)
            
            # 释放数字小棋盘0
            user32.keybd_event(VK_NUMPAD0, 0, 2, 0)
            time.sleep(0.05)
            
            # 释放Alt
            user32.keybd_event(VK_MENU, 0, 2, 0)
            time.sleep(0.05)
            
            # 释放Ctrl
            user32.keybd_event(VK_CONTROL, 0, 2, 0)
            
            obs.script_log(obs.LOG_INFO, "热键发送完成")
        else:
            obs.script_log(obs.LOG_WARNING, "此脚本仅支持Windows系统的热键模拟")
    except Exception as e:
        obs.script_log(obs.LOG_ERROR, f"发送热键失败: {e}")

def refresh_browser_source():
    """通过热键刷新浏览器源"""
    obs.script_log(obs.LOG_INFO, f"正在通过热键刷新浏览器源: {source_name}")
    send_hotkey()
    obs.script_log(obs.LOG_INFO, f"浏览器源刷新命令已发送: {source_name}")

def delayed_refresh():
    """延迟刷新的回调函数"""
    refresh_browser_source()
    obs.remove_current_callback()

def restart_timer():
    """根据当前在线状态重新启动定时器"""
    global current_timer
    
    # 移除现有的定时器
    if current_timer:
        obs.timer_remove(current_timer)
    
    # 根据在线状态设置不同的检测间隔
    if is_online:
        interval = online_interval
        current_timer = obs.timer_add(check_status, interval)
        obs.script_log(obs.LOG_DEBUG, f"已设置为在线状态检测间隔: {online_interval/1000/60}分钟")
    else:
        interval = offline_interval
        current_timer = obs.timer_add(check_status, interval)
        obs.script_log(obs.LOG_DEBUG, f"已设置为离线状态检测间隔: {offline_interval/1000}秒")

def check_status():
    """主检测逻辑"""
    global is_online
    
    current_online = check_ip_online()
    
    if current_online:
        if not is_online:
            # 从离线变为在线
            obs.script_log(obs.LOG_INFO, f"IP {ip_address} 状态变化: 离线 -> 在线, 30秒后将刷新")
            is_online = True
            # 启动延迟刷新定时器
            obs.timer_add(delayed_refresh, wait_before_refresh)
            # 重新启动主检测定时器（使用在线状态间隔）
            restart_timer()
        else:
            # 保持在线状态
            obs.script_log(obs.LOG_DEBUG, f"IP {ip_address} 保持在线状态")
    else:
        if is_online:
            # 从在线变为离线
            obs.script_log(obs.LOG_INFO, f"IP {ip_address} 状态变化: 在线 -> 离线")
            is_online = False
            # 重新启动主检测定时器（使用离线状态间隔）
            restart_timer()
        else:
            # 保持离线状态
            obs.script_log(obs.LOG_DEBUG, f"IP {ip_address} 保持离线状态")

def script_load(settings):
    """脚本加载时调用"""
    global is_online, current_timer
    
    obs.script_log(obs.LOG_INFO, "IP监控脚本已加载 (Python版)")
    
    # 初始状态为离线
    is_online = False
    obs.script_log(obs.LOG_INFO, "初始状态: 离线")
    
    # 立即执行首次检测
    check_status()

def script_unload():
    """脚本卸载时调用"""
    global current_timer
    
    if current_timer:
        obs.timer_remove(current_timer)
        current_timer = None
    
    # 移除所有延迟刷新定时器
    obs.timer_remove(delayed_refresh)
    obs.script_log(obs.LOG_INFO, "IP监控脚本已卸载")

def script_properties():
    """脚本属性"""
    props = obs.obs_properties_create()
    
    info_text = f"""当前配置:
- 监控IP: {ip_address}
- 浏览器源名称: {source_name}
- 在线检测间隔: 10分钟
- 离线检测间隔: 1分钟
- 刷新延迟: 30秒
- 初始状态: 离线

当前状态: {'在线' if is_online else '离线'}"""
    
    obs.obs_properties_add_text(props, "info", info_text, obs.OBS_TEXT_INFO)
    
    return props
