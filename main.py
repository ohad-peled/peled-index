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