# run with uvicorn main:app --reload
# deploy with ?

from fastapi import FastAPI, Request, Cookie, Depends
from fastapi.security import APIKeyCookie
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, EmailStr, UUID4, validator
import uuid
from jose import jwt
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import CookieAuthentication
from fastapi_users.db import MongoDBUserDatabase
import motor.motor_asyncio
import docker
from docker.errors import DockerException, APIError, NotFound

from enum import Enum
from datetime import datetime
from typing import List, Optional
import random
from sys import stderr


cookie_lifetime = 3600  # seconds


# an enum class which contains the Docker container names of our repos
class Repository(str, Enum):
    peracotta = "peracotta"
    sardina = "sardina"
    weeehire_ng = "weeehire-ng_nginx"


# a class to represent a running container
class Container(BaseModel):
    cnt_id: str
    user_email: EmailStr


class User(models.BaseUser):
    container_ids: List[str] = []
    expire_unix: int = int(datetime.utcnow().timestamp()) + cookie_lifetime


class UserCreate(models.BaseUserCreate):
    pass
    # TODO: use random email as userid in frontend, can't override here in backend
    # email: EmailStr = f"{get_random_string()}@example.com"
    # password: str = "softweeere"


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass


def get_random_string(length: int = 64):
    return ''.join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUWXYZ1234567890'_-/,;.:àèìòù")
                   for _ in range(length))


def on_after_register(user: UserDB, request: Request):
    print(f"User {user.email} has registered.")


def get_running_container(repo: str):
    try:
        cnt = client.containers.run(repo, auto_remove=True, detach=True)
        return {
            "repo": repo,
            "id": cnt.id,
        }
    except APIError:
        raise


secret_key = "secret"
cookie_name = "softweeere"
cookie_authentication = CookieAuthentication(
    secret=secret_key,
    lifetime_seconds=cookie_lifetime,
    cookie_name=cookie_name,
)

db_url = "mongodb://localhost:27017"
db = motor.motor_asyncio.AsyncIOMotorClient(db_url, uuidRepresentation="standard")['softweeere_users']
collection = db["users"]
user_db = MongoDBUserDatabase(UserDB, collection)
fastapi_users = FastAPIUsers(
    user_db,
    [cookie_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

api_prefix = "/api"
app = FastAPI()
app.include_router(fastapi_users.get_register_router(on_after_register),
                   prefix=f"{api_prefix}/auth", tags=["auth"])
app.include_router(fastapi_users.get_auth_router(cookie_authentication),
                   prefix=f"{api_prefix}/auth/cookie", tags=["auth"])
app.include_router(fastapi_users.get_users_router(),
                   prefix=f"{api_prefix}/users", tags=["users"])

try:
    client = docker.from_env()
except DockerException:
    print("Docker is not running / Connection refused", file=stderr)


# REST API server

@app.get(api_prefix + "/")
async def root():
    return {"message": "Server is running correctly"}


@app.get(api_prefix + "/container/{repo}")
async def get_container(repo: Repository, user_email: EmailStr):
    user = await user_db.get_by_email(user_email)
    if not user:
        return {"error": f"user {user_email} not found"}
    try:
        cnt = get_running_container(repo)
        # add container id to user's container_ids list
        user.container_ids.append(cnt['id'])
        await user_db.update(user)
        return {"repo": repo, "user": user_email, "cnt_id": cnt['id']}
    except APIError:
        return {"repo": repo, "error": "Cannot instantiate Docker container"}


@app.get(api_prefix + "/stream/{repo}")
async def get_container_stream(cnt_id: str, user_email: EmailStr):
    user = await user_db.get_by_email(user_email)
    if not user:
        return {"error": f"user {user_email} not found"}
    if cnt_id not in user.container_ids:
        return {"error": f"container {cnt_id} does not belong to user {user_email}"}
    try:
        cnt = client.containers.get(cnt_id)
        return StreamingResponse(cnt.attach(stdout=True, stderr=True, stream=True, demux=False))
    except APIError:
        return {"error": "Cannot instantiate stream to container"}


@app.delete(api_prefix + "/container/{repo}")
async def delete_container(cnt_id: str, user_email: EmailStr):
    user = await user_db.get_by_email(user_email)
    if not user:
        return {"error": f"user {user_email} not found"}
    try:
        cnt = client.containers.get(cnt_id)
        cnt.stop()
        # cnt.remove()  # not needed if auto_remove=True
        return {"user": user_email, "cnt_id": cnt_id}
    except NotFound:
        return {"error": f"Container {cnt_id} does not exist"}
    except APIError:
        return {"error": f"Cannot stop container {cnt_id} for user {user_email}"}



