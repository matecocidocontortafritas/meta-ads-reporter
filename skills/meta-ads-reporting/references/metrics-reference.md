# Referencia de Métricas — Meta Ads E-commerce

## Métricas de alcance y visibilidad

| Métrica | Campo API | Descripción |
|---------|-----------|-------------|
| **Impresiones** | `impressions` | Veces que se mostró el anuncio (incluyendo repeticiones al mismo usuario) |
| **Alcance** | `reach` | Personas únicas que vieron el anuncio al menos una vez |
| **CPM** | `cpm` | Costo por 1,000 impresiones. Indica eficiencia de distribución |

**CPM de referencia:** <$5 excelente / $5–$15 normal / >$15 alto para mercados latinoamericanos.

---

## Métricas de interacción

| Métrica | Campo API | Descripción |
|---------|-----------|-------------|
| **Clics totales** | `clicks` | Todos los clics (incluye clics en "Me gusta", comentarios, etc.) |
| **CTR** | `ctr` | Porcentaje de impresiones que generaron algún clic |
| **Clics salientes** | `outbound_clicks` | Clics que llevan al usuario fuera de Meta (hacia el sitio) |
| **Visitas LP** | `landing_page_views` (action) | Páginas de destino que se cargaron completamente |

**CTR de referencia:** <0.5% bajo / 0.5–2% normal / >2% muy bueno.

La diferencia entre clics salientes y visitas LP indica cuántos usuarios abandonaron antes de que cargara el sitio (mala velocidad de carga).

---

## Métricas de gasto

| Métrica | Campo API | Descripción |
|---------|-----------|-------------|
| **Gasto** | `spend` | Total gastado en el período en moneda de la cuenta |

---

## Funnel de conversión e-commerce

El orden del funnel es: Búsqueda → Ver Contenido → Agregar al Carrito → Checkout Iniciado → Info de Pago → Compra.

| Métrica | Acción API | Descripción |
|---------|-----------|-------------|
| **Búsquedas** | `search` | Usuarios que usaron el buscador interno del sitio |
| **Ver Contenido** | `view_content` | Vistas de páginas de producto |
| **Agregar al Carrito** | `add_to_cart` | Productos agregados al carrito |
| **Checkout Iniciado** | `initiate_checkout` | Proceso de compra iniciado |
| **Info de Pago** | `add_payment_info` | Usuarios que ingresaron datos de pago |
| **Compras** | `purchase` | Transacciones completadas |
| **Ingresos** | `action_values → purchase` | Valor total en $ de las compras atribuidas |

### Tasas de conversión de referencia (e-commerce)

- **Carrito → Checkout:** >50% es bueno
- **Checkout → Pago:** >70% es bueno
- **Pago → Compra:** >80% es bueno
- **Tasa de conversión general (visitas → compras):** 1–3% es estándar

---

## ROAS (Return on Ad Spend)

| Métrica | Campo API | Descripción |
|---------|-----------|-------------|
| **ROAS** | `purchase_roas` | Ingresos / Gasto publicitario |

**Interpretación:**
- ROAS < 1x: Pérdida (gastás más de lo que ingresás)
- ROAS 1–2x: Punto de equilibrio dependiendo del margen
- ROAS 2–4x: Rentable para la mayoría de los negocios
- ROAS >4x: Excelente rendimiento

**Nota:** El ROAS mínimo rentable depende del margen de ganancia. Con un margen del 30%, necesitás ROAS >3.3x para cubrir solo el costo del producto.

---

## Cómo leer el reporte en conjunto

1. **Eficiencia de distribución:** CPM alto + bajo alcance → audiencia saturada o competencia alta
2. **Calidad del tráfico:** CTR alto pero pocas visitas LP → problema de velocidad del sitio
3. **Salud del funnel:** Muchos "Ver Contenido" pero pocos "Agregar al Carrito" → problema con páginas de producto o precio
4. **Rentabilidad:** Comparar ROAS entre períodos para detectar tendencias
