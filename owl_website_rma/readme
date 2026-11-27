# OWL Website RMA (`owl_website_rma`)

Módulo personalizado para **Odoo** que implementa un portal web interactivo basado en el framework **OWL (Odoo Web Library)** para la gestión de devoluciones y autorizaciones de mercancía (**RMA - Return Merchandise Authorization**) directamente desde el sitio web / portal de clientes.

---

## Características Principales

* **Portal de Clientes Interactivo (OWL):** Interfaz reactiva en el frontend para solicitar y consultar devoluciones sin recargas de página.
* **Gestión de Solicitudes RMA en Backend:** Flujo completo de estados (borrador, en revisión, aprobado, recibido, rechazado) integrado con pedidos de venta, albaranes y facturas.
* **Controladores Web (`controllers/`):** Rutas HTTP/JSON seguras para la comunicación entre los componentes OWL del portal y el servidor de Odoo.
* **Multidioma (`i18n/`):** Soporte para traducciones (incluyendo localización en español).
* **Datos Iniciales y Secuencias (`data/`):** Secuencias automáticas para códigos de RMA y configuración base.

---

## Estructura del Módulo

```text
owl_website_rma/
├── controllers/        # Endpoints HTTP/JSON para el portal web y llamadas RPC desde OWL
├── data/               # Secuencias (ir.sequence) y datos maestros iniciales
├── i18n/               # Archivos de traducción (.po / .pot)
├── models/             # Modelos ORM, lógica de negocio y flujos de estado RMA
├── static/             # Componentes OWL (JS/XML), hojas de estilo (SCSS/CSS) y recursos
├── views/              # Vistas de backend (tree/list, form, search) y plantillas QWeb del portal
├── __init__.py
└── __manifest__.py
```

---

## Requisitos e Instalación

### 1. Dependencias
* **Odoo** (verificar versión exacta en `__manifest__.py`)
* Módulos estándar requeridos: `website`, `portal`, `sale_management`, `stock` *(ajustar según `depends` en `__manifest__.py`)*

### 2. Instalación
1. Clonar el repositorio dentro de la carpeta de `addons` personalizados:
   ```bash
   git clone https://github.com
   ```
2. Asegurarse de que la ruta esté incluida en `addons_path` dentro de `odoo.conf`.
3. Reiniciar el servicio de Odoo y actualizar la lista de aplicaciones (**Aplicaciones → Actualizar lista de aplicaciones**).
4. Buscar **`owl_website_rma`** y hacer clic en **Activar / Instalar**.

---

## Uso

1. **Cliente (Portal Web):** Accede a **Mi Cuenta → Devoluciones (RMA)** en el sitio web, selecciona el pedido/producto a devolver, indica el motivo y envía la solicitud mediante el componente OWL.
2. **Equipo Interno (Backend):** Gestiona las solicitudes desde el menú de **RMA / Devoluciones**, valida los productos recibidos y genera los movimientos de inventario o notas de crédito correspondientes.

---

## Licencia

Distribuido bajo licencia **LGPL-3** (o la especificada en `__manifest__.py`).

---

## Contacto & Redes

¡Conectemos! Si tienes alguna pregunta sobre este proyecto o estás buscando una Desarrolladora Full-Stack especializada en Odoo e Inteligencia Artificial, no dudes en contactarme:

* 🌍 **Sitio Web / Portfolio:** [lucpinheiro.github.io](https://github.io)
* 💻 **GitHub Profile:** [://github.com](https://://github.com)
* 📧 **Correo Electrónico:** lupinheiro.dev@gmail.com
* 📱 **Teléfono Móvil:** +34 618 38 85 17
