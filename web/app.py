import json
import os
from contextlib import asynccontextmanager
from typing import Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from web.api.routes import router
from web.utils import make_author_id

RESULTS_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'phd_2010-2025_isr_res.json')
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
    with open(RESULTS_JSON_PATH, encoding='utf-8') as f:
        results = json.load(f)
    app.state.results = results
    app.state.index = _build_index(results)
    yield


app = FastAPI(title='Peled Index API', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['GET'],
    allow_headers=['*'],
)

app.include_router(router, prefix='/api')

app.mount('/', StaticFiles(directory=STATIC_DIR, html=True), name='static')
