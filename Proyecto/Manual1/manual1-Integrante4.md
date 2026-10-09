## 4. Cuarta Sección: Automatización del Proceso de Carga con RPA (UiPath)

### 4.1 Problema de Negocio a Resolver

El departamento de ventas de QuetzalMart organizó históricamente su información en una jerarquía de carpetas poco práctica (`clientes`, `proveedores`, `reclamos`, `registro`, `productos`), con nombres de archivo que contienen guiones y descripciones adicionales. Dentro de cada archivo Excel existen **varias hojas con información adicional**, pero únicamente las hojas llamadas **`clientes`** y **`productos`** son relevantes para la carga al ERP.

| Problema detectado | Solución implementada con RPA |
| :--- | :--- |
| Dispersión de archivos en una jerarquía de carpetas profunda | Escaneo recursivo automático de toda la estructura (`AllDirectories`) |
| Archivos con hojas irrelevantes (reclamos, registros, proveedores) | Detección de las hojas `clientes` y `productos` antes de leer; el resto se omite y se registra |
| Horas de digitación manual y errores humanos de transcripción | Lectura programática de cada hoja a un DataTable y envío a la API del ERP |
| Riesgo de duplicar registros si el proceso se repite | Verificación previa de existencia antes de crear cada registro |
| Datos sucios (filas sin nombre, precios no numéricos, encabezados con `*`) | Validaciones por fila: se rechazan o se omiten y quedan en el LOG con el motivo |
| Falta de trazabilidad de lo que se cargó | Archivo LOG por fila (creado, omitido, error) y resumen final en pantalla |

---

### 4.2 Preparación del Entorno RPA

**Herramienta:** UiPath Studio Community Edition (licencia gratuita).

1. Descarga e instalación de UiPath Studio. En el instalador solo se seleccionó el componente **Studio**.

   ![](./imagenes/RPA/instalacion_uipath.png)
   _Instalación de UiPath Studio Community Edition._

2. Inicio de sesión en UiPath Cloud (`https://cloud.uipath.com`) con la cuenta Community.

3. Creación del proyecto **`QuetzalMart_RPA`** (tipo *Proceso*, lenguaje de expresiones VB.NET).

   ![](./imagenes/RPA/crear_proyecto.png)
   _Creación del proyecto de automatización en UiPath Studio._

4. Instalación de los paquetes necesarios desde **Administrar paquetes**:

   | Paquete | Función en el bot |
   | :--- | :--- |
   | `UiPath.Excel.Activities` | **Utilice el archivo de Excel** y **Leer rango** para leer las hojas `clientes` y `productos` |
   | `UiPath.System.Activities` | `Para cada`, `Asignar`, `Try Catch`, `Invocar flujo de trabajo`, `Invocar código` |
   | `UiPath.Web.Activities` | **Solicitud HTTP** (`NetHttpRequest`) para consumir la API XML-RPC de Odoo |

   ![](./imagenes/RPA/paquetes.png)
   _Gestor de paquetes con las actividades instaladas._

---

### 4.3 Arquitectura del Bot

El proyecto se organiza en flujos de trabajo modulares y reutilizables:

| Flujo de trabajo | Responsabilidad |
| :--- | :--- |
| `Main.xaml` | Orquestador: escanea carpetas, detecta hojas, hace login, coordina los sub-flujos y escribe el LOG |
| `OdooLogin.xaml` | Autentica contra Odoo (`authenticate`) y devuelve el `uid` |
| `POST_Xml.xaml` | Envía el XML-RPC con una **Solicitud HTTP** (`POST`, `text/xml`) y devuelve el texto de la respuesta |
| `OdooExec.xaml` | Ejecuta cualquier método de Odoo (`execute_kw`) y lanza una excepción si la respuesta contiene un `fault` |
| `OdooSearch.xaml` | Busca un registro por un campo (`search`); se usa para duplicados y llaves foráneas |
| `ProcesarClientes.xaml` | Lee la hoja `clientes`, arma el payload y crea los registros en `res.partner` |
| `ProcesarProductos.xaml` | Lee la hoja `productos`, valida números, crea plantilla, variante e inventario |

