from fastapi import FastAPI
from pyTigerGraph import TigerGraphConnection
from fastapi.staticfiles import StaticFiles
import os
from fastapi.responses import FileResponse
from dotenv import load_dotenv

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


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
async def graph():
    load_dotenv()  # take environment variables from .env.
    conn = TigerGraphConnection(host=os.environ.get("TG_HOST"), 
                                graphname=os.environ.get("TG_GRAPH"), 
                                username=os.environ.get("TG_USERNAME"), 
                                password=os.environ.get("TG_PASSWORD")) 
    conn.getToken(os.environ.get("TG_SECRET"))
    return conn.getVertexTypes()
