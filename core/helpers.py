import csv
import html
from difflib import SequenceMatcher
import json
import re
import time
import unicodedata
from pathlib import Path

import ftfy
import requests

_session = requests.Session()
_session.headers.update({'User-Agent': 'PeledIndex/1.0 (mailto:your@email.com)'})

CROSSREF_URL = 'https://api.crossref.org/works'
PREPRINT_PLATFORM_NAMES = {'biorxiv', 'medrxiv', 'chemrxiv', 'arxiv'}
PREPRINT_PUBLICATION_TYPES = {'posted-content', 'preprint'}
PREPRINT_SUBTYPES = {'preprint'}


SCIMAGO_AREA_TO_FIELD = {
    'Agricultural and Biological Sciences':             'Life Sciences',
    'Biochemistry, Genetics and Molecular Biology':     'Life Sciences',
    'Environmental Science':                            'Life Sciences',
    'Immunology and Microbiology':                      'Life Sciences',
    'Medicine':                                         'Life Sciences',
    'Neuroscience':                                     'Life Sciences',
    'Nursing':                                          'Life Sciences',
    'Pharmacology, Toxicology and Pharmaceutics':       'Life Sciences',
    'Veterinary':                                       'Life Sciences',
    'Dentistry':                                        'Life Sciences',
    'Health Professions':                               'Life Sciences',
    'Earth and Planetary Sciences':                     'Life Sciences',
    'Chemistry':                                        'Physics and Chemistry',
    'Chemical Engineering':                             'Physics and Chemistry',
    'Materials Science':                                'Physics and Chemistry',
    'Physics and Astronomy':                            'Physics and Chemistry',
    'Energy':                                           'Physics and Chemistry',
    'Computer Science':                                 'Computer Science and Engineering',
    'Engineering':                                      'Computer Science and Engineering',
    'Mathematics':                                      'Computer Science and Engineering',
    'Arts and Humanities':                              'Social Sciences and Humanities',
    'Business, Management and Accounting':              'Social Sciences and Humanities',
    'Decision Sciences':                                'Social Sciences and Humanities',
    'Economics, Econometrics and Finance':              'Social Sciences and Humanities',
    'Psychology':                                       'Social Sciences and Humanities',
    'Social Sciences':                                  'Social Sciences and Humanities',
}

def _fetch_crossref_rows(title, author_name, rows):
	'Fetch a specific number of Crossref candidate records for one paper.'
	params = {
		'query.title': title,
		'query.author': author_name,
		'rows': rows,
	}
	for attempt in range(5):
		response = _session.get(CROSSREF_URL, params=params, timeout=60)
		if response.status_code == 429:
			time.sleep(2 ** attempt)
			continue
		response.raise_for_status()
		return response.json()['message']['items']
	return []



def normalize_text(text_value):
	'Normalize text for matching.'
	text_value = ftfy.fix_text(text_value)
	text_value = html.unescape(text_value)
	text_value = re.sub(r'<[^>]+>', ' ', text_value)
	text_value = unicodedata.normalize('NFKD', text_value)
	text_value = text_value.encode('ascii', 'ignore').decode('ascii')
	text_value = text_value.lower().strip()
	text_value = re.sub(r'[^\w\s]', ' ', text_value)
	return ' '.join(text_value.split())

TITLE_MATCH_THRESHOLD = 0.9

def titles_match(title_a, title_b):
	'Return whether two titles are similar enough to be considered a match.'
	norm_a = normalize_text(title_a)
	norm_b = normalize_text(title_b)
	return SequenceMatcher(None, norm_a, norm_b).ratio() >= TITLE_MATCH_THRESHOLD


def normalize_issn(issn_value):
	'Normalize ISSN values for matching.'
	return re.sub(r'[^0-9Xx]', '', issn_value).upper()


def parse_scimago_sjr(raw_sjr):
	'Convert SCImago SJR values to standard decimal format.'
	raw_sjr = raw_sjr.strip()
	if not raw_sjr:
		return ''
	normalized_sjr = raw_sjr.replace(',', '.')
	return f'{float(normalized_sjr):.3f}'


def parse_scimago_areas(raw_areas):
    'Convert raw SCImago Areas string to a sorted list of mapped fields.'
    if not raw_areas or not raw_areas.strip():
        return []
    mapped_fields = set()
    for area_name in raw_areas.split(';'):
        field = SCIMAGO_AREA_TO_FIELD.get(area_name.strip())
        if field:
            mapped_fields.add(field)
    return sorted(mapped_fields)


