from pymongo import MongoClient
import random

def update_risk_levels():
    client = MongoClient()
    db = client.investimentos
    
    # Get all actions
    acoes = list(db.acoes.find())
    
    # Update each action with a random risk level
    for acao in acoes:
        db.acoes.update_one(
            {'_id': acao['_id']},
            {'$set': {'risco': random.randint(1, 5)}}
        )
        print(f"Updated {acao['nome']} with risk level {random.randint(1, 5)}")

if __name__ == "__main__":
    update_risk_levels()
