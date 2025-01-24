import os
from pymongo import MongoClient
from game import Game
from utils import clear_screen, print_header, print_scores, get_valid_input, ask_player_name

# Configuration MongoDB
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = "game_db"

def show_menu() -> None:
    clear_screen()
    print_header("Jeu de Combat")
    print("1. Démarrer une nouvelle partie")
    print("2. Voir les meilleurs scores")
    print("3. Quitter")

def show_final_scores(game: Game) -> None:
    print("\nVotre score final :", game.wave - 1, "vagues")
    print_scores(game.get_top_scores())
    input("\nAppuyez sur Entrée pour continuer...")

def show_top_scores(game: Game) -> None:
    clear_screen()
    print_scores(game.get_top_scores())
    input("\nAppuyez sur Entrée pour revenir au menu principal...")

def main_menu() -> None:
    client = MongoClient(MONGO_URL)
    game = Game(client, DB_NAME)

    try:
        while True:
            show_menu()

            choice = get_valid_input(
                "\nChoisissez une option (1-3) : ", ["1", "2", "3"])

            if choice == "1":
                clear_screen()
                print_header("Nouvelle Partie")

                name = ask_player_name()
                game.player_name = name

                # Création de l'équipe
                game.create_team()

                # Lancement du jeu
                game.play()

                # Affichage des scores après la partie
                show_final_scores(game)

            elif choice == "2":
                show_top_scores(game)

            else:  # choice == "3"
                print("\nMerci d'avoir joué ! À bientôt !")
                break

    finally:
        client.close()


if __name__ == "__main__":
    main_menu()