def extract_scimago_issns(raw_issn_value):
	'Extract normalized ISSN values from one SCImago field.'
	issn_values = []
	for issn_value in re.split(r'[\s,]+', raw_issn_value.strip()):
		normalized_issn = normalize_issn(issn_value)
		if normalized_issn:
			issn_values.append(normalized_issn)
	return issn_values


def load_scimago_data_by_issn(scimago_file_path):
    'Load SCImago SJR values and scientific fields by ISSN in one pass.'
    sjr_by_issn = {}
    fields_by_issn = {}
    with open(scimago_file_path, newline='', encoding='utf-8') as scimago_handle:
        reader = csv.DictReader(scimago_handle, delimiter=';')
        for row in reader:
            journal_sjr = parse_scimago_sjr(row.get('SJR', ''))
            journal_fields = parse_scimago_areas(row.get('Areas', ''))
            for journal_issn in extract_scimago_issns(row.get('Issn', '')):
                if journal_sjr:
                    sjr_by_issn.setdefault(journal_issn, journal_sjr)
                if journal_fields:
                    fields_by_issn.setdefault(journal_issn, journal_fields)
    return sjr_by_issn, fields_by_issn



def load_author_list(input_json_path):
	'Load the list of authors and their paper titles from the input JSON file.'
	with open(input_json_path, encoding='utf-8') as input_handle:
		return json.load(input_handle)


def save_results_json(output_path, results):
	'Save the scored author results to a JSON file.'
	with open(output_path, 'w', encoding='utf-8') as output_handle:
		json.dump(results, output_handle, indent=2, ensure_ascii=False)


def extract_name_parts(name_value):
	'Extract normalized first and last name parts.'
	name_value = normalize_text(name_value)
	name_parts = name_value.split()
	if not name_parts:
		return '', ''
	return name_parts[0], name_parts[-1]


def extract_crossref_author_name_parts(crossref_hit):
	'Extract normalized first and last name parts for Crossref authors.'
	author_name_parts = []
	for author in crossref_hit.get('author') or []:
		given_name = author.get('given', '')
		family_name = author.get('family', '')
		full_name = ' '.join(part for part in [given_name, family_name] if part).strip()
		if full_name:
			author_name_parts.append(extract_name_parts(full_name))
	return author_name_parts


def has_author_name_match(author_name, crossref_hit):
	'Return whether the query author matches by first or last name.'
	target_first_name, target_last_name = extract_name_parts(author_name)
	for crossref_first_name, crossref_last_name in extract_crossref_author_name_parts(crossref_hit):
		if target_first_name and target_first_name == crossref_first_name:
			return True
		if target_last_name and target_last_name == crossref_last_name:
			return True
	return False


def extract_crossref_title(crossref_hit):
	'Extract the first Crossref title value.'
	title_values = crossref_hit.get('title') or []
	if not title_values:
		return ''
	return title_values[0]


def extract_crossref_issns(crossref_hit):
	'Extract normalized ISSN values from one Crossref hit.'
	journal_issns = []
	for issn_value in crossref_hit.get('ISSN') or []:
		normalized_issn = normalize_issn(issn_value)
		if normalized_issn:
			journal_issns.append(normalized_issn)
	return journal_issns


def extract_crossref_year(crossref_hit):
	'Extract the publication year from a Crossref hit.'
	date_parts = (
		(crossref_hit.get('published') or {})
		.get('date-parts') or [[]]
	)[0]
	if not date_parts:
		return None
	return date_parts[0]


def extract_crossref_venue(crossref_hit):
	'Extract the journal or venue name from a Crossref hit.'
	container_titles = crossref_hit.get('container-title') or []
	if container_titles:
		return container_titles[0]
	return crossref_hit.get('publisher', '')


def extract_crossref_citations(crossref_hit):
	'Extract the citation count from a Crossref hit.'
	return crossref_hit.get('is-referenced-by-count') or 0


def extract_first_crossref_author_name(crossref_hit):
	'Extract the normalized full name of the first Crossref author.'
	authors = crossref_hit.get('author') or []
	if not authors:
		return ''
	first_author = authors[0]
	given_name = first_author.get('given', '')
	family_name = first_author.get('family', '')
	full_name = ' '.join(part for part in [given_name, family_name] if part).strip()
	if not full_name:
		return ''
	return normalize_text(full_name)


