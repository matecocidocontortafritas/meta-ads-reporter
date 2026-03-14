"""
Meta Ads Reporter v2 — MCP Server
Multi-cuenta, generación de dashboard HTML, notificación Discord.

Configuración: ~/.meta-ads-reporter/config.json
O usar la variable de entorno META_ADS_CONFIG_PATH para indicar otra ruta.
"""

import os
import json
import datetime
import pathlib
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("meta-ads-server")

META_API_BASE = "https://graph.facebook.com/v20.0"

INSIGHT_FIELDS = ",".join([
    "impressions", "reach", "clicks", "ctr", "spend", "cpm",
    "outbound_clicks", "purchase_roas", "actions", "action_values",
])

DAILY_FIELDS = ",".join([
    "spend", "impressions", "clicks",
    "purchase_roas", "actions", "action_values",
])

MONTHS_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


# ─── Config ────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    """Lee el archivo config.json desde la ruta configurada."""
    path = os.environ.get(
        "META_ADS_CONFIG_PATH",
        os.path.expanduser("~/.meta-ads-reporter/config.json"),
    )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ─── Helpers ───────────────────────────────────────────────────────────────────

def norm_account(aid: str) -> str:
    return aid if aid.startswith("act_") else f"act_{aid}"


def extract_action(actions: list, action_type: str) -> str:
    for a in actions or []:
        if a.get("action_type") == action_type:
            return a.get("value", "0")
    return "0"


def extract_outbound(outbound: list) -> str:
    for item in outbound or []:
        if item.get("action_type") == "outbound_click":
            return item.get("value", "0")
    return "0"


def extract_roas(purchase_roas: list) -> str:
    for r in purchase_roas or []:
        if r.get("action_type") in ("omni_purchase", "purchase"):
            return r.get("value", "0")
    if purchase_roas:
        return purchase_roas[0].get("value", "0")
    return "0"


def format_insights(raw_list: list) -> dict:
    if not raw_list:
        return {}
    d = raw_list[0]
    actions = d.get("actions", [])
    action_values = d.get("action_values", [])
    return {
        "impressions":        d.get("impressions", "0"),
        "reach":              d.get("reach", "0"),
        "clicks":             d.get("clicks", "0"),
        "ctr":                d.get("ctr", "0"),
        "spend":              d.get("spend", "0"),
        "cpm":                d.get("cpm", "0"),
        "outbound_clicks":    extract_outbound(d.get("outbound_clicks", [])),
        "landing_page_views": extract_action(actions, "landing_page_view"),
        "searches":           extract_action(actions, "search"),
        "view_content":       extract_action(actions, "view_content"),
        "add_to_cart":        extract_action(actions, "add_to_cart"),
        "initiate_checkout":  extract_action(actions, "initiate_checkout"),
        "add_payment_info":   extract_action(actions, "add_payment_info"),
        "purchases":          extract_action(actions, "purchase"),
        "revenue":            extract_action(action_values, "purchase"),
        "roas":               extract_roas(d.get("purchase_roas", [])),
    }


def format_campaign(raw: dict) -> dict:
    actions = raw.get("actions", [])
    action_values = raw.get("action_values", [])
    return {
        "campaign_name":      raw.get("campaign_name", "Sin nombre"),
        "campaign_id":        raw.get("campaign_id", ""),
        "spend":              raw.get("spend", "0"),
        "impressions":        raw.get("impressions", "0"),
        "reach":              raw.get("reach", "0"),
        "cpm":                raw.get("cpm", "0"),
        "clicks":             raw.get("clicks", "0"),
        "ctr":                raw.get("ctr", "0"),
        "outbound_clicks":    extract_outbound(raw.get("outbound_clicks", [])),
        "landing_page_views": extract_action(actions, "landing_page_view"),
        "view_content":       extract_action(actions, "view_content"),
        "add_to_cart":        extract_action(actions, "add_to_cart"),
        "initiate_checkout":  extract_action(actions, "initiate_checkout"),
        "add_payment_info":   extract_action(actions, "add_payment_info"),
        "purchases":          extract_action(actions, "purchase"),
        "revenue":            extract_action(action_values, "purchase"),
        "roas":               extract_roas(raw.get("purchase_roas", [])),
    }


# ─── API calls ─────────────────────────────────────────────────────────────────

def api_insights(token: str, account_id: str, date_preset: str, level: str) -> list:
    """Llama a la API de insights de Meta Ads."""
    fields = INSIGHT_FIELDS
    if level == "campaign":
        fields = "campaign_name,campaign_id," + INSIGHT_FIELDS

    params = {
        "access_token": token,
        "fields": fields,
        "date_preset": date_preset,
        "level": level,
        "filtering": json.dumps([
            {"field": "effective_status", "operator": "IN", "value": ["ACTIVE"]}
        ]),
        "limit": 50,
    }
    resp = requests.get(
        f"{META_API_BASE}/{account_id}/insights",
        params=params, timeout=30,
    )
    data = resp.json()
    if "error" in data:
        raise RuntimeError(data["error"].get("message", "Error en Meta API"))
    return data.get("data", [])


