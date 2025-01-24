import os
from pymongo import MongoClient
from typing import List, Dict, Any
import sys

# Configuration MongoDB
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "game_db"

# Données initiales rééquilibrées
CHARACTERS = [
    {"name": "Paladin", "attack": 20, "defense": 12, "hp": 120},
    {"name": "Chevalier", "attack": 22, "defense": 10, "hp": 110},
    {"name": "Berserker", "attack": 28, "defense": 6, "hp": 90},
    {"name": "Archer", "attack": 25, "defense": 7, "hp": 85},
    {"name": "Sorcier", "attack": 30, "defense": 4, "hp": 75},
    {"name": "Guerrier", "attack": 24, "defense": 8, "hp": 100},
    {"name": "Moine", "attack": 22, "defense": 9, "hp": 95},
    {"name": "Voleur", "attack": 27, "defense": 5, "hp": 80},
    {"name": "Chasseur", "attack": 23, "defense": 8, "hp": 90},
    {"name": "Druide", "attack": 21, "defense": 9, "hp": 100}
]

MONSTERS = [
    {"name": "Gobelin", "attack": 18, "defense": 6, "hp": 150},
    {"name": "Orc", "attack": 22, "defense": 8, "hp": 180},
    {"name": "Dragon", "attack": 25, "defense": 12, "hp": 200},
    {"name": "Zombie", "attack": 20, "defense": 7, "hp": 160},
    {"name": "Troll", "attack": 23, "defense": 10, "hp": 190},
    {"name": "Spectre", "attack": 24, "defense": 6, "hp": 170},
    {"name": "Golem", "attack": 21, "defense": 14, "hp": 210},
    {"name": "Vampire", "attack": 26, "defense": 9, "hp": 175},
    {"name": "Loup-garou", "attack": 24, "defense": 8, "hp": 185},
    {"name": "Squelette", "attack": 19, "defense": 7, "hp": 155}
]


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text: str):
    print("\n" + "=" * 50)
    print(text.center(50))
    print("=" * 50 + "\n")


def get_valid_int_input(prompt: str, min_val: int = 1, max_val: int = 999) -> int:
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            print(f"La valeur doit être entre {min_val} et {max_val}")
        except ValueError:
            print("Veuillez entrer un nombre valide")


def display_entity_list(entities: List[Dict[str, Any]], title: str):
    print_header(title)
    for i, entity in enumerate(entities, 1):
        print(f"{i}. {entity['name']} - ATK: {entity['attack']
                                              }, DEF: {entity['defense']}, PV: {entity['hp']}")


def edit_entity(entity: Dict[str, Any]) -> Dict[str, Any]:
    print(f"\nModification de {entity['name']}")
    print("Appuyez sur Entrée pour garder la valeur actuelle")

    # Nom
    new_name = input(f"Nom ({entity['name']}) : ").strip()
    if new_name:
        entity['name'] = new_name

    # Stats
    for stat in ['attack', 'defense', 'hp']:
        while True:
            try:
                value = input(f"{stat.upper()} ({entity[stat]}) : ").strip()
                if not value:  # Garder la valeur actuelle
                    break
                new_value = int(value)
                if 1 <= new_value <= 999:
                    entity[stat] = new_value
                    break
                print("La valeur doit être entre 1 et 999")
            except ValueError:
                print("Veuillez entrer un nombre valide")

    return entity


def manage_entities(db: Any, collection_name: str, entities: List[Dict[str, Any]], title: str):
    while True:
        clear_screen()
        display_entity_list(entities, title)
        print("\nOptions :")
        print("1. Modifier une entité")
        print("2. Réinitialiser aux valeurs par défaut")
        print("3. Retour au menu principal")

        choice = input("\nChoisissez une option (1-3) : ").strip()

        if choice == "1":
            idx = get_valid_int_input(
                f"Choisissez le numéro (1-{len(entities)}) : ", 1, len(entities)) - 1
            entities[idx] = edit_entity(entities[idx].copy())
            # Mise à jour dans la base de données
            db[collection_name].replace_one(
                {"name": entities[idx]["name"]}, entities[idx])
            print("\nModifications enregistrées!")
            input("Appuyez sur Entrée pour continuer...")

        elif choice == "2":
            confirm = input(
                "Êtes-vous sûr de vouloir réinitialiser ? (o/N) : ").lower()
            if confirm == 'o':
                if collection_name == "characters":
                    entities = CHARACTERS.copy()
                else:
                    entities = MONSTERS.copy()
                db[collection_name].delete_many({})
                db[collection_name].insert_many(entities)
                print("\nRéinitialisation effectuée!")
                input("Appuyez sur Entrée pour continuer...")

        elif choice == "3":
            break


def admin_menu(client: MongoClient):
    db = client[DB_NAME]

    while True:
        clear_screen()
        print_header("Menu d'Administration")
        print("1. Gérer les Personnages")
        print("2. Gérer les Monstres")
        print("3. Réinitialiser la Base de Données")
        print("4. Quitter")

        choice = input("\nChoisissez une option (1-4) : ").strip()

        if choice == "1":
            characters = list(db.characters.find())
            manage_entities(db, "characters", characters,
                            "Gestion des Personnages")

        elif choice == "2":
            monsters = list(db.monsters.find())
            manage_entities(db, "monsters", monsters, "Gestion des Monstres")

        elif choice == "3":
            confirm = input(
                "Êtes-vous sûr de vouloir réinitialiser toute la base ? (o/N) : ").lower()
            if confirm == 'o':
                init_database()
                print("\nBase de données réinitialisée!")
                input("Appuyez sur Entrée pour continuer...")

        elif choice == "4":
            break


def init_database():
    try:
        # Connexion à MongoDB
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]

        # Suppression des collections existantes
        db.characters.drop()
        db.monsters.drop()
        db.scores.drop()

        # Création des collections avec validation
        db.create_collection("characters", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "attack", "defense", "hp"],
                "properties": {
                    "name": {"bsonType": "string"},
                    "attack": {"bsonType": "int"},
                    "defense": {"bsonType": "int"},
                    "hp": {"bsonType": "int"}
                }
            }
        })

        db.create_collection("monsters", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "attack", "defense", "hp"],
                "properties": {
                    "name": {"bsonType": "string"},
                    "attack": {"bsonType": "int"},
                    "defense": {"bsonType": "int"},
                    "hp": {"bsonType": "int"}
                }
            }
        })

        db.create_collection("scores", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["player_name", "waves"],
                "properties": {
                    "player_name": {"bsonType": "string"},
                    "waves": {"bsonType": "int"}
                }
            }
        })

        # Insertion des données
        db.characters.insert_many(CHARACTERS)
        db.monsters.insert_many(MONSTERS)

        # Création des index
        db.scores.create_index([("waves", -1)])

        print("Base de données initialisée avec succès!")
        return client

    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")
        sys.exit(1)


if __name__ == "__main__":
    client = init_database()
    try:
        admin_menu(client)
    finally:
        client.close()
        print("\nAu revoir!")