**Parámetros del proyecto** (argumentos de `Main`, para no dejar credenciales fijas dentro de los flujos):

| Parámetro | Valor |
| :--- | :--- |
| `in_url` | `http://<IP_DEL_SERVIDOR>:8069` |
| `in_db` | *(nombre de la base de datos)* |
| `in_usuario` | *(usuario de Odoo)* |
| `in_password` | *(contraseña, no se publica)* |
| `in_ruta_entrada` | `System.IO.Path.GetFullPath("..\Pruebas")`.  |
| `in_ruta_log` | `System.IO.Path.GetFullPath("..\Logs")` |

---

### 4.4 Capturas Paso a Paso del Diseño del Workflow

#### Paso 1: Comunicación con Odoo (flujos auxiliares)

Odoo expone la API XML-RPC en `/xmlrpc/2/common` (login) y `/xmlrpc/2/object` (operaciones). Se construyeron cuatro flujos reutilizables:

**`POST_Xml.xaml`:** una **Solicitud HTTP** con método `POST`, tipo de cuerpo *Texto*, tipo de contenido `text/xml` y el XML recibido como argumento `in_payload`. La respuesta se guarda en una variable `HttpResponseSummary` y su `TextContent` se devuelve en `out_texto`.

![](./imagenes/RPA/rpa_http_request.png)
_Configuración de la Solicitud HTTP contra el endpoint XML-RPC de Odoo._

**`OdooLogin.xaml`:** arma el XML del método `authenticate` y devuelve el `uid`. Si la respuesta contiene un `fault` o no trae un entero, lanza una excepción con un mensaje claro.

![](./imagenes/RPA/rpa_login.png)
_Login exitoso: el bot obtiene el uid del usuario._

**`OdooExec.xaml`:** recibe el modelo (`res.partner`, `product.template`...), el método (`create`, `write`...) y los parámetros en XML. Construye el `execute_kw`, lo envía mediante `POST_Xml` y, si la respuesta trae un `fault`, lanza la excepción con el mensaje de Odoo. Un caso especial es `action_apply_inventory`, que devuelve `None` y provoca el mensaje `cannot marshal None`; ese caso se tolera porque la operación sí se aplica.

**`OdooSearch.xaml`:** arma un dominio `[campo = valor]`, ejecuta `search` mediante `OdooExec` y devuelve el id del primer resultado, o `0` si no existe.

> Los valores de texto se escapan una sola vez (`&`, `<`, `>`) en la preparación de cada fila, para que nombres como *Snacks & Bebidas* no rompan el XML.

#### Paso 2: Escaneo recursivo y detección de hojas

`Main.xaml` obtiene todos los archivos Excel de la carpeta de entrada y de sus subcarpetas, descartando los temporales de Excel (`~$`):

```vb
System.IO.Directory.GetFiles(in_ruta_entrada, "*.xls*", System.IO.SearchOption.AllDirectories)
```

![](./imagenes/RPA/rpa_escaneo_carpetas.png)
_Actividad de escaneo recursivo de la jerarquía de carpetas._

Para cada archivo, un **Invocar código** (`ListarHojas`) abre el `.xlsx` como archivo comprimido, lee `xl/workbook.xml` y devuelve el nombre exacto de las hojas `clientes` y `productos` sin distinguir mayúsculas. Si el archivo no tiene ninguna de las dos, se registra como `SKIP | Sin hojas clientes/productos` y el bot continúa con el siguiente.

![](./imagenes/RPA/rpa_get_sheets.png)
_Detección de las hojas dentro de cada archivo Excel._

#### Paso 3: Lectura de la hoja

Cada flujo (`ProcesarClientes`, `ProcesarProductos`) abre el archivo con **Utilice el archivo de Excel** (con *Crear si no existe* y *Guardar cambios* desactivados, porque solo se lee) y usa **Leer rango** sobre la hoja detectada, con la primera fila como encabezados. El resultado es un `DataTable`. Después se valida que exista la columna `Name` y que la hoja no esté vacía.

