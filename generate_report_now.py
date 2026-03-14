#!/usr/bin/env python3
"""
Genera el reporte completo de Meta Ads ahora mismo.
Ejecutar en Terminal: python3 generate_report_now.py
"""

import os, sys, glob, importlib.util, json, datetime

print("\n📊 GENERANDO REPORTE META ADS\n" + "─"*40)

# ── Configuración ──────────────────────────────────────────────────────────────
config_path = os.path.expanduser("~/.meta-ads-reporter/config.json")
os.environ["META_ADS_CONFIG_PATH"] = config_path

if not os.path.exists(config_path):
    print(f"❌ No se encontró: {config_path}")
    sys.exit(1)

# ── Localizar el plugin ────────────────────────────────────────────────────────
print("[1/3] Localizando el plugin instalado...")

patterns = [
    os.path.expanduser("~/Library/Application Support/Claude/**/meta-ads-reporter/servers/meta_ads_server.py"),
    os.path.expanduser("~/.claude/**/meta-ads-reporter/servers/meta_ads_server.py"),
    os.path.expanduser("~/Library/Application Support/AnthropicClaude/**/meta-ads-reporter/servers/meta_ads_server.py"),
]

server_path = None
for pattern in patterns:
    matches = glob.glob(pattern, recursive=True)
    if matches:
        local = [m for m in matches if "local-desktop-app-uploads" in m]
        server_path = local[0] if local else matches[0]
        break

if not server_path:
    print("❌ Plugin no encontrado. Asegurate de tener instalado meta-ads-reporter.plugin en Claude.")
    sys.exit(1)

plugin_root = os.path.dirname(os.path.dirname(server_path))
print(f"  ✅ Plugin en: {plugin_root}")

# ── Cargar módulo (sin ejecutar MCP) ──────────────────────────────────────────
spec = importlib.util.spec_from_file_location("meta_ads_server", server_path)
mod = importlib.util.module_from_spec(spec)
original_argv = sys.argv
sys.argv = ["meta_ads_server.py"]
try:
    spec.loader.exec_module(mod)
except SystemExit:
    pass
finally:
    sys.argv = original_argv

# ── Llamar funciones internas directamente (sin wrapper MCP) ──────────────────
print("\n[2/3] Consultando Meta Ads API y generando dashboard...")
print("  (puede tardar 15-30 segundos)\n")

try:
    config = mod.load_config()
except Exception as e:
    print(f"  ❌ Error leyendo config.json: {e}")
    sys.exit(1)

MONTHS_ES = ["enero","febrero","marzo","abril","mayo","junio",
             "julio","agosto","septiembre","octubre","noviembre","diciembre"]
now = datetime.datetime.now()
timestamp = f"{now.day} de {MONTHS_ES[now.month-1]} de {now.year}, {now.strftime('%H:%M')} hs"

accounts_data = []
any_error = False

for account in config.get("accounts", []):
    name      = account["name"]
    token     = account["access_token"]
    account_id = mod.norm_account(account["account_id"])

    print(f"  📡 Consultando: {name} ({account_id})")

    entry = {
        "name":         name,
        "account_id":   account_id,
        "generated_at": timestamp,
        "periods":      {},
        "campaigns":    [],
        "daily_series": [],
    }

    for preset in ["yesterday", "last_7d", "last_30d", "this_quarter"]:
        try:
            raw = mod.api_insights(token, account_id, preset, "account")
            entry["periods"][preset] = mod.format_insights(raw)
            print(f"    ✅ {preset}: gasto ${entry['periods'][preset].get('spend','0')}")
        except RuntimeError as e:
            entry["periods"][preset] = {"error": str(e)}
            print(f"    ⚠️  {preset}: {e}")
            any_error = True

    try:
        raw_camps = mod.api_insights(token, account_id, "yesterday", "campaign")
        camps = [mod.format_campaign(c) for c in raw_camps]
        camps.sort(key=lambda x: float(x.get("spend") or 0), reverse=True)
        entry["campaigns"] = camps
        print(f"    ✅ Campañas activas ayer: {len(camps)}")
    except RuntimeError as e:
        print(f"    ⚠️  Campañas: {e}")
        any_error = True

    entry["daily_series"] = mod.api_daily_series(token, account_id)
    print(f"    ✅ Serie temporal: {len(entry['daily_series'])} días")

    accounts_data.append(entry)

# ── Generar HTML ───────────────────────────────────────────────────────────────
output_path = os.path.expanduser(
    config.get("dashboard_output_path", "~/Documents/meta-ads-dashboard.html")
)
output_path = os.path.expanduser(output_path)
os.makedirs(os.path.dirname(output_path), exist_ok=True)

try:
    html = mod.generate_html(accounts_data)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n  ✅ Dashboard guardado en: {output_path}")
except Exception as e:
    print(f"\n  ❌ Error generando HTML: {e}")
    sys.exit(1)

# ── Enviar a Discord ───────────────────────────────────────────────────────────
print("\n[3/3] Enviando notificación a Discord...")

webhook_url = config.get("discord_webhook_url", "")
if not webhook_url:
    print("  ❌ 'discord_webhook_url' no está en config.json")
    sys.exit(1)

try:
    import requests
    account_names = [a["name"] for a in config.get("accounts", [])]
    today = datetime.date.today()
    today_str = f"{today.day} de {MONTHS_ES[today.month-1]} de {today.year}"

    content = (
        f"📊 **Reporte Meta Ads listo — {today_str}**\n\n"
        f"**Cuentas:** {' | '.join(account_names)}\n"
        f"**Incluye:** KPIs · Embudo de conversión · Gráfico de tendencia · Tabla de campañas\n"
        f"**Períodos:** Ayer · 7 días · 30 días · Trimestre\n\n"
        f"**Para ver el dashboard:**\n"
        f"Copiá y pegá esta ruta en la barra de tu navegador:\n"
        f"`file://{output_path}`"
    )
    resp = requests.post(webhook_url, json={"content": content}, timeout=15)
    if resp.status_code == 204:
        print("  ✅ Notificación enviada a Discord")
    else:
        print(f"  ❌ Discord: HTTP {resp.status_code} — {resp.text[:200]}")
except Exception as e:
    print(f"  ❌ Error Discord: {e}")

print("\n" + "─"*40)
if any_error:
    print("⚠️  Completado con algunas advertencias (ver arriba)")
else:
    print("✅ LISTO — Dashboard generado con datos reales")
print(f"\nAbrilo en el navegador con:\n  file://{output_path}")
print("─"*40 + "\n")
