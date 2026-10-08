# SNK Vendor Bill OCR — Odoo 16 Community

Módulo para crear facturas de proveedor (`account.move`, tipo `in_invoice`) en
borrador a partir de PDF o fotografías. Utiliza el modelo oficial
`prebuilt-invoice` de Azure AI Document Intelligence, API `2024-11-30`.

## Características

- Asistente **Facturación → Proveedores → Digitalizar factura**.
- PDF como formato principal; también JPEG, PNG y TIFF.
- Validación del contenido real, tamaño, cifrado y número de páginas del PDF.
- Procesamiento asíncrono mediante cron, sin dependencias OCA.
- Adjunta y conserva el documento original antes de llamar a Azure.
- Extrae proveedor, NIF/VAT, número, fechas, vencimiento, pedido de compra,
  divisa, bases, impuestos, total, líneas, códigos de producto e IBAN.
- Asocia el proveedor primero por NIF/VAT y después por nombre exacto.
- Creación opcional de proveedor, únicamente cuando se detecta un NIF/VAT.
- Empareja productos por referencia del proveedor o referencia interna.
- Reglas configurables por proveedor/texto para producto, cuenta e impuestos.
- Crea una línea resumen cuando Azure no obtiene un desglose fiable.
- Asigna impuestos de compra por porcentaje y tolerancia configurable. Si Azure
  omite el tipo en una factura con un único IVA, lo infiere como
  `impuestos / base` únicamente cuando coincide con un impuesto de compra de
  Odoo. No aplica tipos efectivos ambiguos en facturas con varios IVAs.
- Para conservar las etiquetas y reparticiones fiscales correctas, tienen
  prioridad los impuestos indicados en una regla de mapeo y, después, los
  impuestos de compra del producto que coincidan con el porcentaje detectado.
- Compara los totales calculados por Odoo con los extraídos por Azure.
- Detecta duplicados exactos por SHA-256 y probables por proveedor/referencia o
  fecha/importe.
- Nunca crea ni cambia cuentas bancarias desde un IBAN OCR. Solo selecciona una
  cuenta ya existente si coincide exactamente.
- Nunca contabiliza automáticamente. Por defecto exige confirmación humana.
- Bloquea `action_post` mientras el OCR esté pendiente, con error o sin revisar.
- Registra usuario y fecha de revisión.
- Reintentos controlados ante timeout, HTTP 429 y errores 5xx.
- Configuración, credencial y cuotas independientes por compañía.
- Límites estrictos diarios, mensuales y de páginas antes de enviar a Azure.
- Registro auditable de cada intento y sus páginas procesadas.
- Protección contra endpoints HTTP, credenciales en URL y hosts ajenos a Azure.

## Instalación

1. Copiar `snk_vendor_bill_ocr` a una ruta de `addons_path`.
2. Reiniciar Odoo.
3. Actualizar la lista de aplicaciones.
4. Instalar **SNK Vendor Bill OCR**.

Utiliza `requests` y el lector PDF incluido en los requisitos estándar de Odoo
16. No necesita el SDK de Azure.

## Azure

Puede utilizar el mismo recurso oficial **Azure AI Document Intelligence** que
el módulo `snk_expense_ocr`; solo tiene que introducir el mismo endpoint y la
misma clave en la configuración de este módulo. No hace falta adquirir ninguna
aplicación de terceros en Azure Marketplace.

El modelo empleado es `prebuilt-invoice`, diseñado para facturas, facturas de
suministros, pedidos de venta y pedidos de compra. Admite PDF y fotografías.

En **Facturación → Configuración → Ajustes**:

1. Active el OCR de facturas.
2. Pegue el endpoint HTTPS del recurso Document Intelligence.
3. Pegue una clave de Azure.
4. Seleccione una cuenta de gasto predeterminada.
5. Ajuste páginas y cuotas.
6. Pulse **Validar configuración**.

La clave se guarda por compañía en `ir.config_parameter` y no vuelve a mostrarse.
La desinstalación elimina estos parámetros.

## Configuración recomendada inicial

| Parámetro | Valor recomendado |
| --- | ---: |
| Revisión humana | Activada |
| Crear proveedor | Desactivado |
| Tamaño máximo | 4 MB en Azure F0 |
| Páginas máximas | 2 en Azure F0 |
| Límite diario | 50 peticiones |
| Límite mensual | 500 peticiones |
| Confianza mínima | 0,75 |
| Tolerancia fiscal | 0,25 puntos |
| Tolerancia de importes | 0,05 |

En S0 puede aumentar tamaño y páginas, pero el coste se calcula por página.
El módulo envía siempre el parámetro `pages=1-N`, por lo que Azure no debe
analizar más páginas que el máximo configurado.

Los límites diarios y mensuales cuentan **intentos de POST**, también si la
respuesta falla o se pierde. Es intencionadamente conservador para proteger el
presupuesto. Los presupuestos y alertas de Azure deben mantenerse como segunda
capa de control.

## Flujo

1. El usuario sube el PDF o foto.
2. Odoo crea inmediatamente una factura vacía en borrador, adjunta el original
   y calcula su SHA-256.
3. El cron envía el documento a Azure y consulta la operación asíncrona.
4. Odoo carga los datos y líneas extraídos.
5. Las incoherencias aparecen como avisos; la factura queda en **Revisar**.
6. El usuario corrige proveedor, fechas, referencia, cuentas, impuestos y líneas.
7. Pulsa **Confirmar revisión OCR**.
8. Solo entonces se permite contabilizar mediante el botón estándar de Odoo.

## Reglas de líneas

En **Facturación → Configuración → Reglas OCR de facturas** se pueden definir
reglas por texto exacto, contenido o expresión regular. Una regla puede limitarse
a un proveedor y asignar producto, cuenta de gasto e impuestos. Se aplica la
primera coincidencia por secuencia.

Sin regla, el módulo intenta:

1. referencia del proveedor (`product.supplierinfo.product_code`);
2. referencia interna del producto (`default_code`);
3. producto y cuenta predeterminados.

## Controles de fraude y duplicados

- El mismo archivo no puede utilizarse dos veces en una compañía.
- Si coincide proveedor y número de factura, se marca un posible duplicado.
- Sin número, se compara proveedor, fecha, divisa e importe.
- Para aceptar un posible duplicado se exige una nota de revisión.
- Un IBAN desconocido genera un aviso y nunca modifica datos bancarios.
- El módulo no crea pagos ni contabiliza asientos automáticamente.

## Privacidad

El documento se envía al endpoint Azure configurado. La respuesta JSON completa
no se conserva por defecto porque puede contener todo el texto, direcciones y
datos bancarios de la factura. Proteja la base de datos y sus copias de seguridad.

## Pruebas

```bash
./odoo-bin -d test_vendor_bill_ocr --test-enable --stop-after-init \
  -i snk_vendor_bill_ocr --test-tags /snk_vendor_bill_ocr
```

Las pruebas cubren parser v4, creación de líneas e impuestos, proveedor por VAT,
revisión, bloqueo de contabilización, seguridad del endpoint, operación
asíncrona, límite de páginas, cuotas, IBAN, reglas, duplicado exacto y protección
de campos técnicos.
