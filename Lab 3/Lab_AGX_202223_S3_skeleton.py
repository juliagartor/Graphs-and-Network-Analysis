import networkx as nx
import networkx as nx
import csv
import sys
import pandas as pd

#Additional functions

def find_max_num(g: nx.Graph):

    max_size = 0

    for min_size_clique in range(2, len(g.nodes)+1):
        cliques = list(nx.find_cliques(g))
        num_cliques = sum(1 for clique in cliques if len(clique) >= min_size_clique)

        if num_cliques >= 2:
            max_size = min_size_clique

    return max_size

#Lab functions

def num_common_nodes(*args):
    """
    Return the number of common nodes between a set of graphs.

    :param args: (an undetermined number of) networkx graphs.
    :return: an integer, number of common nodes.
    """
    common_nodes = set(args[0].nodes())

    for graph in args[1:]:
        common_nodes.intersection_update(graph.nodes())
        
    return len(common_nodes)


def get_degree_distribution(g: nx.Graph) -> dict:
    """
    Get the degree distribution of the graph.

    :param g: networkx graph.
    :return: dictionary with degree distribution (keys are degrees, values are number of occurrences).

    """
    degree_distr = {}

    for node in g.nodes():
        degree = g.degree(node)

        if degree in degree_distr:
            degree_distr[degree] += 1
            
        else:
            degree_distr[degree] = 1

    return degree_distr


def get_k_most_central(g: nx.Graph, metric: str, num_nodes: int) -> list:
    """
    Get the k most central nodes in the graph.

    :param g: networkx graph.
    :param metric: centrality metric. Can be (at least) 'degree', 'betweenness', 'closeness' or 'eigenvector'.
    :param num_nodes: number of nodes to return.
    :return: list with the top num_nodes nodes with the specified centrality. 

    """
    centrality = None
    if metric == 'degree':
        centrality = nx.degree_centrality(g)
    elif metric == 'betweenness':
        centrality = nx.betweenness_centrality(g)
    elif metric == 'closeness':
        centrality = nx.closeness_centrality(g)
    elif metric == 'eigenvector':
        centrality = nx.eigenvector_centrality(g)
    else:
        raise ValueError("Invalid centrality metric. Must be one of 'degree', 'betweenness', 'closeness', or 'eigenvector'.")

    sorted_nodes = sorted(centrality, key=lambda x: centrality[x],reverse=True)[:num_nodes]

    return sorted_nodes


def find_cliques(g: nx.Graph, min_size_clique: int) -> tuple:
    """
    Find cliques in the graph g with size at least min_size_clique.

    :param g: networkx graph.
    :param min_size_clique: minimum size of the cliques to find.
    :return: two-element tuple, list of cliques (each clique is a list of nodes) and
        list of nodes in any of the cliques.
    """
    cliques = [clique for clique in nx.find_cliques(g) if len(clique) >= min_size_clique] # ? len(clique) 
    nodes_in_cliques = list(set(node for clique in cliques for node in clique))

    return cliques, nodes_in_cliques


def detect_communities(g: nx.Graph, method: str, **kwargs) -> tuple:
    """
    Detect communities in the graph g using the specified method.

    :param g: a networkx graph.
    :param method: string with the name of the method to use. Can be (at least) 'girvan-newman' or 'louvain'.
    :param kwargs: additional keyword arguments for the community detection algorithm.
    :return: two-element tuple, list of communities (each community is a list of nodes) and modularity of the partition.

    """
    communities = []
    modularity = None #To return something if invalid method 

    if method == 'girvan-newman':
        communities_generator = nx.community.girvan_newman(g)
        communities = next(communities_generator)
        modularity = nx.community.modularity(g, communities)

    elif method == 'louvain':
        communities = list(nx.community.louvain_communities(g, **kwargs))
        modularity = nx.community.modularity(g, communities)
    else:
        raise ValueError("Invalid community detection method. Must be one of 'girvan-newman' or 'louvain'.")

    return communities, modularity


