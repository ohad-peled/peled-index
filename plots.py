import json
import numpy as np
import matplotlib.pyplot as plt


RESULTS_JSON_PATH = 'C:\\Users\\mukid\\PycharmProjects\\metric\\out\\phd_2022_res.json'
CANDIDATE_NAME = 'Ohad Peled'


def load_results(results_json_path):
	'Load the scored author results from the output JSON file.'
	with open(results_json_path, encoding='utf-8') as results_handle:
		return json.load(results_handle)


def extract_author_scores(results):
	'Extract all author scores from the results list.'
	return [entry['author_score'] for entry in results]


def find_candidate_score(results, candidate_name):
	'Find the score for a specific candidate by name.'
	for entry in results:
		if entry['name'] == candidate_name:
			return entry['author_score']
	return None


def compute_percentile(scores, candidate_score):
	'Compute the percentile of a candidate score in the distribution.'
	return round(np.mean(np.array(scores) < candidate_score) * 100, 1)


def plot_score_distribution(scores, candidate_score, candidate_name, percentile):
	'Plot the author score histogram with an optional candidate marker.'
	fig, ax = plt.subplots(figsize=(10, 6))
	ax.hist(scores, bins=50, color='steelblue', edgecolor='white')
	if candidate_score is not None:
		ax.axvline(candidate_score, color='crimson', linewidth=2, label=f'{candidate_name} (percentile: {percentile})')
		ax.legend()
	ax.set_xlabel('Author Score')
	ax.set_ylabel('Count')
	ax.set_title('Author Score Distribution')
	plt.tight_layout()
	plt.show()


def main():
	results = load_results(RESULTS_JSON_PATH)
	scores = extract_author_scores(results)
	print(scores)
	candidate_score = find_candidate_score(results, CANDIDATE_NAME)
	percentile = compute_percentile(scores, candidate_score) if candidate_score is not None else None
	if candidate_score is None:
		print(f'Candidate not found: {CANDIDATE_NAME}')
	else:
		print(f'{CANDIDATE_NAME}: score={candidate_score}, percentile={percentile}')
	plot_score_distribution(scores, candidate_score, CANDIDATE_NAME, percentile)


if __name__ == '__main__':
	main()