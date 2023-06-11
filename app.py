from fastapi import FastAPI
from pyTigerGraph import TigerGraphConnection
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import Depends
from typing import Annotated, List
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import datetime
import os
import logging

logging.basicConfig(level=os.environ.get("TG_LOG_LEVEL", "INFO"))


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


class DataService(BaseModel):
    id: str
    endpoint_description: str = ""
    endpointURL: str = ""
    keywords: List[str] = []
    landing_page: str = ""
    title: str = ""
    description: str = ""
    issued: datetime = datetime.utcnow()
    modified: datetime = datetime.utcnow()
    language: str = ""
    license: str = ""


class Distribution(BaseModel):
    id: str
    title: str = ""
    description: str = ""
    accessURL: str = ""
    downloadURL: str = ""
    format: str = ""


class Dataset(BaseModel):
    id: str
    title: str = ""
    description: str = ""
    issued: datetime = datetime.utcnow()
    modified: datetime = datetime.utcnow()
    language: str = ""
    keywords: List[str] = []
    license: str = ""


class Catalog(BaseModel):
    id: str
    title: str = ""
    description: str = ""
    issued: datetime = datetime.utcnow()
    modified: datetime = datetime.utcnow()
    language: str = ""
    homepage: str = ""
    license: str = ""


def get_connection():
    load_dotenv()  # take environment variables from .env.
    host = os.environ.get("TG_HOST")
    graph = os.environ.get("TG_GRAPH")
    username = os.environ.get("TG_USERNAME")
    password = os.environ.get("TG_PASSWORD")
    secret = os.environ.get("TG_SECRET")
    logger = logging.getLogger(__file__)
    logger.info(
        "host %s, graph %s, username %s, password %s", host, graph, username, password
    )
    conn = TigerGraphConnection(
        host=host,
        graphname=graph,
        username=username,
        password=password,
    )
    conn.getToken(secret)
    return conn


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    file_name = "favicon.ico"
    file_path = os.path.join(app.root_path, "static", file_name)
    print(file_path)
    return FileResponse(
        path=file_path,
        headers={"Content-Disposition": "attachment; filename=" + file_name},
    )


def to_attrs(d: dict) -> dict:
    if "id" in d:
        del d["id"]
    d1 = {}
    for k, v in d.items():
        d1[k] = v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else v
    return d1


@app.post("/catalog")
async def post_catalog(
    conn: Annotated[object, Depends(get_connection)], catalog: Catalog
):
    return conn.upsertVertex(
        vertexType="Catalog", vertexId=catalog.id, attributes=to_attrs(catalog.dict())
    )


@app.get("/catalog")
async def get_catalog(
    conn: Annotated[object, Depends(get_connection)]
) -> List[Catalog]:
    catalogs = []
    for catalog in conn.getVertices(vertexType="Catalog"):
        attrs = catalog["attributes"]
        catalog = Catalog(
            id=catalog["v_id"],
            title=attrs.get("title", ""),
            description=attrs.get("description", ""),
            language=attrs.get("language", ""),
            license=attrs.get("license", ""),
            homepage=attrs.get("homepage", ""),
            issued=datetime.strptime(
                attrs.get("issued", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"
            ),
            modified=datetime.strptime(
                attrs.get("modified", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"
            ),
        )
        catalogs.append(catalog)
    return catalogs


@app.post("/dataset")
async def post_dataset(
    conn: Annotated[object, Depends(get_connection)], dataset: Dataset
):
    attrs = to_attrs(dataset.dict())
    return conn.upsertVertex(
        vertexType="Dataset", vertexId=dataset.id, attributes=attrs
    )


@app.get("/dataset")
async def get_dataset(
    conn: Annotated[object, Depends(get_connection)]
) -> List[Dataset]:
    datasets = []
    for dataset in conn.getVertices(vertexType="Dataset"):
        attrs = dataset["attributes"]
        dataset = Dataset(
            id=dataset["v_id"],
            title=attrs.get("title", ""),
            description=attrs.get("description", ""),
            language=attrs.get("language", ""),
            license=attrs.get("license", ""),
            keywords=attrs.get("keywords", []),
            issued=datetime.strptime(
                attrs.get("issued", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"
            ),
            modified=datetime.strptime(
                attrs.get("modified", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"
            ),
        )
        datasets.append(dataset)
    return datasets


@app.post("/distribution")
async def post_distribution(
    conn: Annotated[object, Depends(get_connection)], distribution: Distribution
):
    attrs = to_attrs(distribution.dict())
    return conn.upsertVertex(
        vertexType="Distribution", vertexId=distribution.id, attributes=attrs
    )


@app.get("/distribution")
async def get_distribution(
    conn: Annotated[object, Depends(get_connection)]
) -> List[Distribution]:
    distributions = []
    for distribution in conn.getVertices(vertexType="Distribution"):
        attrs = distribution["attributes"]
        distribution1 = Distribution(
            id=distribution["v_id"],
            title=attrs.get("title", ""),
            description=attrs.get("description", ""),
            accessURL=attrs.get("accessURL", ""),
            downloadURL=attrs.get("downloadURL", ""),
            format=attrs.get("format", ""),
        )
        distributions.append(distribution1)
    return distributions


@app.post("/service")
async def post_service(
    conn: Annotated[object, Depends(get_connection)], service: DataService
):
    attrs = to_attrs(service.dict())
    return conn.upsertVertex(
        vertexType="Service", vertexId=service.id, attributes=attrs
    )


@app.get("/service")
async def get_service(
    conn: Annotated[object, Depends(get_connection)]
) -> List[DataService]:
    services = []
    for service in conn.getVertices(vertexType="Service"):
        attrs = service["attributes"]
        service1 = DataService(
            id=service["v_id"],
            endpoint_description=attrs.get("endpoint_description", ""),
            endpointURL=attrs.get("endpointURL", ""),
            keywords=attrs.get("keywords", []),
            landing_page=attrs.get("landing_page", ""),
            title=attrs.get("title", ""),
            description=attrs.get("description", ""),
            issued=datetime.strptime(
                attrs.get("issued", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"
            ),
            modified=datetime.strptime(
                attrs.get("modified", "1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"
            ),
            language=attrs.get("language", ""),
            license=attrs.get("license", ""),
        )
        services.append(service1)
    return services
