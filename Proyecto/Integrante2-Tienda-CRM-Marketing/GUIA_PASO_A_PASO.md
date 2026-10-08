# Guía paso a paso - Integrante 2 (Tienda Web, CRM y Email Marketing)

## Qué te toca y cuánto vale en la rúbrica

| Entregable | Puntos | Dónde se resuelve |
|---|---|---|
| Sitio web del ERP con buena presentación | 5 | Paso 3 (diseño) |
| Productos con imagen, descripción y precio | 2 | Script 02 |
| Carrito: agregar/eliminar, impuestos y envío | 2 | Script 02 |
| Integración de pago | 2 | Script 02 |
| Correo de compra con factura adjunta (llega durante la calificación) | 4 | Scripts 02 + 03 |
| Correo de campaña de marketing (vistoso y original) | 6 | Script 03 |
| 50 facturas en PDF en una carpeta | 1 + 1 | Script 05 |
| Manual 2: flujo del producto en la empresa y flujo del cliente web/tienda | parte de 3 + 5 | `Manual2/Manual2_Integrante2.md` |
| Manual 1: capturas de CRM, facturas y órdenes | parte de 5 | Paso 8 |

Los scripts leen las credenciales de un archivo `.env` que git ignora. No escribas contraseñas en el código.

## Paso 0 - Preparar tu máquina (5 min)

```bash
cd Proyecto/Integrante2-Tienda-CRM-Marketing
pip install pillow
cp .env.example .env
```

Abre `.env` y llena `ODOO_PASSWORD` (y más adelante los datos SMTP). Luego:

```bash
python 00_diagnostico.py
```

Es de solo lectura. Te dice versión de Odoo, moneda, módulos instalados, cuántas facturas hay y si ya existe un servidor de correo. Guarda esa salida; sirve para el Manual 1.

## Paso 1 - Instalar los módulos (10-15 min)

```bash
python 01_instalar_modulos.py
```

Instala tienda en línea, envíos, pagos, CRM, email marketing y reglas automáticas. Odoo se reinicia solo varias veces; el script espera. Si se corta, vuelve a correrlo: omite lo ya instalado.

## Paso 2 - Configurar la tienda (5 min)

```bash
python 02_configurar_tienda.py
```

Hace lo siguiente:
- Publica los 40 productos con categoría, descripción, precio e imagen (imágenes generadas, porque el CSV no trae fotos; si quieres fotos reales, cámbialas desde Odoo > Sitio web > Productos).
- Crea el IVA 12% y lo asigna a los productos.
- Crea el método de envío: 2.50 fijo, gratis sobre 25.
- Activa el pago de demostración y la transferencia bancaria.
- Activa la factura automática al pagar y el registro libre de usuarios.

Abre `http://3.140.234.169:8069/shop` y confirma que ves los productos.

## Paso 3 - Diseño del sitio (30-45 min, manual)

El script no puede hacer esto. En el navegador, como admin:

1. Entra a `http://3.140.234.169:8069/web`, abre **Sitio web** y pulsa **Editar**.
2. En la portada cambia el título y las imágenes por algo de QuetzalMart (alimentos, precios accesibles, 3 países).
3. Menú: deja **Inicio, Tienda, Contáctenos**.
4. En **Sitio web > Configuración > Ajustes** cambia el nombre del sitio a QuetzalMart y sube un logo (puedes hacerlo en Canva).
5. Pásale la **clave de Google Analytics** al Integrante 3 o pídele su ID de medición (`G-XXXXXXX`) y pégalo en **Ajustes > Google Analytics**. Sin eso él no puede medir nada.

## Paso 4 - Correo saliente (30 min)

Tu auxiliar recomendó Postfix con dominio propio. **Mi recomendación es no empezar por ahí:** EC2 bloquea por defecto el puerto 25 saliente (hay que pedir a AWS que lo libere), y sin dominio, SPF, DKIM y PTR los correos caen en spam. Él mismo dijo que si llegan a temp-mail sin dominio no hace falta implementarlo. Prueba en este orden:

**Opción A (la más rápida): cuenta Gmail dedicada al proyecto.**
1. Crea una cuenta nueva solo para esto, por ejemplo `quetzalmart.tienda@gmail.com`. No uses la de ningún integrante: el enunciado prohíbe que el correo salga de uno personal.
2. Actívale la verificación en dos pasos y crea una **contraseña de aplicación** (cuenta de Google > Seguridad > Contraseñas de aplicaciones).
3. En `.env` pon `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USER` y `SMTP_FROM` con esa dirección, `SMTP_PASSWORD` con la contraseña de aplicación.