def api_daily_series(token: str, account_id: str) -> list:
    """Obtiene los últimos 90 días con desglose diario para el gráfico."""
    params = {
        "access_token": token,
        "fields": DAILY_FIELDS,
        "date_preset": "last_90d",
        "level": "account",
        "time_increment": 1,
        "filtering": json.dumps([
            {"field": "effective_status", "operator": "IN", "value": ["ACTIVE"]}
        ]),
        "limit": 100,
    }
    resp = requests.get(
        f"{META_API_BASE}/{account_id}/insights",
        params=params, timeout=30,
    )
    data = resp.json()
    if "error" in data:
        return []

    result = []
    for d in data.get("data", []):
        actions = d.get("actions", [])
        action_values = d.get("action_values", [])
        result.append({
            "date":       d.get("date_start", ""),
            "spend":      d.get("spend", "0"),
            "impressions": d.get("impressions", "0"),
            "clicks":     d.get("clicks", "0"),
            "purchases":  extract_action(actions, "purchase"),
            "revenue":    extract_action(action_values, "purchase"),
            "roas":       extract_roas(d.get("purchase_roas", [])),
        })

    result.sort(key=lambda x: x["date"])
    return result


# ─── HTML Generator ────────────────────────────────────────────────────────────

def generate_html(accounts_data: list) -> str:
    template_path = os.path.join(os.path.dirname(__file__), "dashboard_template.html")
    with open(template_path, encoding="utf-8") as f:
        template = f.read()
    data_json = json.dumps(accounts_data, ensure_ascii=False)
    return template.replace("__DASHBOARD_DATA__", data_json)


# ─── MCP Tools ─────────────────────────────────────────────────────────────────

@mcp.tool()
def create_dashboard_file(output_path: str = "") -> str:
    """
    Genera el dashboard HTML con datos de todas las cuentas configuradas.

    Obtiene métricas para ayer, 7 días, 30 días y trimestre actual.
    Incluye KPIs, embudo de conversión, gráfico de tendencia y tabla de campañas.

    Args:
        output_path: Ruta donde guardar el HTML.
                     Por defecto usa 'dashboard_output_path' del config.json,
                     o ~/Documents/meta-ads-dashboard.html si no está configurado.

    Returns:
        Ruta completa al archivo HTML generado.
    """
    config = load_config()

    if not output_path:
        output_path = config.get(
            "dashboard_output_path",
            os.path.expanduser("~/Documents/meta-ads-dashboard.html"),
        )
    output_path = os.path.expanduser(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    now = datetime.datetime.now()
    timestamp = f"{now.day} de {MONTHS_ES[now.month - 1]} de {now.year}, {now.strftime('%H:%M')} hs"

    accounts_data = []

    for account in config.get("accounts", []):
        token = account["access_token"]
        account_id = norm_account(account["account_id"])

        entry = {
            "name":         account["name"],
            "account_id":   account_id,
            "generated_at": timestamp,
            "periods":      {},
            "campaigns":    [],
            "daily_series": [],
        }

        # Aggregate metrics for 4 periods
        for preset in ["yesterday", "last_7d", "last_30d", "this_quarter"]:
            try:
                raw = api_insights(token, account_id, preset, "account")
                entry["periods"][preset] = format_insights(raw)
            except RuntimeError as e:
                entry["periods"][preset] = {"error": str(e)}

        # Campaign breakdown (yesterday only)
        try:
            raw_camps = api_insights(token, account_id, "yesterday", "campaign")
            camps = [format_campaign(c) for c in raw_camps]
            camps.sort(key=lambda x: float(x.get("spend", 0) or 0), reverse=True)
            entry["campaigns"] = camps
        except RuntimeError:
            entry["campaigns"] = []

        # Daily time series (last 90 days for chart)
        entry["daily_series"] = api_daily_series(token, account_id)

        accounts_data.append(entry)

    html = generate_html(accounts_data)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


@mcp.tool()
def send_discord_notification(dashboard_path: str) -> str:
    """
    Envía una notificación a Discord indicando que el reporte está listo,
    con la ruta al dashboard para abrirlo en el navegador.

    Args:
        dashboard_path: Ruta completa al archivo HTML generado (output de create_dashboard_file).

    Returns:
        Confirmación del envío o descripción del error.
    """
    config = load_config()
    webhook_url = config.get("discord_webhook_url", "")
    if not webhook_url:
        return "Error: 'discord_webhook_url' no está configurado en config.json"

    today = datetime.date.today()
    today_str = f"{today.day} de {MONTHS_ES[today.month - 1]} de {today.year}"

    account_names = [a["name"] for a in config.get("accounts", [])]
    accounts_text = " | ".join(account_names) if account_names else "Sin cuentas"

    content = (
        f"📊 **Reporte Meta Ads listo — {today_str}**\n\n"
        f"**Cuentas:** {accounts_text}\n"
        f"**Incluye:** KPIs · Embudo de conversión · Gráfico de tendencia · Tabla de campañas\n"
        f"**Períodos:** Ayer · 7 días · 30 días · Trimestre\n\n"
        f"**Para ver el dashboard:**\n"
        f"Copiá y pegá esta ruta en la barra de tu navegador:\n"
        f"`file://{dashboard_path}`"
    )

    resp = requests.post(webhook_url, json={"content": content}, timeout=15)
    if resp.status_code == 204:
        return f"✅ Notificación enviada. Dashboard en: {dashboard_path}"
    else:
        return f"❌ Error: HTTP {resp.status_code} — {resp.text[:200]}"


if __name__ == "__main__":
    mcp.run()