if __name__ == '__main__':
    
    #QUESTION 1
    gB = nx.read_graphml("Lab 1/g_gB.graphml")
    hB = nx.read_graphml("Lab 1/g_hB.graphml")
    fB = nx.read_graphml("Lab 1/g_fB.graphml")
   
    common_nodes_hB = num_common_nodes(gB,hB)
    print("Common nodes (gB and hB):", common_nodes_hB)

    common_nodes_fB= num_common_nodes(gB,fB)
    print("Common nodes (gB and fB):", common_nodes_fB)

    #QUESTION 2
    gB_prime = nx.read_graphml("Lab 2/g_gB_prime.graphml")
    gD_prime = nx.read_graphml("Lab 2/g_gD_prime.graphml")

    degree = get_k_most_central(gB_prime, "degree", 25)
    betweeness = get_k_most_central(gB_prime, "betweenness", 25)

    common_elements = set(degree).intersection(betweeness)
    print("Common nodes using different centralities:", len(common_elements))

    #QUESTION 3

    min_size_clique_gB = find_max_num(gB_prime)
    min_size_clique_gD = find_max_num(gD_prime)

    cliques_gB, nodes_gB = find_cliques(gB_prime, min_size_clique_gB)
    print("Number of cliques in gB:", len(cliques_gB), ", Unique Nodes", len(nodes_gB))

    cliques_gD, nodes_gD = find_cliques(gD_prime, min_size_clique_gD)
    print("Number of cliques in gD:", len(cliques_gD), ", Unique nodes:", len(nodes_gD))

    common_nodes = set(nodes_gB).intersection(set(nodes_gD))
    num_common_nodes = len(common_nodes)
    print("Total number of common nodes:", num_common_nodes, ", Number of total nodes:", len(nodes_gD) + len(nodes_gB))

    #QUESTION 4
    largest_clique_gD = max(cliques_gD, key=len)
    characteristics = []
    
    #print(largest_clique_gD)

    with open("Lab 2/mean_audio_features.csv", "r") as csvfile:
        features = csv.DictReader(csvfile)
    
        for row in features:
            artist_id = row["Artist_id"]
            
            if artist_id in largest_clique_gD:
                characteristics.append(row)

    df = pd.DataFrame(characteristics)
    df.to_csv("characteristics.csv", index=False)
    #print(df)

    #QUESTION 5
    gD = nx.read_graphml("Lab 1/g_gD.graphml")
    gD_communities, gD_modularity = detect_communities(gD, method='louvain')

    print("Using the louvian:")
    print("Communities:", len(gD_communities))
    print("Modularity:", gD_modularity)

    gD_communities, gD_modularity = detect_communities(gD, method='girvan-newman')

    print("Using the girvan-newman:")
    print("Communities:", len(gD_communities))
    print("Modularity:", gD_modularity)

    #QUESTION 6
    #Question (a)

    num_artists_gB = len(gB.nodes())
    num_artists_gD = len(gD.nodes())

    cost_per_artist = 100

    minimum_cost_gB = num_artists_gB * cost_per_artist
    minimum_cost_gD = num_artists_gD * cost_per_artist
    print("Artists in gB:", num_artists_gB)
    print("Artists in gD:", num_artists_gD)
    print("Minimum cost for gB:", minimum_cost_gB, "euros")
    print("Minimum cost for gD:", minimum_cost_gD, "euros")

    # Question (b)
   
    gB_characteristics = []
    gD_characteristics = []

    with open("Lab 2/mean_audio_features.csv", "r") as csvfile:
        features = csv.DictReader(csvfile)

        for row in features:
            artist_id = row["Artist_id"]

            if artist_id in gB.nodes():
                gB_characteristics.append(row)

    df_gB = pd.DataFrame(gB_characteristics)
    df_gB_sorted = df_gB.sort_values(by=['Popularity', 'Danceablility'], ascending=[False, False])

    # Select the top 4 artists from gB
    selected_artists_gB = df_gB_sorted.head(4)

    print("Selected artists from gB':")
    print(selected_artists_gB['Artist'])

    with open("Lab 2/mean_audio_features.csv", "r") as csvfile:
        features = csv.DictReader(csvfile)

        for row in features:
            artist_id = row["Artist_id"]

            if artist_id in gD.nodes():
                gD_characteristics.append(row)

    df_gD = pd.DataFrame(gD_characteristics)
    df_gD_sorted = df_gD.sort_values(by=['Popularity', 'Danceablility'], ascending=[False, False])

    # Select the top 4 artists from gD
    selected_artists_gD = df_gD_sorted.head(4)

    print("Selected artists from gD':")
    print(selected_artists_gD['Artist'])


    #QUESTION 7
    
    start_artist = "3ZooCJzNMTLpmJaIRUEorI" #Young Dro
    target_artist = "6z1cicLMt9XArxN10q7m8a" #Travis Porter

    # Perform breadth-first search
    path = nx.shortest_path(gB, start_artist, target_artist)
    hops = len(path) - 1

    # Print the minimum number of hops and the artists to listen to
    print("Minimum number of hops:", hops)
    print("Artists to listen to:")
    for i in range(hops):
        print(path[i])
    






