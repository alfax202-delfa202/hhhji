#!/bin/bash

# أوامر التشغيل الخاصة بـ Ram
SERVER_CMD="python3 quantum_logic_bomb.py"
TUNNEL_CMD="./cloudflared-linux-amd64 tunnel --url http://localhost:8080"

echo "🔥 Phoenix Monitor is ACTIVE. Protecting Ram's Server..."

while true; do
    # فحص هل سيرفر البايثون يعمل؟
    if ! pgrep -f "quantum_logic_bomb.py" > /dev/null; then
        echo "⚠️ Server is DOWN (Suicide triggered). Waiting 10 seconds to rebuild..."
        sleep 10
        
        # إعادة بناء السيرفر وتشغيله
        nohup $SERVER_CMD > /dev/null 2>&1 &
        echo "✅ Server Rebuilt."
    fi

    # فحص هل النفق يعمل؟
    if ! pgrep -f "cloudflared" > /dev/null; then
        echo "⚠️ Tunnel is DOWN. Reconnecting to the world..."
        nohup $TUNNEL_CMD > tunnel.log 2>&1 &
        echo "✅ Tunnel Reconnected."
    fi

    sleep 5 # يفحص كل 5 ثوانٍ
done

