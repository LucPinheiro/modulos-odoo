# Modulos ERP Odoo

Este repositorio contiene una colección de módulos personalizados desarrollados para Odoo, orientados a distintas versiones del ERP y a diferentes aplicaciones funcionales. Los módulos están diseñados para ampliar, adaptar y optimizar las funcionalidades estándar de Odoo según necesidades reales de negocio.

El objetivo del repositorio es centralizar desarrollos propios que abarcan áreas como ventas, contabilidad, inventario, CRM, recursos humanos y automatización de procesos, manteniendo una estructura organizada por versión de Odoo para facilitar su mantenimiento y reutilización. Los módulos están desarrollados siguiendo buenas prácticas de programación en Python y Odoo, con énfasis en la escalabilidad, la claridad del código y la compatibilidad entre versiones.

Este repositorio está pensado tanto como portafolio profesional como base de trabajo para proyectos de consultoría, personalización e integración de Odoo en entornos empresariales. Cada módulo incluye su estructura estándar, dependencias y configuración necesaria para su correcta instalación y uso dentro de Odoo.

---

## Odoo-14

### 📦 Gestión de Inventario y Logística
* **⚓ fcd (Fishing Capture Document):** Gestión del Documento de Captura de Pesca para trazabilidad en el sector pesquero (lotes, zonas FAO/subzonas, buques, QR, etc.).
* **📦 stock_move_line_partner_tree:** Muestra el cliente/proveedor (partner) en la vista lista/árbol de movimientos de stock (`stock.move.line`) para mejorar la trazabilidad logística.
* **📏 stock_secondary_unit_stock_quant:** Añade soporte para unidad de medida secundaria en quants de stock (`stock.quant`) para el control con múltiples unidades.

---

## Odoo-15

### 💼 Facturación y Finanzas
* **💰 account_invoice_user_authorization_payment:** Gestiona y restringe los flujos de autorización para pagos de facturas. Asegura que solo los usuarios permitidos validen transacciones monetarias.

### 🤝 CRM y Soporte
* **📊 crm_expected_closing_kanban:** Añade la fecha de cierre prevista directamente en las tarjetas de la vista Kanban. Facilita el seguimiento visual de las oportunidades del equipo de ventas.
* **🔧 helpdesk_mgmt_maintenance:** Vincula los tickets de soporte con las órdenes de mantenimiento de equipos. Centraliza la asistencia técnica de la empresa.

### 👥 Recursos Humanos y Control de Asistencia
* **⏳ hr_attendance_menu_filter:** Incorpora filtros avanzados e intuitivos en el menú de asistencia de los empleados. Permite búsquedas rápidas por departamento y turnos.
* **⏱️ hr_attendance_user_edit_check_in_out:** Controla los permisos de edición sobre las horas de entrada y salida registradas. Evita alteraciones no autorizadas en el historial laboral.

### 👤 Datos Maestros y Contactos
* **🆔 partner_ref_mandatory:** Establece el campo de referencia interna como obligatorio al crear o editar un contacto. Evita la duplicidad de clientes y proveedores.

### 📂 Gestión de Proyectos
* **📈 project_task_report:** Genera análisis visuales detallados y tablas dinámicas sobre el progreso de las tareas. Permite auditar la productividad del equipo.

### 🛒 Compras (Purchases)
* **🔍 purchase_order_menu_filters:** Añade nuevas opciones de filtrado en el listado de pedidos de compra. Agiliza la búsqueda por estados de entrega y facturación.
* **❗ purchase_order_partner_ref_mandatory:** Exige incluir la referencia del proveedor antes de poder confirmar una orden de compra. Garantiza la trazabilidad en los pedidos.

### 📦 Ventas y Tiempos (Sales & Timesheets)
* **📑 sale_order_analytic_account_mandatory:** Hace obligatorio asociar una cuenta analítica a cada presupuesto o pedido de venta. Asegura la correcta distribución de costes.
* **📌 sale_order_client_order_ref_mandatory:** Fuerza la inclusión del número de pedido propio del cliente en las órdenes de venta. Facilita la conciliación administrativa externa.
* **🔢 sale_order_invoice_qty_number:** Muestra la cantidad precisa de productos facturados directamente en las líneas del pedido. Optimiza el control del stock entregado.
* **🚫 sale_order_remove_portal_timesheet:** Oculta las hojas de horas detalladas dentro del portal web accesible para los clientes. Mantiene la privacidad interna del trabajo.
* **💸 sale_order_report_wo_taxation:** Permite imprimir y enviar presupuestos de venta que muestran importes sin desglosar impuestos. Ideal para negociaciones comerciales iniciales.
* **🔒 task_billable_mangement:** Restringe la carga de horas solo a tareas facturables y en estado de desarrollo activo. Evita errores de imputación del personal.

### 🌐 Desarrollo Web y Sitio Web
* **🇪🇺 web_footer_gdpr_report:** Añade un enlace y reporte de cumplimiento de la normativa de privacidad GDPR en el pie de página web. Garantiza la legalidad del sitio.
* **🔘 website_product_button:** Personaliza y añade botones con llamadas a la acción dinámicas en las páginas de producto. Diseñado para incrementar las conversiones.
* **🏷️ website_product_price:** Optimiza la visualización de las tarifas, descuentos y precios especiales en la tienda online. Mejora la claridad del coste al usuario.
* **📝 website_sale_product_description_extended:** Extiende el campo de descripción técnica de los productos dentro del flujo de la tienda virtual. Ofrece mayor detalle al comprador.
* **🛠️ website_snipper_tabla_edit:** Introduce un bloque modular para diseñar y editar tablas dinámicas directamente en el constructor web. Facilita la creación visual de layouts.

---

## Odoo-16

### 💼 Facturación y Finanzas
* **🤖 snk_vendor_bill_ocr:** (Digitalización de Facturas Azure OCR) Automatiza de forma asíncrona la creación de facturas de proveedor en borrador extrayendo líneas, impuestos e IBAN mediante Azure AI Document Intelligence.

### 🤝 CRM y Soporte
* **📞 website_contacts_product:** Integración funcional que vincula consultas web de productos con el CRM de Odoo, transformando envíos de formularios en iniciativas comerciales.

### 📦 Gestión de Inventario y Logística
* **🗺️ CalculadorRutas:** Módulo de distribución logística para modelar rutas óptimas mediante la definición de nodos, enlaces operativos y un motor de cálculo dedicado.

### 🌐 Desarrollo Web y Comercio Electrónico
* **🛒 e-commerce_sale_order_cart:** Extensión que sobrescribe plantillas QWeb y optimiza flujos de datos en el frontend para mejorar la experiencia en el carrito de compras.
* **🛍️ e-commerce_sale_order_hide_category_shop:** Ajuste de interfaz con estilos SCSS heredados que oculta la barra lateral vertical de categorías para ofrecer una navegación más limpia y minimalista.
* **📄 website_sale_product_description_extended:** Expansión que inyecta capacidades de texto rico y multidimensional para mostrar fichas y descripciones técnicas avanzadas en el portal web.

---

## Odoo-17

### 📦 Gestión de Inventario y Logística
* **🚚 tms (Transport Management System):** Gestión de transporte: rutas, solicitudes, viajes, vehículos, conductores, kilometraje y facturación integrado en Odoo.

### 👤 Datos Maestros y Contactos
* **🥦 food_allergens_product:** Gestión de alérgenos alimentarios asociados a productos para control e información obligatoria.

---

## Odoo-18

### 🏪 Punto de Venta y Restauración
* **📦 pos_restaurant_api (API de Punto de Venta para Restaurantes):** Conexión omnicanal de aplicaciones móviles (React Native) y plataformas de delivery (Glovo, Just Eat) con el flujo de cocina y ventas nativo de Odoo.

---

## Odoo-19

### 📦 Gestión de Inventario y Logística
* **🚚 TMS (Transport Management System):** Módulo integral diseñado para optimizar los servicios de transporte y logística en Odoo 19, automatizando el control de rutas, la asignación de viajes detallados a conductores y la supervisión del mantenimiento vehicular.
