# URL-Zip_to_PC
-------------------------------------------------
## Preparation
- Installer `tqdm`
```bash
pip install tqdm
```

## Execution
```bash
python main.py -u "url" -d "destination"
```
- python ==> Pour executer en python
- main.py ==> Script
- -u "url" ==> Télécharger le fichier de l'url "url"
- -d "destination" ==> Oû le fichier est téléchargé et décompréssé 

*( Si `-d` n'est pas dans la commande le fichier sera stocké dans `extracted_files` dans le répertoire du script )*


## Commandes
- -u --> url du fichier en STRING
- -d --> Destination du fichier en STRING
- -h --> Commande help
- -f --> --Force [Ne pas utiliser]


## Processus

- #### 1) Le script vérifie l'URL
- #### 2) Le script télécharge le fichier
- #### 3) Le script vérifie le fichier
- #### 4) Le script décompresse le fichier
- #### 5) Le script supprime l'archive
