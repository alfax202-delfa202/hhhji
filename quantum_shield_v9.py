
import socket
import os
import random
import base64
import threading

# إعدادات الحصن الرقمي لـ Ram
PORT = 8080
PUBLIC_DIR = "public"
LOG_FILE = "quantum_guard.log"

# قائمة "الهويات المزيفة" لتضليل أدوات الفحص
SERVER_IDENTITIES = [
    "Ram-Quantum-Shield/9.1 (Quantum-OS)",
    "NASA-Secure-Gateway/1.0",
    "Deep-Space-Network-Node",
    "Unknown-Alien-Technology/0.0"
]

def get_random_garbage(size=1024):
    """توليد بيانات مشوشة لتحطيم أدوات الهكر"""
    return os.urandom(size)

def handle_client(client, addr):
    ip = addr[0]
    try:
        request = client.recv(4096).decode('utf-8', errors='ignore')
        
        # 1. كشف محاولات الفحص (Nmap, ZMap, Masscan)
        bad_flags = ["nmap", "scan", "script", "vuln", "../", "etc/passwd", "' OR 1=1"]
        if any(flag in request.lower() for flag in bad_flags):
            print(f"🚨 [KICK] Hacker detected from {ip}. Sending Binary Poison...")
            # إرسال "سم برمي" (بيانات عشوائية ضخمة تسبب انهيار برنامج الهكر)
            client.send(get_random_garbage(5000))
            client.close()
            return

        # 2. نظام الرد الذكي (إظهار الموقع للمستخدم الحقيقي فقط)
        if "GET / " in request or "GET /index.html" in request:
            with open(f"{PUBLIC_DIR}/index.html", "r") as f:
                content = f.read()
            
            # تغيير هوية السيرفر عشوائياً في كل مرة (Quantum Masking)
            identity = random.choice(SERVER_IDENTITIES)
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Server: {identity}\r\n"
                f"X-Shield-Status: Active-Quantum-Link\r\n"
                f"Content-Type: text/html\r\n\r\n"
                f"{content}"
            )
            client.send(response.encode('utf-8'))
        else:
            # 3. فخ المسارات الوهمية (Honeypot)
            # أي محاولة لدخول مسارات غير موجودة تؤدي لإرسال بيانات لا نهائية
            print(f"🛡️ [DECOY] Diverting suspicious request from {ip}")
            client.send(b"HTTP/1.1 200 OK\r\n\r\n")
            while True: # سجن الهكر في تدفق بيانات لا ينتهي
                client.send(get_random_garbage(1024))
                
    except Exception as e:
        client.close()
    finally:
        client.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PORT))
    server.listen(1000)
    print(f"💎 Ram's Quantum Server is LIVE. Even Google can't peek inside.")

    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client, addr))
        thread.start()

if __name__ == "__main__":
    start_server()

