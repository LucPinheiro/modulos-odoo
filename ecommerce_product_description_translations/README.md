## 🌐 E-commerce Product Description Translations

Este módulo, desarrollado por **Kodexia Solutions**, está diseñado para facilitar la **traducción multidioma de las descripciones de productos del comercio electrónico** de Odoo 19, mediante archivos Excel generados con scripts de Python, Claude Code y Google Cloud Translation API.

Permite realizar las siguientes acciones:

- **Importar traducciones desde Excel:** Carga masiva de descripciones de productos traducidas mediante archivos `.xlsx`.
- **Traducir descripciones cortas y largas:** Gestión de los campos `short_description_product` y `full_description_product` del módulo E-commerce Web Enhancements.
- **Integrar Claude Code y Google Cloud Translation:** Utilización de scripts Python externos para generar los archivos Excel con las traducciones.
- **Conservar el formato HTML:** Importación de descripciones traducidas respetando las etiquetas y la estructura del contenido original.
- **Gestionar traducciones multidioma:** Asociación de las descripciones traducidas con los productos y los idiomas correspondientes.
- **Controlar el estado de las traducciones:** Seguimiento de productos pendientes, en proceso y traducidos.
- **Validar las importaciones:** Comprobación de productos, idiomas y registros duplicados.
- **Optimizar la traducción de grandes catálogos:** Procesamiento por lotes de cientos de descripciones.
- **Integrarse con E-commerce Web Enhancements:** Dependencia del módulo `ecommerce_web_enhancements`.

### 📸 Tutorial visual: traducción de 300 productos

Las siguientes capturas proceden de un tutorial de flujo de trabajo. Algunas muestran la implementación anterior y no necesariamente la interfaz exacta de la versión actual del addon.

**1. Selección de productos en Odoo**

![Selección de 300 productos en Odoo](docs/images/traducciones/01-seleccion-productos.png)

**2. Preparación del script con Claude Code**

![Claude Code creando el script de traducción](docs/images/traducciones/02-claude-code-script.png)

**3. Ejecución del script Python**

![Ejecución del script](docs/images/traducciones/03-ejecucion-script.png)

**4. Ajuste y validación del script**

![Corrección de las columnas del Excel](docs/images/traducciones/04-correccion-script.png)

**5. Excel con traducciones**

![Contenido HTML en Excel](docs/images/traducciones/05-excel-traducciones.png)

**6. Archivo Excel generado**

![Resultado del archivo Excel](docs/images/traducciones/06-excel-resultados.png)

**7. Importación de las descripciones en Odoo**

![Asistente de importación de descripciones HTML](docs/images/traducciones/07-importacion-odoo.png)

**8. Resultado en la tienda online**

![Producto con descripción visible en el e-commerce](docs/images/traducciones/08-producto-traducido.png)

> **Seguridad:** no incluyas claves de API en scripts, capturas ni commits. Si una clave real ha quedado expuesta, revócala y genera otra.
