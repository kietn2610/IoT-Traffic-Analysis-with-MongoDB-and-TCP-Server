import socket

maxPacketSize = 1024
defaultPort = 2000
serverIP = 'localhost'

tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    tcpPort = int(input("Please enter the TCP port of the host: "))
except ValueError:
    tcpPort = 0
if tcpPort == 0:
    tcpPort = defaultPort

tcpSocket.connect((serverIP, tcpPort))
print(f"Connected to port {tcpPort}")

# Send a query message to the server
query_message = "hello from client"
tcpSocket.sendall(query_message.encode('utf-8'))

# Receive the highways and average times from the server
serverData = tcpSocket.recv(maxPacketSize).decode('utf-8')
print(serverData)

tcpSocket.close()
