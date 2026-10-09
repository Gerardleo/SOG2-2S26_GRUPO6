# Manual 2 - Diagramas de Flujo de Procesos de Negocio
## QuetzalMart ERP - Sección Compras y Ventas

Este documento contiene la descripción exhaustiva y los diagramas de flujo interactivos en **Mermaid** para los procesos de **Compras a Proveedores** y **Ventas de Productos**, tal como lo estipula el enunciado del proyecto.

---

## 1. Proceso de Compras a Proveedores

### 1.1 Descripción Detallada del Proceso

El proceso de compras de la cadena QuetzalMart está diseñado para abastecer tanto mercadería para venta (alimentos, bebidas, abarrotes) como materiales e insumos operativos requeridos para el funcionamiento de sus sucursales (Guatemala Central, Sucursal México y Sucursal El Salvador).

1. **Detección de Necesidad y Requisición:**
   - La sucursal o el departamento de inventario detecta un nivel bajo de existencias (stock mínimo alcanzado) o una solicitud especial de insumos operativos (materiales de empaque, rollos POS, limpieza).
   - Se genera una **Requisición de Compra interna** en el ERP Odoo.

2. **Gestión de Compras y Solicitud de Cotizaciones (RFQ):**
   - El encargado de compras evalúa la solicitud y genera **Solicitudes de Presupuesto (RFQ)** a uno o más proveedores registrados en el catálogo.
   - Los proveedores envían sus cotizaciones con precios, tiempos de entrega y condiciones de crédito.

3. **Comparativa y Aprobación de Orden de Compra (PO):**
   - Compras compara condiciones y selecciona la oferta óptima.
   - Si el monto excede el límite operativo estándar, pasa por autorización gerencial.
   - Se confirma la orden en Odoo, pasando a estado **Orden de Compra Confirmada (Purchase Order)**. Se notifica formalmente al proveedor vía correo electrónico.

4. **Recepción de Mercadería y Control de Calidad:**
   - El transportista del proveedor arriba a la bodega de la sucursal correspondiente.
   - El equipo de recepción realiza la verificación física de bultos contra la orden de compra y la nota de entrega del proveedor.
   - **Control de Calidad:** Se inspecciona el estado de los productos (fechas de caducidad, empaques íntegros, especificaciones correctas).
     - **Si se detectan anomalías:** Se rechaza el lote dañado, se emite un acta de discrepancia y se solicita reposición o nota de crédito.
     - **Si es conforme:** Se valida la recepción en Odoo, generando el movimiento de entrada en inventario (*Albarán / Stock Picking*).

5. **Recepción y Conciliación de Factura (3-Way Matching):**
   - El proveedor entrega la factura fiscal.
   - Contabilidad realiza el cruce tripartito en Odoo:
     1. Orden de Compra original.
     2. Albarán de recepción de bodega efectivamente recibido.
     3. Factura del proveedor (cantidades y precios unitarios).
   - Si concuerda, la factura se valida y se contabiliza en las cuentas por pagar de la empresa.

6. **Programación y Ejecución del Pago:**
   - Finanzas programa el pago según las condiciones pactadas (contado, 15, 30 o 60 días).
   - Se realiza la transferencia bancaria o cheque y se registra el comprobante de pago en el módulo contable de Odoo, cerrando la orden de compra.

---

### 1.2 Diagrama de Flujo: Compras a Proveedores (Mermaid)

