from datetime import datetime
from helpers import (
	PAGE_SIZE,
	deduplicate_papers,
	extract_author_file_name,
	extract_author_name,
	extract_scholar_papers,
	fetch_author_page,
	find_crossref_match,
	find_journal_sjr,
	has_next_page,
	load_scimago_sjr_by_issn,
	save_papers_csv,
	save_raw_data,
)


def add_paper_metadata(papers, author_name, scimago_sjr_by_issn):
	'Add DOI URLs, SJR values, first-author status, and preprint status.'
	papers_with_metadata = []
	for paper in papers:
		paper_url, journal_issns, is_first_author, is_preprint = find_crossref_match(paper['title'], author_name)
		paper_with_metadata = dict(paper)
		paper_with_metadata['paper_url'] = paper_url
		paper_with_metadata['journal_sjr'] = find_journal_sjr(journal_issns, scimago_sjr_by_issn)
		paper_with_metadata['is_first_author'] = is_first_author
		paper_with_metadata['is_preprint'] = is_preprint
		papers_with_metadata.append(paper_with_metadata)
	return papers_with_metadata


def collect_author_papers(api_key, author_id):
	'Fetch all Scholar pages and return the author metadata and unique papers.'
	start = 0
	raw_pages = []
	all_papers = []
	author_name = None
	while True:
		page_data = fetch_author_page(api_key, author_id, start)
		if author_name is None:
			author_name = extract_author_name(page_data)
		raw_pages.append(page_data)
		all_papers.extend(extract_scholar_papers(page_data))
		if not has_next_page(page_data):
			break
		start += PAGE_SIZE
	author_file_name = extract_author_file_name(author_name)
	return author_name, author_file_name, raw_pages, deduplicate_papers(all_papers)


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

def run_pipeline(api_key, author_id, output_directory, scimago_file_path):
	'Run the Scholar, Crossref, and SCImago pipeline for one author.'
	scimago_sjr_by_issn = load_scimago_sjr_by_issn(scimago_file_path)
	author_name, author_file_name, raw_pages, papers = collect_author_papers(api_key, author_id)
	papers = add_paper_metadata(papers, author_name, scimago_sjr_by_issn)
	current_year = datetime.now().year
	author_score = compute_author_score(papers, current_year)
	raw_path = save_raw_data(output_directory, author_file_name, author_id, raw_pages)
	csv_path = save_papers_csv(output_directory, author_file_name, papers)
	return {
		'author_id': author_id,
		'author_name': author_name,
		'total_papers': len(papers),
		'author_score': author_score,
		'papers_csv_path': str(csv_path),
		'raw_json_path': str(raw_path),
	}