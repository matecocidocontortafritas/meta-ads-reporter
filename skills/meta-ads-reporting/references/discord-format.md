# Formato del Mensaje de Discord

## Estructura del mensaje actual

El mensaje que envía `send_discord_notification()` incluye:
- Fecha del reporte
- Nombres de las cuentas configuradas
- Resumen de qué incluye el dashboard
- Ruta `file://` para abrir el dashboard en el navegador

## Personalización

Para modificar el formato del mensaje, editar la función `send_discord_notification()` en `servers/meta_ads_server.py`.

El mensaje tiene un límite de 2,000 caracteres impuesto por Discord. Si necesitás más contenido, dividirlo en múltiples llamadas POST al webhook.

## Límites de Discord webhooks

- Máximo 2,000 caracteres por mensaje
- Rate limit: 5 requests / 2 segundos por webhook
- Los mensajes soportan Markdown básico: **negrita**, *cursiva*, `código`, bloques de código