```mermaid
flowchart TD
    subgraph Sucursal["Sucursal / Almacen Solicitante"]
        A1["Inicio: Deteccion de necesidad o stock minimo"] --> A2["Generar Requisicion de Compra interna en Odoo"]
    end

    subgraph Compras["Departamento de Compras"]
        A2 --> B1["Revisar y consolidar requisicion"]
        B1 --> B2["Seleccionar proveedores y emitir RFQ (Solicitud de Cotizacion)"]
        B2 --> B3["Recepcion y analisis comparativo de cotizaciones"]
        B3 --> B4{"Requiere aprobacion gerencial?"}
        B4 -- "Si (Monto elevado)" --> B5["Autorizacion de Gerencia General"]
        B4 -- "No" --> B6["Confirmar Orden de Compra (Purchase Order) en Odoo"]
        B5 --> B6
        B6 --> B7["Envio formal de Orden de Compra al Proveedor"]
    end

    subgraph Proveedor["Proveedor Externo"]
        B7 --> C1["Recibir orden y procesar pedido"]
        C1 --> C2["Despacho y transporte de mercaderia a QuetzalMart"]
    end

    subgraph Recepcion["Recepcion y Bodega QuetzalMart"]
        C2 --> D1["Llegada a muelle de descarga"]
        D1 --> D2["Inspeccion fisica y control de calidad"]
        D2 --> D3{"Cumple estandares de calidad y cantidad?"}
        D3 -- "No (Producto danado o faltante)" --> D4["Rechazar mercaderia y levantar Acta de Discrepancia"]
        D4 --> B2
        D3 -- "Si (Aprobado)" --> D5["Firmar comprobante de entrega"]
        D5 --> D6["Validar recepcion en Odoo (Albaran de Entrada)"]
        D6 --> D7["Ubicar mercaderia o insumos en estanterias"]
    end

    subgraph Contabilidad["Contabilidad y Finanzas"]
        D6 --> E1["Recepcion de Factura Fiscal del Proveedor"]
        E1 --> E2["Conciliacion Tripartita (PO vs Recepcion vs Factura)"]
        E2 --> E3{"Datos coinciden al 100%?"}
        E3 -- "No" --> E4["Contactar a proveedor para correccion o nota de credito"]
        E4 --> E1
        E3 -- "Si" --> E5["Validar y asentar Factura en Odoo"]
        E5 --> E6["Programar pago segun terminos (15/30 dias)"]
        E6 --> E7["Emitir pago bancario y conciliar asiento"]
        E7 --> E8["Fin: Proceso de Compra Completado"]
    end
```

---

## 2. Proceso de Ventas de Productos

### 2.1 Descripción Detallada del Proceso

El proceso de ventas de QuetzalMart abarca tanto la atención presencial en salas de venta y supermercados, la atención a clientes mayoristas/corporativos (con presupuestos y cotizaciones formales), como la integración de pedidos provenientes del portal web de e-commerce.

1. **Recepción del Requerimiento / Solicitud del Cliente:**
   - El cliente se presenta en tienda, solicita una cotización formal (clientes mayoristas/empresas) o realiza una solicitud mediante el canal comercial.
   - En ventas corporativas o grandes volúmenes, el asesor comercial elabora un **Presupuesto / Cotización (`sale.order` en estado borrador)** con validez temporal y precios preferenciales.

2. **Verificación de Inventario y Disponibilidad:**
   - El sistema ERP Odoo verifica en tiempo real la disponibilidad de stock en el almacén de la sucursal seleccionada (Guatemala, México o El Salvador).
   - Si no hay existencia suficiente, se notifica al cliente con alternativas de fecha de entrega o se solicita reposición interna de bodega central.

3. **Confirmación de la Orden de Venta:**
   - El cliente acepta la cotización o realiza la compra directa.
   - La orden pasa al estado **Pedido de Venta Confirmado (`sale.order`)**.
   - Odoo reserva de inmediato las unidades en inventario para evitar desabastecimiento o sobreventa.

4. **Preparación del Pedido (Picking y Packing):**
   - El almacén recibe la orden de recolección (*Picking*).
   - El personal de bodega recolecta los artículos de las góndolas/estanterías y realiza el empaque (*Packing*) con los materiales de embalaje de QuetzalMart.
   - Se realiza una verificación de bultos y etiquetado final.

5. **Facturación y Cobro:**
   - El sistema genera la **Factura de Venta (`account.move`)**.
   - Se procesa el cobro a través del medio de pago seleccionado:
     - Efectivo o terminal POS en tienda física.
     - Pasarela de pago en pedidos web.
     - Transferencia bancaria o crédito acordado (15/30 días) para clientes corporativos.
   - El comprobante fiscal y factura electrónica se entrega físicamente o se remite por correo electrónico.

