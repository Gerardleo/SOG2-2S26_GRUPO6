"""
Generador de Datasets para QuetzalMart - Fase 2
Genera archivos CSV listos para importación y uso en scripts de carga masiva:
1. 60 Materiales e insumos operativos para las sucursales (Guatemala, México, El Salvador)
2. Clientes (35 clientes) con campos requeridos por el enunciado
3. Proveedores (20 proveedores)
4. Productos de Venta (40 productos de supermercado)
"""

import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------------------------------
# 1. GENERACIÓN DE 60 MATERIALES PARA LAS SUCURSALES
# -------------------------------------------------------------------------
materiales_data = [
    # Empaque y Embalaje
    ("MAT-001", "Bolsas biodegradables medianas 1000u", "consu", "Materiales / Empaque", 45.00, 0.00, "Bolsas para despacho en caja"),
    ("MAT-002", "Bolsas biodegradables grandes 1000u", "consu", "Materiales / Empaque", 58.00, 0.00, "Bolsas grandes reforzadas"),
    ("MAT-003", "Caja de cartón corrugado estándar 50u", "consu", "Materiales / Empaque", 65.00, 0.00, "Cajas para pedidos a domicilio y envíos"),
    ("MAT-004", "Cinta adhesiva transparente de embalaje 48mm", "consu", "Materiales / Empaque", 3.50, 0.00, "Cinta de empaque para bodega"),
    ("MAT-005", "Cinta de embalaje con logotipo QuetzalMart", "consu", "Materiales / Empaque", 5.20, 0.00, "Cinta selladora de seguridad"),
    ("MAT-006", "Plástico film stretch para paletizado 500m", "consu", "Materiales / Empaque", 28.00, 0.00, "Rollo de film transparente"),
    ("MAT-007", "Papel kraft para envoltorio 100m", "consu", "Materiales / Empaque", 19.50, 0.00, "Envoltorio para frutas y panadería"),
    ("MAT-008", "Malla plástica para frutas y verduras 500m", "consu", "Materiales / Empaque", 22.00, 0.00, "Malla tubular transpirable"),

    # Punto de Venta (POS) y Oficina
    ("MAT-009", "Rollos de papel térmico 80x70mm caja 50u", "consu", "Materiales / POS", 35.00, 0.00, "Papel para impresoras de tickets"),
    ("MAT-010", "Rollos de papel térmico 57x40mm caja 50u", "consu", "Materiales / POS", 24.00, 0.00, "Papel para terminales POS POSNET"),
    ("MAT-011", "Etiquetas adhesivas térmicas 50x30mm 1000u", "consu", "Materiales / POS", 8.50, 0.00, "Etiquetas para balanzas de peso"),
    ("MAT-012", "Etiquetas adhesivas de código de barras 30x20mm", "consu", "Materiales / POS", 6.00, 0.00, "Etiquetas para marcación de góndola"),
    ("MAT-013", "Resma de papel bond carta 500 hojas", "consu", "Materiales / Oficina", 4.20, 0.00, "Papel para impresión administrativa"),
    ("MAT-014", "Tóner para impresora láser administrativa", "consu", "Materiales / Oficina", 68.00, 0.00, "Cartucho de tóner de alta duración"),
    ("MAT-015", "Grapadora metálica de uso pesado", "consu", "Materiales / Oficina", 12.00, 0.00, "Grapadora de caja y recepción"),
    ("MAT-016", "Grapas estándar 26/6 caja 5000u", "consu", "Materiales / Oficina", 2.10, 0.00, "Insumo de oficina"),
    ("MAT-017", "Marcadores permanentes punta gruesa caja 12u", "consu", "Materiales / Oficina", 9.80, 0.00, "Rotulación de cajas de almacén"),
    ("MAT-018", "Cutter retráctil metálico para almacén", "consu", "Materiales / Oficina", 3.00, 0.00, "Navaja de seguridad para apertura"),
    ("MAT-019", "Cuchillas de repuesto para cutter caja 10u", "consu", "Materiales / Oficina", 2.50, 0.00, "Repuestos cortantes"),
    ("MAT-020", "Tableros acrílicos para inventario con clip", "consu", "Materiales / Oficina", 4.50, 0.00, "Portapapeles para auditores"),

    # Limpieza, Desinfección y Sanidad
    ("MAT-021", "Desinfectante multiusos galón 3.78L", "consu", "Materiales / Limpieza", 11.50, 0.00, "Químico de limpieza de pisos"),
    ("MAT-022", "Cloro blanqueador industrial galón 3.78L", "consu", "Materiales / Limpieza", 8.00, 0.00, "Sanitizante de áreas comunes"),
    ("MAT-023", "Jabón líquido antibacterial para manos galón", "consu", "Materiales / Limpieza", 14.00, 0.00, "Repuesto para baños públicos"),
    ("MAT-024", "Gel antibacterial hidroalcohólico al 70% galón", "consu", "Materiales / Limpieza", 16.50, 0.00, "Dispensadores de entrada de tienda"),
    ("MAT-025", "Papel toalla interdoblada caja 20 paquetes", "consu", "Materiales / Limpieza", 32.00, 0.00, "Papel toalla para baños"),
    ("MAT-026", "Papel higiénico institucional jumbo rollo 12u", "consu", "Materiales / Limpieza", 26.00, 0.00, "Papel higiénico de alto tráfico"),
    ("MAT-027", "Bolsas plásticas negras para basura jumbo 100u", "consu", "Materiales / Limpieza", 22.00, 0.00, "Bolsas de 55 galones"),
    ("MAT-028", "Trapeador industrial de algodón hilado", "consu", "Materiales / Limpieza", 7.50, 0.00, "Repuesto de trapeador de góndolas"),
    ("MAT-029", "Mango de aluminio para trapeador 1.5m", "consu", "Materiales / Limpieza", 6.00, 0.00, "Estructura para limpieza"),
    ("MAT-030", "Escobillón industrial con cerdas de nylon", "consu", "Materiales / Limpieza", 8.50, 0.00, "Escoba para exteriores y pasillos"),
    ("MAT-031", "Recogedor de basura basculante con mango", "consu", "Materiales / Limpieza", 13.00, 0.00, "Recogedor móvil para piso de venta"),
    ("MAT-032", "Limpiador desengrasante para carnicería y deli 5L", "consu", "Materiales / Limpieza", 24.00, 0.00, "Desengrasante apto contacto alimentario"),
    ("MAT-033", "Paños de microfibra multiusos paquete 12u", "consu", "Materiales / Limpieza", 10.50, 0.00, "Paños para limpieza de vitrinas"),

    # Seguridad y Uniformes del Personal
    ("MAT-034", "Chaleco reflectivo con logo QuetzalMart", "consu", "Materiales / Uniformes", 8.90, 0.00, "Chaleco para personal de bodega"),
    ("MAT-035", "Guantes de nitrilo desechables caja 100u", "consu", "Materiales / Sanidad", 9.20, 0.00, "Guantes para manipulación de alimentos"),
    ("MAT-036", "Guantes de carnaza reforzados para carga", "consu", "Materiales / Uniformes", 6.80, 0.00, "Guantes de trabajo pesado"),
    ("MAT-037", "Cofias desechables para manipulación caja 100u", "consu", "Materiales / Sanidad", 4.50, 0.00, "Cubre cabellos para panadería"),
    ("MAT-038", "Delantales plásticos impermeables", "consu", "Materiales / Uniformes", 5.20, 0.00, "Protección en carnicería y pescadería"),
    ("MAT-039", "Fajas lumbares de protección para estibadores", "consu", "Materiales / Uniformes", 18.00, 0.00, "Protección ergonómica almacén"),
    ("MAT-040", "Botas de hule antideslizantes", "consu", "Materiales / Uniformes", 21.00, 0.00, "Calzado para área de lavado"),
    ("MAT-041", "Mascarillas quirúrgicas tricapa caja 50u", "consu", "Materiales / Sanidad", 3.80, 0.00, "Insumo de bioseguridad"),

    # Logística de Sucursal, Almacenaje y Exhibición
    ("MAT-042", "Cestas plásticas rojas para clientes 28L", "consu", "Materiales / Equipamiento", 6.50, 0.00, "Canastas manuales de compras"),
    ("MAT-043", "Carretilla de mano para transporte de cajas", "consu", "Materiales / Equipamiento", 75.00, 0.00, "Diablo de carga para descarga de camión"),
    ("MAT-044", "Portaprecios plástico transparente para góndola 1m", "consu", "Materiales / Exhibición", 2.20, 0.00, "Riel porta etiquetas"),
    ("MAT-045", "Separadores acrílicos para estantes", "consu", "Materiales / Exhibición", 3.10, 0.00, "Divisores de productos en anaqueles"),
    ("MAT-046", "Candados de seguridad de combinación para lockers", "consu", "Materiales / Seguridad", 7.00, 0.00, "Lockers de empleados"),
    ("MAT-047", "Cono de seguridad color naranja 'Piso Mojado'", "consu", "Materiales / Seguridad", 14.00, 0.00, "Señalización de prevención"),
    ("MAT-048", "Pilas alcalinas AA para escáneres paquete 24u", "consu", "Materiales / POS", 18.00, 0.00, "Baterías para lectores inalámbricos"),
    ("MAT-049", "Pilas alcalinas AAA para básculas paquete 24u", "consu", "Materiales / POS", 17.50, 0.00, "Baterías para periféricos"),
    ("MAT-050", "Cable de red ethernet RJ45 Cat6 15m", "consu", "Materiales / TI", 12.00, 0.00, "Conexión cajas POS"),

    # Mantenimiento y Conservación de Instalaciones
    ("MAT-051", "Bombillas LED de alto brillo 18W para techo", "consu", "Materiales / Mantenimiento", 4.80, 0.00, "Iluminación de pasillos"),
    ("MAT-052", "Tubo fluorescente LED 36W para góndolas", "consu", "Materiales / Mantenimiento", 7.20, 0.00, "Iluminación vitrinas"),
    ("MAT-053", "Gas refrigerante R404A para cámaras frías cilindro", "consu", "Materiales / Mantenimiento", 135.00, 0.00, "Recarga de sistemas de frío"),
    ("MAT-054", "Aceite lubricante multiusos WD-40 400ml", "consu", "Materiales / Mantenimiento", 6.50, 0.00, "Mantenimiento carretillas y bisagras"),
    ("MAT-055", "Termómetros digitales para congeladores", "consu", "Materiales / Mantenimiento", 15.00, 0.00, "Control de cadena de frío"),
    ("MAT-056", "Extintor de incendios PQS 10lbs recargado", "consu", "Materiales / Seguridad", 38.00, 0.00, "Seguridad contra incendios"),
    ("MAT-057", "Botiquín de primeros auxilios industrial para pared", "consu", "Materiales / Seguridad", 45.00, 0.00, "Atención médica básica sucursal"),
    ("MAT-058", "Precintos plásticos de seguridad numerados 100u", "consu", "Materiales / Seguridad", 16.00, 0.00, "Sellado de camiones y contenedores"),
    ("MAT-059", "Bandejas plásticas para área de carnes y pan", "consu", "Materiales / Exhibición", 5.50, 0.00, "Bandejas expositoras"),
    ("MAT-060", "Tarjetas PVC blancas para credenciales de acceso 100u", "consu", "Materiales / TI", 20.00, 0.00, "Identificación de empleados"),
]

