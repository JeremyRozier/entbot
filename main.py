from ametice_bot import AmeticeBot
import asyncio

print(
    """\nCe programme permet de télécharger toutes les
ressources disponibles sur ton compte Ametice. Tous les fichiers seront stockés dans le chemin : 
'Fichiers Ametice/[annee_debut:annee_fin]'.\n
Tous les dossiers seront automatiquement créés par le programme.\n"""
)

username = input("Nom d'utilisateur : ")
password = input("Mot de passe : ")

ametice_bot = AmeticeBot(username, password)
asyncio.run(ametice_bot.download_all_documents())
