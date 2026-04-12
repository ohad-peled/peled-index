import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.helpers import load_scimago_data_by_issn
from web.api.routes import router
from web.utils import make_author_id

RESULTS_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'phd_isr_res_filtered.json')
SCHOLAR_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'scholar_results.json')
SCIMAGO_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'scimagojr2024.csv')
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')


def _build_index(results):
	"""Build an in-memory lookup dict keyed by author ID."""
	index = {}
	for entry in results:
		author_id = make_author_id(entry['name'], entry.get('institution', ''))
		index[author_id] = entry
	return index


def _load_json_file(path):
	"""Load a JSON array from disk, returning empty list if file missing or invalid."""
	if not os.path.exists(path):
		return []
	with open(path, encoding='utf-8') as f:
		return json.load(f)


def _merge_results(precomputed, scholar):
	"""Merge precomputed and scholar results, with scholar entries taking precedence on collision."""
	index = _build_index(precomputed)
	for entry in scholar:
		author_id = make_author_id(entry['name'], entry.get('institution', ''))
		index[author_id] = entry
	return list(index.values())


def load_results_into_state(app):
	"""Load precomputed and scholar results from disk into app state."""
	precomputed = _load_json_file(RESULTS_JSON_PATH)
	scholar = _load_json_file(SCHOLAR_JSON_PATH)
	merged = _merge_results(precomputed, scholar)
	app.state.results = merged
	app.state.index = _build_index(merged)
	return len(merged)


@asynccontextmanager
async def lifespan(app):
	load_results_into_state(app)
	app.state.scimago_sjr_by_issn, app.state.scimago_fields_by_issn = load_scimago_data_by_issn(SCIMAGO_CSV_PATH)
	app.state.current_year = datetime.now().year
	app.state.serpapi_key = os.environ.get('SERPAPI_KEY', '')
	yield


app = FastAPI(title='Peled Index API', lifespan=lifespan)

app.add_middleware(
	CORSMiddleware,
	allow_origins=['*'],
	allow_methods=['*'],
	allow_headers=['*'],
)

app.include_router(router, prefix='/api')


@app.get('/api/startup-info')
def startup_info():
	"""Return the filenames of the data sources used by this app."""
	return {
		'results_json': os.path.basename(RESULTS_JSON_PATH),
		'scholar_json': os.path.basename(SCHOLAR_JSON_PATH),
		'scimago_csv': os.path.basename(SCIMAGO_CSV_PATH),
	}


@app.post('/api/admin/reload')
def admin_reload(x_admin_key: str = Header(...)):
	"""Re-read all JSON data files from disk into app state."""
	admin_key = os.environ.get('ADMIN_KEY', '')
	if not admin_key or x_admin_key != admin_key:
		raise HTTPException(status_code=403, detail='Invalid admin key')
	author_count = load_results_into_state(app)
	return {'reloaded': True, 'authors_loaded': author_count}


app.mount('/', StaticFiles(directory=STATIC_DIR, html=True), name='static')
