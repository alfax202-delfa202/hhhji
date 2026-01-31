import socket, os, threading, zlib, time

PORT = 8080
PUBLIC_DIR = "public"
SECRET_KEY = "RAM_LION_2026"
BOMB_DATA = zlib.compress(b"0" * 10**8)
# الملفات الحساسة التي تفعّل "بروتوكول الرعب"
SENSITIVE_FILES = [".env", "config", "admin", "setup", "db"]

def self_destruct():
    os.system("pkill -9 cloudflared")
    if os.path.exists(__file__): os.remove(__file__)
    print("💀 Sensitive area breached. Server Vanished.")
    os._exit(0)

def handle_client(client, addr):
    try:
        request = client.recv(4096).decode('utf-8', errors='ignore')
        path = request.split(' ')[1] if len(request.split(' ')) > 1 else "/"

        # 1. إذا حاول الوصول لملف حساس
        if any(x in path.lower() for x in SENSITIVE_FILES):
            print(f"🚨 INTRUDER trying to access {path}!")
            # طلب كلمة سر تعجيزية
            client.send(b"HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm='RESTRICTED'\r\n\r\n")
            time.sleep(0.5) # وقت قصير جداً
            self_destruct()
            return

        # 2. إذا كان طلباً طبيعياً للموقع
        if path == "/" or path == "/index.html":
            with open(f"{PUBLIC_DIR}/index.html", "r") as f:
                content = f.read()
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + content
            client.send(response.encode())
        else:
            client.send(b"HTTP/1.1 404 Not Found\r\n\r\nStay away.")

    except:
        pass
    finally:
        client.close()

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PORT))
    server.listen(100)
    print("💎 Smart Shield Active: Public is Welcome, Hackers are Trapped.")
    while True:
        c, a = server.accept()
        threading.Thread(target=handle_client, args=(c, a)).start()

if __name__ == "__main__":
    start()

