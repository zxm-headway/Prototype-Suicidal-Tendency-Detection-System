from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')


async def get_map_data():
    db = client['suiDection']
    collection = db['map_data1']
    all_documents = list(collection.find({}, {'_id': 0}))
    return all_documents


async def get_save_user():
    db = client['suiDection']
    return db['saveUsers']
