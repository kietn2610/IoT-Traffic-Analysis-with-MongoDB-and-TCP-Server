from pymongo import MongoClient
from datetime import datetime, timedelta

DBName = "test"
connectionURL = "mongodb+srv://kietnguyen:kiet2610@cluster0.lh3cdhx.mongodb.net/?retryWrites=true&w=majority"
sensorTables = ['traffic data', 'traffic data2', 'traffic data3']

def QueryToList(query):
    return list(query)

def QueryDatabase() -> []:
    global sensorTables
    cluster = None
    client = None
    db = None
    sensor_data = []

    try:
        cluster = connectionURL
        client = MongoClient(cluster)
        db = client[DBName]

        for table in sensorTables:
            sensorTable = db[table]
            timeCutOff = datetime.now() - timedelta(minutes=5)
            sensor_data.extend(QueryToList(sensorTable.find({"time": {"$gte": timeCutOff}})))

        return sensor_data

    except Exception as e:
        print("Please make sure that this machine's IP has access to MongoDB.")
        print("Error:", e)
        exit(0)
