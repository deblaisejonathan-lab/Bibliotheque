from typing import List
from APPs.models.models import Livre, Membre, Emprunt


class BibliothequeView:
    @staticmethod
    def afficher_menu() -> str:
        print("\n=========================================")
        print("   SYSTÈME DE GESTION DE BIBLIOTHÈQUE")
        print("=========================================")
        print("1. Catalogue : Afficher les livres")
        print("2. Catalogue : Ajouter un livre")
        print("3. Adhérents : Inscrire un nouveau membre")
        print("4. Adhérents : Afficher les membres")
        print("5. Guichet   : Emprunter un livre")
        print("6. Guichet   : Retourner un livre")
        print("7. Guichet   : Voir les emprunts en cours")
        print("8. Catalogue : Importer des livres via API")
        print("9. Quitter")
        return input("\nVotre choix (1-9) : ").strip()

    @staticmethod
    def afficher_livres(livres: List[Livre]):
        print("\n--- Catalogue des livres ---")
        if not livres:
            print("Aucun livre enregistré.")
            return
        for l in livres:
            statut = "Disponible" if l.disponible else "Emprunté"
            print(f"[{l.isbn}] '{l.titre}' - {l.auteur} ({l.annee}) | {statut}")

    @staticmethod
    def afficher_membres(membres: List[Membre]):
        print("\n--- Liste des adhérents ---")
        if not membres:
            print("Aucun adhérent inscrit.")
            return
        for m in membres:
            print(f"[ID: {m.id_membre}] {m.prenom} {m.nom} | {m.email} | {m.statut}")

    @staticmethod
    def afficher_emprunts(emprunts: List[Emprunt]):
        print("\n--- Emprunts actuellement en cours ---")
        if not emprunts:
            print("Aucun emprunt en cours.")
            return
        for e in emprunts:
            print(
                f"Livre ISBN [{e.isbn_livre}] -> Adhérent [{e.id_membre}] "
                f"| Emprunté le : {e.date_emprunt} | Retour prévu : {e.date_retour_prevue}"
            )

    @staticmethod
    def demander_infos_livre() -> dict:
        print("\n--- Nouveau Livre ---")
        return {
            "titre": input("Titre : ").strip(),
            "auteur": input("Auteur : ").strip(),
            "annee": input("Année : ").strip(),
            "isbn": input("ISBN : ").strip(),
        }

    @staticmethod
    def demander_infos_membre() -> dict:
        print("\n--- Inscription Adhérent ---")
        return {
            "id_membre": input("Numéro de carte adhérent (ex: M001) : ").strip(),
            "nom": input("Nom : ").strip(),
            "prenom": input("Prénom : ").strip(),
            "email": input("Email : ").strip(),
            "statut": input("Statut : ").strip(),
        }

    @staticmethod
    def demander_emprunt() -> tuple[str, str]:
        print("\n--- Guichet Emprunt ---")
        id_membre = input("Numéro de carte adhérent : ").strip()
        isbn = input("ISBN du livre à emprunter : ").strip()
        return id_membre, isbn

    @staticmethod
    def demander_retour() -> str:
        print("\n--- Guichet Retour ---")
        return input("ISBN du livre retourné : ").strip()

    @staticmethod
    def demander_import_api() -> tuple[str, int]:
        print("\n--- Importation depuis l'API Open Library ---")
        recherche = input("Mot-clé, thème ou auteur à rechercher : ").strip()
        limite_str = input("Nombre max de livres à importer (défaut 10) : ").strip()
        try:
            limite = int(limite_str) if limite_str else 10
            if limite <= 0:
                limite = 10
        except ValueError:
            limite = 10
        return recherche, limite

    @staticmethod
    def afficher_message(msg: str):
        print(f"\n>> {msg}")