from fastapi import APIRouter, HTTPException, Query, Request

from web.api.handlers import get_author, generate_plot, search_authors

router = APIRouter(prefix='/authors', tags=['authors'])


@router.get('/search')
def search(request: Request, query: str = Query(..., min_length=1)):
    """Search authors by name (case-insensitive substring match)."""
    return search_authors(query, request.app.state.index)


@router.get('/{author_id}')
def author_detail(author_id: str, request: Request):
    """Return full details for a specific author."""
    result = get_author(author_id, request.app.state.index)
    if result is None:
        raise HTTPException(status_code=404, detail='Author not found')
    return result


@router.get('/{author_id}/plot/{field}')
def author_plot(author_id: str, field: str, request: Request):
    """Generate and return a plot for an author in a given field as Base64 PNG."""
    result = generate_plot(author_id, field, request.app.state.results, request.app.state.index)
    if result is None:
        raise HTTPException(status_code=404, detail='Author not found')
    if 'error' in result:
        raise HTTPException(status_code=422, detail=result['error'])
    return result
