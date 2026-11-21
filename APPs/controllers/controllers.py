from APPs.models.models import BibliothequeModel, Livre, Membre
from APPs.views.views import BibliothequeView


class BibliothequeController:
    def __init__(self):
        self.model = BibliothequeModel()
        self.view = BibliothequeView()

    def _importer_livres_api(self):
        recherche, limite = self.view.demander_import_api()
        if not recherche:
            self.view.afficher_message("Erreur : Veuillez saisir un mot-clé ou un thème.")
            return

        self.view.afficher_message("Recherche et importation en cours depuis Open Library...")
        try:
            ajoutes, ignores = self.model.importer_depuis_api(recherche, limite=limite)
            self.view.afficher_message(
                f"Importation terminée : {ajoutes} livre(s) ajouté(s), {ignores} ignoré(s) (doublon ou incomplet)."
            )
        except RuntimeError as e:
            self.view.afficher_message(f"Erreur d'importation : {e}")

    def executer(self):
        while True:
            choix = self.view.afficher_menu()

            if choix == "1":
                self.view.afficher_livres(self.model.livres)

            elif choix == "2":
                infos = self.view.demander_infos_livre()
                try:
                    annee = int(infos["annee"])
                except ValueError:
                    self.view.afficher_message("Erreur : L'année doit être un nombre.")
                    continue
                livre = Livre(infos["titre"], infos["auteur"], annee, infos["isbn"])
                if self.model.ajouter_livre(livre):
                    self.view.afficher_message("Livre ajouté au catalogue.")
                else:
                    self.view.afficher_message("Erreur : Cet ISBN existe déjà.")

            elif choix == "3":
                infos = self.view.demander_infos_membre()
                membre = Membre(
                    infos["id_membre"],
                    infos["nom"],
                    infos["prenom"],
                    infos["email"],
                    infos["statut"],
                )
                if self.model.inscrire_membre(membre):
                    self.view.afficher_message(
                        f"Adhérent {membre.prenom} {membre.nom} inscrit !"
                    )
                else:
                    self.view.afficher_message(
                        "Erreur : Ce numéro de carte existe déjà."
                    )

            elif choix == "4":
                self.view.afficher_membres(self.model.membres)

            elif choix == "5":
                id_membre, isbn = self.view.demander_emprunt()
                succes, message = self.model.emprunter_livre(isbn, id_membre)
                self.view.afficher_message(message)

            elif choix == "6":
                isbn = self.view.demander_retour()
                succes, message = self.model.retourner_livre(isbn)
                self.view.afficher_message(message)

            elif choix == "7":
                self.view.afficher_emprunts(self.model.emprunts)

            elif choix == "8":
                self._importer_livres_api()

            elif choix == "9":
                self.view.afficher_message("Fermeture du système. À bientôt !")
                break

            else:
                self.view.afficher_message("Choix invalide.")