# Modulos Personalizados Odoo 15

### 💼 Facturación y Finanzas
* **💰 account_invoice_user_authorization_payment**: Gestiona y restringe los flujos de autorización para pagos de facturas. Asegura que solo los usuarios permitidos validen transacciones monetarias.

### 🤝 CRM y Soporte
* **📊 crm_expected_closing_kanban**: Añade la fecha de cierre prevista directamente en las tarjetas de la vista Kanban. Facilita el seguimiento visual de las oportunidades del equipo de ventas.
* **🔧 helpdesk_mgmt_maintenance**: Vincula los tickets de soporte con las órdenes de mantenimiento de equipos. Centraliza la asistencia técnica de la empresa.

### 👥 Recursos Humanos y Control de Asistencia
* **⏳ hr_attendance_menu_filter**: Incorpora filtros avanzados e intuitivos en el menú de asistencia de los empleados. Permite búsquedas rápidas por departamento y turnos.
* **⏱️ hr_attendance_user_edit_check_in_out**: Controla los permisos de edición sobre las horas de entrada y salida registradas. Evita alteraciones no autorizadas en el historial laboral.

### 👤 Datos Maestros y Contactos
* **🆔 partner_ref_mandatory**: Establece el campo de referencia interna como obligatorio al crear o editar un contacto. Evita la duplicidad de clientes y proveedores.

### 📂 Gestión de Proyectos
* **📈 project_task_report**: Genera análisis visuales detallados y tablas dinámicas sobre el progreso de las tareas. Permite auditar la productividad del equipo.

### 🛒 Compras (Purchases)
* **🔍 purchase_order_menu_filters**: Añade nuevas opciones de filtrado en el listado de pedidos de compra. Agiliza la búsqueda por estados de entrega y facturación.
* **❗ purchase_order_partner_ref_mandatory**: Exige incluir la referencia del proveedor antes de poder confirmar una orden de compra. Garantiza la trazabilidad en los pedidos.

### 📦 Ventas y Tiempos (Sales & Timesheets)
* **📑 sale_order_analytic_account_mandatory**: Hace obligatorio asociar una cuenta analítica a cada presupuesto o pedido de venta. Asegura la correcta distribución de costes.
* **📌 sale_order_client_order_ref_mandatory**: Fuerza la inclusión del número de pedido propio del cliente en las órdenes de venta. Facilita la conciliación administrativa externa.
* **🔢 sale_order_invoice_qty_number**: Muestra la cantidad precisa de productos facturados directamente en las líneas del pedido. Optimiza el control del stock entregado.
* **🚫 sale_order_remove_portal_timesheet**: Oculta las hojas de horas detalladas dentro del portal web accesible para los clientes. Mantiene la privacidad interna del trabajo.
* **💸 sale_order_report_wo_taxation**: Permite imprimir y enviar presupuestos de venta que muestran importes sin desglosar impuestos. Ideal para negociaciones comerciales iniciales.
* **🔒 task_billable_mangement**: Restringe la carga de horas solo a tareas facturables y en estado de desarrollo activo. Evita errores de imputación del personal.

### 🌐 Desarrollo Web y Sitio Web
* **🇪🇺 web_footer_gdpr_report**: Añade un enlace y reporte de cumplimiento de la normativa de privacidad GDPR en el pie de página web. Garantiza la legalidad del sitio.
* **🔘 website_product_button**: Personaliza y añade botones con llamadas a la acción dinámicas en las páginas de producto. Diseñado para incrementar las conversiones.
* **🏷️ website_product_price**: Optimiza la visualización de las tarifas, descuentos y precios especiales en la tienda online. Mejora la claridad del coste al usuario.
* **📝 website_sale_product_description_extended**: Extiende el campo de descripción técnica de los productos dentro del flujo de la tienda virtual. Ofrece mayor detalle al comprador.
* **🛠️ website_snipper_tabla_edit**: Introduce un bloque modular para diseñar y editar tablas dinámicas directamente en el constructor web. Facilita la creación visual de layouts.


