
def summary_to_markdown(summary):
    """ Renders a PaperSummary as the Markdown literature review note. """
    terms = "\n".join(f"- **{t.term}**: {t.definition}" for t in summary.terms)

    return (
        f"# {summary.title}\n\n"
        f"## Authors\n{', '.join(summary.authors)}\n\n"
        f"## Keywords\n{', '.join(summary.keywords)}\n\n"
        f"## 1. Core Contribution & Objective\n{summary.core_contribution}\n\n"
        f"## 2. Methodology & Framework\n{summary.methodology}\n\n"
        f"## 3. Key Findings & Data Insights\n{summary.key_findings}\n\n"
        f"## 4. Limitations & Future Work\n{summary.limitations}\n\n"
        f"## 5. Terms\n{terms}\n\n"
    )


def save_markdown_file(markdown_content, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"\nAcademic summary successfully saved to: {output_path}")
