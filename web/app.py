import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List
from fastapi import UploadFile, File
import shutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.helpers import load_scimago_data_by_issn
from web.api.routes import router
from web.utils import make_author_id

RESULTS_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'phd_isr_res_filtered.json')
SCIMAGO_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'scimagojr2024.csv')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')


def _build_index(results: List[dict]) -> Dict[str, dict]:
    """Build an in-memory lookup dict keyed by author ID."""
    index: Dict[str, dict] = {}
    for entry in results:
        author_id = make_author_id(entry['name'], entry.get('institution', ''))
        index[author_id] = entry
    return index

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.path.exists(RESULTS_JSON_PATH):
        with open(RESULTS_JSON_PATH, encoding='utf-8') as f:
            results = json.load(f)
            app.state.results = results
            app.state.index = _build_index(results)
            app.state.scimago_sjr_by_issn, app.state.scimago_fields_by_issn = load_scimago_data_by_issn(SCIMAGO_CSV_PATH)
            app.state.current_year = datetime.now().year
            app.state.serpapi_key = os.environ.get('SERPAPI_KEY', '')
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = f"/data/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "path": file_path}

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     with open(RESULTS_JSON_PATH, encoding='utf-8') as f:
#         results = json.load(f)
#     app.state.results = results
#     app.state.index = _build_index(results)
#     app.state.scimago_sjr_by_issn, app.state.scimago_fields_by_issn = load_scimago_data_by_issn(SCIMAGO_CSV_PATH)
#     app.state.current_year = datetime.now().year
#     app.state.serpapi_key = os.environ.get('SERPAPI_KEY', '')
#     yield


# app = FastAPI(title='Peled Index API', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router, prefix='/api')

app.mount('/', StaticFiles(directory=STATIC_DIR, html=True), name='static')
