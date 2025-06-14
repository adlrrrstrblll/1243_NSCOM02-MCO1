# Custom Ping Utility Using ICMP (MCO1)

## 📌 Overview

This project implements a simplified version of the **ping** command using **Python** and **raw sockets**, focusing on the **Internet Control Message Protocol (ICMP)**. It sends Echo Request packets to a destination host, receives Echo Replies, and measures the **Round-Trip Time (RTT)**.

This utility deepens the understanding of network-layer communication, binary packet structure, and ICMP message handling.

---

## 🎯 Objectives

- Understand the structure and purpose of ICMP Echo Request/Reply messages.
- Implement raw socket programming in Python.
- Measure RTT and simulate basic network diagnostics.
- Handle packet timeouts and compute packet loss.
- Learn binary packing/unpacking and packet inspection.

---

## 🛠️ Features

- Sends ICMP Echo Request packets every 1 second.
- Embeds a timestamp in the payload.
- Computes per-packet RTT.
- Handles packet loss with a 2000 ms timeout.
- Prints per-packet output:
  - Sequence number
  - RTT in milliseconds

### ✅ BONUS FEATURES
- **RTT Summary Stats**
  - Min, Max, Average RTT
  - Packet Loss Rate (%)
- **ICMP Error Code Parsing**
  - TTL Expired
  - Host/Network Unreachable (optional)

---

## 🧪 Test Results

### 1. **Localhost (127.0.0.1)**
- Simulates local reachability testing.

### 2. **External Hosts**
Pinged the following hosts from the Philippines:
- `google.com` (USA)
- `baidu.com` (China)
- `bbc.co.uk` (UK)

Screenshots and analysis are included in the attached PDF documentation.

---

## 📂 Files

| File Name      | Description                                      |
|----------------|--------------------------------------------------|
| `ICMP.py`      | Main Python file with complete ping logic        |
| `README.md`    | This file                                        |
| `Screenshots.pdf` | Test results with screenshots & brief summaries |

---

## 🖥️ How to Run

> ⚠️ **Note:** Raw sockets require administrative privileges.  
> Run the script with `sudo` (Linux/macOS) or as Administrator (Windows).

### 🐍 Requirements
- Python 3.x
- Run with root/admin privileges

### ▶️ Usage
# Linux / macOS (Terminal)
sudo python3 ICMP.py google.com

# Windows (Command Prompt as Administrator)
python ICMP.py google.com

Ping to google.com (142.250.183.206), 56 bytes of data:

Reply from 142.250.183.206: seq=1, RTT=12.45 ms
Reply from 142.250.183.206: seq=2, RTT=11.98 ms
Reply from 142.250.183.206: seq=3, RTT=13.12 ms
Request timed out for seq=4

--- Ping Statistics ---
Packets: Sent = 4, Received = 3, Lost = 1 (25% loss)
RTT (min/avg/max) = 11.98 / 12.52 / 13.12 ms

👨‍💻 --- Author ---
Adler Clarence E. Strebel 
College of Computer Studies : Bachelor of Science in Computer Science Major in Network and Information Security
