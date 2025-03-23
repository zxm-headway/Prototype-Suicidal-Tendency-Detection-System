
import datetime
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel
from utils.help import *
from mogodb_oper.conect_db import *


client = MongoClient('mongodb://localhost:27017/')
db = client['suiDection']  # 替换为你的数据库名称
collection = db['weibo_data']  # 替换为你的集合名称
app = FastAPI()
origins = [
    "http://127.0.0.1:5173",  # Vite 开发服务器
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的请求源
    allow_credentials=True,
    allow_methods=["*"],  # 允许的 HTTP 方法
    allow_headers=["*"],  # 允许的请求头
)


class DetectionData(BaseModel):
    texts: List[str]
    is_sui: Union[bool, int]
    user_name: str
    inputType: str


@app.post("/process-list", response_model=dict)
async def process_list(data: List[str], ):
    words, emotion_num = await preprocess_words(data)
    res = await pre_textData(data)
    result_list = [item[0] for item in words]
    pos = emotion_num[2]
    mod = emotion_num[1]
    neg = emotion_num[0]
    emtion_dict = {
        '正向': pos,
        '中性': mod,
        '负面': neg,
    }
    data = {
        'words': result_list,
        'emotion_num': emtion_dict,
        'res': res
    }
    return data


@app.get("/map", response_model=list[dict])
async def greet():
    res = await get_map_data()
    return res


class UserDataModel(Dict):
    id: int
    username: str
    dataSource: str
    sampleData: str
    status: int


class ResponseModel(Dict[str, Any]):
    items: List[UserDataModel]
    total: int


class PostList(BaseModel):
    sentence_list: List[str]


@app.get("/data", response_model=Dict[str, Any])
async def get_items(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1),
        dataSource: str = Query("dataset", regex="^(dataset|detected)$")
):
    if dataSource == "detected":
        coll = db['saveUsers']
    else:
        coll = db['weibo_data']

    print(coll)
    skip = (page - 1) * size
    cursor = coll.find().skip(skip).limit(size)
    items = list(cursor)
    response_items = []
    for item in items:
        posts = item.get("posts", [])
        content_list = [post.get('content', '') for post in posts[:2]]
        concatenated_content = '.'.join(content_list)
        response_items.append({
            "id": item.get("user_id"),
            "username": item.get("user_name"),
            "dataSource": item.get("data_source"),
            "sampleData": concatenated_content,
            "status": item.get("labels")
        })
    total = coll.count_documents({})
    return {
        "items": response_items,
        "total": total
    }


@app.get("/user/posts/detail", response_model=Dict[str, Any])
async def get_user_posts(
        user_id: int = Query(..., alias="userId"),
        data_type: str = Query(...)
):
    if data_type == "detected":
        coll = db['saveUsers']
    else:
        coll = db['weibo_data']
    user_data = coll.find_one({"user_id": user_id})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    posts = user_data.get("posts", [])
    return {
        "user_id": user_data.get("user_id"),
        "username": user_data.get("user_name"),
        "posts": posts,
        "labels": user_data.get("labels"),
    }


@app.post("/user/emotionsWave", response_model=dict)
async def checkUsersWave(post_list: PostList):
    result = get_emotions_wave(post_list.sentence_list)
    return {"emotions_wave": result}


@app.get("/user/emotions/detail", response_model=dict)
async def get_user_emotions(
        user_id: int = Query(..., alias="userId"),
        data_type: str = Query(...)
):
    if data_type == "detected":
        coll = db['saveUsers']
    else:
        coll = db['weibo_data']
    contents = []
    user_data = coll.find_one({"user_id": user_id})
    posts = user_data.get("posts", [])
    for post in posts:
        contents.append(post["content"])
    res = await posts_emtions(contents)
    data = {
        'emotion_num': res
    }
    return data


async def save_detection_data(document: dict) -> dict:
    try:
        saveUsers = db['saveUsers']
        document['user_id'] = int(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        count = saveUsers.count_documents({})
        if count == 0:
            result = saveUsers.insert_one(document)
            return {"message": "数据存储成功", "id": str(result.inserted_id)}
        else:
            user_name = document.get("user_name")
            if not user_name:
                raise HTTPException(status_code=400, detail="缺少用户名字段")
            existing_user = saveUsers.find_one({"user_name": user_name})
            if existing_user:
                raise HTTPException(status_code=400, detail="用户名已存在")
            result = saveUsers.insert_one(document)
            return {"message": "数据存储成功", "id": str(result.inserted_id)}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="存储失败：" + str(e))


@app.get("/data", response_model=Dict[str, Any])
async def get_items(
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1),
        dataSource: str = Query("dataset", regex="^(dataset|detected)$")
):
    if dataSource == "detected":
        coll = db['saveUsers']
    else:
        coll = db['weibo_data']
    skip = (page - 1) * size
    cursor = coll.find().skip(skip).limit(size)
    items = list(cursor)
    response_items = []
    for item in items:
        posts = item.get("posts", [])
        content_list = [post.get('content', '') for post in posts[:2]]
        concatenated_content = '.'.join(content_list)
        response_items.append({
            "id": item.get("user_id"),
            "username": item.get("user_name"),
            "dataSource": item.get("data_source"),
            "sampleData": concatenated_content,
            "status": item.get("labels")
        })
    total = coll.count_documents({})
    return {
        "items": response_items,
        "total": total
    }


@app.post("/store_detection")
async def store_detection(data: DetectionData):
    posts = [{"post_id": str(i + 1), "content": text} for i, text in enumerate(data.texts)]
    document = {
        "posts": posts,
        "labels": data.is_sui,
        "user_name": data.user_name,
        "data_source": data.inputType
    }
    return await save_detection_data(document)