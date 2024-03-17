from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated

from sqlalchemy.orm import Session

import models
from database import engine, SessionLocal
app = FastAPI()
models.Base.metadata.create_all(bind=engine)


class PostBase(BaseModel):
    title: str
    content: str
    user_id: int


class UserBase(BaseModel):
    username: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_Dependency = Annotated[Session, Depends(get_db)]

# * Create


@app.post('/posts', tags=["Posts"], status_code=status.HTTP_201_CREATED)
async def create_post(post: PostBase, db: db_Dependency):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()


@app.post('/users', tags=["Users"], status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_Dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()


# * Read

@app.get('/users/{user_id}', tags=['Users'], status_code=status.HTTP_200_OK)
async def get_users(user_id: int, db: db_Dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    handle_error(user, "User don't found🥰")
    return user


@app.get('/posts/{post_id}', tags=['Posts'], status_code=status.HTTP_200_OK)
async def get_posts(post_id: int, db: db_Dependency):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    handle_error(post, "This post is invalid🥱")
    return post


# * Delete
@app.delete('/posts{post_id}', tags=['Posts'], status_code=status.HTTP_200_OK)
async def delete_post(post_id: int, db: db_Dependency):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    handle_error(db_post, "Post was not found🫠")
    db.delete(db_post)
    db.commit()

# * Handling errors


def handle_error(condition, message: str):
    if condition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )
