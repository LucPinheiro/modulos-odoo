# Modulos ERP Odoo

Este repositorio contiene una colección de módulos personalizados desarrollados para Odoo, orientados a distintas versiones del ERP y a diferentes aplicaciones funcionales. Los módulos están diseñados para ampliar, adaptar y optimizar las funcionalidades estándar de Odoo según necesidades reales de negocio.

El objetivo del repositorio es centralizar desarrollos propios que abarcan áreas como ventas, contabilidad, inventario, CRM, recursos humanos y automatización de procesos, manteniendo una estructura organizada por versión de Odoo para facilitar su mantenimiento y reutilización.

Los módulos están desarrollados siguiendo buenas prácticas de programación en Python y Odoo, con énfasis en la escalabilidad, la claridad del código y la compatibilidad entre versiones. Este repositorio está pensado tanto como portafolio profesional como base de trabajo para proyectos de consultoría, personalización e integración de Odoo en entornos empresariales.

Cada módulo incluye su estructura estándar, dependencias y configuración necesaria para su correcta instalación y uso dentro de Odoo.

## Odoo-14

Módulos en la raíz de la rama: fcd, stock_move_line_partner_tree, stock_secondary_unit_stock_quant.

fcd (Fishing Capture Document): 
Gestión del Documento de Captura de Pesca para trazabilidad en el sector pesquero (lotes, zonas FAO/subzonas, buques, QR, etc.).

stock_move_line_partner_tree: 
Muestra el cliente/proveedor (partner) en la vista lista/árbol de movimientos de stock (stock.move.line) para mejorar trazabilidad logística.

stock_secondary_unit_stock_quant: 
Añade soporte para unidad de medida secundaria en quants de stock (stock.quant) para control con múltiples unidades.

## Odoo-15

* **📦 web_footer_gdpr_report (Cláusulas GDPR en Informes):** Agrega de forma automática las cláusulas legales de protección de datos (GDPR) en los pies de página de los informes de facturas y pedidos de venta.
* **📊 sale_order_invoice_qty_number (Contador de Facturas en Ventas):** Cuenta la cantidad de facturas generadas por cada pedido de venta e introduce nuevos filtros avanzados de búsqueda en la interfaz.
* **⏳ hr_attendance_menu_filter (Filtros de Tiempo en Asistencias):** Incorpora un filtro predeterminado por semanas y filtros dinámicos gráficos para analizar las entradas y salidas de los empleados.
* **✏️ hr_attendance_user_edit_check_in_out (Edición Manual de Asistencias):** Concede permisos a los usuarios de control de presencia manual para modificar y corregir sus propios registros de asistencia.


## Odoo-16

* **🗺️ CalculadorRutas:** Módulo de distribución logística para modelar rutas óptimas mediante la definición de nodos, enlaces operativos y un motor de cálculo dedicado.
* **🛒 e-commerce_sale_order_cart:** Extensión que sobrescribe plantillas QWeb y optimiza flujos de datos en el frontend para mejorar la experiencia en el carrito de compras.
* **🛍️ e-commerce_sale_order_hide_category_shop:** Ajuste de interfaz con estilos SCSS heredados que oculta la barra lateral vertical de categorías para ofrecer una navegación más limpia y minimalista.
* **📞 website_contacts_product:** Integración funcional que vincula consultas web de productos con el CRM de Odoo, transformando envíos de formularios en iniciativas comerciales.
* **📄 website_sale_product_description_extended:** Expansión que inyecta capacidades de texto rico y multidimensional para mostrar fichas y descripciones técnicas avanzadas en el portal web.


## Odoo-17

Módulos en la raíz de la rama: food_allergens_product, tms.

tms (Transport Management System): 
Gestión de transporte: rutas, solicitudes, viajes, vehículos, conductores, kilometraje y facturación integrado en Odoo.

food_allergens_product: 
Gestión de alérgenos alimentarios asociados a productos para control e información obligatoria.

## Odoo-18
Módulos en la raíz de la rama: `pos_restaurant_api`.

**pos_restaurant_api (API de Punto de Venta para Restaurantes):** Conexión omnicanal de aplicaciones móviles (React Native) y plataformas de delivery (Glovo, Just Eat) con el flujo de cocina y ventas nativo de Odoo.


## Odoo-19
**TMS (Transport Management System):**
Módulo integral diseñado para optimizar los servicios de transporte y logística en Odoo 19, automatizando el control de rutas, la asignación de viajes detallados a conductores y la supervisión del mantenimiento vehicular.


