
import matplotlib.pyplot as plt
import networkx as nx

def disparity_filter(G, weight='weight'):
    """
    Calculates the alpha significance value for each edge in a weighted graph.
    Adds 'alpha' as an edge attribute.
    """
    # Calculate degree and strength (sum of weights) for all nodes
    degrees = dict(G.degree())
    strengths = dict(G.degree(weight=weight))
    
    # Initialize dictionary to store the minimum alpha for each edge
    alpha_dict = {}
    
    for u, v, data in G.edges(data=True):
        w = data.get(weight, 1.0)
        
        # Alpha from u's perspective
        k_u = degrees[u]
        s_u = strengths[u]
        p_u = w / s_u if s_u > 0 else 0
        alpha_u = (1 - p_u) ** (k_u - 1) if k_u > 1 else 1.0
        
        # Alpha from v's perspective
        k_v = degrees[v]
        s_v = strengths[v]
        p_v = w / s_v if s_v > 0 else 0
        alpha_v = (1 - p_v) ** (k_v - 1) if k_v > 1 else 1.0
        
        # The edge is significant if it passes the threshold for EITHER node
        alpha_dict[(u, v)] = min(alpha_u, alpha_v)
        
    nx.set_edge_attributes(G, alpha_dict, 'alpha')
    return G

def extract_backbone(G, threshold=0.35):
    """
    Filters the graph to keep only edges with alpha below the given threshold.
    """
    # Ensure alpha values are calculated
    if not nx.get_edge_attributes(G, 'alpha'):
        G = disparity_filter(G)
        
    # Create a new graph with filtered edges
    backbone = G.copy()
    edges_to_remove = [(u, v) for u, v, data in backbone.edges(data=True) if data['alpha'] >= threshold]
    backbone.remove_edges_from(edges_to_remove)
    
    return backbone




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

def similarity_to_gexf(embeddings, paper_titles, output_file):
    """
    Converts the similarity matrix to a GEXF file for visualization in Gephi.

    Args:
        embeddings (np.ndarray): The embeddings of the papers.
        paper_titles (list): List of paper titles corresponding to the embeddings.
        output_file (str): Path to save the GEXF file.
    """
    import networkx as nx
    import numpy as np

    C = embeddings @ embeddings.T
    G = nx.Graph()

    for i, title in enumerate(paper_titles):
        G.add_node(i, label=title)

    for i in range(len(paper_titles)):
        for j in range(i + 1, len(paper_titles)):
            weight = C[i, j]
            if weight > 0:  # Only add edges with positive similarity
                G.add_edge(i, j, weight=weight)


    #filter graph using seranos disparity filter
    G = extract_backbone(G)

    nx.write_gexf(G, output_file)