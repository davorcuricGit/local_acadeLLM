
import matplotlib.pyplot as plt

def plot_similarity_matrix(embeddings, paper_titles = None):
    """
    Plots a similarity matrix based on the embeddings of the papers.

    Args:
        embeddings (np.ndarray): The embeddings of the papers.
        paper_titles (list): List of paper titles corresponding to the embeddings.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    C = embeddings @ embeddings.T

    fig, ax = plt.subplots(figsize=(14, 8))
    im = ax.imshow(C, aspect='auto', interpolation='none', cmap='Blues')

    if paper_titles is not None:
        ax.set_xticks(np.arange(len(paper_titles)))
        ax.set_yticks(np.arange(len(paper_titles)))
        ax.set_xticklabels(paper_titles, rotation=45, ha='right', fontsize=10)
        ax.set_yticklabels(paper_titles, fontsize=10)

    plt.show()