# URL-Zip_to_PC
-------------------------------------------------
## Preparation
- Installer `tqdm` et `requests`
Il y a 2 façons de procéder :
### 1
```bash
pip install tqdm requests
```
```bash
python pip install tqdm requests
```
OU
### 2
```bash
pip install -r "requirements.txt"
```
```bash
python pip install -r "requirements.txt"
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

Mindmap : [PDF](https://github.com/Nicocrafti0105/URL-Zip_to_PC/blob/main/Mindmap-code.pdf)
