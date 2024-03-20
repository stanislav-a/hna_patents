import csv
from matplotlib import pyplot as plt
from collections import Counter
import networkx as nx
import numpy as np
import matplotlib.colors as mcolors



def clean(string: str):
    characters_to_remove = ",.;:" #TODO: dont do this
    return ''.join(char for char in string if char not in characters_to_remove).lower()

lawsuits = []
company_importances = {}  # company -> importance
company_aggression_scores = {}  # company -> [attack score, defence score]

with open('cases.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Note: I arbitrarily deemed a lasuit to have more weight if it involves multiple patents
        amount_of_patents = row['patents'].count(';') + 1  # patents are separated by ";"
        attacker = clean(row['Patent Asserter'])  # the one who is trying to sue
        defender = clean(row['Alleged Infringer'])
        lawsuits.append([attacker, defender, amount_of_patents])
        # inefficient, but good enough
        if attacker not in company_importances:
            company_importances[attacker] = 0
            company_aggression_scores[attacker] = [0, 0]
        if defender not in company_importances:
            company_importances[defender] = 0
            company_aggression_scores[defender] = [0, 0]
        company_importances[attacker] += amount_of_patents
        company_importances[defender] += amount_of_patents
        company_aggression_scores[attacker][0] += amount_of_patents
        company_aggression_scores[defender][1] += amount_of_patents


print(len(lawsuits))
print(lawsuits[100])

# the most important companies
top_companies = sorted(company_importances.items(), key=lambda x: x[1], reverse=True)
top50 = [i[0] for i in top_companies[0:100]]
print("Top 50 companies:")
print(top50)

# get edges into format
# {(attacker, defender): strength}
edges = {}

for lawsuit in lawsuits:
    if lawsuit[0] in top50 and lawsuit[1] in top50:
        edge = (lawsuit[0], lawsuit[1])
        if edge not in edges:
            edges[edge] = 0
        edges[edge] += lawsuit[2]

print(len(edges))
edges_parsed = [i for i in edges.items()]
print(edges_parsed[0])


G = nx.DiGraph()
for edge in edges_parsed:
    G.add_edge(edge[0][0], edge[0][1], weight=edge[1])

pos = nx.shell_layout(G)
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=10, edge_color='k', linewidths=1, font_size=10, arrows=True)


aggression = {company: company_aggression_scores[company][0]/(company_aggression_scores[company][0] + company_aggression_scores[company][1])for company in top50}
# aggression = how many percentages of lawsuits are attacks
cmap = mcolors.LinearSegmentedColormap.from_list("custom_cmap", ['green', 'white', 'red'])
node_colors = {company: cmap(value) for company, value in aggression.items()}

# Draw edge labels with weights
edge_weights = nx.get_edge_attributes(G, 'weight')
log_weights = [np.log(i) for i in edge_weights.values()]
for node in G.nodes():
    nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color=[node_colors[node]], node_size=company_importances[node])

plt.show()


'''
Ideas:
some heatmap of how much suing/being sued
maybe colors/thickness of arrows could communicate their weight
replace " " in company name with "\n"

visualize as a bubble chart, size=importance, color=aggressiveness
do analysis about exchanging blows
look for wars, importance of a war = (litigation in one direction * litigation in the other direction)

apple has been sued a lot. Is it typical, that a lot of lawsuits come at the same time?
This could mean that other companies try ty overwhelm apples resources. Same for other companies
Or then they just did something stupid and suffer as a result

really what would be good is having companies and arrows between them

check if there are multiple companies with sony/amazon/google in their name

Look for clusters


'''
