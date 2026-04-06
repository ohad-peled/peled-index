from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from web.api.handlers import get_author, generate_plot, search_authors, scrape_and_score_scholar_author

router = APIRouter(prefix='/authors', tags=['authors'])


class ScholarRequest(BaseModel):
    scholar_id: str


@router.get('/search')
def search(request: Request, query: str = Query(..., min_length=1)):
    """Search authors by name (case-insensitive substring match)."""
    return search_authors(query, request.app.state.index)


@router.post('/scholar')
def scholar_scrape(body: ScholarRequest, request: Request):
    """Scrape a Google Scholar profile and return the scored author entry."""
    state = request.app.state
    if not state.serpapi_key:
        raise HTTPException(status_code=500, detail='SERPAPI_KEY not configured')
    result = scrape_and_score_scholar_author(
        body.scholar_id,
        state.serpapi_key,
        state.scimago_sjr_by_issn,
        state.scimago_fields_by_issn,
        state.current_year,
        state.results,
        state.index,
    )
    if result is None:
        raise HTTPException(status_code=404, detail='No papers found for this Scholar ID')
    return result


@router.get('/{author_id}')
def author_detail(author_id: str, request: Request):
    """Return full details for a specific author."""
    result = get_author(author_id, request.app.state.index)
    if result is None:
        raise HTTPException(status_code=404, detail='Author not found')
    return result


@router.get('/{author_id}/plot')
def author_plot(author_id: str, request: Request):
    """Generate and return a plot for an author in their primary field as Base64 PNG."""
    result = generate_plot(author_id, request.app.state.results, request.app.state.index)
    if result is None:
        raise HTTPException(status_code=404, detail='Author not found')
    if 'error' in result:
        raise HTTPException(status_code=422, detail=result['error'])
    return result

