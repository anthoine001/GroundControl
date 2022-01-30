# GroundControl
Programme de télémétrie et de visualtion au sol pour lanceurs expérimentaux légers.
![GroundControl-screenshot](Capture%20d%E2%80%99%C3%A9cran%202022-01-30%20170953.png)

Projet démarré en février 2021.

Contributeurs :
Antoine SELOSSE

## Dépendance
Nécessite les packages système Python3, Cython.
sous debian/ubuntu:

```bash
$ sudo apt install python3-venv python3-pip cython
```

## Installation
Apres le telechargement du projet avec git:
```bash
$ git clone https://github.com/anthoine001/GroundControl
```

L'installation peut etre faite facilement dans un environment virtuel
```bash
$ python3 -m venv venv
$ . venv/bin/activate
$ pip3 install -r requirements.txt
```

## Usage
```bash
$ ./main.py
```

## Détails
codes en C pour la fonction emeteur et recepteur (de test)
