import requests

from core.helpers import normalize_text


SERPAPI_URL = 'https://serpapi.com/search.json'
SCHOLAR_PAGE_SIZE = 100


def fetch_scholar_page(serpapi_key, scholar_id, start):
	'Fetch one page of articles from a Google Scholar author profile via SerpAPI.'
	params = {
		'engine': 'google_scholar_author',
		'author_id': scholar_id,
		'api_key': serpapi_key,
		'num': SCHOLAR_PAGE_SIZE,
		'start': start,
	}
	response = requests.get(SERPAPI_URL, params=params, timeout=60)
	response.raise_for_status()
	return response.json()


def extract_scholar_author_name(page_data):
	'Extract the author name from a Scholar profile response.'
	return page_data.get('author', {}).get('name', '')


def extract_scholar_institution(page_data):
	'Extract the affiliation string from a Scholar profile response.'
	return page_data.get('author', {}).get('affiliations', '')


def extract_scholar_paper_titles(page_data):
	'Extract paper titles from one page of Scholar articles.'
	titles = []
	for article in page_data.get('articles', []):
		title = article.get('title', '').strip()
		if title:
			titles.append(title)
	return titles


def has_next_page(page_data):
	'Return whether SerpAPI indicates another page is available.'
	pagination = page_data.get('serpapi_pagination') or {}
	return bool(pagination.get('next') or pagination.get('next_link'))


def deduplicate_titles(titles):
	'Keep the first occurrence of each normalized title.'
	seen_normalized = set()
	unique_titles = []
	for title in titles:
		normalized = normalize_text(title)
		if normalized in seen_normalized:
			continue
		seen_normalized.add(normalized)
		unique_titles.append(title)
	return unique_titles


def fetch_all_scholar_papers(serpapi_key, scholar_id):
	'Fetch all paper titles and profile info for a Google Scholar author.'
	start = 0
	all_titles = []
	author_name = ''
	institution = ''
	while True:
		page_data = fetch_scholar_page(serpapi_key, scholar_id, start)
		if not author_name:
			author_name = extract_scholar_author_name(page_data)
			institution = extract_scholar_institution(page_data)
		page_titles = extract_scholar_paper_titles(page_data)
		if not page_titles:
			break
		all_titles.extend(page_titles)
		if not has_next_page(page_data):
			break
		start += SCHOLAR_PAGE_SIZE
	return author_name, institution, deduplicate_titles(all_titles)


def search_scholar_by_name(serpapi_key, author_name):
	'''Search Google Scholar for author name candidates.
	Returns a list of dicts with author_id, name, and sample_paper_title.
	'''
	params = {
		'engine': 'google_scholar',
		'q': 'author:"' + author_name + '"',
		'api_key': serpapi_key,
		'num': 20,
	}
	response = requests.get(SERPAPI_URL, params=params, timeout=60)
	response.raise_for_status()
	data = response.json()
	return _extract_unique_candidates(data.get('organic_results', []))


def _extract_unique_candidates(organic_results):
	'''Extract unique author candidates from organic search results.'''
	candidates_by_id = {}
	for result in organic_results:
		paper_title = result.get('title', '')
		for author in result.get('publication_info', {}).get('authors', []):
			author_id = author.get('author_id')
			if not author_id:
				continue
			if author_id not in candidates_by_id:
				candidates_by_id[author_id] = {
					'author_id': author_id,
					'name': author.get('name', ''),
					'sample_paper_title': paper_title,
				}
	return list(candidates_by_id.values())
