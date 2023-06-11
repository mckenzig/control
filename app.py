from fastapi import FastAPI
from pyTigerGraph import TigerGraphConnection
from fastapi.staticfiles import StaticFiles
import os
from fastapi.responses import FileResponse
from fastapi import Depends
from typing import Annotated
from dotenv import load_dotenv
from pydantic import BaseModel


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class Catalog(BaseModel):
    id: str
    title: str = ""
    description: str = ""

def get_connection():
    load_dotenv()  # take environment variables from .env.
    conn = TigerGraphConnection(host=os.environ.get("TG_HOST"), 
                                graphname=os.environ.get("TG_GRAPH"), 
                                username=os.environ.get("TG_USERNAME"), 
                                password=os.environ.get("TG_PASSWORD")) 
    conn.getToken(os.environ.get("TG_SECRET"))
    return conn


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    file_name = "favicon.ico"
    file_path = os.path.join(app.root_path, "static", file_name)
    print(file_path)
    return FileResponse(path=file_path, headers={"Content-Disposition": "attachment; filename=" + file_name})



@app.get("/graph")
async def graph(conn: Annotated[object, Depends(get_connection)]):
    return conn.getVertexTypes()


@app.post("/catalog")
async def post_catalog(conn: Annotated[object, Depends(get_connection)], catalog:Catalog):
    attributes = catalog.dict()
    if 'id' in attributes:
        del attributes['id']
    return conn.upsertVertex(vertexType = 'Catalog', vertexId = catalog.id, attributes = attributes)


@app.get("/catalog")
async def get_catalog(conn: Annotated[object, Depends(get_connection)]):
    return conn.getVertices(vertexType='Catalog')