6. **Despacho, Entrega y Cierre:**
   - El pedido se entrega al cliente en mostrador o se despacha mediante la unidad de transporte/envío a domicilio.
   - El cliente firma el acuse de recibo conforme.
   - El albarán de salida se valida en Odoo, rebajando definitivamente el inventario físico y contable.
   - Fin del ciclo de venta.

---

### 2.2 Diagrama de Flujo: Ventas de Productos (Mermaid)

```mermaid
flowchart TD
    subgraph Cliente["Cliente (Minorista, Mayorista o Web)"]
        V1["Inicio: Solicitud de compra o pedido de cotizacion"] --> V2["Seleccion de productos y requerimiento"]
    end

    subgraph Ventas["Departamento Comercial / Caja / E-Commerce"]
        V2 --> W1["Ingreso de requerimiento al ERP Odoo"]
        W1 --> W2{"Tipo de cliente / Venta?"}
        W2 -- "Corporativo / Mayorista" --> W3["Elaborar Presupuesto/Cotizacion en Odoo"]
        W2 -- "Tienda Directa o Web" --> W4["Cargar articulos al carrito / orden"]
        W3 --> W5["Envio de cotizacion al cliente para aprobacion"]
        W5 --> W6{"Cliente aprueba presupuesto?"}
        W6 -- "No" --> W7["Modificar propuesta o Cancelar Cotizacion"]
        W6 -- "Si" --> W4
        W4 --> W8["Verificar disponibilidad de stock en ERP Odoo"]
        W8 --> W9{"Hay stock disponible suficiente?"}
        W9 -- "No" --> W10["Informar tiempo de reposicion o sugerir producto sustituto"]
        W10 --> W2
        W9 -- "Si" --> W11["Confirmar Pedido de Venta en Odoo"]
        W11 --> W12["Reserva automatica de mercaderia en inventario"]
    end

    subgraph Almacen["Bodega y Despacho QuetzalMart"]
        W12 --> X1["Generacion de Albaran de Salida (Picking List)"]
        X1 --> X2["Recoleccion de mercaderia en estantes (Picking)"]
        X2 --> X3["Empaque y etiquetado de seguridad (Packing)"]
        X3 --> X4["Control de verificacion final de pedido"]
    end

    subgraph Finanzas["Facturacion y Cobranza"]
        W11 --> Y1["Emision automatica de Factura de Venta en Odoo"]
        Y1 --> Y2["Procesar cobro (POS, Efectivo, Tarjeta, Credito corporativo)"]
        Y2 --> Y3{"Pago aprobado o credito validado?"}
        Y3 -- "No" --> Y4["Gestionar reintento o retener despacho"]
        Y3 -- "Si" --> Y5["Emitir Factura Electronica y Recibo Oficial"]
    end

    subgraph Entrega["Entrega al Cliente"]
        X4 --> Z1["Coordinar entrega en tienda o ruta de envio"]
        Y5 --> Z1
        Z1 --> Z2["Entrega fisica de producto y factura al cliente"]
        Z2 --> Z3["Firma de recepcion a conformidad por el cliente"]
        Z3 --> Z4["Validar salida definitiva de stock en Odoo"]
        Z4 --> Z5["Fin: Transaccion de Venta Finalizada"]
    end
```

---

## 3. Puntos de Auditoría y Verificación en el ERP Odoo

Para corroborar la correcta ejecución de estos dos flujos en la calificación del proyecto:

