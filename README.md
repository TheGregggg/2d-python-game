# Projet jeu 2d en python et pygame
Jeu d'aventure RPG en vue de dessus 

But:
 - faire des quetes 
 - avoir du meilleur equipements
 - gagner de l'expérience
 - avancer dans le jeu

But final : avoir battu les 5 bosses du jeu

## Utilisation:
 - pygame installé 
 - vous pouvez changer les parametres graphiques (scale multiplier, HUD scale multiplier) dans config.json
 - lancer game.py
 - Touches:
    - haut,bas,gauche,droite -> z,s,q,d
    - sprinter -> maj gauche
    - attaque -> espace
    - inventaire -> i (ou click sur la 'main' en haut a droit)
    - arbre de compétences -> tab
    - menu pause -> echape

## Fonctionalité:
 - affichage moderne du jeu (fenetre réglable)
 - collision avec le monde
 - déplacement du perso dans les 4 directions
 - camera suis le perso
 - perso peut sprinter (utilise de l'énergie)
 - animation du perso dans les 4 directions
 - systeme de 'main' et d'inventaire 
 - peut ramasser object au sol
 - perso peut attaquer
 - animation attaque avec l'arme équipé dans la 'main'
 - degat infligé au monstre en fonction des statistiques de l'arme equipée
 - monstre avec systeme de pv et de collision
 - monstre déplace dans 4 direction + animation
 - monstre suit le joueur
 - monstre attaque le joueur
 - animation attaque du monstre
 - HUD d'inventaire
 - deplacements objets dans l'inventaire
 - gestion stacks
 - items utilisable (potion, nourriture)
 - afficher nom objets dans inventaire
 - HUD pv des monstres au dessus d'eux
 - menu in-game (touche esc)
 - editeur de carte complet
 - gestion argent perso
 - gestion experience + montée de niveau perso
 - gestion drop quand monstre meurt
 - menu player utiliser points (arbre compétences)
 - modification des stats du joueur en fonctions de l'arbre de compétences
 - systeme sauvegarde
   - player pos
   - player inventaire
   - player competences
   - entité
 - menu démarrer 
 - systeme de particules
   

## Dossiers:
 - gregngine : dossier moteur de jeu perso
 - entities : dossier contenant l'inititialisation de chaque entité au format .json (image,attaque de base, vitesse, etc..)
 - items : dossier contenant les infos de chaque item au format .json
 - saves : dossier contenant les fichiers de sauvegardes
 - sprites : dossier contenant les differents images 
 - pickle5 : dossier contenant la derniere version de pickle pour assurer la compatibilité entre python 3.8 et 3.6

## Todo:
 - 3d son

 - traduction

 - ajouter du son
    - deplacement perso
    - attaque
    - utilisation object
    - monstre deplacement 
    - monstre attaque
    - monstre mort
    - menu ouverture/fermture
    - menu click
    - monté de niveau son
    - ambiance sonore
    
 - gestion de la mort
 - ajouter items 
 - ajouter armes
 - ajouter monstres
 - npc pour acheter objects
 - donjons infini
 - systeme quetes

 - optimization world renderer
 - multi-threading

## Gregngine:
Gregngine est le moteur de jeu réalisé pour créer des jeux en 2d et en vue de dessus.
Il s'occupe de la gestion des entitées (perso,ennemies,items ...), de la physique et de l'affichage des elements et HUDs.
Il contient tout ce qui est réutilisable et non propre au projet actuelle.

## Flow :

![alt text](readme/graph.png "graph")

- main() -> appelle la fonction main a chaque frame
- applyPhysicalChanges() -> applique la physique à chaque entitées, pour chaque entitée, leur fonction .move() est appelée
- Draws() -> appelle pour chaque entitée visible leur fonction .draw()
- DrawHUDs -> appelle pour chaque entitée visible leur fonction .drawHUD()
- clock.tick(120) -> bloque le jeu à 120 fps