**Opción B (si Gmail falla o la bloquea):** un relay gratuito como Brevo o SMTP2GO. Verificas un remitente, te dan host, usuario y clave SMTP, y los pones en el mismo `.env` (puerto 587).

**Opción C (último recurso): Postfix** en la instancia, con dominio, registros SPF/DKIM/DMARC y el puerto 25 liberado.

Cuando tengas la opción elegida:

```bash
python 03_configurar_correo.py
python 04_probar_correo.py --to TU_DIRECCION@temp-mail.org
```

Abre https://temp-mail.org/es, copia la dirección temporal y úsala en `--to`. Debe llegar el correo de prueba. Luego prueba la campaña:

```bash
python 04_probar_correo.py --to TU_DIRECCION@temp-mail.org --marketing
```

El script 03 también crea la regla automática: cuando una factura de una compra web queda pagada, se encola el correo de marketing 1 minuto después. Así llegan primero los correos de la compra y después el de campaña.

## Paso 5 - Prueba de compra completa (15 min)

Esto es exactamente lo que hará el auxiliar. Hazlo en una ventana de incógnito:

1. Entra a `http://3.140.234.169:8069/shop`, agrega 2-3 productos, elimina uno.
2. Verifica que se calculan impuestos y envío.
3. **Pagar pedido**: regístrate con una dirección de temp-mail.org, elige el pago de demostración.
4. Espera 1-3 minutos y revisa temp-mail. Deben llegar: la confirmación del pedido, la factura en PDF adjunta y, al final, la campaña de marketing.
5. En Odoo revisa **Facturación > Clientes > Facturas** que la factura esté publicada y pagada.

Si el correo de campaña no llega, mira **Ajustes > Técnico > Automatización > Reglas de acción automatizada** y **Técnico > Correo electrónico > Correos** (ahí aparece el motivo del fallo). Alternativa manual: crea la regla desde la interfaz con el mismo filtro.

Nota: Odoo envía por defecto el correo de confirmación del pedido y además el de la factura. Son tres correos, no dos. Si el auxiliar exige exactamente dos, desactiva la factura automática en **Ventas > Ajustes > Facturación automática**, pero entonces la factura no se genera sola.

## Paso 6 - Las 50 facturas en PDF (10 min)

```bash
python 05_exportar_facturas_pdf.py
```

Si dice que hay pocas publicadas y sí hay borradores (la carga masiva del Integrante 1 las deja en borrador), repite así. Esto modifica datos compartidos, avísale a tu equipo:

```bash
python 05_exportar_facturas_pdf.py --publicar-borradores
```

Los PDF quedan en `Proyecto/Facturas-PDF/`. Esa carpeta es la que muestras en la calificación; cópiala también a la máquina que llevarás.

## Paso 7 - CRM (10 min)

```bash
python 06_cargar_crm.py
```

Crea 12 oportunidades en el embudo. Entra a **CRM** y arrastra algunas entre etapas para tener capturas. En el Manual 1 se pide "manejo de clientes en CRM": captura el listado de contactos, una oportunidad abierta y el formulario de contacto del sitio generando un lead.

## Paso 8 - Capturas para el Manual 1 (30 min)

Toma estas capturas con fecha y URL visibles:
1. Instalación de los módulos (salida del script 01 o la pantalla Aplicaciones).
2. Catálogo de la tienda, carrito con impuestos y envío, pago.
3. Configuración del método de pago y del servidor de correo (oculta la contraseña).
4. Correo de compra con factura adjunta y correo de marketing en temp-mail.
5. Listado de facturas en Odoo y la carpeta `Facturas-PDF`.
6. CRM: embudo y una oportunidad.

Pásale esas capturas y un párrafo corto de explicación al Integrante 5, que arma los manuales.

## Paso 9 - Manual 2

Ya está escrito en `Proyecto/Manual2/Manual2_Integrante2.md`: flujo del producto en la empresa y flujo del cliente web/tienda, ambos en Mermaid. Para el PDF conviene renderizarlos en https://mermaid.live y exportar a PNG.

## Antes del día de calificación

- Repite la compra de prueba 24 horas antes y confirma que llegan los correos.
- Ten abierto el temp-mail del auxiliar o pídele que use la dirección que él quiera: el correo sale del servidor, no depende de la dirección.
- Si la instancia EC2 se reinicia, Odoo debe levantar solo (`restart: unless-stopped`), pero confírmalo.
- Anota quién del equipo tiene acceso al SMTP; si se bloquea la cuenta durante la calificación no habrá puntos de correo (10 pts).
