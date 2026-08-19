-- tablas creadas y catalogos usados para la base de datos

CREATE TABLE IF NOT EXISTS catalogo_genero (
    id_genero SMALLINT PRIMARY KEY,
    descripcion VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS catalogo_metodo_pago (
    id_metodo_pago SMALLINT PRIMARY KEY,
    descripcion VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS catalogo_canal_venta (
    id_canal SMALLINT PRIMARY KEY,
    descripcion VARCHAR(30) NOT NULL UNIQUE
);

INSERT INTO catalogo_genero (id_genero, descripcion) VALUES
    (0, 'Masculino'), (1, 'Femenino')
ON CONFLICT (id_genero) DO NOTHING;

INSERT INTO catalogo_metodo_pago (id_metodo_pago, descripcion) VALUES
    (0, 'Efectivo'), (1, 'Tarjeta de credito'), (2, 'Tarjeta de debito')
ON CONFLICT (id_metodo_pago) DO NOTHING;

INSERT INTO catalogo_canal_venta (id_canal, descripcion) VALUES
    (0, 'Tienda fisica'), (1, 'Navegador 1'), (2, 'Navegador 2'),
    (3, 'Navegador 3'), (4, 'Navegador 4')
ON CONFLICT (id_canal) DO NOTHING;

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente BIGINT PRIMARY KEY,
    edad SMALLINT NOT NULL CHECK (edad BETWEEN 18 AND 79),
    id_genero SMALLINT NOT NULL REFERENCES catalogo_genero (id_genero)
);

CREATE TABLE IF NOT EXISTS preferencias_cliente (
    id_cliente BIGINT PRIMARY KEY REFERENCES clientes (id_cliente),
    recibe_boletin BOOLEAN NOT NULL,
    utiliza_vale BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS resumen_cliente_anual (
    id_cliente BIGINT PRIMARY KEY REFERENCES clientes (id_cliente),
    n_compras INTEGER NOT NULL CHECK (n_compras > 0),
    venta_total NUMERIC(12, 2) NOT NULL CHECK (venta_total >= 0)
);

CREATE TABLE IF NOT EXISTS compras_registradas (
    id_compra BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente BIGINT NOT NULL REFERENCES clientes (id_cliente),
    fecha_compra DATE NOT NULL,
    monto_compra NUMERIC(12, 3) NOT NULL CHECK (monto_compra >= 0),
    id_metodo_pago SMALLINT NOT NULL REFERENCES catalogo_metodo_pago (id_metodo_pago),
    id_canal SMALLINT NOT NULL REFERENCES catalogo_canal_venta (id_canal),
    tiempo INTEGER NOT NULL CHECK (tiempo >= 0)
);

CREATE INDEX IF NOT EXISTS idx_compras_fecha ON compras_registradas (fecha_compra);
CREATE INDEX IF NOT EXISTS idx_compras_cliente ON compras_registradas (id_cliente);
