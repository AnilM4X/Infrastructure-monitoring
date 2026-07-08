#!/bin/bash

API_ENDPOINT="http://IP:8000/api/node_metrics"

check_service() {

    url=$1

    status_code=$(curl -k -o /dev/null -s -w "%{http_code}" --connect-timeout 5 "$url")

    if [[ "$status_code" == "200" || "$status_code" == "301" || "$status_code" == "302" ]]; then
        echo "RUNNING"
    else
        echo "DOWN"
    fi
}

while true
do

hostname=$(hostname)

ip_address=$(hostname -I | awk '{print $1}')

operating_system=$(cat /etc/redhat-release)

kernel_version=$(uname -r)

uptime=$(uptime -p)

current_time_stamp=$(date)

if netstat -ulnp 2>/dev/null | grep ":123 " >/dev/null
then
    status_ntp="RUNNING"
    ntp_sync_status="SYNCED"
else
    status_ntp="DOWN"
    ntp_sync_status="NOT_SYNCED"
fi

status_nexus=$(check_service "<URL>")

status_freeipa=$(check_service "<URL>")

status_rancher=$(check_service "<URL>")

status_elk=$(check_service "<URL>")

status_ingress=$(check_service "<URL>")

status_ovirt=$(check_service "<URL>")

total_cpu=$(nproc)

cpu_usage=$(vmstat 1 2 | tail -1 | awk '{print 100 - $15}')

total_processes=$(ps -ef | wc -l)

total_memory=$(free -h | awk '/Mem:/ {print $2}')

used_memory_percentage=$(free | awk '/Mem:/ {printf("%.2f%%"), $3/$2 * 100.0}')

free_memory_percent=$(free | awk '/Mem:/ {printf("%.2f%%"), $4/$2 * 100.0}')

status_ovirt=$(curl -k -I -m 5 https://ovirtemt.cdot.in | head -1 | grep -q "200\|301\|302" && echo "RUNNING" || echo "DOWN")

available_memory_percent=$(free | awk '/Mem:/ {printf("%.2f%%"), $7/$2 * 100.0}')

total_swap=$(free -h | awk '/Swap:/ {print $2}')

used_swap_percent=$(free | awk '/Swap:/ {if ($2==0) print "0%"; else printf("%.2f%%"), $3/$2 * 100.0}')

disk_data=$(chroot /host df -h | awk '
NR>1 {

print "{\"filesystem\":\""$1"\",\"size\":\""$2"\",\"used\":\""$3"\",\"avail\":\""$4"\",\"use\":\""$5"\",\"mount\":\""$6"\"}"

}' | paste -sd "," -)

active_users=$(uptime | sed 's/,/ /g' | awk '{for(i=1;i<=NF;i++) if($i=="users") print $(i-1)}')

json_payload=$(cat <<EOF
{
    "hostname": "$hostname",
    "ip_address": "$ip_address",
    "operating_system": "$operating_system",
    "kernel_version": "$kernel_version",
    "uptime": "$uptime",
    "current_time_stamp": "$current_time_stamp",
    "status_ntp": "$status_ntp",
    "ntp_sync_status": "$ntp_sync_status",
    "status_nexus": "$status_nexus",
    "status_freeipa": "$status_freeipa",
    "status_rancher": "$status_rancher",
    "status_elk": "$status_elk",
    "status_ingress": "$status_ingress",
    "status_ovirt": "$status_ovirt",

    "total_cpu": $total_cpu,
    "cpu_usage": $cpu_usage,

    "total_processes": $total_processes,

    "total_memory": "$total_memory",
    "used_memory_percentage": "$used_memory_percentage",
    "free_memory_percent": "$free_memory_percent",
    "available_memory_percent": "$available_memory_percent",

    "total_swap": "$total_swap",
    "used_swap_percent": "$used_swap_percent",

    "disk_data": [ $disk_data ],
    "active_users": $active_users
}
EOF
)

echo "=================================="
echo "Sending metrics to backend API..."
echo "$json_payload"

response=$(curl -s -X POST "$API_ENDPOINT" \
-H "Content-Type: application/json" \
-d "$json_payload")

echo "API Response:"
echo "$response"

echo "Sleeping for 60 seconds..."
echo "=================================="

sleep 60

done
