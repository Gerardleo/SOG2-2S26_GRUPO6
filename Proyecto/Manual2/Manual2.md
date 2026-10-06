# Manual 2 - Diagramas de Flujo de Procesos de Negocio
## QuetzalMart ERP - Sección Compras y Ventas (Integrante 1)

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
