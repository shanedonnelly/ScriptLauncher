#!/bin/bash
# filepath: /home/ubuntu/Documents/projet_perso/ScriptLauncher/qt_app/reinstall.sh

# Afficher un en-tête
echo "==================================================="
echo "      Script de réinstallation de ScriptLauncher"
echo "==================================================="

# Désinstaller l'application existante
echo "[1/4] Désinstallation de scriptlauncher..."
sudo apt remove -y scriptlauncher
echo "[2/4] Suppression des dépendances inutiles..."
sudo apt autoremove -y

# Trouver le package .deb
echo "[3/4] Recherche du paquet d'installation..."
DEB_FILE=$(ls -t scriptlauncher_*.deb 2>/dev/null | head -n 1)

if [ -z "$DEB_FILE" ]; then
    echo "Erreur: Aucun fichier scriptlauncher_*.deb trouvé!"
    exit 1
fi

echo "Paquet trouvé: $DEB_FILE"

# Installer le package
echo "[4/4] Installation de $DEB_FILE..."
sudo apt install -y ./$DEB_FILE

# Vérifier si l'installation a réussi
if [ $? -eq 0 ]; then
    echo "==================================================="
    echo "    ScriptLauncher a été réinstallé avec succès"
    echo "==================================================="
else
    echo "Erreur: L'installation a échoué!"
    exit 1
fi

exit 0