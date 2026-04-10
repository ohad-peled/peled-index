# import json
# from pipeline import run_pipeline
#
# def main():
# 	input_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\phd_isr.json'
# 	output_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\out\\phd_isr_res2.json'
# 	scimago_file_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\scimagojr2024.csv'
# 	results = run_pipeline(input_json_path, output_json_path, scimago_file_path)
# 	print(json.dumps(results, indent=2))
#
# if __name__ == '__main__':
# 	main()


import json
from datetime import datetime
from pipeline import (
	load_author_list,
	load_scimago_data_by_issn,
	score_author,
	save_results_json,
)


def main_debug_20():
	input_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\phd_isr.json'
	output_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\out\\phd_isr_res_debug_20.json'
	scimago_file_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\scimagojr2024.csv'
	scimago_sjr_by_issn, scimago_fields_by_issn = load_scimago_data_by_issn(scimago_file_path)
	author_list = load_author_list(input_json_path)
	current_year = datetime.now().year
	results = []
	for author_index, author_entry in enumerate(author_list[:20], start=1):
		author_name = author_entry['name']
		print(f'[{author_index}] Processing: {author_name}')
		result = score_author(author_entry, scimago_sjr_by_issn, scimago_fields_by_issn, current_year, False)
		results.append(result)
		print(f'    Papers: {result["total_papers"]}')
		print(f'    Fields: {result["fields"]}')
		print(f'    Author Score: {result["author_score"]}\n')
	# save_results_json(output_json_path, results)
if __name__ == '__main__':
	main_debug_20()


# import json
# input_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\out\\phd_isr_res.json'
# output_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\out\\phd_isr_res_filtered.json'
# with open(input_json_path, "r", encoding="utf-8") as f:
#     data = json.load(f)
# filtered_data = [author for author in data if author["author_score"] != 0]
# with open(output_json_path, "w", encoding="utf-8") as f:
#     json.dump(filtered_data, f, ensure_ascii=False, indent=2)
# print(f"Kept {len(filtered_data)} of {len(data)} authors")