![](./imagenes/RPA/rpa_read_range.png)
_Lectura de la hoja a un DataTable con encabezados._

#### Paso 4: Preparación de cada fila

Un **Invocar código** (`PrepararFila`) convierte cada fila en un diccionario `columna → valor` con tres ajustes importantes:

- **Normaliza los encabezados:** quita el `*` y los espacios (`Name*` pasa a `Name`), porque las plantillas de importación de Odoo marcan así los campos obligatorios.
- **Escapa los caracteres XML** (`&`, `<`, `>`).
- **Rellena con vacío** las columnas que falten, para evitar errores por claves inexistentes.

Además, las filas completamente vacías se ignoran sin registrar error.

#### Paso 5: Mapeo de columnas a campos de Odoo

**Hoja `clientes` → modelo `res.partner`:**

| Columna del Excel | Campo en Odoo |
| :--- | :--- |
| `Name` | `name` |
| `Company Type` | `company_type` (`company` o `person`) |
| `Related Company` | `parent_id` (búsqueda por nombre) |
| `Email`, `Phone` | `email`, `phone` |
| `Street`, `Street2` | `street`, `street2` |
| `City`, `Zip` | `city`, `zip` |
| `State` | `state_id` (búsqueda por nombre; si no existe se omite) |
| `Country` | `country_id` (búsqueda por nombre; si no existe se omite) |
| `Tax ID` | `vat` |
| `Website` | `website` |
| `Tags` | `category_id` (se busca la etiqueta y, si no existe, se crea) |
| `Reference` | `ref` |
| `Notes` | `comment` |

**Hoja `productos` → modelo `product.template` / `product.product`:**

| Columna del Excel | Campo en Odoo |
| :--- | :--- |
| `Name` | `name` |
| `Product Type` | `detailed_type` (`product` almacenable, `consu` consumible, `service`) |
| `Internal Reference` / `External ID` | `default_code` (código interno de la variante) |
| `Barcode` | `barcode` (variante) |
| `Sales Price` | `list_price` |
| `Cost` | `standard_price` |
| `Weight` | `weight` |
| `Sales Description` | `description_sale` |
| `Product Values` | `description` |
| `Está publicado` | `is_published` (acepta `TRUE`, `1`, `Sí`) |
| `Cantidad a la mano` | `stock.quant` (inventario inicial) |

#### Paso 6: Verificación de duplicados antes de crear

Para que el bot sea re-ejecutable sin duplicar, cada fila se consulta antes de crearse mediante `OdooSearch` (método `search` de Odoo):

- **Clientes:** se busca por `name` en `res.partner`.
- **Productos:** se busca por `barcode`, luego por código interno (`default_code`) y, por último, por `name`.

Si el registro ya existe, la fila se registra como `SKIP | DUPLICADO` y no se crea de nuevo.

![](./imagenes/RPA/rpa_validacion_duplicados.png)
_Actividades de validación de duplicados._

#### Paso 7: Creación en Odoo mediante XML-RPC

Para clientes, el bot resuelve primero las llaves foráneas (país, estado, empresa relacionada, etiqueta) y arma el diccionario de campos con un **Invocar código**; luego `OdooExec` ejecuta `create` sobre `res.partner`.

Para productos se sigue un proceso en varios pasos:

1. `ArmarProducto` (Invocar código) valida los campos numéricos y arma los parámetros.
2. `create` sobre `product.template`.
3. `search` de la variante creada automáticamente (`product.product`).
4. `write` de `default_code` y `barcode` sobre la variante.
5. Si hay `Cantidad a la mano`, se crea un `stock.quant` en la ubicación de stock y se aplica con `action_apply_inventory`.

Ejemplo del tipo de petición que envía el bot (los datos sensibles se omiten):

```
POST http://<IP_DEL_SERVIDOR>:8069/xmlrpc/2/object
Content-Type: text/xml
```