| Proceso | Modelo / Objeto Odoo | Tabla Base de Datos | Estado Requerido |
| :--- | :--- | :--- | :--- |
| **Compras Realizadas** | `purchase.order` | `purchase_order` | `purchase` / `done` (Mínimo 100 registros) |
| **Facturas de Compras** | `account.move` | `account_move` | `move_type = 'in_invoice'`, `posted` |
| **Cotizaciones de Compra** | `purchase.order` | `purchase_order` | `draft` / `sent` (Mínimo 10 solicitudes) |
| **Cotizaciones de Venta** | `sale.order` | `sale_order` | `draft` / `sent` (Mínimo 10 presupuestos) |
| **Ventas Confirmadas** | `sale.order` | `sale_order` | `sale` / `done` (Mínimo 150 órdenes) |
| **Facturas de Ventas** | `account.move` | `account_move` | `move_type = 'out_invoice'`, `posted` |
| **Materiales e Insumos** | `product.product` | `product_product` | `default_code LIKE 'MAT-%'` (Mínimo 60) |

## 4. Diagrama de Flujo del Proceso RPA con UiPath (Incisos Realizados con UiPath)

### 4.1 Descripción Detallada del Proceso Automatizado

Este diagrama describe la automatización de Robotic Process Automation (RPA) desarrollada en **UiPath** para solucionar el problema planteado en el enunciado: el departamento de ventas posee una jerarquía inicialmente poco práctica de carpetas (clientes, proveedores, reclamos, registro, productos) con nombres de archivo que contienen guiones y descripciones adicionales, y cada archivo Excel contiene varias hojas, de las cuales únicamente interesan las hojas llamadas **`clientes`** y **`productos`**.

El bot se divide en tres niveles: el orquestador (`Main`), el procesamiento de cada hoja (`ProcesarClientes` y `ProcesarProductos`) y los flujos de comunicación con Odoo (`OdooLogin`, `OdooSearch`, `OdooExec` y `POST_Xml`).

1. **Inicialización del Bot:**
   - El robot se ejecuta desde UiPath Studio (*Ejecutar*) durante la calificación.
   - Se cargan los argumentos: ruta de la carpeta de entrada, ruta de la carpeta del LOG, URL del ERP Odoo en la nube, nombre de la base de datos, usuario y contraseña.

2. **Exploración Recursiva de la Jerarquía de Carpetas:**
   - El bot obtiene todos los archivos Excel (`*.xls*`) de forma recursiva, sin importar la profundidad de las carpetas, y descarta los archivos temporales de Excel (`~$`).
   - Si no se encuentra ningún archivo, el bot muestra un mensaje y finaliza con error.

3. **Autenticación en Odoo:**
   - `OdooLogin` envía el método `authenticate` al endpoint `/xmlrpc/2/common` y obtiene el `uid` del usuario.
   - Si el `uid` no es válido o la respuesta trae un `fault`, el bot se detiene con un mensaje claro. El login se realiza una sola vez y el `uid` se reutiliza en todo el proceso.

4. **Detección de Hojas Relevantes:**
   - Para cada archivo, un **Invocar código** (`ListarHojas`) abre el `.xlsx` como archivo comprimido, lee la lista de hojas y devuelve el nombre exacto de las hojas `clientes` y `productos` (sin distinguir mayúsculas).
   - Los archivos que no tienen ninguna de las dos se omiten y se registran en el LOG como `SKIP | Sin hojas clientes/productos`.

5. **Procesamiento de la hoja `clientes` (`ProcesarClientes`):**
   - Se lee la hoja con **Utilice el archivo de Excel** y **Leer rango** (primera fila como encabezados) y se valida que exista la columna `Name` (se aceptan encabezados como `Name*`).
   - Cada fila pasa por `PrepararFila`, que normaliza los encabezados y escapa los caracteres XML. Las filas totalmente vacías se ignoran.
   - Si la fila no tiene `Name`, se registra `ERROR`. Si el cliente ya existe (búsqueda por `name`), se registra `SKIP | DUPLICADO`.
   - Se resuelven las llaves foráneas: país, estado, empresa relacionada y etiqueta (la etiqueta se crea si no existe). Si país o estado no existen en Odoo, se omiten y el cliente se crea igual.
   - Se arma el diccionario de campos y se crea el registro en `res.partner` con `execute_kw`.

