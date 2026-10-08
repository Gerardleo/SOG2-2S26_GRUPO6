"""
Utilidades compartidas por los scripts del Integrante 2 (Tienda Web, CRM, Marketing).
Las credenciales NO van en el codigo: se leen del archivo .env (ignorado por git)
o de variables de entorno. Copia .env.example a .env y llenalo.
"""

import os
import sys
import xmlrpc.client
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def cargar_env():
    valores = {}
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        for linea in env_path.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, valor = linea.split("=", 1)
            valores[clave.strip()] = valor.strip().strip('"').strip("'")
    for clave in list(valores) + ["ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_PASSWORD"]:
        if clave in os.environ:
            valores[clave] = os.environ[clave]
    return valores


class Odoo:
    def __init__(self, url, db, user, password):
        self.url, self.db, self.user, self.password = url.rstrip("/"), db, user, password
        common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", allow_none=True)
        self.version = common.version().get("server_version", "?")
        self.uid = common.authenticate(db, user, password, {})
        if not self.uid:
            sys.exit("[ERROR] Autenticacion fallida: revisa ODOO_DB / ODOO_USER / ODOO_PASSWORD en .env")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=True)

    def call(self, model, method, *args, **kwargs):
        try:
            return self.models.execute_kw(self.db, self.uid, self.password, model, method, list(args), kwargs)
        except xmlrpc.client.Fault as e:
            # Metodos de Odoo que devuelven None (ej. mail.mail.send): el metodo SI se ejecuto,
            # solo falla el empaquetado de la respuesta por XML-RPC.
            if "cannot marshal None" in str(e):
                return None
            raise

    def search(self, model, dominio, **kw):
        return self.call(model, "search", dominio, **kw)

    def read(self, model, ids, campos):
        return self.call(model, "read", ids, campos)

    def search_read(self, model, dominio, campos, **kw):
        return self.call(model, "search_read", dominio, fields=campos, **kw)

    def create(self, model, vals):
        return self.call(model, "create", vals)

    def write(self, model, ids, vals):
        return self.call(model, "write", ids, vals)

    def ref(self, xmlid):
        """Devuelve el id de un registro por su xml id ('modulo.nombre') o None."""
        modulo, nombre = xmlid.split(".", 1)
        r = self.search_read("ir.model.data", [["module", "=", modulo], ["name", "=", nombre]], ["res_id"], limit=1)
        return r[0]["res_id"] if r else None

    def set_param(self, clave, valor):
        self.call("ir.config_parameter", "set_param", clave, valor)


def conectar():
    env = cargar_env()
    faltan = [k for k in ("ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_PASSWORD") if not env.get(k)]
    if faltan:
        sys.exit(f"[ERROR] Faltan variables en .env: {', '.join(faltan)} (copia .env.example a .env)")
    print(f"[*] Conectando a {env['ODOO_URL']} (BD {env['ODOO_DB']})...")
    odoo = Odoo(env["ODOO_URL"], env["ODOO_DB"], env["ODOO_USER"], env["ODOO_PASSWORD"])
    print(f"[+] Conectado. Odoo {odoo.version}, uid {odoo.uid}")
    return odoo, env
