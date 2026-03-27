import json
from pipeline import run_pipeline

# from author_resolver import resolve_author_ids_from_csv
#
# api_key = '71bb10ca0c813eed9a31871949e8863e2b6147a36b0f3cee667b9968bbcb310c'
# input_csv_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\orcid_huji_phd_2020.csv'
# output_csv_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\orcid_huji_phd_2020_id.csv'
#
# resolve_author_ids_from_csv(api_key, input_csv_path, output_csv_path)

def main():
	api_key = '71bb10ca0c813eed9a31871949e8863e2b6147a36b0f3cee667b9968bbcb310c'
	author_id = 'bAGGaVkAAAAJ'						#'2w2RgPkAAAAJ' #'bAGGaVkAAAAJ'
	output_directory = 'C:\\Users\\mukid\\PycharmProjects\\metric\\out'
	scimago_file_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\scimagojr2024.csv'
	result = run_pipeline(api_key, author_id, output_directory, scimago_file_path)
	print(json.dumps(result, indent=2))


if __name__ == '__main__':
	main()