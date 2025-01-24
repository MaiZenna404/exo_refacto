import random
from typing import List, Tuple, Optional
from pymongo import MongoClient
from models import Character, Monster, Score
from utils import (
    print_combat_status, print_team, print_monster,
    animate_combat, get_valid_int_input, clear_screen
)
import time


class Game:
    def __init__(self, mongo_client: MongoClient, db_name: str = "game_db"):
        self.db = mongo_client[db_name]
        self.team: List[Character] = []
        self.wave = 1
        self.player_name = ""

    def load_characters(self) -> List[Character]:
        characters_data = list(self.db.characters.find())
        return [Character.from_dict(char) for char in characters_data]

    def get_random_monster(self) -> Monster:
        monster_data = list(self.db.monsters.find())
        monster_dict = random.choice(monster_data)
        return Monster.from_dict(monster_dict)

##### Début Fonctionnalités regroupées dans des fonctions #####

    def verify_input(self, available_characters: List[Character], choice: int) -> bool:
        choice = get_valid_int_input(
                f"\nChoisissez le personnage {
                    len(self.team) + 1} (1-{len(available_characters)}) : ",
                1, len(available_characters)
            )
        return choice 
    
    def add_character_to_team(self, available_characters: List[Character], choice: int) -> None:
        selected = available_characters.pop(choice - 1)
        self.team.append(selected)
        print(f"\n{selected.name} a rejoint votre équipe!")

    def characters_attack_monster(self, character: Character, monster: Monster) -> None:
         for character in self.team:
            if character.is_alive() and monster.is_alive():
                damage = monster.take_damage(character.attack)
                animate_combat(f"{character.name} attaque {monster.name}")
                print(f"{character.name} inflige {damage} points de dégâts à {monster.name}")
    
    def monster_attack_random_character(self, monster: Monster) -> None:
        alive_characters = [char for char in self.team if char.is_alive()]
        if alive_characters:
            target = random.choice(alive_characters)
            damage = target.take_damage(monster.attack)
            animate_combat(f"{monster.name} attaque {target.name}")
            print(f"{monster.name} inflige {damage} points de dégâts à {target.name}")

    def team_healing(self, character: Character) -> None:
         for character in self.team:
                if not character.is_alive():
                    continue
                heal_amount = int(character.max_hp * 0.1)
                character.hp = min(
                    character.max_hp, character.hp + heal_amount)
                print(f"{character.name} récupère {heal_amount * 0.1} % de PV!")

##### Fin Fonctionnalités regroupées dans des fonctions #####

    def create_team(self) -> None:
        available_characters = self.load_characters()
        self.team = []

        print("\nCréation de votre équipe (3 personnages) :")
        while len(self.team) < 3:
            print("\nPersonnages disponibles :")
            for i, char in enumerate(available_characters, 1):
                print(f"{i}. {char}")

            ## Vérifie si le choix mis en input retourne bien le type de valeur attendu (= TRUE)
            choice = self.verify_input(available_characters, len(self.team) + 1)

            ## Si le choix renvoie True, on ajoute le perso à l'équipe
            if choice : self.add_character_to_team(available_characters, choice)

    def combat_round(self, character: Character, monster: Monster) -> bool:
        """Effectue un tour de combat. Retourne True si l'équipe gagne, False sinon."""
        # Fonction permettant de gérer la mécanique de combat du perso de l'équipe
        self.characters_attack_monster(character, monster)

        # Vérification de la mort du monstre
        if not monster.is_alive():
            return True

        # # Fonction permettant de gérer la mécanique de combat du monstre
        self.monster_attack_random_character(monster)

        # Vérification de la survie de l'équipe
        return self.is_team_alive()

    def is_team_alive(self) -> bool:
        return any(char.is_alive() for char in self.team)

    def save_score(self) -> None:
        score = Score(player_name=self.player_name, waves=self.wave - 1)
        self.db.scores.insert_one(score.to_dict())

    def get_top_scores(self, limit: int = 3) -> List[Score]:
        scores_data = self.db.scores.find().sort("waves", -1).limit(limit)
        return [Score.from_dict(score) for score in scores_data]

    def random_reanimation(self):
        dead_characters = [char for char in self.team if not char.is_alive()]
        if len(dead_characters) == 0:
            print("Aucun mort dans l'equipe, personne n'est reanimé")
            return
        random_character = random.choice(dead_characters)
        random_character.hp = random_character.max_hp
        print(f"{random_character.name} a été réanimé avec {
              random_character.hp} PV!")

    def play(self) -> None:
        self.wave = 1

        while self.is_team_alive():
            monster = self.get_random_monster()
            print_combat_status(self.team, monster, self.wave)
            while monster.is_alive() and self.is_team_alive():
                # input("\nAppuyez sur Entrée pour continuer le combat...")
                time.sleep(1)
                clear_screen()
                print_combat_status(self.team, monster, self.wave)
                if not self.combat_round(monster):
                    break

            if not self.is_team_alive():
                print("\nGame Over! Votre équipe a été vaincue!")
                break

            print(f"\nVictoire! Vous avez vaincu {monster.name}!")
            self.wave += 1

            # Restauration partielle des PV (10% des PV max)
            self.team_healing(self.team)

        self.save_score()
