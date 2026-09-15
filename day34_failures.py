import json

with open("evaluation/results/hard_retrieval_results.json") as f:
    data = json.load(f)

for x in data:
    if not x["legal_reranker"]["recall_at_1"]:
        print(
            f'Q{x["id"]}: '
            f'expected section {x["expected_section"]} | '
            f'LegalRAG top={x["legal_reranker"]["sections"][0]} | '
            f'top5={x["legal_reranker"]["sections"]} | '
            f'query={x["query"]}'
        )
