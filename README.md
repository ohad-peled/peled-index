# Ranki

Author-level research impact scoring. Search by name, see where you rank among your peers.

## Why Ranki?
Academic impact is hard to measure fairly. Counting citations rewards popularity but ignores where those citations come from. Counting papers rewards prolixity. Ranki tries to balance both—penalizing venue shopping while acknowledging that research matures over time. Ranki scores academic researchers based on publication quality and citation impact, normalized for career stage. You provide a name—the system enriches it with metadata, cross-references journal rankings, and tells you how you compare within your field. The underlying assumption is simple: impact compounds over time. A paper in a top-tier journal with 100 citations matters more than 10 papers in low-impact venues. But a researcher with 5 papers should not be compared directly to one with 50. We normalize by career years to level the playing field.

## How is Ranki computed?

For each paper, we calculate:
paper_score = author_weight × (0.3 × citation_intensity + 0.7 × journal_prestige)
**Author weight** is 1.0 if you're first author, 0.1 if you're a co-author. This reflects that first-author papers represent more direct contribution.

**Citation intensity** is citations divided by paper age. A 2-year-old paper with 20 citations is more impressive than a 10-year-old paper with 20 citations.

**Journal prestige** is the SCImago Journal Rank (SJR), a measure of journal impact normalized across fields. We weight it at 0.7 because venue choice matters—publishing in *Nature* versus a niche conference is not random.

The **author score** is the sum of all valid paper scores, divided by your career length. This normalization ensures early-career researchers aren't penalized for fewer papers.

Finally, we apply log₁p compression to reduce the influence of outliers.

For more details, feel free to reach out ohad.peled@mail.huji.ac.il

