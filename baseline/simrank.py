import networkx as nx
import random
import numpy as np

g = nx.DiGraph()

nodes = [f"n{i}" for i in range(10)]

for n in nodes:
    g.add_node(n)

edges = set([tuple(sorted((random.choice(nodes), random.choice(nodes)))) for _ in range(int(10 * 10 * 0.6))])
edges = [(t1, t2) for t1, t2 in edges if t1 != t2]

for e1, e2 in edges:
    g.add_edge(e1, e2)


def similarities(g, iters=8, C=0.6):
    E = len(g.nodes())
    A = nx.adjacency_matrix(g).astype('float')
    columns_norm = A.sum(axis=0)
    columns_norm[columns_norm == 0.] = 1.
    A /= columns_norm
    I_ = np.eye(E)
    S = np.eye(E)

    for _ in range(iters):
        S = np.maximum(C * A.T * S * A, I_)

    return S


s1 = similarities(g)
print(s1)
