# 📊 Meta Ads Reporter — Plugin para Claude Cowork

Plugin para Claude que genera un **dashboard diario de Meta Ads** (Facebook / Instagram) y lo envía automáticamente a Discord. Cubre el funnel completo de e-commerce con gráficos de tendencia, KPIs y tabla de campañas para múltiples cuentas.

---

## ¿Qué hace?

Cada mañana a la hora que configurés, Claude:

1. Consulta la API de Meta Ads para todas las cuentas configuradas
2. Genera un archivo HTML interactivo con todos los datos
3. Envía una notificación a Discord con el link para abrirlo

El dashboard incluye:

- **Selector de cuenta** — si administrás múltiples cuentas, todas en un solo lugar
- **4 períodos** — Ayer · Últimos 7 días · Últimos 30 días · Trimestre actual
- **KPI cards** — Gasto, Ingresos, ROAS, Compras, Impresiones, Alcance, CTR, CPM
- **Embudo de conversión** — Ver Contenido → Carrito → Checkout → Info de Pago → Compras (con % entre etapas)
- **Gráfico de tendencia** — Gasto + ROAS + Compras diarios (últimos 90 días)
- **Tabla de campañas** — Todas las métricas por campaña, ordenable por columna
- **Exportar PDF** — Snapshot estático del estado actual

---

## Requisitos

- [Claude Cowork](https://claude.ai) (plan Pro o Max)
- Python 3.8 o superior instalado en tu computadora
- Cuenta de Meta Business con campañas activas
- Servidor de Discord donde tengas permisos de administrador

---

## Instalación del plugin

1. Descargá el archivo `meta-ads-reporter.plugin` desde [Releases](../../releases)
2. Abrí Claude Cowork
3. Andá a **Configuración → Plugins → Instalar desde archivo**
4. Seleccioná el archivo `.plugin`

---

## Configuración paso a paso

### Paso 1 — Crear la aplicación en Meta for Developers

**1.1 — Crear cuenta de desarrollador**

1. Ir a [developers.facebook.com](https://developers.facebook.com)
2. Hacer clic en **Comenzar**
3. Seguir los pasos para verificar tu cuenta

**1.2 — Crear la aplicación**

1. Ir al [Panel de Apps](https://developers.facebook.com/apps/)
2. Hacer clic en **Crear app**
3. En tipo de uso, elegir **Otros** → **Empresa** (Business)
4. Completar nombre de la app y correo de contacto
5. Hacer clic en **Crear app**

**1.3 — Agregar el producto "Marketing API"**

1. Dentro de tu app, ir a **Panel → Agregar productos**
2. Buscar **Marketing API** y hacer clic en **Configurar**

---

### Paso 2 — Obtener el token de acceso

**2.1 — Generar el token**

1. Ir al [Explorador de la API Graph](https://developers.facebook.com/tools/explorer/)
2. Seleccionar tu app en el menú desplegable superior derecho
3. Hacer clic en **Generar token de acceso**
4. Tildar los permisos: `ads_read` (obligatorio) y `ads_management` (recomendado)
5. Copiar el token generado (empieza con `EAA...`)

**2.2 — Extender la duración del token (hasta 60 días)**

1. Ir a la [herramienta de debug](https://developers.facebook.com/tools/debug/accesstoken/)
2. Pegar el token y hacer clic en **Depurar**
3. Hacer clic en **Ampliar token de acceso**
4. Copiar el nuevo token — este dura ~60 días

> Si usás n8n, Make, o cualquier herramienta de automatización, podés configurar la renovación automática del token antes de que venza.

---

### Paso 3 — Obtener el ID de tu cuenta publicitaria

1. Ir al [Administrador de Anuncios](https://business.facebook.com/adsmanager)
2. El ID aparece en la URL: `?act=XXXXXXXXXX`
3. El formato es `act_XXXXXXXXXX` (con el prefijo `act_`)

Si administrás múltiples cuentas, repetí este paso para cada una.

---

### Paso 4 — Crear el webhook de Discord

1. Abrir Discord → ir al canal donde querés recibir los reportes
2. Hacer clic derecho sobre el canal → **Editar canal**
3. Ir a **Integraciones** → **Webhooks** → **Nuevo Webhook**
4. Darle nombre y hacer clic en **Copiar URL del Webhook**

---

### Paso 5 — Instalar dependencias Python

```bash
pip install mcp requests
```

Verificar:
```bash
python3 -c "import mcp, requests; print('OK')"
```

---

### Paso 6 — Crear el archivo de configuración

```bash
mkdir -p ~/.meta-ads-reporter
```

Crear `~/.meta-ads-reporter/config.json`:

```json
{
  "accounts": [
    {
      "name": "Mi Tienda Principal",
      "account_id": "act_XXXXXXXXXX",
      "access_token": "EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    }
  ],
  "discord_webhook_url": "https://discord.com/api/webhooks/XXXXXXXXXX/xxxxxxxxxx",
  "dashboard_output_path": "~/Documents/meta-ads-dashboard.html"
}
```

> **Seguridad:** este archivo contiene credenciales. Nunca lo subas a un repositorio público.

---

### Paso 7 — Generar tu primer reporte

```bash
python3 generate_report_now.py
```

Si todo está bien, verás:
```
✅ yesterday: gasto $XX.XX
✅ Campañas activas ayer: X
✅ Dashboard guardado en: ~/Documents/meta-ads-dashboard.html
✅ Notificación enviada a Discord
```

---

### Paso 8 — Configurar el reporte automático diario

En Claude Cowork, crear una tarea programada con el prompt:

```
Genera el reporte diario de Meta Ads:
1. Llamar a create_dashboard_file()
2. Usar la ruta retornada en send_discord_notification(dashboard_path)
```

Horario sugerido: todos los días a las 8:00 AM (cron: `0 8 * * *`).

> La tarea corre cuando Claude Cowork está abierto. Si la computadora estaba en suspensión, la tarea se ejecuta al despertar.

---

## Estructura del repositorio

```
meta-ads-reporter/
├── .claude-plugin/
│   ├── plugin.json              # Manifiesto del plugin
│   └── marketplace.json         # Configuración de marketplace
├── servers/
│   ├── meta_ads_server.py       # Servidor MCP
│   ├── dashboard_template.html  # Template del dashboard
│   └── requirements.txt
├── skills/
│   └── meta-ads-reporting/
│       ├── SKILL.md
│       └── references/
│           ├── metrics-reference.md
│           └── discord-format.md
├── .mcp.json
├── .gitignore
├── config.template.json
├── generate_report_now.py       # Script para generar manualmente
└── README.md
```

---

## Solución de problemas

**Dashboard vacío (sin datos):** verificar que el `access_token` es válido y no venció.

**Error de conexión a Meta API:** verificar que la app tiene "Marketing API" habilitado y el permiso `ads_read` otorgado.

**No llega el mensaje a Discord:** verificar que la URL del webhook es correcta y sigue activa.

**El gráfico no aparece:** el dashboard necesita conexión a internet para cargar Chart.js desde CDN.

**La tarea programada no corrió:** Claude Cowork debe estar ejecutándose cuando se dispara la tarea.

---

## Licencia

MIT License — libre para uso personal y comercial.

---

*Construido con [Claude Cowork](https://claude.ai) de Anthropic.*
