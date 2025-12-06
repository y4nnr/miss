# Configuration réseau macOS pour l'accès local

## Problème
L'application fonctionne sur localhost mais pas via l'adresse IP locale (192.168.100.12:5001).

## Solutions à essayer

### 1. Vérifier le pare-feu macOS

1. Ouvrez **Préférences Système** (ou **Réglages Système** sur macOS Ventura+)
2. Allez dans **Réseau** → **Pare-feu**
3. Cliquez sur **Options du pare-feu...**
4. Vérifiez que le pare-feu est **désactivé** ou que Python est autorisé

### 2. Autoriser Python dans le pare-feu (si activé)

```bash
# Trouver le chemin de Python
which python3

# Autoriser Python dans le pare-feu
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/bin/python3

# Ou pour le Python du venv
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Users/yann/dev/miss/venv/bin/python
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /Users/yann/dev/miss/venv/bin/python
```

### 3. Vérifier les paramètres de partage

1. **Préférences Système** → **Partage**
2. Assurez-vous que **Partage de fichiers** est activé (même si vous ne partagez pas de fichiers)
3. Cela permet les connexions réseau entrantes

### 4. Désactiver AirPlay Receiver (si activé)

AirPlay peut interférer avec les ports réseau :

1. **Préférences Système** → **Général** → **AirDrop et partage**
2. Désactivez **AirPlay Receiver** temporairement

### 5. Vérifier que le serveur écoute sur toutes les interfaces

Le serveur doit écouter sur `0.0.0.0` et non `127.0.0.1`. Vérifiez avec :

```bash
netstat -an | grep 5001 | grep LISTEN
```

Vous devriez voir quelque chose comme :
```
tcp4  0  0  *.5001  *.*  LISTEN
```

Si vous voyez `127.0.0.1.5001` au lieu de `*.5001`, le serveur n'écoute que sur localhost.

### 6. Test de connectivité

Testez depuis un autre appareil ou depuis votre Mac :

```bash
# Depuis votre Mac
curl -v http://192.168.100.12:5001

# Ou depuis un autre appareil sur le réseau
# Ouvrez un navigateur et allez sur http://192.168.100.12:5001
```

### 7. Alternative : Utiliser un autre port

Si le problème persiste, essayez un port différent (comme 8080) :

Modifiez `app.py` ligne ~410 :
```python
port = 8080
```

Puis redémarrez le serveur.