# -------------------------------------------------------------------------
# 2. GENERACIÓN DE CLIENTES (35 registros con campos exactos)
# -------------------------------------------------------------------------
clientes_data = [
    ("Carlos Roberto Méndez", "person", "", "carlos.mendez@gmail.com", "+502 4123-5501", "7ma Avenida 12-34 Zona 1", "Apto 3B", "Ciudad de Guatemala", "Guatemala", "01001", "Guatemala", "1234567-8", "https://carlosmendez.com", "Cliente Frecuente", "REF-CLI-001", "Cliente con entrega a domicilio regular"),
    ("María Fernanda Morales", "person", "", "mf.morales@yahoo.com", "+502 5544-3322", "Boulevard Los Próceres 18-90 Zona 10", "", "Ciudad de Guatemala", "Guatemala", "01010", "Guatemala", "8765432-1", "", "VIP", "REF-CLI-002", "Prefiere compras los fines de semana"),
    ("Restaurante El Quetzal S.A.", "company", "", "compras@restelquetzal.gt", "+502 2333-8899", "6ta Calle Poniente #15", "Local 2", "Antigua Guatemala", "Sacatepéquez", "03001", "Guatemala", "9988776-5", "https://restauranteelquetzal.gt", "Corporativo, Mayorista", "REF-CLI-003", "Facturación con crédito 15 días"),
    ("Juan José Morales Estrada", "person", "", "jj.morales@hotmail.com", "+502 5201-9988", "12 Calle 4-55 Zona 14", "", "Ciudad de Guatemala", "Guatemala", "01014", "Guatemala", "1122334-4", "", "Minorista", "REF-CLI-004", "Cliente online frecuente"),
    ("Distribuidora Chapina Express", "company", "", "ventas@chapinaexpress.gt", "+502 2450-1122", "Calzada Roosevelt 34-01 Zona 11", "Km 14", "Mixco", "Guatemala", "01057", "Guatemala", "5544332-9", "https://chapinaexpress.gt", "Mayorista", "REF-CLI-005", "Pedidos quincenales"),
    ("Ana Lucía De León", "person", "", "analucia.deleon@outlook.com", "+502 4099-8811", "5ta Avenida 8-40 Zona 9", "Oficina 402", "Ciudad de Guatemala", "Guatemala", "01009", "Guatemala", "6677889-0", "", "Cliente Frecuente", "REF-CLI-006", "Pagos por tarjeta de crédito"),
    ("Supermercados del Norte S.A.", "company", "", "adquisiciones@supernorte.com.mx", "+52 55 5589-3200", "Av. Paseo de la Reforma 250", "Piso 8", "Ciudad de México", "CDMX", "06600", "Mexico", "SNO890412AA1", "https://supernorte.com.mx", "Corporativo, Internacional", "REF-CLI-007", "Sucursal México compras corporativas"),
    ("Pedro Alfonso Ramírez", "person", "", "pedro.ramirez.mx@gmail.com", "+52 55 4321-9870", "Calle Insurgentes Sur 1450", "Depto 204", "Ciudad de México", "CDMX", "03920", "Mexico", "RAMP850614M1", "", "Minorista", "REF-CLI-008", "Cliente de sucursal CDMX"),
    ("Comercializadora San Salvador", "company", "", "gerencia@comercializasv.com", "+503 2288-9900", "Calle El Mirador y 89 Av. Norte", "Edificio Torre Futura", "San Salvador", "San Salvador", "1101", "El Salvador", "0614-290590-102-1", "https://comercializasv.com", "Mayorista, Internacional", "REF-CLI-009", "Cliente de expansión en El Salvador"),
    ("Sofía Patricia Guardado", "person", "", "sofia.guardado@svmail.com", "+503 7744-1122", "Colonia Escalón, Paseo General Escalón", "#3450", "San Salvador", "San Salvador", "1101", "El Salvador", "0511-120988-101-4", "", "VIP", "REF-CLI-010", "Cliente sucursal El Salvador"),
    ("Marvin Gabriel Soto", "person", "", "marvin.soto@gmail.com", "+502 4588-1234", "Diagonal 6 10-01 Zona 10", "Nivel 3", "Ciudad de Guatemala", "Guatemala", "01010", "Guatemala", "3344556-7", "", "Cliente Frecuente", "REF-CLI-011", "Comprador habitual de abarrotes"),
    ("Cafetería Luna Llena", "company", "", "administracion@lunallena.gt", "+502 7832-4455", "4ta Calle Oriente #8", "", "Antigua Guatemala", "Sacatepéquez", "03001", "Guatemala", "7788990-1", "", "Pyme", "REF-CLI-012", "Compra café e insumos de pastelería"),
    ("Elena Beatriz Cifuentes", "person", "", "elena.cifuentes@gmail.com", "+502 5901-2233", "20 Calle 10-20 Zona 10", "", "Ciudad de Guatemala", "Guatemala", "01010", "Guatemala", "4455667-8", "", "Minorista", "REF-CLI-013", "Compras para el hogar"),
    ("Hotel y Centro de Convenciones Real", "company", "", "compras@hotelreal.gt", "+502 2411-9000", "14 Calle 3-40 Zona 1", "", "Ciudad de Guatemala", "Guatemala", "01001", "Guatemala", "2233445-5", "https://hotelreal.gt", "Corporativo", "REF-CLI-014", "Pedidos de bebidas en gran escala"),
    ("Jorge Luis Alvarado", "person", "", "jorge.alvarado@hotmail.com", "+502 4433-2211", "Calzada San Juan 15-40 Zona 7", "", "Ciudad de Guatemala", "Guatemala", "01007", "Guatemala", "8899001-2", "", "Minorista", "REF-CLI-015", "Cliente particular"),
    ("Tiendas de Conveniencia Express", "company", "", "operaciones@convenienciaexpress.com", "+502 2399-5566", "Avenida Las Américas 18-00 Zona 13", "", "Ciudad de Guatemala", "Guatemala", "01013", "Guatemala", "9900112-3", "", "Mayorista", "REF-CLI-016", "Surtido semanal"),
    ("Patricia Eugenia Rivera", "person", "", "patricia.rivera@gmail.com", "+502 5677-8899", "Km 18.5 Carretera a El Salvador", "Condominio La Fuente", "Fraijanes", "Guatemala", "01062", "Guatemala", "1029384-5", "", "VIP", "REF-CLI-017", "Cliente residencial"),
    ("Bebidas y Más del Pacífico", "company", "", "contacto@bebidaspacifico.gt", "+502 7766-5544", "Avenida Centroamérica 4-50", "", "Escuintla", "Escuintla", "05001", "Guatemala", "2039485-6", "", "Mayorista", "REF-CLI-018", "Distribuidor regional sur"),
    ("Rodrigo Esteban Fuentes", "person", "", "rodrigo.fuentes@yahoo.com", "+502 4112-3344", "3ra Calle 7-22 Zona 2", "", "Quetzaltenango", "Quetzaltenango", "09001", "Guatemala", "3049586-7", "", "Minorista", "REF-CLI-019", "Envío al occidente"),
    ("Comedores Populares El Éxito", "company", "", "comedor.exito@gmail.com", "+502 5566-7788", "11 Avenida 4-12 Zona 1", "", "Ciudad de Guatemala", "Guatemala", "01001", "Guatemala", "4059687-8", "", "Pyme", "REF-CLI-020", "Granos básicos y aceite"),
    ("Valeria Denise Aguilar", "person", "", "valeria.aguilar@gmail.com", "+502 5022-3344", "Boulevard Vista Hermosa 23-45 Zona 15", "", "Ciudad de Guatemala", "Guatemala", "01015", "Guatemala", "5069788-9", "", "Minorista", "REF-CLI-021", "Compra semanal de despensa"),
    ("Industrias Alimenticias Maya", "company", "", "abastecimiento@alamaya.gt", "+502 2422-3300", "Calzada Atanasio Tzul 22-00 Zona 12", "", "Ciudad de Guatemala", "Guatemala", "01012", "Guatemala", "6079889-0", "https://alamaya.gt", "Corporativo", "REF-CLI-022", "Insumos y conservas"),
    ("Diego Fernando Castillo", "person", "", "diego.castillo@outlook.com", "+502 4344-5566", "15 Avenida 8-30 Zona 11", "", "Ciudad de Guatemala", "Guatemala", "01011", "Guatemala", "7089990-1", "", "Minorista", "REF-CLI-023", "Cliente habitual"),
    ("Mini Súper Los Ángeles", "company", "", "losangelesminisuper@gmail.com", "+502 7888-1122", "Calle Real 5-60", "", "San Lucas Sacatepéquez", "Sacatepéquez", "03008", "Guatemala", "8090001-2", "", "Pyme", "REF-CLI-024", "Compras mayoristas quincenales"),
    ("Gabriela Nicole Salazar", "person", "", "gabriela.salazar@gmail.com", "+502 5455-6677", "9na Calle 2-15 Zona 1", "", "Ciudad de Guatemala", "Guatemala", "01001", "Guatemala", "9101112-3", "", "Minorista", "REF-CLI-025", "Entrega centro histórico"),
    ("Corporación Gastronómica Azteca", "company", "", "adquisiciones@gastronomicaazteca.mx", "+52 55 5678-1234", "Av. División del Norte 1200", "", "Ciudad de México", "CDMX", "03300", "Mexico", "CGA990215AB2", "https://gastronomicaazteca.mx", "Corporativo, Internacional", "REF-CLI-026", "Consumo para red de restaurantes"),
    ("Héctor Manuel Villatoro", "person", "", "hector.villatoro@gmail.com", "+502 4899-0011", "Boulevard San Cristóbal 14-80 Zona 8", "", "Mixco", "Guatemala", "01057", "Guatemala", "1213141-5", "", "Cliente Frecuente", "REF-CLI-027", "Recoge en tienda"),
    ("Panadería y Pastelería La Estrella", "company", "", "compras@panlaestrella.gt", "+502 2255-6677", "8va Avenida 15-44 Zona 6", "", "Ciudad de Guatemala", "Guatemala", "01006", "Guatemala", "2324252-6", "", "Pyme", "REF-CLI-028", "Harinas y lácteos"),
    ("Lucía Mariana Pineda", "person", "", "lucia.pineda@yahoo.com", "+502 5122-4466", "2da Calle 1-50 Zona 3", "", "Chimaltenango", "Chimaltenango", "04001", "Guatemala", "3435363-7", "", "Minorista", "REF-CLI-029", "Cliente regional"),
    ("Inversiones Cuscatlecas S.A.", "company", "", "contacto@inversionescuscatlecas.sv", "+503 2500-8800", "Boulevard de Los Héroes #12", "", "San Salvador", "San Salvador", "1101", "El Salvador", "0614-101099-103-2", "", "Mayorista, Internacional", "REF-CLI-030", "Cadena comercial El Salvador"),
    ("Guillermo Andrés Portillo", "person", "", "guillermo.portillo@svnet.com", "+503 7112-3344", "Colonia San Benito, Calle La Mascota", "#501", "San Salvador", "San Salvador", "1101", "El Salvador", "0511-040485-102-3", "", "VIP", "REF-CLI-031", "Cliente residencial San Salvador"),
    ("Claudia Marcela Santos", "person", "", "claudia.santos@gmail.com", "+502 4233-5577", "10ma Avenida 14-22 Zona 14", "", "Ciudad de Guatemala", "Guatemala", "01014", "Guatemala", "4546474-8", "", "Minorista", "REF-CLI-032", "Compras quincenales"),
    ("Servicios de Banquetes Delicias", "company", "", "eventos@banquetesdelicias.gt", "+502 2366-7788", "Avenida Reforma 8-60 Zona 9", "Oficina 301", "Ciudad de Guatemala", "Guatemala", "01009", "Guatemala", "5657585-9", "", "Corporativo", "REF-CLI-033", "Bebidas y canapés"),
    ("Óscar René Hernández", "person", "", "oscar.hernandez@hotmail.com", "+502 5344-6688", "1ra Avenida 9-33 Zona 2", "", "Ciudad de Guatemala", "Guatemala", "01002", "Guatemala", "6768696-0", "", "Minorista", "REF-CLI-034", "Cliente web"),
    ("Tienda de Abarrotes San Judas", "company", "", "sanjudas.tienda@gmail.com", "+502 5899-4411", "Calle Real 10-20", "", "Villa Nueva", "Guatemala", "01064", "Guatemala", "7879808-1", "", "Pyme", "REF-CLI-035", "Cliente de abarrotes"),
]

