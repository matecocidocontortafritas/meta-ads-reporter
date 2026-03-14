#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# push-to-github.sh
# Inicializa el repo y sube todos los archivos a GitHub.
# Ejecutar desde Terminal: bash push-to-github.sh
# ─────────────────────────────────────────────────────────────────

set -e

REPO_URL="https://github.com/matecocidocontortafritas/meta-ads-reporter.git"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "🚀 Subiendo meta-ads-reporter a GitHub"
echo "   Repo: $REPO_URL"
echo "   Directorio: $SCRIPT_DIR"
echo ""

cd "$SCRIPT_DIR"

# Inicializar git si no existe
if [ ! -d ".git" ]; then
  echo "[1/4] Inicializando repositorio git..."
  git init
  git branch -M main
else
  echo "[1/4] Repositorio git ya existe, continuando..."
fi

# Configurar remote
echo "[2/4] Configurando remote origin..."
if git remote get-url origin &>/dev/null; then
  git remote set-url origin "$REPO_URL"
else
  git remote add origin "$REPO_URL"
fi

# Agregar archivos y hacer commit
echo "[3/4] Agregando archivos y haciendo commit..."
git add .
git status --short

if git diff --cached --quiet; then
  echo "  (no hay cambios nuevos para commitear)"
else
  git commit -m "feat: add meta-ads-reporter plugin v0.1.0

Plugin completo para Claude Cowork que genera dashboards diarios
de Meta Ads con envío automático a Discord.

- Servidor MCP con FastMCP (create_dashboard_file, send_discord_notification)
- Dashboard HTML interactivo con Chart.js (KPIs, funnel, gráfico, tabla)
- Soporte para múltiples cuentas publicitarias
- Skill y referencias para Claude
- Script de generación manual (generate_report_now.py)
- README completo con guía de configuración paso a paso"
fi

# Push a GitHub
echo "[4/4] Subiendo a GitHub..."
echo "  (si te pide usuario/contraseña, usá tu usuario de GitHub y un Personal Access Token como contraseña)"
echo ""
git push -u origin main

echo ""
echo "✅ ¡Listo! El plugin está en:"
echo "   $REPO_URL"
echo ""
