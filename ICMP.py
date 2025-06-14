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
        if whatReady[0] == []: # Timeout
            return "Request timed out."
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        #Fill in start
        #Fetch the ICMP header from the IP packet
        icmpHeader = recPacket[20:28]  # The first 20 bytes are IP header
        icmpType, icmpCode, icmpChecksum, icmpId, icmpSeq = struct.unpack("bbHHh", icmpHeader)
        
        # Check if this is an echo reply (type 0) and matches our ID
        if icmpType == 0 and icmpId == ID:
            # Extract timestamp from the packet data
            timeSent = struct.unpack("d", recPacket[28:36])[0]
            
            # Calculate round-trip time
            rtt = (timeReceived - timeSent) * 1000  # Convert to milliseconds
            return f"Reply from {destAddr}: bytes={len(recPacket)} time={rtt:.3f}ms"
        #Fill in end
        
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID, seq=1):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, seq)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)
    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout, seq=1):
    icmp = getprotobyname("icmp")
    # SOCK_RAW is a powerful socket type. For more details:
    # http://sockraw.org/papers/sock_raw
    
    #Fill in start
    #create socket
    try:
        mySocket = socket(AF_INET, SOCK_RAW, icmp)
    except error as e:
        if e.errno == 1:
            # Operation not permitted
            print("Socket creation requires root privileges")
            raise e
        raise e  # Something else went wrong
    #Fill in end
    
    myID = os.getpid() & 0xFFFF # Return the current process i
    
    #Fill in start
    #send a single ping using the socket, dst addr and ID
    sendOnePing(mySocket, destAddr, myID, seq)
    
    #add delay using timeout
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    
    #close socket
    mySocket.close()
    #Fill in end
    
    return delay

def ping(host, timeout=2):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")

    seq_num = 0
    # Send ping requests to a server separated by approximately one second
    while 1 :
        seq_num += 1

        delay = doOnePing(dest, timeout)
        print(delay)

        time.sleep(1)# one second
    return delay

if __name__ == '__main__':
    if len(sys.argv) > 1:
        ping(sys.argv[1])
    else:
        ping('127.0.0.1')