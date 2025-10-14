from sentence_transformers import SentenceTransformer
import torch
import json
from handlers.backbone import fetch_table
import numpy as np

model = SentenceTransformer("google/embeddinggemma-300m")
talent_embeddings = np.load('data/weights/talent_embeddings.npy')
mantra_embeddings = np.load('data/weights/mantra_embeddings.npy')
outfit_embeddings = np.load('data/weights/outfit_embeddings.npy')
equipment_embeddings = np.load('data/weights/equipment_embeddings.npy')
weapon_embeddings = np.load('data/weights/weapon_embeddings.npy')

def initialise_data():
    weapon_names = [wb['name'] for wb in fetch_table('weapons')]
    mantra_names = [mb.get('name', '') for mb in fetch_table('mantras')]
    equipment_names = [eb['data']['name'] for eb in fetch_table('equipment')]
    outfit_names = [ob['data']['name'] for ob in fetch_table('outfits')]
    talent_names = [tb.get('name', '') for tb in fetch_table('talents')]

    model = SentenceTransformer("google/embeddinggemma-300m")

    np.save('data/weights/mantra_embeddings.npy', model.encode_document(mantra_names))
    np.save('data/weights/equipment_embeddings.npy', model.encode_document(equipment_names))
    np.save('data/weights/outfit_embeddings.npy', model.encode_document(outfit_names))
    np.save('data/weights/talent_embeddings.npy', model.encode_document(talent_names))
    np.save('data/weights/weapon_embeddings.npy', model.encode_document(weapon_names))

    return weapon_names, mantra_names, equipment_names, outfit_names, talent_names

weapon_names, mantra_names, equipment_names, outfit_names, talent_names = initialise_data()

embeddings_dict = {
    "talent": talent_embeddings,
    "mantra": mantra_embeddings,
    "outfit": outfit_embeddings,
    "equipment": equipment_embeddings,
    "weapon": weapon_embeddings
}

names_dict = {
    "talent": talent_names,
    "mantra": mantra_names,
    "outfit": outfit_names,
    "equipment": equipment_names,
    "weapon": weapon_names
}

def find(argument, type):
    query_embedding = model.encode_query(argument)
    similarities = model.similarity(query_embedding, embeddings_dict[type])
    most_similar_index = torch.argmax(similarities).item()
    most_similar_name = names_dict[type][most_similar_index]
    return most_similar_name