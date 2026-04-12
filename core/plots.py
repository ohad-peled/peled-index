import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import io
import base64


def load_results(results_json_path):
    """Load the scored author results from the output JSON file."""
    with open(results_json_path, encoding='utf-8') as results_handle:
        return json.load(results_handle)


def find_candidate_entry(results, candidate_name):
    """Find the full entry for a specific candidate by name."""
    for entry in results:
        if entry['name'] == candidate_name:
            return entry
    return None


def filter_eligible_authors_by_field(results, field):
    """Return authors with a non-zero score, non-empty fields, and membership in the given field."""
    return [
        entry for entry in results
        if entry['author_score'] > 0
        and entry['fields']
        and field in entry['fields']
    ]


def extract_author_scores(results):
    """Extract all author scores from the results list."""
    return [entry['author_score'] for entry in results]


def apply_log1p_transform(scores):
    """Apply log1p transformation to scores to reduce outlier noise."""
    return np.log1p(np.array(scores))


def compute_percentile(scores, candidate_score):
    """Compute the percentile of a candidate score within the distribution using log1p transformation."""
    scores_transformed = apply_log1p_transform(scores)
    candidate_transformed = np.log1p(candidate_score)
    return round(np.mean(scores_transformed < candidate_transformed) * 100, 1)


def _ordinal_suffix(percentile):
    """Return the ordinal suffix for a percentile number."""
    p = int(percentile)
    if 11 <= p % 100 <= 13:
        return 'th'
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(p % 10, 'th')


def plot_score_distribution_for_field(scores, candidate_score, candidate_name, percentile, field):
    """
    Generate a styled author score histogram as a Base64 PNG image using log1p-transformed scores.
    Returns the plot as a Base64-encoded string instead of displaying it.
    """
    # Apply log1p transformation to reduce outlier noise
    scores_transformed = apply_log1p_transform(scores)
    candidate_transformed = np.log1p(candidate_score)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Background
    fig.patch.set_facecolor('#0f1117')
    ax.set_facecolor('#0f1117')

    # Histogram
    n, bins, patches = ax.hist(
        scores_transformed,
        bins=60,
        color='#4a90d9',
        edgecolor='#0f1117',
        linewidth=0.4,
        alpha=0.85,
        zorder=2
    )

    # Gradient-style coloring: bins to the left of candidate darker
    if candidate_transformed is not None:
        for patch, left_edge in zip(patches, bins[:-1]):
            if left_edge < candidate_transformed:
                patch.set_facecolor('#be915c')
            else:
                patch.set_facecolor('#eeb674')

    # Candidate vertical line
    if candidate_transformed is not None:
        ax.axvline(
            candidate_transformed,
            color='#ee7974',
            linewidth=2,
            linestyle='--',
            zorder=5
        )

        # Annotation text
        ordinal = _ordinal_suffix(percentile)
        annotation_text = f'Your rank: {percentile}{ordinal} percentile'

        # Position text left or right depending on space
        x_range = max(scores_transformed) - min(scores_transformed) if scores_transformed.size else 1
        text_x_offset = x_range * 0.02
        ha = 'left'
        if percentile > 80:
            text_x_offset = -x_range * 0.02
            ha = 'right'

        ax.text(
            candidate_transformed + text_x_offset,
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
    ax.set_xlabel('Author Score (log1p)', color='#cccccc', fontsize=20, labelpad=10)
    ax.set_ylabel('Number of Authors', color='#cccccc', fontsize=20, labelpad=10)
    ax.set_title(
        f'{candidate_name}',
        color='#ffffff',
        fontsize=26,
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

    # ===== NEW: Convert plot to Base64 instead of showing it =====
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', facecolor='#0f1117')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)  # Close to free memory
    
    return image_base64


def generate_plots_for_author(results_json_path, candidate_name):
    """
    Generate plots for all fields of an author.
    Returns a dictionary: { field_name: base64_image, ... }
    """
    results = load_results(results_json_path)
    candidate_entry = find_candidate_entry(results, candidate_name)

    if candidate_entry is None:
        return {'error': f'Candidate not found: {candidate_name}'}

    candidate_score = candidate_entry['author_score']
    candidate_fields = candidate_entry['fields']

    if candidate_score == 0:
        return {'error': f'{candidate_name} has a score of 0.'}

    if not candidate_fields:
        return {'error': f'{candidate_name} has no fields.'}

    plots_by_field = {}
    
    for field in candidate_fields:
        eligible = filter_eligible_authors_by_field(results, field)
        scores = extract_author_scores(eligible)

        if not scores:
            continue

        percentile = compute_percentile(scores, candidate_score)
        
        # Generate plot as Base64
        plot_base64 = plot_score_distribution_for_field(
            scores, 
            candidate_score, 
            candidate_name, 
            percentile, 
            field
        )
        
        plots_by_field[field] = {
            'plot_base64': plot_base64,
            'percentile': percentile,
            'comparison_group_size': len(scores)
        }

    return plots_by_field
