import os
import time
from typing import List, Optional
from models import Character, Monster, Score


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text: str):
    print("\n" + "=" * 50)
    print(text.center(50))
    print("=" * 50 + "\n")


def print_team(team: List[Character]):
    print("\nVotre équipe :")
    for i, character in enumerate(team, 1):
        print(f"{i}. {character}")


def print_monster(monster: Monster):
    print("\nMonstre actuel :")
    print(monster)


def print_combat_status(team: List[Character], monster: Monster, wave: int):
    clear_screen()
    print_header(f"Vague {wave}")
    print_team(team)
    print_monster(monster)


def print_scores(scores: List[Score]):
    print_header("Meilleurs scores")
    for i, score in enumerate(scores, 1):
        print(f"{i}. {score.player_name}: {score.waves} vagues")


def get_valid_input(prompt: str, valid_options: List[str]) -> str:
    while True:
        choice = input(prompt).strip()
        if choice in valid_options:
            return choice
        print(f"Entrée invalide. Veuillez choisir parmi : {
              ', '.join(valid_options)}")


def ask_player_name() -> str:
    # Demande du nom du joueur
    while True:
        name = input(
            "Entrez votre nom (3-20 caractères) : ").strip()
        if 3 <= len(name) <= 20:
            break
        print("Le nom doit contenir entre 3 et 20 caractères.")


def get_valid_int_input(prompt: str, min_val: int, max_val: int) -> int:
    while True:
        try:
            choice = int(input(prompt))
            if min_val <= choice <= max_val:
                return choice
            print(f"Veuillez entrer un nombre entre {min_val} et {max_val}")
        except ValueError:
            print("Veuillez entrer un nombre valide")


def animate_combat(text: str):
    print(text, end='', flush=True)
    time.sleep(0.5)
    print(".", end='', flush=True)
    time.sleep(0.5)
    print(".", end='', flush=True)
    time.sleep(0.5)
    print(".", flush=True)
    time.sleep(0.5)
