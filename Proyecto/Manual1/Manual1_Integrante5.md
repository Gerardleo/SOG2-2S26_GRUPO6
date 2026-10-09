Manual 1 — Recursos humanos y gestor documental

Alcance: configuración de recursos humanos, carga de empleados y organización de documentos.
Esta sección describe el trabajo realizado desde el navegador sobre la instalación de Odoo del proyecto. Comprende la carga de 35 empleados, su distribución en cinco departamentos y seis cargos, y la organización de 15 documentos: cinco facturas de proveedores, cinco contratos de outsourcing y cinco contratos de empleados.
Los registros de empleados y los contratos preparados para esta práctica contienen datos ficticios con fines académicos.
1. Configuración de los módulos
1.1. Acceso al sistema
La configuración se realizó desde el navegador, utilizando la cuenta Administrator de la base de datos de QuetzalMart. Se trabajó con el módulo Empleados y el gestor documental Documentos, correspondiente al módulo DMS de OCA, disponible en la instalación del proyecto.
1.2. Configuración de recursos humanos
1. Ingresar a Odoo con la cuenta autorizada.
2. Acceder a Aplicaciones y activar el módulo Empleados.
3. Abrir el módulo Empleados.
4. Ingresar a Configuración → Departamentos y crear o comprobar los departamentos de la empresa.
5. Ingresar a Configuración → Puestos de trabajo y crear los seis cargos que utilizarán los registros importados.
La distribución utilizada es la siguiente:
Departamento	Cargo	Empleados cargados
Administración	Gerente administrativo	3
Ventas y Atención al Cliente	Cajero	10
Ventas y Atención al Cliente	Asesor de ventas	8
Compras	Encargado de compras	4
Inventario y Logística	Auxiliar de bodega	7
Recursos Humanos	Analista de Recursos Humanos	3
Total	6 cargos en 5 departamentos	35


En la base utilizada, el departamento de Administración aparece con el nombre Administration. El archivo de importación utiliza ese nombre para asociar los empleados con el departamento existente.
Captura 1: lista de los cinco departamentos configurados.
Captura 2: lista de los seis puestos de trabajo.

1.3. Almacenamiento del gestor documental
1. Abrir Documentos.
2. Ingresar a la configuración de almacenamientos.
3. Crear el almacenamiento Documentos QuetzalMart.
4. Seleccionar Base de datos como tipo de guardado.
5. Asociarlo a la empresa QuetzalMart y guardar.
Este almacenamiento permite conservar los archivos dentro de la base de datos utilizada por el sistema.
Captura 3: configuración del almacenamiento, mostrando su nombre, tipo y empresa.

1.4. Permisos y estructura de carpetas
Se configuró el grupo Administración documental QuetzalMart, incluyendo al usuario Administrator. Se habilitaron los permisos de creación y escritura; el permiso de eliminación quedó desactivado.
Para establecer la estructura:
1. Acceder a Documentos → Carpetas.
2. Crear la carpeta QuetzalMart y marcarla como carpeta raíz.
3. Seleccionar el almacenamiento Documentos QuetzalMart.
4. En la pestaña de grupos, agregar Administración documental QuetzalMart y guardar.
5. Crear dentro de la raíz las carpetas Facturas de proveedores, Contratos de outsourcing y Contratos de empleados.
6. En cada subcarpeta, seleccionar QuetzalMart como carpeta padre, mantener desmarcada la opción de carpeta raíz y habilitar la herencia de grupos.
7. Guardar cada registro.
En esta interfaz, el campo que identifica la carpeta padre puede aparecer como Categoría padre. Se utiliza para establecer la jerarquía de carpetas; la categoría de clasificación del archivo se asigna por separado.
Durante la configuración inicial se presentó una restricción para crear carpetas. Se resolvió asignando el grupo documental con permisos de creación y escritura a la carpeta raíz.
Captura 4: grupo documental y permisos.
Captura 5: carpeta raíz con sus tres subcarpetas.

1.5. Categorías y etiquetas
Desde Documentos → Configuración → Categorías se crearon las tres categorías. Después, desde Configuración → Etiquetas, se crearon las etiquetas correspondientes y se asociaron a su categoría.
Carpeta	Categoría del archivo	Etiqueta	Cantidad
Facturas de proveedores	Facturas de proveedores	Compra	5
Contratos de outsourcing	Contratos de outsourcing	Servicio externo	5
Contratos de empleados	Contratos de empleados	RRHH	5
Total			15


Captura 6: categorías y etiquetas configuradas.

