#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# create-release.sh
# Empaqueta el plugin y crea el Release v0.1.0 en GitHub.
#
# Uso:
#   bash create-release.sh TU_GITHUB_TOKEN
#
# El token necesita permiso "repo". Crealo en:
#   https://github.com/settings/tokens
# ─────────────────────────────────────────────────────────────────

set -e

TOKEN="$1"
OWNER="matecocidocontortafritas"
REPO="meta-ads-reporter"
VERSION="v0.1.0"
PLUGIN_NAME="meta-ads-reporter.plugin"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -z "$TOKEN" ]; then
  echo "❌ Falta el token."
  echo "   Uso: bash create-release.sh TU_GITHUB_TOKEN"
  exit 1
fi

echo ""
echo "📦 CREANDO RELEASE $VERSION EN GITHUB"
echo "────────────────────────────────────────"

# ── 1. Empaquetar el plugin ────────────────────────────────────────
echo "[1/3] Empaquetando plugin..."

PLUGIN_PATH="$SCRIPT_DIR/$PLUGIN_NAME"

# Crear zip excluyendo archivos innecesarios
cd "$SCRIPT_DIR"
zip -r "$PLUGIN_PATH" . \
  --exclude "*.git*" \
  --exclude "*__pycache__*" \
  --exclude "*.pyc" \
  --exclude "*.DS_Store" \
  --exclude "create-release.sh" \
  --exclude "push-to-github.sh" \
  --exclude "meta-ads-reporter.plugin" \
  -q

echo "  ✅ Plugin creado: $PLUGIN_PATH ($(du -sh "$PLUGIN_PATH" | cut -f1))"

# ── 2. Crear el Release en GitHub ─────────────────────────────────
echo "[2/3] Creando Release $VERSION en GitHub..."

RELEASE_BODY="## Meta Ads Reporter $VERSION\n\n### Instalación rápida\n\n1. Descargá \`meta-ads-reporter.plugin\` desde los assets de abajo\n2. Abrí Claude Cowork → Configuración → Plugins → Instalar desde archivo\n3. Seguí la guía completa en el README\n\n### Qué incluye\n\n- Dashboard HTML interactivo con KPIs, embudo de conversión, gráfico de tendencia y tabla de campañas\n- Soporte para múltiples cuentas publicitarias\n- Notificación automática a Discord\n- 4 períodos: Ayer · 7 días · 30 días · Trimestre\n- Tarea programada diaria a las 8 AM\n\n### Requisitos\n\n- Claude Cowork (Pro o Max)\n- Python 3.8+\n- Cuenta de Meta Business con campañas activas"

RELEASE_JSON=$(curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$OWNER/$REPO/releases" \
  -d "{
    \"tag_name\": \"$VERSION\",
    \"name\": \"Meta Ads Reporter $VERSION\",
    \"body\": \"$RELEASE_BODY\",
    \"draft\": false,
    \"prerelease\": false
  }")

RELEASE_ID=$(echo "$RELEASE_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))" 2>/dev/null)
RELEASE_URL=$(echo "$RELEASE_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('html_url',''))" 2>/dev/null)

if [ -z "$RELEASE_ID" ]; then
  echo "  ❌ Error creando el release:"
  echo "$RELEASE_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','Error desconocido'))" 2>/dev/null
  exit 1
fi

echo "  ✅ Release creado (ID: $RELEASE_ID)"

# ── 3. Subir el archivo .plugin como asset ─────────────────────────
echo "[3/3] Subiendo $PLUGIN_NAME al Release..."

UPLOAD_URL="https://uploads.github.com/repos/$OWNER/$REPO/releases/$RELEASE_ID/assets?name=$PLUGIN_NAME"

UPLOAD_RESULT=$(curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/zip" \
  --data-binary "@$PLUGIN_PATH" \
  "$UPLOAD_URL")

ASSET_URL=$(echo "$UPLOAD_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('browser_download_url',''))" 2>/dev/null)

if [ -z "$ASSET_URL" ]; then
  echo "  ❌ Error subiendo el asset:"
  echo "$UPLOAD_RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('message','Error desconocido'))" 2>/dev/null
  exit 1
fi

echo "  ✅ Plugin subido"
echo ""
echo "────────────────────────────────────────"
echo "✅ RELEASE PUBLICADO"
echo ""
echo "  🔗 Release:      $RELEASE_URL"
echo "  📦 Plugin directo: $ASSET_URL"
echo ""
echo "  La gente puede instalar el plugin con ese link."
echo "────────────────────────────────────────"
echo ""
