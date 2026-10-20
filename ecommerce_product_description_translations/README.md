# E-commerce Product Description Translations

**Odoo 19** · **Kodexia Solutions** · **AGPL-3.0**

Complemento de `ecommerce_web_enhancements` para importar traducciones HTML de las descripciones corta y larga de productos mediante Excel `.xlsx`.

## Dependencias

- Odoo 19, módulo `ecommerce_web_enhancements` instalado.
- `openpyxl` en el Python de Odoo (`pip install openpyxl`).
- El script externo de ejemplo requiere además `requests` y una clave habilitada de **Google Cloud Translation API**. El addon no necesita clave API y no llama a Google.

## Flujo según el tutorial de exportación de 300 productos

1. En Odoo, exporta productos con su **ID de base de datos** y los campos `short_description_product` y `full_description_product`. Si exportas ID externos, conviértelos a IDs de base de datos antes de la importación.
2. Pide a Claude Code que genere o adapte un script, o utiliza `tools/traducir_excel_google.py`, para traducir ambos campos por Google Cloud Translation conservando HTML.
3. El script genera un `.xlsx` con las columnas `id`, `lang`, `short_description_product` y `full_description_product`.
4. En Odoo, abre **Productos → Acción → Importar traducciones HTML** y sube el Excel.
5. Revisa el estado y la visualización de cada idioma. Haz primero una prueba con pocos productos.

## Formato del Excel

| id | lang | short_description_product | full_description_product |
|---|---|---|---|
| 42 | es_ES | `<p>Descripción breve</p>` | `<p>Detalles</p>` |
| 42 | en_US | `<p>Short description</p>` | `<p>Details</p>` |

- Una fila por producto e idioma. `id` es el ID numérico interno de `product.template`.
- `lang` debe estar activo en Odoo (p. ej., `es_ES`, `en_US`).
- Se requiere al menos una columna de descripciones; las celdas vacías no eliminan contenido.
- El campo `name` y el campo estándar `website_description` **no se traducen** con este módulo.
- Estado **Traducido** significa que en la importación hay contenido en ambos campos del producto, no que todos los idiomas estén traducidos.

## Script de ejemplo (fuera de Odoo)

```bash
pip install openpyxl requests
export GOOGLE_TRANSLATE_API_KEY="tu_clave"  # Git Bash/Linux/macOS; nunca subir la clave a Git
python tools/traducir_excel_google.py --input productos.xlsx --output traducidos_es.xlsx --source de_DE --target es_ES
```

En PowerShell: `$env:GOOGLE_TRANSLATE_API_KEY="tu_clave"`. Debes tener activada la API de Cloud Translation y la facturación correspondiente. La traducción automática requiere revisión editorial.

## Limitaciones importantes

- **La descripción larga personalizada** `full_description_product` existe en el addon web, pero la plantilla actual del addon web usa `website_description` para la descripción larga principal. Traducir `full_description_product` **no la publica automáticamente en esa pestaña**: es necesaria una personalización del frontal si quieres mostrarla allí.
- La importación actualiza por `product.template.id`. No usar IDs de variantes ni IDs externos.
- Recomendada la prueba en una copia de la base de datos Odoo 19.
- Sintaxis de Python y XML comprobada; no se ha probado instalación en Odoo real.

## Licencia

AGPL-3.0 · Kodexia Solutions.
