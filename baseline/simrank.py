import networkx as nx
import random
import numpy as np

g = nx.DiGraph()

nodes = [f"n{i}" for i in range(10)]

for n in nodes:
    g.add_node(n)

edges = set([tuple(sorted((random.choice(nodes), random.choice(nodes)))) for _ in range(int(10*10*0.6))])
edges = [(t1,t2) for t1,t2 in edges if t1 != t2]

for e1, e2 in edges:
    g.add_edge(e1, e2)

def similarities(g, iters=5, C=0.6):
    def I(e):
        return g.in_degree(e)

    def O(e):
        return g.out_degree(e)

    e = [u for u in g.nodes()]
    se = {e:i for i,e in enumerate(e)}
    E = len(e)

    s_k = np.eye(E)
    for _ in range(iters):
        s_k1 = np.eye(E)
        for i in range(E):
            for j in range(E):
                if i == j: continue
                a, b = e[i], e[j]
                partial_sum = 0.0
                if I(a) != 0 and I(b) != 0:
                    for ai,_ in g.in_edges(a):
                        for bi,_ in g.in_edges(b):
                            partial_sum += s_k[se[ai]][se[bi]]
                    s_k1[i][j] = (C / (I(a) * I(b))) * partial_sum
                else:
                    s_k1[i][j] = 0.0
        s_k = s_k1
    return s_k

similarities(g)