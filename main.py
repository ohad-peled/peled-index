import json
from pipeline import run_pipeline


def main():
	input_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\phd_2022.json'
	output_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\out\\phd_2022_res.json'
	scimago_file_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\scimagojr2024.csv'
	results = run_pipeline(input_json_path, output_json_path, scimago_file_path)
	print(json.dumps(results, indent=2))


if __name__ == '__main__':
	main()

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