6. **Procesamiento de la hoja `productos` (`ProcesarProductos`):**
   - Se lee la hoja de la misma forma y se ubica una sola vez la ubicación de stock (`stock.location`).
   - Cada fila pasa por `PrepararFila`. Se calcula un código único a partir de `Internal Reference` o `External ID`.
   - Duplicados: se busca por `barcode`, luego por código interno (`default_code`) y por último por `name`.
   - `ArmarProducto` valida `Sales Price`, `Cost` y `Weight`. Si alguno no es numérico, la fila se omite como `SKIP | DATO INVALIDO` y no se crea nada.
   - Creación en pasos: `create` en `product.template`, búsqueda de la variante, `write` de `default_code` y `barcode` en `product.product` y, si hay `Cantidad a la mano`, creación y aplicación de un `stock.quant`.

7. **Comunicación con Odoo:**
   - `OdooExec` arma el `execute_kw` y lo envía mediante `POST_Xml` (una **Solicitud HTTP** `POST` con `text/xml`). Si la respuesta trae un `fault`, lanza una excepción con el mensaje de Odoo.
   - `OdooSearch` ejecuta `search` con un dominio `[campo = valor]` y devuelve el id o `0` si no existe. Se usa para duplicados y llaves foráneas.

8. **Manejo de Errores y Trazabilidad:**
   - Cada fila se procesa dentro de un `Try/Catch`: un error puntual no detiene el proceso; se registra y continúa con la siguiente fila.
   - Cada archivo se procesa dentro de su propio `Try/Catch` en `Main`, por lo que un archivo dañado o con formato no soportado no detiene a los demás.

9. **Cierre y Verificación:**
   - En el bloque `Finally`, el bot escribe `log_carga_rpa.txt` con el detalle por fila y muestra un cuadro de resumen con clientes cargados, productos cargados y archivos ignorados.
   - La información se verifica en las aplicaciones **Contactos** e **Inventario** de Odoo y con consultas SQL en PostgreSQL.

---

### 4.2 Diagrama de Flujo General (`Main`)

```mermaid
flowchart TD
    A0(["Inicio: ejecucion del bot en UiPath Studio"]) --> A1["Cargar argumentos: ruta de entrada, ruta de LOG,<br/>URL de Odoo, BD, usuario y password"]
    A1 --> A2["Crear carpeta de LOG y obtener archivos Excel<br/>GetFiles(ruta, '*.xls*', AllDirectories)<br/>descartando temporales ~$"]
    A2 --> A3{"Se encontraron archivos?"}
    A3 -- "No" --> A4["Mostrar mensaje: no se encontraron archivos Excel"]
    A4 --> Z1(["Fin con error"])
    A3 -- "Si" --> A5["OdooLogin: authenticate en /xmlrpc/2/common<br/>obtener uid"]
    A5 --> A6{"uid valido?"}
    A6 -- "No" --> A7["Detener: login fallido en Odoo"]
    A7 --> Z1
    A6 -- "Si" --> B1

    B1["Para cada archivo: tomar el siguiente"] --> B2["ListarHojas: leer nombres de hojas del .xlsx<br/>y detectar clientes / productos"]
    B2 --> B3{"Tiene hoja clientes<br/>o productos?"}
    B3 -- "No" --> B4["LOG: SKIP - sin hojas clientes/productos<br/>ignorados + 1"]
    B4 --> B9
    B3 -- "Si" --> C1{"Tiene hoja clientes?"}
    C1 -- "Si" --> C2["Invocar ProcesarClientes<br/>(ver diagrama 4.3)"]
    C1 -- "No" --> D1
    C2 --> D1{"Tiene hoja productos?"}
    D1 -- "Si" --> D2["Invocar ProcesarProductos<br/>(ver diagrama 4.4)"]
    D1 -- "No" --> B9
    D2 --> B9{"Quedan archivos por procesar?"}
    B9 -- "Si" --> B1
    B9 -- "No" --> E1

    X1["Error en un archivo: Try/Catch de Main<br/>registra ERROR en LOG y sigue con el siguiente"]
    B2 -.-> X1
    C2 -.-> X1
    D2 -.-> X1
    X1 -.-> B9

    E1["Finally: agregar encabezado al LOG<br/>y escribir log_carga_rpa.txt"] --> E2["Cuadro de resumen: clientes cargados,<br/>productos cargados y archivos ignorados"]
    E2 --> E3["Verificacion en Odoo: Contactos e Inventario"]
    E3 --> E4["Verificacion en PostgreSQL: consultas SQL<br/>de conteo y ultimos registros"]
    E4 --> Z2(["Fin: proceso completado"])
```

