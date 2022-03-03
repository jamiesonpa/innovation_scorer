

import pandas as pd

innovation_matrix = pd.read_csv("innovation_words.csv")

company_matrix = pd.read_csv("bli_10k.csv")


#first get the core technologies from the innovation matrix
core_technologies = list(set(innovation_matrix["keyword"].to_list()))


#here we will tally up the scores for each of the technologies
scores = {}
for ct in core_technologies:
    scores[ct] = 0

betweeness_scores = {}
for ct in core_technologies:
    betweeness_scores[ct] = 0

for index, row in company_matrix.iterrows():
    node_name = row["node name"]
    node_normalized_fd = row["normalized_fd"]
    node_betweeness = row["betweenness"]
    for id, inorow in innovation_matrix.iterrows():
        if node_name == inorow["node name"]:
            keyword = inorow["keyword"]
            kw_normalized_fd = inorow["normalized_fd"]
            kw_betweenness = inorow["betweenness"]
            scores[keyword] = scores[keyword] + (node_normalized_fd/kw_normalized_fd)
            betweeness_scores[keyword] = betweeness_scores[keyword] + (node_betweeness/kw_betweenness)

total_score = 0
for score in scores.keys():
    total_score = total_score + scores[score]

total_bt_score = 0
for score in betweeness_scores.keys():
    total_bt_score = total_bt_score + betweeness_scores[score]


print("normalized fd total = " + str(total_score))

for score in scores.keys():
    print(score + ": " + str(round((scores[score]/total_score)*100,2)) + "%")


print("total betweenness score = " + str(total_bt_score))

for score in betweeness_scores.keys():
    print(score + ": " + str(round((betweeness_scores[score]/total_bt_score)*100,2)) + "%")
            
            
