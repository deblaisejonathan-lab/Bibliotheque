from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from typing import List, Optional
import requests


class Livre:
    def __init__(
        self,
        titre: str,
        auteur: str,
        annee: int,
        isbn: str,
        disponible: bool = True,
    ):
        self.titre = titre
        self.auteur = auteur
        self.annee = annee
        self.isbn = isbn
        self.disponible = disponible


class Membre:
    def __init__(
        self, id_membre: str, nom: str, prenom: str, email: str, statut: str
    ):
        self.id_membre = id_membre
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.statut = statut


class Emprunt:
    def __init__(
        self,
        isbn_livre: str,
        id_membre: str,
        date_emprunt: str,
        date_retour_prevue: str,
        id_emprunt: int = None,
    ):
        self.id_emprunt = id_emprunt
        self.isbn_livre = isbn_livre
        self.id_membre = id_membre
        self.date_emprunt = date_emprunt
        self.date_retour_prevue = date_retour_prevue


class BibliothequeModel:
    def __init__(self, db_path: str = "data/bibliotheque.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialiser_bd()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialiser_bd(self):
        """Crée les tables SQL si elles n'existent pas encore."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS livres (
                    isbn TEXT PRIMARY KEY,
                    titre TEXT NOT NULL,
                    auteur TEXT NOT NULL,
                    annee INTEGER NOT NULL,
                    disponible INTEGER NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS membres (
                    id_membre TEXT PRIMARY KEY,
                    nom TEXT NOT NULL,
                    prenom TEXT NOT NULL,
                    email TEXT NOT NULL,
                    statut TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emprunts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    isbn_livre TEXT NOT NULL,
                    id_membre TEXT NOT NULL,
                    date_emprunt TEXT NOT NULL,
                    date_retour_prevue TEXT NOT NULL,
                    FOREIGN KEY (isbn_livre) REFERENCES livres (isbn),
                    FOREIGN KEY (id_membre) REFERENCES membres (id_membre)
                )
            """)
            conn.commit()

    # --- PROPRIÉTÉS ---
    @property
    def livres(self) -> List[Livre]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM livres").fetchall()
            return [
                Livre(
                    row["titre"],
                    row["auteur"],
                    row["annee"],
                    row["isbn"],
                    bool(row["disponible"]),
                )
                for row in rows
            ]

    @property
    def membres(self) -> List[Membre]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM membres").fetchall()
            return [
                Membre(
                    row["id_membre"],
                    row["nom"],
                    row["prenom"],
                    row["email"],
                    row["statut"],
                )
                for row in rows
            ]

    @property
    def emprunts(self) -> List[Emprunt]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM emprunts").fetchall()
            return [
                Emprunt(
                    row["isbn_livre"],
                    row["id_membre"],
                    row["date_emprunt"],
                    row["date_retour_prevue"],
                    row["id"],
                )
                for row in rows
            ]

    # --- GESTION DES LIVRES ---
    def ajouter_livre(self, livre: Livre) -> bool:
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO livres (isbn, titre, auteur, annee, disponible) VALUES (?, ?, ?, ?, ?)",
                    (
                        livre.isbn,
                        livre.titre,
                        livre.auteur,
                        livre.annee,
                        1 if livre.disponible else 0,
                    ),
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def chercher_livre(self, titre: str) -> Optional[Livre]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM livres WHERE titre = ?", (titre,)
            ).fetchone()
            if row:
                return Livre(
                    row["titre"],
                    row["auteur"],
                    row["annee"],
                    row["isbn"],
                    bool(row["disponible"]),
                )
            return None

    def chercher_livre_par_isbn(self, isbn: str) -> Optional[Livre]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM livres WHERE isbn = ?", (isbn,)
            ).fetchone()
            if row:
                return Livre(
                    row["titre"],
                    row["auteur"],
                    row["annee"],
                    row["isbn"],
                    bool(row["disponible"]),
                )
            return None

    def importer_depuis_api(
        self, recherche: str, limite: int = 10
    ) -> tuple[int, int]:
        """
        Récupère des livres via l'API Open Library et les insère en base.
        Retourne (nb_ajoutes, nb_ignores).
        """
        url = "https://openlibrary.org/search.json"
        params = {"q": recherche, "limit": limite}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"Erreur réseau lors de l'appel à l'API : {e}"
            ) from e

        docs = data.get("docs", [])
        ajoutes = 0
        ignores = 0

        for idx, item in enumerate(docs, start=1):
            titre = (item.get("title") or "").strip()
            if not titre:
                ignores += 1
                continue

            auteurs = item.get("author_name")
            auteur = auteurs[0] if auteurs else "Auteur inconnu"

            annee = item.get("first_publish_year")
            if not isinstance(annee, int):
                annee = 0

            isbns = item.get("isbn")
            if isbns:
                isbn = str(isbns[0])
            else:
                prefixe = "".join(c for c in recherche.upper() if c.isalnum())[:6] or "BOOK"
                isbn = f"OL-{prefixe}-{idx}"

            livre = Livre(
                titre=titre,
                auteur=auteur,
                annee=annee,
                isbn=isbn,
                disponible=True,
            )

            if self.ajouter_livre(livre):
                ajoutes += 1
            else:
                ignores += 1

        return ajoutes, ignores

    # --- GESTION DES MEMBRES ---
    def inscrire_membre(self, membre: Membre) -> bool:
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO membres (id_membre, nom, prenom, email, statut) VALUES (?, ?, ?, ?, ?)",
                    (
                        membre.id_membre,
                        membre.nom,
                        membre.prenom,
                        membre.email,
                        membre.statut,
                    ),
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def chercher_membre(self, id_membre: str) -> Optional[Membre]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM membres WHERE id_membre = ?", (id_membre,)
            ).fetchone()
            if row:
                return Membre(
                    row["id_membre"],
                    row["nom"],
                    row["prenom"],
                    row["email"],
                    row["statut"],
                )
            return None

    # --- LOGIQUE D'EMPRUNT ET DE RETOUR ---
    def emprunter_livre(
        self, isbn: str, id_membre: str, duree_jours: int = 14
    ) -> tuple[bool, str]:
        livre = self.chercher_livre_par_isbn(isbn)
        if not livre:
            return False, "Livre introuvable dans le catalogue."
        if not livre.disponible:
            return False, "Ce livre est déjà emprunté par quelqu'un d'autre."

        membre = self.chercher_membre(id_membre)
        if not membre:
            return False, "Adhérent introuvable. Veuillez d'abord l'inscrire."

        aujourdhui = datetime.now()
        retour_prevu = aujourdhui + timedelta(days=duree_jours)
        d_emprunt = aujourdhui.strftime("%Y-%m-%d")
        d_retour = retour_prevu.strftime("%Y-%m-%d")

        with self._get_connection() as conn:
            conn.execute(
                "UPDATE livres SET disponible = 0 WHERE isbn = ?", (isbn,)
            )
            conn.execute(
                "INSERT INTO emprunts (isbn_livre, id_membre, date_emprunt, date_retour_prevue) VALUES (?, ?, ?, ?)",
                (isbn, id_membre, d_emprunt, d_retour),
            )
            conn.commit()

        return (
            True,
            f"Emprunt validé pour {membre.prenom} {membre.nom}. À rendre avant le {d_retour}.",
        )

    def retourner_livre(self, isbn: str) -> tuple[bool, str]:
        livre = self.chercher_livre_par_isbn(isbn)
        if not livre or livre.disponible:
            return False, "Ce livre n'est pas enregistré comme étant emprunté."

        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM emprunts WHERE isbn_livre = ?", (isbn,)
            ).fetchone()
            if not row:
                return False, "Erreur système : aucun dossier d'emprunt trouvé."
            date_retour_prevue_str = row["date_retour_prevue"]

        aujourdhui = datetime.now().date()
        date_limite = datetime.strptime(date_retour_prevue_str, "%Y-%m-%d").date()

        message_retard = ""
        if aujourdhui > date_limite:
            jours_retard = (aujourdhui - date_limite).days
            message_retard = (
                f" ATTENTION : Livre rendu avec {jours_retard} jour(s) de retard !"
            )

        with self._get_connection() as conn:
            conn.execute(
                "UPDATE livres SET disponible = 1 WHERE isbn = ?", (isbn,)
            )
            conn.execute("DELETE FROM emprunts WHERE isbn_livre = ?", (isbn,))
            conn.commit()

        return (
            True,
            f"Livre '{livre.titre}' restitué avec succès.{message_retard}",
        )