---

### 4.3 Diagrama de Flujo: `ProcesarClientes`

```mermaid
flowchart TD
    P0(["Entrada: archivo, hoja, credenciales, uid"]) --> P1["Utilice el archivo de Excel + Leer rango<br/>hoja clientes con encabezados: dtClientes"]
    P1 --> P2{"Existe la columna Name<br/>o Name*?"}
    P2 -- "No" --> PX["Lanzar error: el archivo se registra<br/>como ERROR en Main"]
    P2 -- "Si" --> P3{"La hoja tiene filas?"}
    P3 -- "No" --> PF(["Fin: hoja vacia"])
    P3 -- "Si" --> R0

    R0["Para cada fila"] --> R1["Reiniciar ids a 0"]
    R1 --> R2["PrepararFila: normalizar encabezados (Name* a Name)<br/>y escapar caracteres XML"]
    R2 --> R3{"Fila completamente vacia?"}
    R3 -- "Si" --> RN
    R3 -- "No" --> R4{"Name vacio?"}
    R4 -- "Si" --> R5["LOG: CREATE - ERROR: fila sin Name"]
    R5 --> RN
    R4 -- "No" --> R6["OdooSearch en res.partner por name"]
    R6 --> R7{"Ya existe?"}
    R7 -- "Si" --> R8["LOG: SKIP - DUPLICADO"]
    R8 --> RN
    R7 -- "No" --> R9["Resolver llaves foraneas con OdooSearch:<br/>pais, estado, empresa relacionada, etiqueta<br/>(crear etiqueta si no existe)"]
    R9 --> R10["Armar el diccionario de campos<br/>(campos vacios o ids en 0 se omiten)"]
    R10 --> R11["OdooExec: execute_kw create en res.partner"]
    R11 --> R12{"Respuesta exitosa?"}
    R12 -- "Si" --> R13["LOG: CREATE - OK (id)<br/>total clientes + 1"]
    R12 -- "No" --> R14["Catch: LOG - ERROR con el mensaje<br/>(el bot sigue con la siguiente fila)"]
    R13 --> RN
    R14 --> RN
    RN{"Quedan filas?"}
    RN -- "Si" --> R0
    RN -- "No" --> PF2(["Fin de ProcesarClientes"])
```

---

### 4.4 Diagrama de Flujo: `ProcesarProductos`

