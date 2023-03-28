from typing import List

import requests
from bs4 import BeautifulSoup
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import schemas
from db import Base, SessionLocal, engine
from models import URL

Base.metadata.create_all(engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")


configure_static(app)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_unique_tags_count(url):
    page = requests.get(url.url)
    soup = BeautifulSoup(page.text, 'html.parser')
    tags = soup.find_all()

    tag_counts = {'id': url.id, 'url': url.url}
    for tag in tags:
        tag_name = tag.name
        if tag_name not in tag_counts:
            tag_counts[tag_name] = {"count": 1, "nested": 0}
        else:
            tag_counts[tag_name]["count"] += 1

        nested_count = len(tag.find_all())
        if nested_count > 0:
            tag_counts[tag_name]["nested"] += nested_count

    return tag_counts


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("homepage.html", {"request": request})


@app.post("/url", response_model=schemas.URls, status_code=status.HTTP_201_CREATED)
def create_url(url: schemas.URLsCreate, session: Session = Depends(get_session)):
    urldb = URL(url=url.url)
    try:
        response = requests.get(urldb.url)
        if response.status_code == 200:
            session.add(urldb)
            session.commit()
            session.refresh(urldb)
            return urldb
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


@app.get("/url/{id}")
def read_url(id: int):
    # create a new database session
    session = SessionLocal()

    url = session.query(URL).get(id)
    res = get_unique_tags_count(url)
    # close the session
    session.close()

    if not url:
        raise HTTPException(status_code=404, detail=f"todo item with id {id} not found")

    return res


# @app.put("/url/{id}")
# def update_url(id: int):
#     # create a new database session
#     session = SessionLocal()
#
#     url = session.query(URL).get(id)
#
#     if url:
#         url.url = url
#         session.commit()
#
#     # close the session
#     session.close()
#
#     if not url:
#         raise HTTPException(status_code=404, detail=f"url item with id {id} not found")
#
#     return url


@app.delete("/url/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_url(id: int):
    # create a new database session
    session = SessionLocal()

    url = session.query(URL).get(id)

    if url:
        session.delete(url)
        session.commit()
        session.close()
    else:
        raise HTTPException(status_code=404, detail=f"url item with id {id} not found")

    return None


@app.get("/url", response_model=List[schemas.URls])
def read_url_list(request: Request):
    # create a new database session
    session = SessionLocal()

    url_list = session.query(URL).all()

    # close the session
    session.close()

    return url_list
    # return templates.TemplateResponse(
    #     "homepage.html", {"request": request, "url_list": url_list}
    # )
