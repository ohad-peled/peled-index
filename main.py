import json
from pipeline import run_pipeline


def main():
	input_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\phd_isr.json'
	output_json_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\out\\phd_isr_res.json'
	scimago_file_path = 'C:\\Users\\mukid\\PycharmProjects\\metric\\scimagojr2024.csv'
	results = run_pipeline(input_json_path, output_json_path, scimago_file_path)
	print(json.dumps(results, indent=2))

if __name__ == '__main__':
	main()