```mermaid
flowchart TD
    Q0(["Entrada: archivo, hoja, credenciales, uid"]) --> Q1["Utilice el archivo de Excel + Leer rango<br/>hoja productos con encabezados: dtProductos"]
    Q1 --> Q2{"Existe la columna Name?"}
    Q2 -- "No" --> QX["Lanzar error: el archivo se registra<br/>como ERROR en Main"]
    Q2 -- "Si" --> Q3{"La hoja tiene filas?"}
    Q3 -- "No" --> QF(["Fin: hoja vacia"])
    Q3 -- "Si" --> Q4["OdooSearch: ubicacion de stock<br/>(stock.location, una sola vez)"]
    Q4 --> S0

    S0["Para cada fila"] --> S1["Reiniciar ids y errores"]
    S1 --> S2["PrepararFila: normalizar encabezados, escapar XML<br/>y calcular codigo (Internal Reference o External ID)"]
    S2 --> S3{"Fila completamente vacia?"}
    S3 -- "Si" --> SN
    S3 -- "No" --> S4{"Name vacio?"}
    S4 -- "Si" --> S5["LOG: CREATE - ERROR: fila sin Name"]
    S5 --> SN
    S4 -- "No" --> S6["Buscar duplicado con OdooSearch:<br/>1) barcode  2) codigo interno  3) nombre"]
    S6 --> S7{"Ya existe?"}
    S7 -- "Si" --> S8["LOG: SKIP - DUPLICADO"]
    S8 --> SN
    S7 -- "No" --> S9["ArmarProducto: validar Sales Price, Cost y Weight<br/>y armar parametros"]
    S9 --> S10{"Algun numero invalido?"}
    S10 -- "Si" --> S11["LOG: SKIP - DATO INVALIDO<br/>(no se crea el producto)"]
    S11 --> SN
    S10 -- "No" --> S12["OdooExec: create en product.template"]
    S12 --> S13["OdooSearch: variante en product.product"]
    S13 --> S14{"Tiene codigo o barcode?"}
    S14 -- "Si" --> S15["OdooExec: write de default_code<br/>y barcode en la variante"]
    S14 -- "No" --> S16
    S15 --> S16{"Cantidad a la mano mayor a 0?"}
    S16 -- "Si" --> S17["OdooExec: create en stock.quant<br/>y action_apply_inventory"]
    S16 -- "No" --> S18
    S17 --> S18["LOG: CREATE - OK (id)<br/>total productos + 1"]
    S18 --> SN
    S12 -.->|"error"| S19["Catch: LOG - ERROR con el mensaje"]
    S13 -.->|"error"| S19
    S15 -.->|"error"| S19
    S17 -.->|"error"| S19
    S19 --> SN
    SN{"Quedan filas?"}
    SN -- "Si" --> S0
    SN -- "No" --> QF2(["Fin de ProcesarProductos"])
```

---

### 4.5 Flujos Auxiliares de Comunicación con Odoo

```mermaid
flowchart LR
    L1["OdooLogin<br/>authenticate"] --> POST
    L2["OdooSearch<br/>search por campo"] --> EX["OdooExec<br/>execute_kw"]
    EX --> POST["POST_Xml<br/>Solicitud HTTP POST text/xml"]
    POST --> ODOO[("Odoo en la nube<br/>/xmlrpc/2/common y /xmlrpc/2/object")]
    ODOO --> R{"Respuesta con fault?"}
    R -- "Si" --> ERR["Lanzar excepcion con el mensaje de Odoo"]
    R -- "No" --> OK["Devolver el texto XML al flujo que llamo"]
```

---

### 4.6 Puntos de Verificación del Proceso RPA

| Etapa del Bot | Evidencia / Verificación | Dónde se comprueba |
| :--- | :--- | :--- |
| Escaneo recursivo de carpetas | Cantidad de archivos encontrados | Panel Salida y mensaje `[RPA] ... archivos=N` |
| Login en Odoo | `uid` válido | Panel Salida (mensaje de login correcto) |
| Detección de hojas `clientes`/`productos` | Archivos ignorados anotados como `SKIP \| Sin hojas clientes/productos` | Archivo `log_carga_rpa.txt` |
| Carga de clientes | Líneas `CREATE \| OK (id N)` y registros nuevos en Contactos | LOG + Web Odoo + `SELECT COUNT(*) FROM res_partner WHERE create_date >= CURRENT_DATE AND create_uid = 2` |
| Carga de productos | Líneas `CREATE \| OK (id N)` y registros nuevos con precio e inventario | LOG + Web Odoo + `SELECT COUNT(*) FROM product_template WHERE create_date >= CURRENT_DATE AND create_uid = 2` |
| Duplicados | Segunda ejecución con todo en `SKIP \| DUPLICADO` y totales en 0 | `log_carga_rpa.txt` |
| Datos inválidos | `ERROR: fila sin Name` y `SKIP \| DATO INVALIDO` | `log_carga_rpa.txt` |
| Resumen final | Cuadro con totales cargados e ignorados | Captura de la ejecución en vivo |