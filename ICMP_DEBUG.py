from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
DEBUG = True  # Enable debug messages

def checksum(data):
    # Same implementation as your existing checksum function
    # ...

def print_debug(msg):
    if DEBUG:
        print(f"DEBUG: {msg}")

def parse_ip_header(packet):
    """Parse and return info from IP header"""
    ip_header = packet[0:20]
    iph = struct.unpack('!BBHHHBBH4s4s', ip_header)
    version_ihl = iph[0]
    version = version_ihl >> 4
    ihl = version_ihl & 0xF
    iph_length = ihl * 4
    ttl = iph[5]
    protocol = iph[6]
    s_addr = inet_ntoa(iph[8])
    d_addr = inet_ntoa(iph[9])
    
    return {
        'version': version,
        'ihl': ihl,
        'ttl': ttl,
        'protocol': protocol,
        'src_addr': s_addr,
        'dest_addr': d_addr
    }

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:
            print_debug(f"Select timeout occurred while waiting for {destAddr}")
            return "Request timed out."
            
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)
        
        print_debug(f"Received packet from {addr[0]} with length {len(recPacket)}")
        
        # Parse the IP header for debugging
        ip_info = parse_ip_header(recPacket)
        print_debug(f"IP Header: TTL={ip_info['ttl']}, Protocol={ip_info['protocol']}")
        print_debug(f"Source: {ip_info['src_addr']}, Dest: {ip_info['dest_addr']}")
        
        # Fetch the ICMP header from the IP packet
        icmpHeader = recPacket[20:28]
        try:
            icmpType, icmpCode, icmpChecksum, icmpId, icmpSeq = struct.unpack("bbHHh", icmpHeader)
            print_debug(f"ICMP Type={icmpType}, Code={icmpCode}, Checksum={icmpChecksum}, ID={icmpId}, Seq={icmpSeq}")
            print_debug(f"Our ID={ID}")
            
            # Echo Reply (Type 0) - Match by ID
            if icmpType == 0 and icmpId == ID:
                timeSent = struct.unpack("d", recPacket[28:36])[0]
                rtt = (timeReceived - timeSent) * 1000  # in milliseconds
                return f"Reply from {addr[0]}: bytes={len(recPacket)} time={rtt:.3f}ms"
            
            # ICMP Error Parsing with detailed debug
            elif icmpType == 3:  # Destination Unreachable
                error_messages = {
                    0: "Destination Network Unreachable",
                    1: "Destination Host Unreachable",
                    2: "Destination Protocol Unreachable",
                    3: "Destination Port Unreachable",
                    4: "Fragmentation needed but DF bit set",
                    5: "Source route failed"
                }
                error_msg = error_messages.get(icmpCode, f"Destination Unreachable (code {icmpCode})")
                print_debug(f"Detected error: {error_msg}")
                return f"Error: {error_msg}"
            
            # Handle other ICMP types
            # ...
            else:
                print_debug(f"Ignoring packet: Type {icmpType} not matching our request or known error")
        
        except Exception as e:
            print_debug(f"Error unpacking ICMP header: {e}")
        
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            print_debug(f"Timeout occurred for destination {destAddr}")
            return "Request timed out."

# Rest of the functions remain the same
# ...

def ping(host, timeout=2):
    dest = gethostbyname(host)
    print(f"Pinging {dest} ({host}) using Python with debug output:")
    print("")
    
    # ... rest of the function remains the same with added debug prints ...

if __name__ == '__main__':
    if len(sys.argv) > 1:
        ping(sys.argv[1])
    else:
        print("Usage: sudo python3 ICMP_DEBUG.py <hostname_or_ip>")
        print("This is a debug version that will show detailed ICMP packet information")