# -------------------------------------------------------------------------
# 3. GENERACIÓN DE PROVEEDORES (20 empresas abastecedoras)
# -------------------------------------------------------------------------
proveedores_data = [
    ("PRV-001", "Distribuidora de Alimentos La Campiña S.A.", "proveedor.campina@gmail.com", "+502 2333-1000", "Calzada Roosevelt 10-00 Zona 7", "Ciudad de Guatemala", "Guatemala", "01007", "Guatemala", "4567890-1", "Alimentos, Granos, Abarrotes"),
    ("PRV-002", "Lácteos y Derivados San Antonio", "ventas@lacteosanantonio.gt", "+502 7832-1122", "Km 45 Carretera Interamericana", "Sumpango", "Sacatepéquez", "03004", "Guatemala", "7890123-4", "Lácteos, Quesos, Leche"),
    ("PRV-003", "Bebidas Gaseosas y Jugos del Valle S.A.", "pedidos@bebidasdelvalle.gt", "+502 2470-8800", "Avenida Petapa 45-20 Zona 12", "Ciudad de Guatemala", "Guatemala", "01012", "Guatemala", "1230984-5", "Refrescos, Aguas, Jugos"),
    ("PRV-004", "Avícola y Embutidos Santa Lucía", "contacto@avicolasantalucia.gt", "+502 2444-5566", "Calzada San Juan 30-10 Zona 7", "Ciudad de Guatemala", "Guatemala", "01007", "Guatemala", "9081726-3", "Carnes, Pollo, Embutidos"),
    ("PRV-005", "Molinos y Harinas Centroamericanas", "ventas@molinosca.com", "+502 2230-4000", "Calle Martí 12-40 Zona 2", "Ciudad de Guatemala", "Guatemala", "01002", "Guatemala", "5432167-8", "Harinas, Panificación, Pastas"),
    ("PRV-006", "Suministros de Empaque y Cartón Maya", "empaquesmaya@gmail.com", "+502 2490-3322", "Calzada Atanasio Tzul 35-50 Zona 12", "Ciudad de Guatemala", "Guatemala", "01012", "Guatemala", "3456789-0", "Cajas, Bolsas, Film"),
    ("PRV-007", "Química e Higiene Industrial S.A.", "ventas@quimicahigiene.gt", "+502 2380-7700", "Avenida Las Américas 12-30 Zona 13", "Ciudad de Guatemala", "Guatemala", "01013", "Guatemala", "6789012-3", "Desinfectantes, Cloro, Jabones"),
    ("PRV-008", "Papelera y Rollos Térmicos del Istmo", "pedidos@rollostermicos.gt", "+502 2420-9911", "12 Avenida 10-33 Zona 1", "Ciudad de Guatemala", "Guatemala", "01001", "Guatemala", "8901234-5", "Papel térmico, Resmas, Etiquetas"),
    ("PRV-009", "Seguridad Ocupacional y Uniformes Pro", "uniformespro@gmail.com", "+502 2360-1144", "Boulevard Los Próceres 20-50 Zona 10", "Ciudad de Guatemala", "Guatemala", "01010", "Guatemala", "2345678-9", "Chalecos, Botas, Guantes, Fajas"),
    ("PRV-010", "Tecnología POS y Redes de Guatemala", "soporte@tecnologiapos.gt", "+502 2415-3000", "Diagonal 6 15-20 Zona 10", "Ciudad de Guatemala", "Guatemala", "01010", "Guatemala", "4561237-8", "Cables, Escáneres, Baterías, POS"),
    ("PRV-011", "Distribuidora Internacional México S.A. de C.V.", "ventas@distmexico.com.mx", "+52 55 5200-1100", "Av. Industrial 400", "Ciudad de México", "CDMX", "02300", "Mexico", "DIM020415XYZ", "Surtido General Sucursal México"),
    ("PRV-012", "Comercial de Insumos y Empaques CDMX", "empaquescdmx@gmail.com", "+52 55 5340-2211", "Calzada Vallejo 850", "Ciudad de México", "CDMX", "07700", "Mexico", "CIE050912ABC", "Insumos y Cajas México"),
    ("PRV-013", "Alimentos Cuscatlán S.A. de C.V.", "contacto@alimentosalvador.sv", "+503 2210-4400", "Carretera al Puerto de La Libertad Km 10", "Santa Tecla", "La Libertad", "1501", "El Salvador", "0614-150280-101-1", "Alimentos Sucursal El Salvador"),
    ("PRV-014", "Suministros Industriales San Salvador", "ventas@suministrossv.com", "+503 2270-3322", "Zona Industrial Merliot", "Antiguo Cuscatlán", "La Libertad", "1502", "El Salvador", "0614-220895-102-4", "Materiales e Insumos El Salvador"),
    ("PRV-015", "Agrícola y Verduras Frescas El Paraíso", "frescosparaiso@gmail.com", "+502 7744-2299", "Valle de Almolonga", "Quetzaltenango", "Quetzaltenango", "09001", "Guatemala", "1357924-6", "Verduras, Hortalizas"),
    ("PRV-016", "Frutas y Cítricos de la Costa S.A.", "frutascosta@gmail.com", "+502 7880-4411", "Autopista a Puerto San José Km 70", "Escuintla", "Escuintla", "05001", "Guatemala", "2468013-5", "Frutas frescas"),
    ("PRV-017", "Snacks y Frituras La Tradición", "pedidos@snacksguate.gt", "+502 2440-7766", "Calzada Aguilar Batres 24-10 Zona 11", "Ciudad de Guatemala", "Guatemala", "01011", "Guatemala", "9876543-2", "Snacks, Papas fritas, Golosinas"),
    ("PRV-018", "Café y Tostaduría Los Volcanes", "ventas@cafelosvolcanes.gt", "+502 7831-5500", "Calle Ancha de Los Herreros #22", "Antigua Guatemala", "Sacatepéquez", "03001", "Guatemala", "8765432-1", "Café gourmet en grano y molido"),
    ("PRV-019", "Cuidado del Hogar y Plásticos del Sur", "contacto@plasticosdelsur.gt", "+502 2477-9922", "Villa Hermosa 1 Sector 2", "San Miguel Petapa", "Guatemala", "01066", "Guatemala", "7654321-0", "Cestas, Baldes, Contenedores"),
    ("PRV-020", "Equipos Frigoríficos y Clima S.A.", "mantenimiento@climafrigo.gt", "+502 2385-4433", "Calzada Roosevelt 22-50 Zona 11", "Ciudad de Guatemala", "Guatemala", "01011", "Guatemala", "6543210-9", "Refrigerantes, Mantenimiento"),
]

