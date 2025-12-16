import subprocess
import threading
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

ADB = "adb.exe"

DEVICES = [
    # first 5 (near mr hays desk)
    # add true to all of them in brackets
    ("192.168.140.50:5555", True), # TV 1
    ("192.168.140.49:5555", True), # TV 2
    ("192.168.140.51:5555", True), # TV 3
    ("192.168.140.48:5555", True), # TV 4
    ("192.168.140.33:5555", True), # TV 5
    ("192.168.140.44:5555", True), # TV 6

    # next 4 (to the left of me)
    ("192.168.140.54:5555", True), # TV 7
    ("192.168.140.56:5555", True), # TV 8
    # one that should be here is off and idk why
    ("192.168.140.57:5555", True), # TV 9
    ("192.168.140.58:5555", True), # TV 10

    # other 4 behind me
    ("192.168.140.59:5555", True), # TV 11
    ("192.168.140.60:5555", True), # TV 12
    ("192.168.140.61:5555", True),  # TV 13
    ("192.168.140.53:5555", True),  # TV 14
]

def run(cmd):
    subprocess.run([ADB] + cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def open_link(device, url):
    run([
        "-s", device,
        "shell", "am", "start",
        "-a", "android.intent.action.VIEW",
        "-d", url,
        "-f", "0x10000000"
    ])

def screen_off(device):
    # Set brightness to 0 (screen appears off but TV stays on)
    run(["-s", device, "shell", "settings", "put", "system", "screen_brightness", "0"])

def screen_on(device):
    # Set brightness back to maximum (255 = 100%)
    run(["-s", device, "shell", "settings", "put", "system", "screen_brightness", "255"])

# Connect once on startup
for d, online in DEVICES:
    if online and d:
        run(["connect", d])

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TV Manager</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #ffffff;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        h1 {{
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 30px;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
        }}
        
        .global-controls {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        .global-controls h2 {{
            color: #00d4ff;
            margin-bottom: 20px;
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .url-form {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }}
        
        .url-form input[type="text"] {{
            flex: 1;
            min-width: 300px;
            padding: 15px 20px;
            border: none;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
        }}
        
        .url-form input[type="text"]:focus {{
            background: rgba(255, 255, 255, 0.2);
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        }}
        
        .url-form input[type="text"]::placeholder {{
            color: rgba(255, 255, 255, 0.5);
        }}
        
        .btn {{
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: #ffffff;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.4);
        }}
        
        .btn-success {{
            background: linear-gradient(135deg, #00c853, #009624);
            color: #ffffff;
        }}
        
        .btn-success:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 200, 83, 0.4);
        }}
        
        .btn-danger {{
            background: linear-gradient(135deg, #ff5252, #d50000);
            color: #ffffff;
        }}
        
        .btn-danger:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(255, 82, 82, 0.4);
        }}
        
        .btn-warning {{
            background: linear-gradient(135deg, #ffc107, #ff9800);
            color: #1a1a2e;
        }}
        
        .btn-warning:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(255, 193, 7, 0.4);
        }}
        
        .btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            transform: none !important;
        }}
        
        .screen-controls {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .section-title {{
            color: #00d4ff;
            font-size: 1.5rem;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .tv-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}
        
        .tv-card {{
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }}
        
        .tv-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
            border-color: rgba(0, 212, 255, 0.3);
        }}
        
        .tv-card.offline {{
            opacity: 0.6;
            border-color: rgba(255, 82, 82, 0.3);
        }}
        
        .tv-card.offline:hover {{
            transform: none;
            border-color: rgba(255, 82, 82, 0.3);
        }}
        
        .tv-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .tv-name {{
            font-size: 1.3rem;
            font-weight: 600;
            color: #ffffff;
        }}
        
        .tv-ip {{
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.6);
            font-family: 'Courier New', monospace;
            background: rgba(0, 0, 0, 0.3);
            padding: 5px 10px;
            border-radius: 6px;
        }}
        
        .tv-actions {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        
        .tv-url-form {{
            display: flex;
            gap: 10px;
        }}
        
        .tv-url-form input[type="text"] {{
            flex: 1;
            padding: 12px 15px;
            border: none;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            font-size: 0.9rem;
            outline: none;
            transition: all 0.3s ease;
        }}
        
        .tv-url-form input[type="text"]:focus {{
            background: rgba(255, 255, 255, 0.2);
        }}
        
        .tv-url-form input[type="text"]::placeholder {{
            color: rgba(255, 255, 255, 0.4);
        }}
        
        .tv-url-form .btn {{
            padding: 12px 20px;
            font-size: 0.85rem;
        }}
        
        .tv-screen-controls {{
            display: flex;
            gap: 10px;
        }}
        
        .tv-screen-controls .btn {{
            flex: 1;
            padding: 10px;
            font-size: 0.8rem;
        }}
        
        .status-indicator {{
            width: 12px;
            height: 12px;
            background: #00c853;
            border-radius: 50%;
            box-shadow: 0 0 10px #00c853;
            animation: pulse 2s infinite;
        }}
        
        .status-indicator.offline {{
            background: #ff5252;
            box-shadow: 0 0 10px #ff5252;
            animation: none;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: rgba(255, 255, 255, 0.4);
            font-size: 0.9rem;
        }}
        
        .toast {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 200, 83, 0.9);
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            font-weight: 600;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s ease;
            z-index: 1000;
        }}
        
        .toast.show {{
            opacity: 1;
            transform: translateY(0);
        }}
        
        .toast.error {{
            background: rgba(255, 82, 82, 0.9);
        }}
        
        @media (max-width: 768px) {{
            h1 {{ font-size: 1.8rem; }}
            .url-form {{ flex-direction: column; }}
            .url-form input[type="text"] {{ min-width: 100%; }}
            .tv-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>TV Control Center</h1>
        
        <div class="global-controls">
            <h2>Global Controls</h2>
            <div class="url-form">
                <input type="text" id="global-url" placeholder="https://example.com">
                <button class="btn btn-primary" onclick="sendToAll()">Send to All TVs</button>
            </div>
            <div class="screen-controls">
                <button class="btn btn-success" onclick="screenAll('on')">Turn All Screens ON</button>
                <button class="btn btn-danger" onclick="screenAll('off')">Turn All Screens OFF</button>
            </div>
        </div>
        
        <h2 class="section-title">Individual TVs</h2>
        <div class="tv-grid">
            {tv_cards}
        </div>
        
        <div class="footer">
            <p>TV Manager - {device_count} Devices ({online_count} Online)</p>
        </div>
    </div>
    
    <div id="toast" class="toast"></div>
    
    <script>
        function showToast(message, isError = false) {{
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = 'toast show' + (isError ? ' error' : '');
            setTimeout(() => {{
                toast.className = 'toast';
            }}, 3000);
        }}
        
        function sendRequest(data) {{
            return fetch('/api', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(data)
            }})
            .then(r => r.json())
            .then(result => {{
                if (result.success) {{
                    showToast(result.message || 'Action completed');
                }} else {{
                    showToast(result.message || 'Action failed', true);
                }}
            }})
            .catch(err => {{
                showToast('Error: ' + err.message, true);
            }});
        }}
        
        function sendToAll() {{
            const url = document.getElementById('global-url').value;
            if (!url.startsWith('http')) {{
                showToast('Please enter a valid URL starting with http', true);
                return;
            }}
            sendRequest({{ action: 'open_url', all: true, url: url }});
        }}
        
        function screenAll(action) {{
            sendRequest({{ action: 'screen', all: true, screen_action: action }});
        }}
        
        function sendToDevice(idx) {{
            const url = document.getElementById('url-' + idx).value;
            if (!url.startsWith('http')) {{
                showToast('Please enter a valid URL starting with http', true);
                return;
            }}
            sendRequest({{ action: 'open_url', device: idx, url: url }});
        }}
        
        function screenDevice(idx, action) {{
            sendRequest({{ action: 'screen', device: idx, screen_action: action }});
        }}
    </script>
