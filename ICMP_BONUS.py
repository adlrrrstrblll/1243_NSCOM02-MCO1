from socket import *
import os
import sys
import struct
import time
import select
import binascii
ICMP_ECHO_REQUEST = 8

def checksum(data):
    csum = 0
    countTo = (len(data) // 2) * 2
    count = 0
    
    while count < countTo:
        if isinstance(data, bytes):
            thisVal = data[count+1] * 256 + data[count]
        else:
            thisVal = ord(data[count+1]) * 256 + ord(data[count])
        
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2
    
    if countTo < len(data):
        if isinstance(data, bytes):
            csum = csum + data[len(data) - 1]
        else:
            csum = csum + ord(data[len(data) - 1])
        csum = csum & 0xffffffff
    
    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:
            return "Request timed out."
            
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)
        
        # Fetch the ICMP header from the IP packet
        icmpHeader = recPacket[20:28]
        icmpType, icmpCode, icmpChecksum, icmpId, icmpSeq = struct.unpack("bbHHh", icmpHeader)
        
        # Echo Reply (Type 0) - Match by ID
        if icmpType == 0 and icmpId == ID:
            timeSent = struct.unpack("d", recPacket[28:36])[0]
            rtt = (timeReceived - timeSent) * 1000  # in milliseconds
            return f"Reply from {addr[0]}: bytes={len(recPacket)} time={rtt:.3f}ms"
        
        # ICMP Error Parsing - For bonus feature requirement
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
            return f"Error: {error_msg}"
            
        elif icmpType == 11:  # Time Exceeded
            error_msg = "TTL Expired in Transit" if icmpCode == 0 else f"Time Exceeded (code {icmpCode})"
            return f"Error: {error_msg}"
            
        elif icmpType == 4:  # Source Quench
            return "Error: Source Quench (Congestion Control)"
            
        elif icmpType == 5:  # Redirect
            return f"Error: Redirect (code {icmpCode})"
            
        elif icmpType == 12:  # Parameter Problem
            return f"Error: Parameter Problem (code {icmpCode})"
        
        # If it's some other ICMP packet, just continue waiting for our echo reply
        
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID, seq=1):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, seq)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header
    myChecksum = checksum(header + data)
    
    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)
    
    # Create final header with correct checksum and sequence number
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, seq)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1))

def doOnePing(destAddr, timeout, seq=1):
    icmp = getprotobyname("icmp")
    
    # Create socket
    try:
        mySocket = socket(AF_INET, SOCK_RAW, icmp)
    except error as e:
        if e.errno == 1:
            # Operation not permitted
            print("Socket creation requires root privileges")
            raise e
        raise e  # Something else went wrong
    
    myID = os.getpid() & 0xFFFF  # Get process ID as identifier
    
    # Send ping and get response
    sendOnePing(mySocket, destAddr, myID, seq)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    
    return delay

def ping(host, timeout=2):
    # timeout=2 means: If two seconds go by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    
    # Stats tracking for RTT Summary requirement
    rtts = []
    packets_sent = 0
    packets_received = 0
    seq_num = 0
    
    try:
        # Send ping requests to a server separated by approximately one second
        while 1:
            seq_num += 1
            packets_sent += 1
            delay = doOnePing(dest, timeout, seq_num)
            
            if "Request timed out" in str(delay) or "Error" in str(delay):
                print(f"Sequence {seq_num}: {delay}")
            else:
                packets_received += 1
                # Extract RTT from response
                try:
                    rtt_val = float(delay.split("time=")[1].split("ms")[0])
                    rtts.append(rtt_val)
                except (IndexError, ValueError):
                    pass  # Skip if parsing fails
                print(f"Sequence {seq_num}: {delay}")
                
            time.sleep(1)  # one second
    except KeyboardInterrupt:
        # RTT Summary Stats - For bonus feature requirement
        print("\n--- " + dest + " ping statistics ---")
        loss_percentage = 0 if packets_sent == 0 else ((packets_sent - packets_received) / packets_sent) * 100
        print(f"{packets_sent} packets transmitted, {packets_received} packets received, {loss_percentage:.1f}% packet loss")
        
        if rtts:
            print(f"round-trip min/avg/max = {min(rtts):.3f}/{sum(rtts)/len(rtts):.3f}/{max(rtts):.3f} ms")
        print()
    
    return delay

if __name__ == '__main__':
    if len(sys.argv) > 1:
        ping(sys.argv[1])
    else:
        print("Usage: sudo python3 ICMP_BONUS.py <hostname_or_ip>")