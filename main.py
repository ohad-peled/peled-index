import json
from pipeline import run_pipeline


def main():
	input_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\phd_2010-2025_isr_noyear.json'
	# input_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\test.json'
	output_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\out\\phd_2010-2025_isr_noyear.json'
	scimago_file_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\scimagojr2024.csv'
	results = run_pipeline(input_json_path, output_json_path, scimago_file_path)
	print(json.dumps(results, indent=2))

if __name__ == '__main__':
	main()





# from helpers import load_author_list
# def summarize_zero_publication_authors(input_json_paths):
# 	'Print the share of authors with zero publications in one or more input files.'
# 	if isinstance(input_json_paths, str):
# 		input_json_paths = [input_json_paths]
# 	overall_author_count = 0
# 	overall_zero_publication_count = 0
# 	for input_json_path in input_json_paths:
# 		author_list = load_author_list(input_json_path)
# 		author_count = len(author_list)
# 		zero_publication_count = sum(
# 			1
# 			for author_entry in author_list
# 			if not author_entry.get('publications')
# 		)
# 		zero_publication_percent = (
# 			100 * zero_publication_count / author_count
# 			if author_count else 0.0
# 		)
# 		overall_author_count += author_count
# 		overall_zero_publication_count += zero_publication_count
# 		print(f'File: {input_json_path}')
# 		print(f'Authors total: {author_count}')
# 		print(f'Authors with 0 publications: {zero_publication_count}')
# 		print(f'Percent with 0 publications: {zero_publication_percent:.2f}%')
# 		print()
# 	overall_zero_publication_percent = (
# 		100 * overall_zero_publication_count / overall_author_count
# 		if overall_author_count else 0.0
# 	)
# 	print(f'Authors total: {overall_author_count}')
# 	print(f'Authors with 0 publications: {overall_zero_publication_count}')
# 	print(f'Percent with 0 publications: {overall_zero_publication_percent:.2f}%')
# summarize_zero_publication_authors('phd_2010-2025_isr.json')

#
# import json
# from pipeline import run_pipeline, score_author
# from helpers import load_author_list, load_scimago_sjr_by_issn
# from datetime import datetime
#
#
# def main():
# 	input_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\phd_2022.json'
# 	output_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\out\\results.json'
# 	scimago_file_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\scimagojr2024.csv'
# 	test_author_name = 'Ohad Peled'
# 	author_list = load_author_list(input_json_path)
# 	author_entry = next((a for a in author_list if a['name'] == test_author_name), None)
# 	if author_entry is None:
# 		print(f'Author not found: {test_author_name}')
# 		return
# 	scimago_sjr_by_issn = load_scimago_sjr_by_issn(scimago_file_path)
# 	result = score_author(author_entry, scimago_sjr_by_issn, datetime.now().year)
# 	print(json.dumps(result, indent=2))
#
#
# if __name__ == '__main__':
# 	main()