2. Funcionalidad de los módulos
2.1. Recursos humanos
El módulo Empleados permite consultar y administrar los registros de personal. Cada ficha incluye el nombre, correo laboral, departamento y puesto de trabajo. La distribución por departamentos y cargos facilita identificar a qué área pertenece cada empleado.
La importación permite cargar los registros desde una hoja de cálculo. Los identificadores externos incluidos en el archivo ayudan a identificar los registros cuando se realizan actualizaciones mediante importación.
2.2. Gestor documental
El módulo Documentos centraliza los archivos del proyecto. Las carpetas organizan los documentos según su uso, las categorías establecen su clasificación y las etiquetas permiten identificarlos y filtrarlos.
Los grupos de acceso controlan las acciones disponibles sobre las carpetas y sus archivos. En la configuración de QuetzalMart se habilitó la creación y modificación para el grupo responsable de la administración documental.
3. Carga de datos y documentos
3.1. Importación masiva de los 35 empleados
Se utilizó el archivo empleados_quetzalmart_35.xlsx, preparado con las siguientes columnas:
Columna	Información
External ID	Identificador externo único, desde quetzalmart_emp_001 hasta quetzalmart_emp_035
Name	Nombre del empleado
Work Email	Correo de ejemplo para la práctica
Department	Nombre del departamento existente
Job Position	Nombre del puesto de trabajo existente
Notes	Indicación de que el registro es ficticio y académico


Para realizar la importación se siguió este procedimiento:
1. Abrir el listado de Empleados.
2. Seleccionar la opción Importar registros disponible en el menú del listado.
3. Cargar el archivo Excel.
4. Revisar que cada columna esté asociada al campo correspondiente de Odoo.
5. Comprobar que los departamentos y puestos coincidan con los registros creados previamente.
6. Ejecutar Importar y revisar los empleados creados.
La carga realizada contiene 35 empleados del proyecto. Si el listado incluye también al empleado Administrator creado previamente, puede mostrar 36 registros; ese registro adicional no forma parte de los 35 empleados importados.
Captura 7: archivo y correspondencia de columnas en la pantalla de importación.
Captura 8: resultado de la importación y listado con el conteo de empleados.

3.2. Generación de las cinco facturas de proveedores
Se utilizaron las compras existentes P00100, P00099, P00098, P00097 y P00096 para obtener las cinco facturas destinadas al gestor documental.
Para cada compra:
1. Abrir la orden desde Compras.
2. Acceder a su recepción y comprobar las cantidades recibidas.
3. Validar la recepción de los productos.
4. Regresar a la orden y seleccionar Crear factura.
5. Revisar el proveedor, los productos, cantidades e importes.
6. Completar la fecha de factura y la referencia de la orden; para P00100 se utilizó SIM-P00100.
7. Confirmar la factura después de revisar sus datos.
8. Usar Imprimir → Facturas sin pago y guardar el PDF.
La factura correspondiente a P00100 quedó registrada con el número FACTU/2026/10/0001, fecha 08/10/2026 y total Q165.20. Los PDF se identificaron con nombres como Factura_proveedor_P00100.pdf.
Los PDF obtenidos se utilizaron como documentos de respaldo en la carpeta Facturas de proveedores.
Captura 9: factura de proveedor confirmada y opción de impresión.

3.3. Preparación de los contratos
Se prepararon diez contratos en PDF para la práctica:
- Cinco contratos de outsourcing: limpieza, seguridad, soporte de tecnología, transporte y mantenimiento.
- Cinco contratos de empleados, utilizando datos de personal incluido en la carga de recursos humanos.
Los documentos se identificaron como ejemplos académicos con datos ficticios. Los contratos se cargaron individualmente en formato PDF dentro de sus carpetas correspondientes.
3.4. Carga y clasificación de los 15 archivos
1. Abrir la carpeta correspondiente en Documentos → Carpetas.
2. Acceder a la pestaña Archivos y seleccionar Agregar una línea.
3. Escribir el nombre del documento.
4. En Contenido, utilizar Sube tu archivo para seleccionar el PDF.
5. Comprobar la carpeta y el almacenamiento asignados.
6. Seleccionar la categoría y etiqueta indicadas en la tabla del apartado 1.5.
7. Utilizar Guardar y crear nuevo para continuar cargando archivos, o Guardar y cerrar al terminar.
8. Guardar también el registro de la carpeta para confirmar los cambios de su tabla de archivos.
9. Revisar la lista de archivos cargados en cada carpeta.
Guardar la carpeta es necesario cuando las filas agregadas todavía están pendientes de confirmación. Antes de guardar, la tabla puede mostrar archivos que aún no se reflejan en el contador del registro.
Captura 10: cinco facturas con carpeta, categoría y etiqueta.
Captura 11: cinco contratos de outsourcing clasificados.
Captura 12: cinco contratos de empleados clasificados.