```xml
<methodCall>
  <methodName>execute_kw</methodName>
  <params>
    <param><value><string>[BASE_DE_DATOS]</string></value></param>
    <param><value><int>2</int></value></param>             <!-- uid autenticado -->
    <param><value><string>********</string></value></param>
    <param><value><string>res.partner</string></value></param>
    <param><value><string>create</string></value></param>
    <param><value><array><data>
      <value><struct>
        <member><name>name</name><value><string>Carlos Roberto Méndez</string></value></member>
        <member><name>email</name><value><string>carlos.mendez@ejemplo.com</string></value></member>
      </struct></value>
    </data></array></value></param>
    <param><value><struct/></value></param>
  </params>
</methodCall>
```

*Nota: el login se realiza una sola vez al iniciar el bot y el `uid` se reutiliza en todo el proceso.*

#### Paso 8: Manejo de errores y datos inválidos

Cada fila se procesa dentro de un bloque `Try Catch`. Un fallo no detiene el bot: se registra en el LOG y continúa con la siguiente fila. Casos contemplados:

| Caso | Comportamiento | Registro en el LOG |
| :--- | :--- | :--- |
| Fila sin `Name` | No se crea | `CREATE \| ERROR: fila sin Name` |
| Registro ya existente | No se crea | `SKIP \| DUPLICADO` |
| `Sales Price`, `Cost` o `Weight` no numérico | No se crea el producto | `SKIP \| DATO INVALIDO: <campo y valor>` |
| País, estado o relación inexistente en Odoo | Se crea el registro sin ese campo | `CREATE \| OK` |
| Archivo sin hojas `clientes`/`productos` | Se omite el archivo | `SKIP \| Sin hojas clientes/productos` |
| Error de Odoo o de red en una fila | La fila se omite y continúa | `CREATE \| ERROR: <mensaje>` |
| Error en un archivo completo | Se registra y sigue con el siguiente archivo | `ERROR \| <mensaje>` |

![](./imagenes/RPA/try_catch.png)
_Bloque Try Catch con manejo de excepciones por fila._

#### Paso 9: Archivo de trazabilidad (LOG)

Al finalizar (incluso si hubo errores), `Main` escribe el archivo `log_carga_rpa.txt` en la carpeta de logs, con campos separados por `|`:

| timestamp | archivo | hoja | fila | registro | accion | resultado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-10-08 16:59:49 | clientes-archivo de ejemplo.xlsx | clientes | fila 2 | Distribuidora La Esperanza | CREATE | OK (id 141) |
| 2026-10-08 16:59:59 | clientes-archivo de ejemplo.xlsx | clientes | fila 10 | Cliente Prueba Uno | SKIP | DUPLICADO |
| 2026-10-08 17:00:00 | clientes-archivo de ejemplo.xlsx | clientes | fila 12 | (sin nombre) | CREATE | ERROR: fila sin Name |

![](./imagenes/RPA/log_evidencia.png)
_Archivo LOG de trazabilidad generado por el bot._

---

### 4.5 Ejecución en Vivo del RPA

1. Abrir `QuetzalMart_RPA` en UiPath Studio y cambiar el argumento `in_ruta_entrada` a la carpeta entregada el día de la calificación.
2. Cerrar todos los archivos Excel de la carpeta.
3. Presionar **Ejecutar** (F5).
4. Observar el progreso en el panel **Salida** (login, archivos encontrados y cada acción realizada).
5. Al finalizar, el bot muestra un cuadro de resumen con los clientes y productos cargados, los archivos ignorados y la ruta del LOG.

![](./imagenes/RPA/ejecucion.png)
_Ejecución del bot en UiPath Studio._

![](./imagenes/RPA/message_box_resumen.png)
_Ventana de resumen final de la carga._

#### Resultados de las pruebas realizadas

| Prueba | Resultado |
| :--- | :--- |
| Archivo de clientes (12 filas) | 9 creados (ids 141 a 149), 2 `SKIP` por duplicado, 1 `ERROR` por fila sin nombre |
| Segunda ejecución con los mismos archivos | 0 creados: todas las filas existentes salen como `SKIP \| DUPLICADO` |
| Nombres con `&` y comillas | Creados correctamente y detectados como duplicados en la segunda corrida |
| Archivo de productos | *(completar con el resultado final de tu última corrida)* |
| Archivo sin hojas relevantes | `SKIP \| Sin hojas clientes/productos` |