</body>
</html>
"""

TV_CARD_TEMPLATE = """
<div class="tv-card{offline_class}">
    <div class="tv-header">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div class="status-indicator{status_class}"></div>
            <span class="tv-name">TV {index}</span>
        </div>
        <span class="tv-ip">{device_display}</span>
    </div>
    <div class="tv-actions">
        <div class="tv-url-form">
            <input type="text" id="url-{device_index}" placeholder="Enter URL..."{disabled}>
            <button class="btn btn-primary" onclick="sendToDevice({device_index})"{disabled}>Send</button>
        </div>
        <div class="tv-screen-controls">
            <button class="btn btn-success" onclick="screenDevice({device_index}, 'on')"{disabled}>Screen ON</button>
            <button class="btn btn-danger" onclick="screenDevice({device_index}, 'off')"{disabled}>Screen OFF</button>
        </div>
    </div>
</div>
"""

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress logging
    
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        tv_cards = ""
        online_count = 0
        for i, (d, online) in enumerate(DEVICES):
            if online:
                online_count += 1
            tv_cards += TV_CARD_TEMPLATE.format(
                index=i + 1,
                device_display=d if d else "Not configured",
                device_index=i,
                offline_class="" if online else " offline",
                status_class="" if online else " offline",
                disabled="" if online else " disabled"
            )

        html = HTML_TEMPLATE.format(
            tv_cards=tv_cards,
            device_count=len(DEVICES),
            online_count=online_count
        )
        self.wfile.write(html.encode())

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        raw_data = self.rfile.read(length).decode()
        
        # Check if it's JSON (new API) or form data (legacy)
        content_type = self.headers.get("Content-Type", "")
        
        if "application/json" in content_type:
            # New JSON API
            try:
                data = json.loads(raw_data)
            except:
                self.send_json_response(False, "Invalid JSON")
                return
            
            action = data.get("action", "")
            
            if action == "screen":
                screen_action = data.get("screen_action", "on")
                if data.get("all"):
                    threads = []
                    for d, online in DEVICES:
                        if online and d:
                            if screen_action == "on":
                                threads.append(threading.Thread(target=screen_on, args=(d,)))
                            else:
                                threads.append(threading.Thread(target=screen_off, args=(d,)))
                    for t in threads:
                        t.start()
                    for t in threads:
                        t.join()
                    self.send_json_response(True, f"All screens turned {screen_action.upper()}")
                else:
                    idx = int(data.get("device", 0))
                    device, online = DEVICES[idx]
                    if not online or not device:
                        self.send_json_response(False, "Device is offline")
                        return
                    if screen_action == "on":
                        screen_on(device)
                    else:
                        screen_off(device)
                    self.send_json_response(True, f"TV {idx + 1} screen turned {screen_action.upper()}")
                return
            
            elif action == "open_url":
                url = data.get("url", "")
                if not url.startswith("http"):
                    self.send_json_response(False, "Invalid URL")
                    return
                
                if data.get("all"):
                    threads = []
                    for d, online in DEVICES:
                        if online and d:
                            threads.append(threading.Thread(target=open_link, args=(d, url)))
                    for t in threads:
                        t.start()
                    for t in threads:
                        t.join()
                    self.send_json_response(True, "URL sent to all TVs")
                else:
                    idx = int(data.get("device", 0))
                    device, online = DEVICES[idx]
                    if not online or not device:
                        self.send_json_response(False, "Device is offline")
                        return
                    open_link(device, url)
                    self.send_json_response(True, f"URL sent to TV {idx + 1}")
                return
            
            self.send_json_response(False, "Unknown action")
            return
        
        # Legacy form handling (redirect response)
        data = parse_qs(raw_data)

        # Handle screen on/off for all TVs
        if "screen_all" in data:
            action = data["screen_all"][0]
            threads = []
            for d, online in DEVICES:
                if online and d:
                    if action == "on":
                        threads.append(threading.Thread(target=screen_on, args=(d,)))
                    else:
                        threads.append(threading.Thread(target=screen_off, args=(d,)))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        # Handle screen on/off for individual TV
        if "screen_device" in data:
            idx = int(data["screen_device"][0])
            action = data.get("screen_action", ["on"])[0]
            device, online = DEVICES[idx]
            if online and device:
                if action == "on":
                    screen_on(device)
                else:
                    screen_off(device)
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        # Handle URL opening
        url = data.get("url", [""])[0]

        if not url.startswith("http"):
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        if "all" in data:
            threads = []
            for d, online in DEVICES:
                if online and d:
                    threads.append(threading.Thread(target=open_link, args=(d, url)))
        else:
            idx = int(data["device"][0])
            device, online = DEVICES[idx]
            threads = []
            if online and device:
                threads.append(threading.Thread(target=open_link, args=(device, url)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()
    
    def send_json_response(self, success, message):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = json.dumps({"success": success, "message": message})
        self.wfile.write(response.encode())

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("TV Manager running on:")
    print("  http://localhost:8080")
    print("  http://<this-pc-ip>:8080  (LAN access)")
    server.serve_forever()