# -------------------------------------------------------------------------
# 4. GENERACIÓN DE PRODUCTOS DE VENTA (40 productos de supermercado)
# -------------------------------------------------------------------------
productos_venta_data = [
    # Abarrotes y Granos
    ("PROD-001", "Arroz Blanco Grano Entero 1 lb", "consu", "Alimentos / Abarrotes", "740100100001", 0.55, 0.75, 0.45, "Arroz blanco de primera calidad 1 lb"),
    ("PROD-002", "Frijol Negro Volcán 1 lb", "consu", "Alimentos / Abarrotes", "740100100002", 0.80, 1.15, 0.45, "Frijol negro seleccionado de cosecha reciente"),
    ("PROD-003", "Azúcar Blanca Estándar 1 kg", "consu", "Alimentos / Abarrotes", "740100100003", 0.70, 0.95, 1.00, "Azúcar pura de caña refinada"),
    ("PROD-004", "Aceite Vegetal Ideal 800 ml", "consu", "Alimentos / Abarrotes", "740100100004", 1.90, 2.50, 0.80, "Aceite vegetal comestible puro"),
    ("PROD-005", "Harina de Trigo Selecta 1 kg", "consu", "Alimentos / Abarrotes", "740100100005", 0.90, 1.25, 1.00, "Harina de trigo enriquecida"),
    ("PROD-006", "Pasta Spaghetti Roma 200 g", "consu", "Alimentos / Abarrotes", "740100100006", 0.40, 0.60, 0.20, "Spaghetti clásico de trigo durum"),
    ("PROD-007", "Salsa de Tomate Naturas 106 g", "consu", "Alimentos / Abarrotes", "740100100007", 0.35, 0.50, 0.11, "Salsa de tomate lista con especias"),
    ("PROD-008", "Avena en Hojuelas Quaker 360 g", "consu", "Alimentos / Abarrotes", "740100100008", 1.20, 1.65, 0.36, "Avena 100% integral en bolsa"),
    ("PROD-009", "Sal Yodada de Mesa 500 g", "consu", "Alimentos / Abarrotes", "740100100009", 0.25, 0.40, 0.50, "Sal fina yodada y fluorada"),
    ("PROD-010", "Café Molido Quetzal Gourmet 400 g", "consu", "Alimentos / Café", "740100100010", 3.20, 4.50, 0.40, "Café de altura tostado y molido"),

    # Lácteos y Refrigerados
    ("PROD-011", "Leche Entera Trebolac 1 Litro", "consu", "Lácteos / Leches", "740100100011", 1.10, 1.50, 1.00, "Leche de vaca pasteurizada entera"),
    ("PROD-012", "Leche Deslactosada 1 Litro", "consu", "Lácteos / Leches", "740100100012", 1.25, 1.70, 1.00, "Leche semidescremada libre de lactosa"),
    ("PROD-013", "Queso Fresco Tipo Capas 400 g", "consu", "Lácteos / Quesos", "740100100013", 2.20, 3.10, 0.40, "Queso artesanal fresco empacado"),
    ("PROD-014", "Crema Pura Pasteurizada 250 ml", "consu", "Lácteos / Cremas", "740100100014", 1.00, 1.45, 0.25, "Crema fresca para cocina"),
    ("PROD-015", "Mantequilla con Sal 200 g", "consu", "Lácteos / Mantequillas", "740100100015", 1.30, 1.85, 0.20, "Mantequilla de leche de vaca"),
    ("PROD-016", "Yogurt Fresa Familiar 1 Litro", "consu", "Lácteos / Yogurts", "740100100016", 1.80, 2.60, 1.00, "Yogurt con trozos de fruta"),

    # Bebidas y Refrescos
    ("PROD-017", "Agua Pura Salvavidas 1.5 Litros", "consu", "Bebidas / Aguas", "740100100017", 0.60, 0.90, 1.50, "Agua purificada sin gas"),
    ("PROD-018", "Gaseosa Cola Quetzal 2 Litros", "consu", "Bebidas / Gaseosas", "740100100018", 1.20, 1.75, 2.00, "Bebida carbonatada sabor cola"),
    ("PROD-019", "Jugo de Naranja del Frutal 1 Litro", "consu", "Bebidas / Jugos", "740100100019", 1.30, 1.90, 1.00, "Jugo 100% néctar enriquecido con vitamina C"),
    ("PROD-020", "Té Frío Limón Botella 500 ml", "consu", "Bebidas / Té", "740100100020", 0.70, 1.00, 0.50, "Bebida refrescante sabor a té de limón"),

    # Carnes, Aves y Embutidos
    ("PROD-021", "Pechuga de Pollo Fresca 1 lb", "consu", "Carnes / Aves", "740100100021", 2.10, 2.90, 0.45, "Pechuga de pollo sin hueso"),
    ("PROD-022", "Carne Molida Especial de Res 1 lb", "consu", "Carnes / Res", "740100100022", 2.60, 3.60, 0.45, "Carne magra molida 90/10"),
    ("PROD-023", "Salchicha Viena Paquete 10u", "consu", "Carnes / Embutidos", "740100100023", 1.40, 2.00, 0.35, "Salchicha tipo viena de pavo"),
    ("PROD-024", "Jamón Cocido de Pavo 250 g", "consu", "Carnes / Embutidos", "740100100024", 1.75, 2.50, 0.25, "Jamón rebanado empacado al vacío"),

    # Panadería y Snacks
    ("PROD-025", "Pan de Rodaja Blanco Familiar 550 g", "consu", "Panadería / Pan", "740100100025", 1.50, 2.15, 0.55, "Pan blanco de molde clásico"),
    ("PROD-026", "Galletas Dulces Vainilla Tubo", "consu", "Snacks / Galletas", "740100100026", 0.45, 0.70, 0.15, "Galletas dulces crujientes"),
    ("PROD-027", "Tortrix Barbacoa Bolsa Familiar 180 g", "consu", "Snacks / Frituras", "740100100027", 1.00, 1.50, 0.18, "Frituras de maíz sabor barbacoa"),
    ("PROD-028", "Cereal Copos de Maíz Tostados 400 g", "consu", "Alimentos / Cereales", "740100100028", 1.90, 2.75, 0.40, "Cereal para desayuno fortificado"),

    # Cuidado Personal e Higiene
    ("PROD-029", "Jabón de Tocador Protex 110 g", "consu", "Cuidado Personal / Jabones", "740100100029", 0.70, 1.00, 0.11, "Jabón en barra antibacterial"),
    ("PROD-030", "Shampoo Capilar Anticaspa 400 ml", "consu", "Cuidado Personal / Cabello", "740100100030", 2.80, 3.95, 0.40, "Shampoo con aloe vera y piritionato"),
    ("PROD-031", "Crema Dental Protección Total 100 ml", "consu", "Cuidado Personal / Dental", "740100100031", 1.20, 1.75, 0.10, "Pasta de dientes anticaries con flúor"),
    ("PROD-032", "Desodorante Antitranspirante Roll-On 50 ml", "consu", "Cuidado Personal / Desodorantes", "740100100032", 1.60, 2.30, 0.05, "Protección 48 horas sin alcohol"),

    # Limpieza del Hogar
    ("PROD-033", "Detergente en Polvo Blanca Nieves 1 kg", "consu", "Limpieza / Lavandería", "740100100033", 1.40, 2.05, 1.00, "Detergente biodegradable con oxígeno activo"),
    ("PROD-034", "Suavizante de Telas Suavitel 850 ml", "consu", "Limpieza / Lavandería", "740100100034", 1.50, 2.20, 0.85, "Aroma primaveral para ropa"),
    ("PROD-035", "Lavaplatos Líquido Axion 750 ml", "consu", "Limpieza / Cocina", "740100100035", 1.60, 2.35, 0.75, "Jabón lavatrastes arranca grasa"),
    ("PROD-036", "Desinfectante para Pisos Lavanda 1 Litro", "consu", "Limpieza / Pisos", "740100100036", 1.10, 1.65, 1.00, "Limpiador aromático antibacterial"),
    ("PROD-037", "Cloro Blanqueador Hogar 1 Litro", "consu", "Limpieza / Hogar", "740100100037", 0.75, 1.10, 1.00, "Solución desinfectante de hipoclorito"),
    ("PROD-038", "Esponja Abrasiva Verde Doble Uso 3u", "consu", "Limpieza / Cocina", "740100100038", 0.80, 1.25, 0.08, "Fibra verde con esponja amarilla"),
    ("PROD-039", "Papel Higiénico Suave 4 Rollos", "consu", "Hogar / Papelería", "740100100039", 1.30, 1.95, 0.40, "Papel higiénico doble hoja acolchado"),
    ("PROD-040", "Fósforos de Seguridad Paquete 10 cajitas", "consu", "Hogar / Cocina", "740100100040", 0.40, 0.65, 0.10, "Cerillos clásicos de madera"),
]


