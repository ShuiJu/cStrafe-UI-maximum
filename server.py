# server.py
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json
import asyncio
from input_events import InputListener
from classifier import ShotResult

app = FastAPI()

# 修改 HTML 模板，确保跑打状态显示急停数据
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
    <head>
        <title>cStrafe HUD</title>
        <style>
            body { 
                background-color: #000000;
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
                background-color: #000000;
            }
            .line { 
                font-size: 40px;
                white-space: pre; 
                line-height: 1.2;
            }
            .hidden { display: none; }
        </style>
    </head>
    <body>
        <div id="container">
            <div id="line1" class="line" style="color: white;">Waiting...</div>
            <div id="line2" class="line" style="color: white;"></div>
            <div id="line3" class="line" style="color: white;"></div>
        </div>
        <script>
            var ws = new WebSocket("ws://" + location.host + "/ws");
            var container = document.getElementById("container");
            var l1 = document.getElementById("line1");
            var l2 = document.getElementById("line2");
            var l3 = document.getElementById("line3");

            ws.onmessage = function(event) {
                var data = JSON.parse(event.data);
                
                // 设置所有行的颜色
                l1.style.color = data.color;
                l2.style.color = data.color;
                l3.style.color = data.color;

                if (data.type === "Run&Gun") {
                    l1.innerText = "RUN & GUN";
                    if (data.diff !== null && data.delay !== null) {
                        // 显示急停数据：时间差和射击延迟
                        l2.innerText = "Stop Diff    " + data.diff + " ms";
                        l3.innerText = "Shot Delay   " + data.delay + " ms";
                    } else {
                        // 没有急停数据，清空第二行和第三行
                        l2.innerText = "";
                        l3.innerText = "";
                    }
                } else if (data.type === "Static") {
                    l1.innerText = "STATIC";
                    l2.innerText = "";
                    l3.innerText = "";
                } else {
                    // Overlap 或 EarlyRelease
                    var label = (data.type === "Overlap") ? "Overlap" : "Gap";
                    l1.innerText = label + "    " + data.diff + " ms";
                    l2.innerText = "Shot Delay   " + data.delay + " ms";
                    l3.innerText = ""; // 第三行留空
                }
            };
            
            ws.onclose = function() {
                setTimeout(function() {
                    location.reload();
                }, 1000);
            };
        </script>
    </body>
</html>
"""

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(data))

manager = ConnectionManager()

listener = None

@app.get("/")
async def get():
    return HTMLResponse(HTML_TEMPLATE)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def broadcast_shot(result: ShotResult):
    # 添加调试输出，便于检查数据
    # print(f"Debug: Broadcasting shot result - {result.to_display_data()}")
    if manager:
        asyncio.run_coroutine_threadsafe(
            manager.broadcast(result.to_display_data()), 
            loop
        )

loop = None

def start_server():
    global loop, listener
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    listener = InputListener(on_shot_callback=broadcast_shot)
    listener.start()
    
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    try:
        loop.run_until_complete(server.serve())
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()

if __name__ == "__main__":
    start_server()
