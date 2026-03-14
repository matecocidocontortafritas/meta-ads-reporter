---
name: meta-ads-reporting
description: >
  Este skill se usa cuando hay que generar el reporte diario de Meta Ads,
  crear el dashboard de campañas, analizar rendimiento de Facebook o Instagram Ads,
  enviar notificación a Discord, o revisar métricas publicitarias.
  Frases que lo activan: "reporte meta ads", "generar dashboard", "crear reporte",
  "enviar reporte a discord", "cómo van mis campañas", "rendimiento de campañas",
  "dashboard publicidad", "daily ads report".
version: 0.2.0
---

# Skill: Meta Ads Daily Reporting

Genera el dashboard HTML y envía la notificación a Discord de forma automática.

## Flujo principal (tarea programada diaria)

Ejecutar en este orden:

1. Llamar a `create_dashboard_file()` — descarga todos los datos, genera el HTML y guarda el archivo
2. Usar el valor retornado (ruta al archivo) como argumento para `send_discord_notification(dashboard_path)`

Eso es todo. Las dos herramientas manejan internamente la autenticación, las múltiples cuentas, los 4 períodos y los datos del gráfico.

## Manejo de errores

Si `create_dashboard_file()` falla con error de archivo no encontrado:
→ El config.json no está en `~/.meta-ads-reporter/config.json`. Indicarle al usuario que lo cree usando `config.template.json`.

Si falla con error de Meta API sobre token:
→ El token de acceso venció. Indicar al usuario que lo renueve en https://developers.facebook.com/tools/explorer/

Si falla con error de conexión:
→ Problema de red. Reintentar en unos minutos.

## Sobre el dashboard generado

El archivo HTML es completamente autocontenido. Al abrirlo en un navegador el usuario verá:
- **Selector de cuenta** (si hay más de una)
- **Tabs de período:** Ayer / 7 días / 30 días / Trimestre
- **KPI cards:** Gasto, Ingresos, ROAS, Compras, Impresiones, Clics, CTR, CPM
- **Embudo de conversión:** Ver Contenido → Carrito → Checkout → Info Pago → Compras
- **Gráfico de tendencia diaria** (últimos 90 días): Gasto + ROAS + Compras
- **Tabla de campañas** (ayer): todas las métricas, ordenable por columna
- **Botón "Exportar PDF"** para imprimir como PDF estático

## Referencias adicionales

- **`references/metrics-reference.md`** — qué significa cada métrica y rangos de referencia
- **`references/discord-format.md`** — formato del mensaje de Discord (para customización futura)
