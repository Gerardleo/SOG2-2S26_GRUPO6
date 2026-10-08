# Manual 2 - Diagramas de Flujo (Sección Integrante 2)
## QuetzalMart - Flujo del producto en la empresa y flujo del cliente web/tienda

Este documento complementa a `Manual2.md` (Compras y Ventas). Al unificar el PDF final, agregar estas secciones al Manual 2.

---

## 1. Flujo de proceso de la empresa: desde que entra un producto hasta que se vende

### 1.1 Descripción detallada

1. **Recepción del producto:** el transportista llega al muelle de descarga de la sucursal. El encargado de bodega verifica los bultos contra la orden de compra y la nota de entrega del proveedor.
2. **Productos defectuosos o en mal estado:** se revisa empaque, fecha de caducidad y temperatura (refrigerados). Lo que no cumple se separa en la zona de cuarentena, se levanta un acta de discrepancia y se solicita reposición o nota de crédito al proveedor. Lo dañado nunca entra al inventario vendible.
3. **Registro en el ERP:** la mercadería conforme se valida en Odoo (Albarán de entrada), lo que genera el movimiento de inventario y aumenta la existencia.
4. **Almacenamiento por sector:** cada producto se ubica según su tipo: secos/abarrotes, refrigerados (lácteos y carnes), bebidas, higiene y limpieza, panadería. Se respeta la regla FEFO (primero en vencer, primero en salir).
5. **Control de inventario:** conteos cíclicos por sector y comparación contra Odoo. Si hay diferencia se ajusta el inventario con justificación; si la existencia baja del mínimo se dispara una nueva requisición de compra.
6. **Empaque:** para pedidos web se hace picking y packing con materiales de empaque (bolsas, cajas, etiquetas); para piso de venta se rotula y se coloca en góndola.
7. **Control de calidad para ponerlo a la venta:** última inspección (precio, etiqueta, código de barras, fecha). Si pasa, se publica en tienda física y en la tienda web; si no, regresa a cuarentena.
8. **Venta:** el producto se vende en caja (POS) o en la tienda en línea; Odoo descuenta la existencia y genera la factura.

### 1.2 Diagrama

```mermaid
flowchart TD
    subgraph Recepcion["Recepcion"]
        A1["Inicio: llega el transportista con la mercaderia"] --> A2["Descarga en muelle y conteo de bultos"]
        A2 --> A3["Comparar contra orden de compra y nota de entrega"]
        A3 --> A4{"Cantidad y documentos coinciden?"}
        A4 -- "No" --> A5["Levantar acta de discrepancia y contactar al proveedor"]
        A5 --> A3
    end

    subgraph Calidad_Entrada["Revision de estado"]
        A4 -- "Si" --> B1["Inspeccion: empaque, caducidad y temperatura"]
        B1 --> B2{"Producto en buen estado?"}
        B2 -- "No: defectuoso o danado" --> B3["Mover a zona de cuarentena"]
        B3 --> B4["Solicitar reposicion o nota de credito al proveedor"]
        B4 --> B5["Baja o devolucion registrada en Odoo"]
    end

    subgraph Almacen["Almacenamiento e inventario"]
        B2 -- "Si" --> C1["Validar Albaran de entrada en Odoo"]
        C1 --> C2{"Sector de almacenamiento"}
        C2 -- "Abarrotes y secos" --> C3["Estanteria seca"]
        C2 -- "Lacteos y carnes" --> C4["Cuarto frio"]
        C2 -- "Bebidas" --> C5["Zona de bebidas"]
        C2 -- "Higiene y limpieza" --> C6["Zona de higiene y limpieza"]
        C2 -- "Panaderia" --> C7["Zona de panaderia"]
        C3 --> C8["Control de inventario: conteo ciclico vs Odoo"]
        C4 --> C8
        C5 --> C8
        C6 --> C8
        C7 --> C8
        C8 --> C9{"Existencia coincide con el sistema?"}
        C9 -- "No" --> C10["Ajuste de inventario con justificacion"]
        C10 --> C11
        C9 -- "Si" --> C11{"Existencia bajo el minimo?"}
        C11 -- "Si" --> C12["Generar requisicion de compra"]
    end

    subgraph Preparacion["Empaque y calidad para la venta"]
        C11 -- "No" --> D1["Empaque y etiquetado con materiales de la sucursal"]
        D1 --> D2["Control de calidad final: precio, etiqueta, codigo de barras, fecha"]
        D2 --> D3{"Apto para la venta?"}
        D3 -- "No" --> B3
        D3 -- "Si" --> D4["Publicar en gondola y en la tienda web"]
    end

    subgraph Venta["Venta"]
        D4 --> E1["Cliente compra en caja o en la tienda en linea"]
        E1 --> E2["Odoo descuenta existencia y emite la factura"]
        E2 --> E3["Fin: producto vendido"]
    end
```

