"""Helpers for finding edges in a graph by their OSM tag values."""



def find_edges_with_tag(G, tag, value):
    edge_by_tag = []
    for u, v, k, data in G.edges(keys=True, data=True):
        if data.get(tag) == value:
            edge_by_tag.append((u,v,k))
    return edge_by_tag
        
