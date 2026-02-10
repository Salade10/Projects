# un gestionnaire de mots de passe

# importer des modules
import pyfiglet
import bcrypt
import argparse
import os
import msvcrt

# Variables
titre = "LockedBox"

# Function pour effacer le CLI
def clear(): 
    os.system("cls" if os.name == "nt" else "clear")

# Engine est le function qui contrôle le program
def engine(option):
    if option == "1":
        cmd.sinscrire()



# dessine le titre
def dessine_le_titre(titre):
    titre = pyfiglet.figlet_format(titre)
    print(titre)


# ou tu saisis tes commandes
class cmd:
    
    # Toutes les options pour des menus CLI
    
    @staticmethod
    def demmarer():
        clear()
        dessine_le_titre(titre)
        # dessine le menu
        menu = """
        ====================
        1. S'inscrire
        2. Se connecter
        """
        print(menu)
        option = input("choisissez une option: ")
        engine(option)
    
    def sinscrire():
        clear()
        dessine_le_titre(titre)

        confirme = False

        while not confirme:
            # obtenir le nom d'utilisateur et mot de passe
            print("\n====================")
            nom = input("\nEcrivez votre nom d'utilisateur: ")
            print("Mot de passe: ", end="", flush=True)
            mot_de_passe_1 = ""
            mot_de_passe_2 = ""
            while True:
                # utiliser msvcrt pour s'afficher le mot de passse
                
                char = msvcrt.getch()
                # entree = fin
                if char == b"\r":
                    break

                elif char == b"\x08":
                    if len(mot_de_passe_1) > 0:
                        mot_de_passe_1 = mot_de_passe_1[:-1]
                        print("\b \b", end="",flush=True)
                
                else:
                    mot_de_passe_1 += char.decode()
                    print("*", end="",flush=True)

            print("\nMot de passe encore: ", end="", flush=True)
            while True:
                # utiliser msvcrt pour s'afficher le mot de passse
                    
                char = msvcrt.getch()
                # entree = fin
                if char == b"\r":
                    break

                elif char == b"\x08":
                    if len(mot_de_passe_2) > 0:
                        mot_de_passe_2 = mot_de_passe_2[:-1]
                        print("\b \b", end="",flush=True)
                    
                else:
                    mot_de_passe_2 += char.decode()
                    print("*", end="",flush=True)

            if mot_de_passe_1 == mot_de_passe_2:
                # confirmer ce que l'utiliseur a entree
                print("\nIls sont le meme")
                match input("\nVous etes content de la saisie O/N: ").lower():
                    case "o":
                        confirme = True
                        # chiffrer le mot de passe (on utilise bcrypt)
                        salt = bcrypt.gensalt()
                        hashed = bcrypt.hashpw(mot_de_passe_1.encode(),salt)

                        # mettre le mot de passse dans une bas des donees
                        print(hashed)

                    case "n":
                        clear()
                        dessine_le_titre(titre)
                        confirme = False
                    case _:
                        print("entrez O/N")
            else:
                confirme = False


if __name__ == "__main__":
    cmd.demmarer()
