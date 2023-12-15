import socket
import threading
import time
import contextlib
import errno


maxPacketSize = 1024
defaultPort = 8888
exitSignal = False
tcpSocket = None

def GetFreePort(minPort: int = 2000, maxPort: int = 65535):
    for i in range(minPort, maxPort):
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as potentialPort:
            try:
                potentialPort.bind(('localhost', i))
                potentialPort.close()
                return i
            except socket.error as e:
                if e.errno == errno.EADDRINUSE:
                    print("Port", i, "already in use. Checking next...")
                else:
                    print("An exotic error occurred:", e)

    print("No free port found.")
    return None

def GetServerData() -> []:
    import MongoDBConnection as mongo
    return mongo.QueryDatabase()

def CalculateAverage(sensor_data):
    averages = {}
    counts = {}

    for sensor in sensor_data:
        sensor_name = sensor.get("payload", {}).get("topic", "")
        traffic_counts_80 = sensor.get("payload", {}).get("Traffic Sensor 80", 0)
        traffic_counts_105 = sensor.get("payload", {}).get("Traffic Sensor 105", 0)
        traffic_counts_110 = sensor.get("payload", {}).get("Traffic Sensor 110", 0)

        try:
            counts[sensor_name] = counts.get(sensor_name, 0) + 1
            averages[sensor_name] = averages.get(sensor_name, 0) + int(traffic_counts_80) + int(traffic_counts_105) + int(traffic_counts_110)
        except ValueError:
            print(f"Invalid value for sensor {sensor_name}. Skipping.")
            continue

    for sensor_name, count in counts.items():
        averages[sensor_name] = round(averages[sensor_name] / count, 1)

    return averages

def ListenOnTCP(clientSocket: socket.socket, socketAddress):
    # Receive the query message from the client
    query_message = clientSocket.recv(maxPacketSize).decode('utf-8')
    print(f"Received query message from client: {query_message}")

    # Process sensor data
    sensor_data = GetServerData()
    averages = CalculateAverage(sensor_data)

    # Find the best highway with the least average traffic
    best_highway = min(averages, key=averages.get)
    best_average_time = averages[best_highway]

    # Print all highways and average times on the server side
    for highway, average in averages.items():
        print(f"Highway: {highway}, Average time: {average}")

    # Send only the best highway and average time to the client
    response = f"Best highway: {best_highway}, Average time: {best_average_time}\n"
    clientSocket.sendall(response.encode('utf-8'))

    # Close the client socket
    clientSocket.close()

    # Exit the program
    print("Sent Best Average to Client.")
    print("Goodbye")
    exit()


def CreateTCPSocket() -> socket.socket:
    global tcpSocket
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpPort = GetFreePort()
    print("Listening to Port:", tcpPort)
    tcpSocket.bind(('localhost', tcpPort))
    return tcpSocket

def LaunchTCPThreads():
    tcpSocket = CreateTCPSocket()
    tcpSocket.listen(5)
    while True:
        connectionSocket, connectionAddress = tcpSocket.accept()
        connectionThread = threading.Thread(target=ListenOnTCP, args=[connectionSocket, connectionAddress])
        connectionThread.start()

if __name__ == "__main__":
    tcpThread = threading.Thread(target=LaunchTCPThreads)
    tcpThread.start()

    try:
        while not exitSignal:
            time.sleep(1)
    except KeyboardInterrupt:
        exitSignal = True
        print("Ending program by exit signal...")
    finally:
        if 'tcpSocket' in locals():
            tcpSocket.close()

