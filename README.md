# Modulos Personalizados Odoo 16

# 📖 Resumen

**Odoo 16 Custom Modules Suite** es una colección de módulos empresariales a medida desarrollados para **Odoo v16 Community & Enterprise**. 

Esta suite se enfoca en mejorar la gestión logística mediante herramientas de rutas personalizadas, optimizar la experiencia de usuario (UX) en la tienda web y el carrito de compras, y conectar los formularios web de contacto directamente con el flujo de captura de iniciativas en Odoo CRM.

Diseñado para extender las capacidades nativas de Odoo, este repositorio demuestra un desarrollo limpio, modular y seguro para futuras actualizaciones en aplicaciones empresariales.

---

# 🚀 Características

- **Optimización de Rutas**: Modelado de redes estructurales para nodos de distribución logística.
- **Personalización del Carrito**: Alteración del diseño del flujo de pago y plantillas de comportamiento en el frontend.
- **UX Limpia en Tienda**: Visibilidad alternable de la barra lateral de categorías en la vista de la tienda.
- **Captura en CRM**: Correlación nativa de producto a iniciativa directamente desde formularios de consulta web.
- **Contenido Extendido**: Descripción ampliada para las plantillas de producto en las páginas del sitio web.
- **Arquitectura Limpia**: Extensiones seguras para actualizaciones sin alterar el código fuente original.

---

# 🏗 Arquitectura

```text
  Sitio Web E-commerce / Interfaz Web Frontend
                        │
                        ▼
               Motor Central Odoo 16
       (Website, CRM, Sale, Stock, Base)
                        │
                        ▼
      [ Esta Suite / Módulos Personalizados ]
                        │
                        ▼
               Base de Datos PostgreSQL
```

---

# 🛠 Tecnologías Utilizadas

- Python 3.8+
- Framework Odoo 16 (QWeb, Plantillas QWeb)
- XML (Vistas de Odoo, Acciones, Datos)
- SCSS / CSS
- JavaScript
- PostgreSQL
- Git

---

# 📂 Resumen de los Módulos

### 🗺 CalculadorRutas
Un módulo especializado en distribución logística creado para modelar rutas de transporte. Define nodos (ciudades), mapea enlaces operativos (conexiones), categoriza métodos de tránsito e introduce un motor de cálculo dedicado para computar rutas óptimas basadas en atributos variables del sistema.

### 🛒 e-commerce_sale_order_cart
Una extensión de comercio electrónico que sobrescribe las plantillas QWeb del frontend para personalizar el comportamiento y la apariencia de la página del carrito de compras. Refina la experiencia de pago del cliente al introducir flujos de datos optimizados y cambios de diseño durante la confirmación de la compra.

### 🙈 e-commerce_sale_order_hide_category_shop
Un ajuste elegante de la interfaz de usuario diseñado para ocultar la barra lateral vertical de categorías de productos por defecto en la tienda. Utiliza estilos SCSS personalizados y herencia de plantillas para ofrecer una interfaz de navegación minimalista y centrada en el producto.

### 🧲 website_contacts_product
Un componente funcional de integración con el CRM que vincula artículos del inventario comercial directamente con los formularios de consulta de los clientes. Rastrea los contextos específicos del producto durante las interacciones web y convierte los envíos de los usuarios en iniciativas estructuradas dentro del flujo del CRM.

### 📝 website_sale_product_description_extended
Un paquete de expansión de descripciones de inventario que actualiza los modelos estándar de las plantillas de producto y los diseños web. Inyecta capacidades para manejar textos ricos y multidimensionales, permitiendo que las descripciones técnicas profundas se muestren correctamente en las páginas de perfil del producto.

---

# ⚙ Instalación

1. Copia las cinco carpetas dentro del directorio de addons personalizados de Odoo (custom addons).
2. Reinicia tu instancia del Servidor Odoo 16.
3. Activa el **Modo Desarrollador** dentro de los Ajustes de Odoo.
4. Ve al menú **Aplicaciones** y haz clic en **Actualizar lista de aplicaciones**.
5. Busca los nombres de los módulos y haz clic en **Activar**.

---

# 📂 Estructura del Proyecto

```text
modulos-odoo/
├── CalculadorRutas/
├── e-commerce_sale_order_cart/
├── e-commerce_sale_order_hide_category_shop/
├── website_contacts_product/
└── website_sale_product_description_extended/
```

---

# 🎯 Propósito

El propósito de este repositorio es actuar como un espacio de despliegue centralizado para extensiones de Odoo 16 listas para entornos de producción. Cada módulo resuelve problemas técnicos específicos que van desde la lógica de distribución geométrica hasta modificaciones de la interfaz frontend, demostrando cómo el desarrollo modular optimiza los flujos de trabajo empresariales nativos.

---

# 👩‍💻 Autor

**Luciana Pinheiro**

Senior Odoo Developer • Odoo Functional Consultant • Python Developer

[![GitHub](https://shields.io)](https://github.com)
[![Portfolio](https://shields.io)](https://github.io)

*No dudes en conectar o abrir una incidencia si encuentras algún comportamiento inesperado.*