---

### 4.6 Verificación de la Información Cargada (Web y Base de Datos)

El enunciado exige que la información cargada se visualice **tanto en el sitio web como a nivel de base de datos**.

#### 4.6.1 Verificación a nivel de sitio web (Odoo)

- **Aplicación Contactos:** muestra los clientes cargados con correos, teléfonos, direcciones, país y etiquetas.

  ![](./imagenes/RPA/verificacion_web_contactos.png)
  _Clientes cargados por el bot visibles en Contactos._

- **Aplicación Inventario / Productos:** muestra los productos con precio, costo, código de barras y cantidad a la mano.

  ![](./imagenes/RPA/verificacion_web_productos.png)
  _Productos cargados por el bot visibles en el catálogo._

#### 4.6.2 Verificación a nivel de base de datos (PostgreSQL)

> Estas consultas deben probarse antes de la calificación. Se filtra por fecha de creación y por el usuario con el que se autentica el bot (`create_uid`).

```sql
-- Cantidad de clientes creados hoy por el bot
SELECT COUNT(*) AS clientes_rpa
FROM res_partner
WHERE create_date >= CURRENT_DATE
  AND create_uid = 2;

-- Últimos 10 clientes cargados
SELECT id, name, email, phone, vat, ref, create_date
FROM res_partner
WHERE create_uid = 2
ORDER BY create_date DESC
LIMIT 10;

-- Cantidad de productos creados hoy por el bot
SELECT COUNT(*) AS productos_rpa
FROM product_template
WHERE create_date >= CURRENT_DATE
  AND create_uid = 2;

-- Últimos productos cargados, con su código interno y código de barras
SELECT pp.default_code, pp.barcode, pt.name, pt.list_price, pt.standard_price, pt.create_date
FROM product_template pt
JOIN product_product pp ON pp.product_tmpl_id = pt.id
WHERE pt.create_uid = 2
ORDER BY pt.create_date DESC
LIMIT 10;
```

![](./imagenes/RPA/verificacion_sql.png)
_Consultas SQL de verificación de los registros insertados por el bot en PostgreSQL._

---

### 4.7 Ventajas de Implementar el RPA en QuetzalMart

1. **Reducción drástica del tiempo de proceso:** la consolidación manual de la jerarquía de carpetas y la digitación de cientos de filas pasa de varias horas de trabajo humano a una ejecución de pocos minutos, liberando al personal para actividades de mayor valor estratégico.

2. **Reducción significativa de errores de digitación:** al no existir transcripción manual, disminuyen los errores de transposición de dígitos, campos incompletos o precios cargados incorrectamente, y los datos inválidos se detectan y registran en lugar de cargarse.

3. **Selección automática de la información relevante:** el bot solo extrae las hojas `clientes` y `productos`, ignorando hojas como reclamos o registros, sin que una persona revise archivo por archivo.

4. **Proceso re-ejecutable sin duplicados:** la verificación previa de existencia permite volver a correr el bot (por ejemplo, durante la calificación) sin contaminar la base de datos.

5. **Tolerancia a datos imperfectos:** normaliza encabezados (`Name*`), ignora filas vacías, omite países o etiquetas inexistentes sin perder el registro y continúa ante errores en filas o archivos individuales.

6. **Trazabilidad y auditoría completa:** el LOG registra fecha, archivo, hoja, fila, registro y resultado de cada operación, lo que facilita el control de calidad y la resolución de incidencias.

7. **Escalabilidad:** ante la expansión de QuetzalMart a nuevas sucursales, basta con depositar los nuevos archivos en la carpeta de entrada para que el bot los procese sin modificar la automatización.

8. **Centralización de la información:** los datos dispersos en carpetas locales se consolidan en el ERP en la nube, disponibles de inmediato para el sitio web, los reportes y la toma de decisiones.