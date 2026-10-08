# Manual 1 - Sección del Integrante 2: Tienda Web, CRM y Correo Electrónico

## Proyecto QuetzalMart

> Esta sección se integra al Manual 1 junto con las de los demás integrantes. Las imágenes están en `./imagenes/integrante2/`.

---

## 1. Módulos instalados para la tienda, el CRM y el marketing

Sobre el ERP Odoo 17 ya desplegado en AWS se instalaron los módulos siguientes, mediante el script `01_instalar_modulos.py` (que usa la API XML-RPC de Odoo):

| Módulo | Para qué sirve |
| :--- | :--- |
| `website`, `website_sale` | Sitio web y tienda en línea: catálogo, carrito y proceso de compra |
| `delivery`, `website_sale_delivery` | Métodos y costo de envío dentro del carrito |
| `payment_demo`, `payment_custom` | Integración de pago (pasarela de demostración y transferencia bancaria) |
| `crm`, `website_crm` | Gestión de clientes y oportunidades; el formulario de contacto del sitio genera leads |
| `mass_mailing`, `website_mass_mailing` | Correo de marketing y suscripción desde la web |
| `base_automation` | Regla automática que envía la campaña después de una compra |

---

## 2. Tienda en línea

### 2.1 Configuración y publicación del catálogo

Con `02_configurar_tienda.py` se publicaron los 40 productos del catálogo, agrupados en 9 categorías (Alimentos, Lácteos, Bebidas, Carnes, Panadería, Snacks, Cuidado Personal, Limpieza y Hogar). Cada producto tiene imagen, descripción y precio con IVA incluido. También se creó el impuesto **IVA 12%** y el método de envío **Envío estándar QuetzalMart** (tarifa fija de 2.50, gratis en compras mayores a 25).

![](./imagenes/integrante2/10-productos-catalogo.png)
_Productos del catálogo en el ERP._

![](./imagenes/integrante2/11-metodos-envio.png)
_Método de envío configurado._

### 2.2 Portada y catálogo para el cliente

![](./imagenes/integrante2/01-portada.png)
_Portada de QuetzalMart con logo y categorías._

![](./imagenes/integrante2/02-catalogo.png)
_Catálogo con imágenes, nombre y precio de cada producto._

![](./imagenes/integrante2/03-detalle-producto.png)
_Detalle de un producto._

### 2.3 Carrito de compras, impuestos y envío

El cliente puede agregar y eliminar productos. El carrito calcula el IVA (12%) y el costo de envío.

![](./imagenes/integrante2/04-carrito.png)
_Carrito de compras._

### 2.4 Proceso de pago

Se activaron dos proveedores de pago: **Demo** (pasarela de demostración que simula el cobro con tarjeta) y **Transferencia bancaria**.

### 2.5 Pedidos y facturas generadas automáticamente

Al completar el pago, Odoo confirma el pedido de venta, genera la factura, la publica y registra el pago de forma automática (opción *Facturación automática* de Ventas).

![](./imagenes/integrante2/14-facturas.png)
_Listado de facturas._

![](./imagenes/integrante2/22-detalle-factura.png)
_Factura publicada y pagada, con su PDF._

---

## 3. Correo electrónico

### 3.1 Servidor de correo saliente

Odoo envía los correos por SMTP (`smtp.gmail.com`, puerto 587, cifrado STARTTLS) mediante el servidor saliente **QuetzalMart SMTP**, configurado con `03_configurar_correo.py`. Allí también se fijó la dirección pública del sitio (`web.base.url`) para que los enlaces de los correos funcionen, y se acortó el intervalo de la cola de correo a un minuto.

### 3.2 Correos de la compra

Tras una compra el cliente recibe, en este orden:
1. **Confirmación del pedido** (`QuetzalMart Orden (Ref S0xxxx)`) con el pedido en PDF adjunto.
2. **Factura** (`QuetzalMart Factura (Ref INV/...)`) con la factura en PDF adjunta.
3. **Campaña de marketing** (`QuetzalMart: gracias por tu compra, tienes 10% de descuento`).

![](./imagenes/integrante2/30-correo-confirmacion.png)
_Correo de confirmación recibido en una bandeja temporal._

![](./imagenes/integrante2/31-correo-factura.png)
_Correo con la factura adjunta._

### 3.3 Campaña de marketing automática

Se creó la plantilla HTML **QuetzalMart - Campaña de Marketing** (degradado naranja, cupón de descuento, botón a la tienda y tarjetas de categorías). Una regla automática la envía cuando la factura de una compra web queda pagada: se encola y sale aproximadamente un minuto después, para que llegue después del correo de la compra. Los dos tipos de correo tienen asuntos distintos y salen del servidor de la tienda, no de un buzón personal de un integrante.

![](./imagenes/integrante2/32-correo-marketing.png)
_Campaña de marketing recibida._

![](./imagenes/integrante2/16-correos-enviados.png)
_Registro de correos enviados por Odoo._

---

## 4. CRM: manejo de clientes

Se cargaron los clientes del ERP y 12 oportunidades de ejemplo (pedidos mayoristas, contratos de suministro, cotizaciones) con el script `06_cargar_crm.py`, repartidas en las etapas del embudo de ventas. Los visitantes que llenan el formulario de contacto del sitio generan un lead automáticamente.

---

## 5. Procedimiento de reproducción

Desde `Proyecto/Integrante2-Tienda-CRM-Marketing/`, con el archivo `.env` completo (se parte de `.env.example`):

```bash
pip install pillow
python 00_diagnostico.py          # estado inicial (solo lectura)
python 01_instalar_modulos.py     # módulos
python 02_configurar_tienda.py    # catálogo, IVA, envío, pagos
python 03_configurar_correo.py    # SMTP, campaña, regla automática
python 04_probar_correo.py --to alguien@temp-mail.org
python 06_cargar_crm.py           # oportunidades de ejemplo
python 08_logo_y_portada.py       # logo y portada
```

---

### Capturas que se toman a mano (temp-mail)
Hacer una compra en `http://3.140.234.169:8069/shop` con una dirección de temp-mail.org y guardar en `Manual1/imagenes/integrante2/`:
- `30-correo-confirmacion.png`: correo de la orden
- `31-correo-factura.png`: correo de la factura (con el clip de adjunto visible)
- `32-correo-marketing.png`: correo de la campaña
