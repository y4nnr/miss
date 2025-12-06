#!/bin/bash

# Script pour configurer l'accès réseau sur macOS

echo "🔧 Configuration de l'accès réseau pour Miss France 2026"
echo ""

# Trouver le Python utilisé
PYTHON_PATH=$(which python3)
if [ -f "venv/bin/python" ]; then
    PYTHON_PATH="$(pwd)/venv/bin/python"
    echo "✅ Utilisation du Python du venv: $PYTHON_PATH"
else
    echo "✅ Utilisation du Python système: $PYTHON_PATH"
fi

# Vérifier l'état du pare-feu
echo ""
echo "📋 État du pare-feu:"
FIREWALL_STATE=$(/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null | grep -o "enabled\|disabled")
echo "   Pare-feu: $FIREWALL_STATE"

if [ "$FIREWALL_STATE" = "enabled" ]; then
    echo ""
    echo "🔓 Le pare-feu est activé. Ajout de Python à la liste autorisée..."
    
    # Ajouter Python au pare-feu
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add "$PYTHON_PATH" 2>/dev/null
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp "$PYTHON_PATH" 2>/dev/null
    
    echo "✅ Python ajouté au pare-feu"
    echo ""
    echo "⚠️  Si le problème persiste, vous pouvez désactiver temporairement le pare-feu:"
    echo "   Préférences Système → Réseau → Pare-feu → Désactiver"
else
    echo "✅ Le pare-feu est désactivé"
fi

# Vérifier le port
echo ""
echo "🔍 Vérification du port 5001..."
if lsof -i :5001 | grep -q LISTEN; then
    echo "   ⚠️  Le port 5001 est déjà utilisé"
    lsof -i :5001 | grep LISTEN
else
    echo "   ✅ Le port 5001 est libre"
fi

# Obtenir l'adresse IP locale
echo ""
echo "🌐 Adresse IP locale:"
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
if [ -n "$LOCAL_IP" ]; then
    echo "   IP: $LOCAL_IP"
    echo "   URL: http://$LOCAL_IP:5001"
else
    echo "   ⚠️  Impossible de déterminer l'adresse IP"
fi

echo ""
echo "📝 Instructions:"
echo "   1. Redémarrez le serveur: python app.py"
echo "   2. Testez depuis un autre appareil: http://$LOCAL_IP:5001"
echo "   3. Si ça ne fonctionne pas, vérifiez:"
echo "      - Préférences Système → Partage → Partage de fichiers (activé)"
echo "      - Préférences Système → Général → AirDrop et partage → AirPlay Receiver (désactivé)"
echo ""


