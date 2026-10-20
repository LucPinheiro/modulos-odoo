# E-commerce Web Enhancements — Odoo 19

Módulo independiente de `vitosec_custom` orientado a la presentación visual de la tienda.

## Funciones conservadas
- Estilos SCSS del e-commerce y tarjetas de producto.
- Ajustes visuales de búsqueda, ordenación, referencias y precios.
- Descripción corta HTML en la ficha del producto.
- Pestaña de descripciones web en el formulario del producto.
- Mejoras de la ficha, pestañas, categorías y cintas de producto.

## Eliminado
- Dependencia `vitosec_custom`.
- Asistente de importación/traducción HTML, permisos y menús.
- Estados, fechas, prioridad y filtros de traducción.
- Archivos de traducción propios (i18n).
- Referencia al campo `product.datasheet` no estándar y su pestaña de descargas.

Los campos de descripción HTML siguen admitiendo el sistema habitual de idiomas de Odoo (`translate=True`), pero no incluyen funciones de gestión de traducciones.

## Atención a instalaciones existentes
Este ZIP usa el nombre técnico **ecommerce_web_enhancements**, distinto de `vitosec_web`.
No desinstales el módulo antiguo sin revisar antes la migración de datos y las vistas: desinstalar puede eliminar columnas de campos y perder descripciones. Prueba primero en una copia de la base de datos. Los dos módulos no deben quedar activos simultáneamente porque heredan las mismas plantillas.

## Verificación
Se ha verificado la sintaxis Python y XML. No se ha ejecutado una instalación real en Odoo 19.