def exportar_csv():
    # 1. Materiales CSV
    path_mat = os.path.join(BASE_DIR, "60_materiales.csv")
    with open(path_mat, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["default_code", "name", "type", "categ_id", "standard_price", "list_price", "description"])
        for m in materiales_data:
            writer.writerow(m)
    print(f"[OK] Generado: {path_mat} ({len(materiales_data)} materiales)")

    # 2. Clientes CSV
    path_cli = os.path.join(BASE_DIR, "clientes.csv")
    with open(path_cli, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Company Type", "Related Company", "Email", "Phone", "Street", "Street2", "City", "State", "Zip", "Country", "Tax ID", "Website", "Tags", "Reference", "Notes"])
        for c in clientes_data:
            writer.writerow(c)
    print(f"[OK] Generado: {path_cli} ({len(clientes_data)} clientes)")

    # 3. Proveedores CSV
    path_prv = os.path.join(BASE_DIR, "proveedores.csv")
    with open(path_prv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Reference", "Name", "Email", "Phone", "Street", "City", "State", "Zip", "Country", "Tax ID", "Notes"])
        for p in proveedores_data:
            writer.writerow(p)
    print(f"[OK] Generado: {path_prv} ({len(proveedores_data)} proveedores)")

    # 4. Productos de Venta CSV
    path_prod = os.path.join(BASE_DIR, "productos_venta.csv")
    with open(path_prod, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Internal Reference", "Name", "Product Type", "Category", "Barcode", "Cost", "Sales Price", "Weight", "Sales Description"])
        for pr in productos_venta_data:
            writer.writerow([pr[0], pr[1], pr[2], pr[3], pr[4], pr[5], pr[6], pr[7], pr[8]])
    print(f"[OK] Generado: {path_prod} ({len(productos_venta_data)} productos de venta)")


if __name__ == "__main__":
    exportar_csv()
