
import socket
import os

# إعدادات Ram الصارمة
PORT = 8080
TOR_LIST = "tor_ips.txt"

def load_tor_ips():
    if os.path.exists(TOR_LIST):
        with open(TOR_LIST, 'r') as f:
            return set(f.read().splitlines())
    return set()

def start_ghost_server():
    tor_ips = load_tor_ips()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PORT))
    server.listen(100)
    print(f"🛡️ Ghost Server is Active for Ram on port {PORT}")

    while True:
        client, addr = server.accept()
        ip = addr[0]

        # 1. حظر شبكة Tor فوراً
        if ip in tor_ips:
            client.close()
            continue

        try:
            data = client.recv(1024).decode('utf-8')
            
            # 2. كشف أدوات الفحص (Nmap / Scanners)
            # إذا كان الطلب لا يبدو كطلب متصفح طبيعي، أرسل بيانات مشفرة "مجنونة"
            if "HTTP" not in data or any(x in data for x in ["nmap", "scan", "script"]):
                # إرسال بيانات ثنائية غير مفهومة لتحطيم أداة الهكر
                client.send(os.urandom(1024)) 
                client.close()
                continue

            # 3. توجيه المستخدم الحقيقي للموقع الأخضر
            with open("public/index.html", "r") as f:
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + f.read()
                client.send(response.encode('utf-8'))
        except:
            # أي محاولة تلاعب تؤدي لإغلاق الاتصال بصمت
            client.close()
        finally:
            client.close()

if __name__ == "__main__":
    start_ghost_server()

