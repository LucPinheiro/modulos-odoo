# Módulos Personalizados Odoo 19

## 🌐 E-commerce Product Description Translations

Este módulo, desarrollado por **Kodexia Solutions**, está diseñado para facilitar la **traducción multidioma de las descripciones de productos del comercio electrónico** de Odoo 19, mediante la importación de archivos Excel generados con scripts de Python, Claude Code y Google Cloud Translation API.

Permite realizar las siguientes acciones:

- **Importar traducciones desde Excel:** Carga masiva de descripciones de productos traducidas mediante archivos `.xlsx`.
- **Traducir descripciones cortas y largas:** Gestión de los campos `short_description_product` y `full_description_product` del módulo E-commerce Web Enhancements.
- **Integrar Claude Code y Google Cloud Translation:** Utilización de scripts Python externos para generar automáticamente los archivos Excel con las traducciones.
- **Conservar el formato HTML:** Importación de descripciones traducidas respetando las etiquetas y la estructura del contenido original.
- **Gestionar traducciones multidioma:** Asociación de las descripciones traducidas con los productos y los idiomas correspondientes.
- **Controlar el estado de las traducciones:** Seguimiento de productos pendientes, en proceso y traducidos.
- **Validar las importaciones:** Comprobación de productos, idiomas y registros duplicados para reducir errores durante la carga masiva.
- **Optimizar la traducción de grandes catálogos:** Procesamiento por lotes de productos, facilitando la gestión de cientos de descripciones.
- **Integrarse con E-commerce Web Enhancements:** Dependencia del módulo `ecommerce_web_enhancements` para utilizar sus campos personalizados de descripción web.

## 🛒 E-commerce Web Enhancements

Este módulo, desarrollado por **Kodexia Solutions**, está diseñado para mejorar la **apariencia, presentación de productos y experiencia de navegación** de las tiendas online de Odoo 19.

Permite realizar las siguientes acciones:

- **Mejorar las tarjetas de productos:** Personalización de nombres, precios, referencias y botones de compra para conseguir una presentación más atractiva.
- **Optimizar los carruseles de productos:** Mejoras en la distribución y visualización de los artículos destacados de la tienda.
- **Personalizar las fichas de productos:** Incorporación de descripciones web y mejoras en la organización de la información comercial.
- **Mejorar la presentación del catálogo:** Ajustes visuales en categorías, búsqueda y ordenación de productos.
- **Personalizar las etiquetas promocionales:** Mejoras en la presentación de las cintas y distintivos de productos.
- **Optimizar los estilos de la tienda:** Incorporación de estilos SCSS personalizados para conseguir una interfaz más moderna y uniforme.
  
## 🚚 TMS (Transport Management System)
Este módulo está diseñado para gestionar de forma integral los servicios de **transporte y logística** en Odoo. 

Permite realizar las siguientes acciones:
* **Registrar rutas comerciales:** Definición de trayectos, distancias y costos asociados.
* **Controlar solicitudes de clientes:** Gestión integral desde el estado de borrador hasta la planificación.
* **Planificar viajes detallados:** Asignación de vehículos, conductores y control de estados en tránsito.
* **Automatizar la facturación:** Generación automática de facturas de venta basadas en el servicio prestado.
* **Supervisar el mantenimiento:** Herramientas específicas para el control de kilometraje y cambio de neumáticos.