---

## 2. Flujo del cliente que compra por la web y visita la tienda

### 2.1 Descripción detallada

1. **Ingreso al sitio:** el cliente llega por una campaña, buscador o enlace directo; se registran sus eventos en Google Analytics (`view_item`, `add_to_cart`, `begin_checkout`, `purchase`).
2. **Exploración del catálogo:** navega por categorías, ve imágenes, descripción y precio de cada producto.
3. **Carrito:** agrega o elimina productos; el sistema calcula IVA y costo de envío (gratis sobre el monto mínimo). Si abandona el carrito queda registrado y alimenta la audiencia de "abandono de carrito".
4. **Identificación:** inicia sesión o se registra; su ficha de cliente queda en el ERP/CRM.
5. **Pago:** elige el método (pasarela de pago o transferencia). Si el pago falla, puede reintentar o cambiar de método.
6. **Confirmación y facturación:** Odoo confirma el pedido, genera y publica la factura y envía el correo de compra con la factura en PDF. Poco después el CRM envía el correo de campaña de marketing.
7. **Entrega o recojo:** el cliente elige envío a domicilio o recoger en sucursal. La bodega prepara el pedido (picking y packing).
8. **Visita a la tienda:** al recoger o visitar la sucursal presenta su número de pedido o factura; el personal valida la identidad, entrega el pedido y puede ofrecer compras adicionales en caja.
9. **Cierre:** el cliente firma de conformidad, Odoo valida la salida del inventario y se invita a registrar una reseña o volver a comprar.

### 2.2 Diagrama

```mermaid
flowchart TD
    subgraph Cliente["Cliente"]
        A1["Inicio: llega al sitio por campana, buscador o enlace"] --> A2["Explora el catalogo por categorias"]
        A2 --> A3["Ve producto: imagen, descripcion y precio"]
        A3 --> A4["Agrega productos al carrito"]
    end

    subgraph Analitica["Google Analytics 4"]
        A3 -.-> G1["Evento view_item"]
        A4 -.-> G2["Evento add_to_cart"]
        A8 -.-> G3["Evento begin_checkout"]
        B5 -.-> G4["Evento purchase"]
    end

    subgraph Tienda["Tienda web en Odoo"]
        A4 --> T1["Carrito calcula IVA y costo de envio"]
        T1 --> T2{"Cliente continua?"}
        T2 -- "No: abandona" --> T3["Abandono de carrito registrado: audiencia para remarketing"]
        T2 -- "Si" --> A8["Iniciar compra"]
        A8 --> T4{"Tiene cuenta?"}
        T4 -- "No" --> T5["Registro de usuario y ficha en CRM"]
        T4 -- "Si" --> T6["Inicio de sesion"]
        T5 --> T7["Datos de entrega: domicilio o recoger en sucursal"]
        T6 --> T7
        T7 --> T8["Seleccion de metodo de pago"]
        T8 --> T9{"Pago aprobado?"}
        T9 -- "No" --> T10["Reintentar o cambiar metodo de pago"]
        T10 --> T8
    end

    subgraph Backoffice["ERP y CRM"]
        T9 -- "Si" --> B1["Confirmar pedido de venta en Odoo"]
        B1 --> B2["Generar y publicar factura"]
        B2 --> B3["Enviar correo de compra con factura PDF"]
        B3 --> B4["CRM envia correo de campana de marketing"]
        B3 --> B5["Compra completada"]
    end

    subgraph Bodega["Bodega y sucursal"]
        B1 --> D1["Picking y packing del pedido"]
        D1 --> D2{"Modalidad de entrega"}
        D2 -- "Domicilio" --> D3["Despacho con transporte de la empresa"]
        D2 -- "Recoger en tienda" --> D4["Pedido listo en mostrador de la sucursal"]
        D4 --> D5["Cliente visita la tienda y presenta numero de pedido o factura"]
        D5 --> D6["Personal valida identidad y entrega el pedido"]
        D6 --> D7["Oferta de compras adicionales en caja"]
        D3 --> E1
        D7 --> E1["Cliente firma de conformidad"]
    end

    subgraph Cierre["Cierre"]
        E1 --> E2["Validar salida de inventario en Odoo"]
        E2 --> E3["Fin: cliente satisfecho, posible recompra"]
    end
```