def extract_preprint_platform_name(crossref_hit):
	'Extract a normalized platform identifier from the matched Crossref record.'
	for institution_data in crossref_hit.get('institution') or []:
		institution_name = institution_data.get('name', '')
		normalized_institution_name = normalize_text(institution_name)
		for platform_name in PREPRINT_PLATFORM_NAMES:
			if platform_name in normalized_institution_name:
				return platform_name
	resource_data = crossref_hit.get('resource') or {}
	resource_primary = resource_data.get('primary') or {}
	resource_url = normalize_text(resource_primary.get('URL', ''))
	for platform_name in PREPRINT_PLATFORM_NAMES:
		if platform_name in resource_url:
			return platform_name
	return ''

def deduplicate_papers(papers):
	'Keep the first occurrence of each title.'
	seen_titles = set()
	unique_papers = []
	for paper in papers:
		title = paper['title']
		if title in seen_titles:
			continue
		seen_titles.add(title)
		unique_papers.append(paper)
	return unique_papers


def is_crossref_preprint(crossref_hit):
	'Return whether the matched Crossref record is a target preprint.'
	publication_type = crossref_hit.get('type', '')
	publication_subtype = crossref_hit.get('subtype', '')
	if publication_type not in PREPRINT_PUBLICATION_TYPES and publication_subtype not in PREPRINT_SUBTYPES:
		return False
	return bool(extract_preprint_platform_name(crossref_hit))


def build_doi_url(doi_value):
	'Build a DOI URL from a DOI string.'
	return f'https://doi.org/{doi_value}'


def build_match_data(crossref_hit, author_name):
	'Build the extracted metadata for one matched Crossref record.'
	doi_value = crossref_hit.get('DOI')
	journal_issns = extract_crossref_issns(crossref_hit)
	first_author_name = extract_first_crossref_author_name(crossref_hit)
	query_first_name, query_last_name = extract_name_parts(author_name)
	first_author_first_name, first_author_last_name = extract_name_parts(first_author_name)
	if first_author_name:
		is_first_author = (
			(query_first_name and query_first_name == first_author_first_name) or
			(query_last_name and query_last_name == first_author_last_name)
		)
	else:
		is_first_author = ''
	is_preprint = is_crossref_preprint(crossref_hit)
	year = extract_crossref_year(crossref_hit)
	venue = extract_crossref_venue(crossref_hit)
	citations = extract_crossref_citations(crossref_hit)
	return build_doi_url(doi_value), journal_issns, is_first_author, is_preprint, year, venue, citations

def _try_match_hits(crossref_hits, title, author_name):
	'Return the best match from a list of Crossref hits, or None.'
	fallback_match = None
	for crossref_hit in crossref_hits:
		crossref_title = extract_crossref_title(crossref_hit)
		doi_value = crossref_hit.get('DOI')
		publication_type = crossref_hit.get('type', '')
		if not titles_match(title, crossref_title):
			continue
		if not has_author_name_match(author_name, crossref_hit):
			continue
		if not doi_value:
			continue
		match_data = build_match_data(crossref_hit, author_name)
		if publication_type == 'journal-article':
			return match_data
		if fallback_match is None:
			fallback_match = match_data
	return fallback_match



def find_crossref_match(title, author_name):
	'Return the preferred Crossref match for one paper. Try top-1 first, then next 3.'
	no_match = ('', [], '', False, None, '', 0)
	first_hit = _fetch_crossref_rows(title, author_name, 1)
	result = _try_match_hits(first_hit, title, author_name)
	if result is not None:
		return result
	extra_hits = _fetch_crossref_rows(title, author_name, 4)
	result = _try_match_hits(extra_hits[1:], title, author_name)
	if result is not None:
		return result
	return no_match


def find_journal_sjr(journal_issns, scimago_sjr_by_issn):
	'Return the first SCImago SJR value matched by ISSN.'
	for journal_issn in journal_issns:
		if journal_issn in scimago_sjr_by_issn:
			return scimago_sjr_by_issn[journal_issn]
	return ''

def find_journal_fields(journal_issns, scimago_fields_by_issn):
    'Return the list of scientific fields matched by ISSN.'
    for journal_issn in journal_issns:
        if journal_issn in scimago_fields_by_issn:
            return scimago_fields_by_issn[journal_issn]
    return []


def rank_fields_by_paper_count(papers, scimago_fields_by_issn):
	'Return fields sorted by how many papers belong to each, descending.'
	field_paper_counts = {}
	for paper in papers:
		for field in find_journal_fields(paper.get('journal_issns', []), scimago_fields_by_issn):
			field_paper_counts[field] = field_paper_counts.get(field, 0) + 1
	return sorted(field_paper_counts, key=field_paper_counts.get, reverse=True)