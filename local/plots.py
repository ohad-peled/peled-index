import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter


RESULTS_JSON_PATH = 'C:\\Users\\mukid\\PycharmProjects\\metric\\out\\phd_2010-2025_isr_Res.json'
CANDIDATE_NAME = 'Ohad Peled'


def load_results(results_json_path):
    'Load the scored author results from the output JSON file.'
    with open(results_json_path, encoding='utf-8') as results_handle:
        return json.load(results_handle)


def find_candidate_entry(results, candidate_name):
    'Find the full entry for a specific candidate by name.'
    for entry in results:
        if entry['name'] == candidate_name:
            return entry
    return None


def filter_eligible_authors_by_field(results, field):
    'Return authors with a non-zero score, non-empty fields, and membership in the given field.'
    return [
        entry for entry in results
        if entry['author_score'] > 0
        and entry['fields']
        and field in entry['fields']
    ]


def extract_author_scores(results):
    'Extract all author scores from the results list.'
    return [entry['author_score'] for entry in results]


def compute_percentile(scores, candidate_score):
    'Compute the percentile of a candidate score within the distribution.'
    return round(np.mean(np.array(scores) < candidate_score) * 100, 1)


def plot_score_distribution_for_field(scores, candidate_score, candidate_name, percentile, field):
    'Plot a styled author score histogram for a single field with an annotated candidate marker.'
    fig, ax = plt.subplots(figsize=(12, 6))

    # Background
    fig.patch.set_facecolor('#0f1117')
    ax.set_facecolor('#0f1117')

    # Histogram
    n, bins, patches = ax.hist(
        scores,
        bins=60,
        color='#d9934a',
        edgecolor='#0f1117',
        linewidth=0.4,
        alpha=0.85,
        zorder=2
    )

    # Gradient-style coloring: bins to the left of candidate darker
    if candidate_score is not None:
        for patch, left_edge in zip(patches, bins[:-1]):
            if left_edge < candidate_score:
                patch.set_facecolor('#be915c')
            else:
                patch.set_facecolor('#eeb674')

    # Candidate vertical line
    if candidate_score is not None:
        ax.axvline(
            candidate_score,
            color='#ee7974',
            linewidth=2,
            linestyle='--',
            zorder=5
        )

        # Annotation text
        ordinal = _ordinal_suffix(percentile)
        annotation_text = f'Your rank: {percentile}{ordinal} percentile'

        # Position text left or right depending on space
        x_range = max(scores) - min(scores) if scores else 1
        text_x_offset = x_range * 0.02
        ha = 'left'
        if percentile > 80:
            text_x_offset = -x_range * 0.02
            ha = 'right'

        ax.text(
            candidate_score + text_x_offset,
            ax.get_ylim()[1] * 0.92,
            annotation_text,
            color='#ee7974',
            fontsize=14,
            fontweight='bold',
            ha=ha,
            va='top',
            zorder=6,
            bbox=dict(
                boxstyle='round,pad=0.4',
                facecolor='#0f1117',
                edgecolor='#ee7974',
                alpha=0.85
            )
        )

    # Axis labels and title
    ax.set_xlabel('Author Score', color='#cccccc', fontsize=20, labelpad=10)
    ax.set_ylabel('Number of Authors', color='#cccccc', fontsize=20, labelpad=10)
    ax.set_title(
        f'{candidate_name} - {field}\n',
        color='#ffffff',
        fontsize=30,
        fontweight='bold',
        pad=16
    )

    # Tick styling
    ax.tick_params(colors='#aaaaaa', labelsize=20)
    for spine in ax.spines.values():
        spine.set_edgecolor('#333344')

    # Grid
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.grid(axis='y', color='#2a2a3a', linestyle='-', linewidth=0.7, zorder=1)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.show()


def _ordinal_suffix(percentile):
    'Return the ordinal suffix for a percentile number.'
    p = int(percentile)
    if 11 <= p % 100 <= 13:
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(p % 10, 'th')


def main():
    results = load_results(RESULTS_JSON_PATH)
    candidate_entry = find_candidate_entry(results, CANDIDATE_NAME)

    if candidate_entry is None:
        print(f'Candidate not found: {CANDIDATE_NAME}')
        return

    candidate_score = candidate_entry['author_score']
    candidate_fields = candidate_entry['fields']

    if candidate_score == 0:
        print(f'Warning: {CANDIDATE_NAME} has a score of 0.')

    if not candidate_fields:
        print(f'Warning: {CANDIDATE_NAME} has no fields — no comparison group can be built.')
        return

    print(f'\nCandidate : {CANDIDATE_NAME}')
    print(f'Score     : {candidate_score}')
    print(f'Fields    : {", ".join(candidate_fields)}')
    print(f'Producing one plot per field.\n')

    for field in candidate_fields:
        eligible = filter_eligible_authors_by_field(results, field)
        scores = extract_author_scores(eligible)

        if not scores:
            print(f'  [{field}] No eligible authors in comparison group — skipping plot.')
            continue

        percentile = compute_percentile(scores, candidate_score)
        print(f'  [{field}] comparison_group={len(scores)}, percentile={percentile}')
        plot_score_distribution_for_field(scores, candidate_score, CANDIDATE_NAME, percentile, field)


if __name__ == '__main__':
    main()
