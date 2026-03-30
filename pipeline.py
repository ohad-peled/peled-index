from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from helpers import (
    deduplicate_papers,
    find_crossref_match,
    find_journal_fields,
    find_journal_sjr,
    load_author_list,
    load_scimago_data_by_issn,
    save_results_json,
)


from concurrent.futures import ThreadPoolExecutor


def build_papers_from_titles(titles, author_name, scimago_sjr_by_issn, scimago_fields_by_issn, max_workers=8):
    'Fetch and enrich all papers for one author from Crossref and SCImago.'
    def process_title(title):
        paper_url, journal_issns, is_first_author, is_preprint, year, venue, citations = find_crossref_match(title, author_name)
        return {
            'title': title,
            'year': year,
            'venue_raw': venue,
            'citations': citations,
            'paper_url': paper_url,
            'journal_sjr': find_journal_sjr(journal_issns, scimago_sjr_by_issn),
            'journal_issns': journal_issns,
            'is_first_author': is_first_author,
            'is_preprint': is_preprint,
        }
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        papers = list(executor.map(process_title, titles))
    return deduplicate_papers(papers)


def parse_year(year_value):
	'Parse a paper year to int.'
	try:
		return int(year_value)
	except (TypeError, ValueError):
		return None


def parse_int(value):
	'Parse a numeric value to int.'
	try:
		return int(value)
	except (TypeError, ValueError):
		return 0


def parse_float(value):
	'Parse a numeric value to float.'
	try:
		return float(value)
	except (TypeError, ValueError):
		return None


def compute_author_score(papers, current_year):
	'Compute the raw author score from the paper table.'
	publication_years = []
	paper_scores = []
	for paper in papers:
		paper_year = parse_year(paper.get('year'))
		if paper_year is not None:
			publication_years.append(paper_year)
		journal_sjr = parse_float(paper.get('journal_sjr'))
		if journal_sjr is None or paper_year is None:
			continue
		paper_age = current_year - paper_year + 1
		if paper_age <= 0:
			continue
		citations = parse_int(paper.get('citations'))
		citations_per_year = citations / paper_age
		is_first_author = paper.get('is_first_author')
		authorship_weight = 1.0 if is_first_author is True or is_first_author == 'True' else 0.4
		paper_score = authorship_weight * (
			(0.6 * citations_per_year) +
			(0.4 * journal_sjr)
		)
		paper_scores.append(paper_score)
	if not publication_years:
		return 0.0
	active_years = current_year - min(publication_years) + 1
	if active_years <= 0:
		return 0.0
	return round(sum(paper_scores) / active_years, 6)


def score_author(author_entry, scimago_sjr_by_issn, scimago_fields_by_issn, current_year):
    'Build and score one author entry from the input JSON.'
    author_name = author_entry['name']
    papers = build_papers_from_titles(author_entry['publications'], author_name, scimago_sjr_by_issn, scimago_fields_by_issn)
    author_score = compute_author_score(papers, current_year)
    author_fields = sorted({
        field
        for paper in papers
        for field in find_journal_fields(paper.pop('journal_issns', []), scimago_fields_by_issn)
    })
    return {
        'name': author_name,
        'institution': author_entry.get('institution', ''),
        'author_score': author_score,
        'total_papers': len(papers),
        'fields': author_fields,
        'papers': papers,
    }



def run_pipeline(input_json_path, output_json_path, scimago_file_path):
    'Run the Crossref and SCImago pipeline for all authors in the input file.'
    scimago_sjr_by_issn, scimago_fields_by_issn = load_scimago_data_by_issn(scimago_file_path)
    author_list = load_author_list(input_json_path)
    current_year = datetime.now().year
    results = []
    for author_index, author_entry in enumerate(author_list, start=1):
        print(f'Processing author {author_index}: {author_entry["name"]}')
        results.append(score_author(author_entry, scimago_sjr_by_issn, scimago_fields_by_issn, current_year))
    save_results_json(output_json_path, results)
    return results

