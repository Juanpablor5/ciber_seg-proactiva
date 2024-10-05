import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, Session
from prefect import task, flow

config_bd = {
    "local": {
        "host": "localhost",
        "port": "5432",
        "user": "postgres",
        "password": "postgres",
        "database": "juan_rocha",
    },
    "aws": {
        "host": "postgres.cspcvpb5rw4y.us-east-1.rds.amazonaws.com",
        "port": "5432",
        "user": "jrocha",
        "password": "fjwvacC_d6iupULVdyK7",
        "database": "analitica",
    },
}


def config_conexion(func):
    def inner(tipo, *args, **kwargs):
        data = config_bd[tipo]
        return func(data, *args, **kwargs)

    return inner


@config_conexion
@task
def conectar_bd(env_data):
    print(f'connected to {env_data["database"]} db')

    host = env_data["host"]
    port = env_data["port"]
    user = env_data["user"]
    password = env_data["password"]
    database = env_data["database"]

    return sa.create_engine(
        f"postgresql://{user}:{password}@{host}:{port}/{database}", echo=False
    )


@task
def obtener_datos_colegio(env):
    conn = conectar_bd(env)
    sql_query = """
        select
            s.cole_cod_dane_establecimiento,
            s.cole_jornada,
            s.cole_naturaleza,
            s.cole_calendario,
            s.cole_nombre_establecimiento,
            s.cole_caracter,
            s.cole_area_ubicacion,
            s.cole_genero,
            AVG(s.punt_global) as prom_punt_global
        from
            saber_11 s
        group by
            s.cole_cod_dane_establecimiento,
            s.cole_jornada,
            s.cole_naturaleza,
            s.cole_calendario,
            s.cole_nombre_establecimiento,
            s.cole_caracter,
            s.cole_area_ubicacion,
            s.cole_genero
        order by
            prom_punt_global desc;
      """
    datos_colegio = pd.read_sql_query(sql_query, con=conn)

    conn.dispose()
    return datos_colegio


@task
def obtener_datos_estudiante(env):
    conn = conectar_bd(env)
    sql_query = """
        select
            s.estu_consecutivo,
            s.periodo,
            s.cole_cod_dane_establecimiento,
            s.estu_fechanacimiento,
            s.estu_genero,
            s.fami_estratovivienda,
            s.fami_tieneinternet,
            s.fami_tienecomputador,
            s.fami_educacionmadre,
            s.fami_educacionpadre,
            s.punt_ingles,
            s.punt_matematicas,
            s.punt_sociales_ciudadanas,
            s.punt_c_naturales,
            s.punt_lectura_critica,
            s.punt_global
        from
            saber_11 s;
      """
    datos_estudiante = pd.read_sql_query(sql_query, con=conn)

    conn.dispose()
    return datos_estudiante


def nivel_educacion_maximo(row):
    education_levels = [
        "Ninguno",
        "Primaria incompleta",
        "Primaria completa",
        "Secundaria (Bachillerato) incompleta",
        "Secundaria (Bachillerato) completa",
        "Técnica o tecnológica incompleta",
        "Técnica o tecnológica completa",
        "Educación profesional incompleta",
        "Educación profesional completa",
        "Postgrado",
    ]

    levels = [row["fami_educacionmadre"], row["fami_educacionpadre"]]

    levels = [level for level in levels if level in education_levels]

    if levels:
        return max(levels, key=lambda level: education_levels.index(level))
    return "Ninguno"


@task
def limpiar_datos_estudiantes(datos_estudiante):
    datos_estudiante = datos_estudiante[
        datos_estudiante["estu_genero"].isin(["F", "M"])
    ]

    datos_estudiante["fami_estratovivienda"] = datos_estudiante[
        "fami_estratovivienda"
    ].replace("", "Sin Estrato")

    datos_estudiante = datos_estudiante[
        datos_estudiante["fami_tieneinternet"].isin(["Si", "No"])
    ]

    datos_estudiante["nivel_educacion_maximo"] = datos_estudiante.apply(
        nivel_educacion_maximo, axis=1
    )

    return datos_estudiante


@task
def promedio_puntaje_periodo(datos_colegio, datos_estudiante):
    merged_data = pd.merge(
        datos_estudiante,
        datos_colegio,
        on="cole_cod_dane_establecimiento",
        how="inner",
        validate="m:m",
    )

    return (
        merged_data.groupby(["periodo", "cole_naturaleza", "cole_jornada"])
        .agg(
            prom_punt_global=("punt_global", "mean"),
            numero_estudiantes=("punt_global", "size"),
        )
        .reset_index()
    )


@task
def promedio_puntaje_genero(datos_colegio, datos_estudiante):
    merged_data = pd.merge(
        datos_estudiante,
        datos_colegio,
        on="cole_cod_dane_establecimiento",
        how="inner",
        validate="m:m",
    )

    return (
        merged_data.groupby(["estu_genero", "cole_naturaleza", "cole_jornada"])
        .agg(
            prom_punt_global=("punt_global", "mean"),
            numero_estudiantes=("punt_global", "size"),
        )
        .reset_index()
    )


@task
def promedio_puntaje_estrato(datos_colegio, datos_estudiante):
    merged_data = pd.merge(
        datos_estudiante,
        datos_colegio,
        on="cole_cod_dane_establecimiento",
        how="inner",
        validate="m:m",
    )

    return (
        merged_data.groupby(["fami_estratovivienda", "cole_naturaleza", "cole_jornada"])
        .agg(
            prom_punt_global=("punt_global", "mean"),
            numero_estudiantes=("punt_global", "size"),
        )
        .reset_index()
    )


@task
def promedio_puntaje_internet(datos_colegio, datos_estudiante):
    merged_data = pd.merge(
        datos_estudiante,
        datos_colegio,
        on="cole_cod_dane_establecimiento",
        how="inner",
        validate="m:m",
    )

    return (
        merged_data.groupby(["fami_tieneinternet", "cole_naturaleza", "cole_jornada"])
        .agg(
            prom_punt_global=("punt_global", "mean"),
            numero_estudiantes=("punt_global", "size"),
        )
        .reset_index()
    )


@task
def promedio_puntaje_educacion_familia(datos_colegio, datos_estudiante):
    merged_data = pd.merge(
        datos_estudiante,
        datos_colegio,
        on="cole_cod_dane_establecimiento",
        how="inner",
        validate="m:m",
    )

    return (
        merged_data.groupby(
            ["nivel_educacion_maximo", "cole_naturaleza", "cole_jornada"]
        )
        .agg(
            prom_punt_global=("punt_global", "mean"),
            numero_estudiantes=("punt_global", "size"),
        )
        .reset_index()
    )


Base = declarative_base()


@task
def cargar_tablas_analitica(
    env,
    datos_colegio,
    puntaje_periodo,
    puntaje_genero,
    puntaje_estrato,
    puntaje_internet,
    puntaje_educacion_familia,
):
    class AnaliticaColegio(Base):
        __tablename__ = "analitica_colegio"

        id = sa.Column(sa.Integer, primary_key=True)
        cole_cod_dane_establecimiento = sa.Column(sa.String)
        cole_jornada = sa.Column(sa.String)
        cole_naturaleza = sa.Column(sa.String)
        cole_calendario = sa.Column(sa.String)
        cole_nombre_establecimiento = sa.Column(sa.String)
        cole_caracter = sa.Column(sa.String)
        cole_area_ubicacion = sa.Column(sa.String)
        cole_genero = sa.Column(sa.String)
        prom_punt_global = sa.Column(sa.Float)

        def _repr_(self):
            return f"AnaliticaColegio(id={self.id!r}, cole_cod_dane_establecimiento={self.cole_cod_dane_establecimiento!r}, \
                    cole_jornada = {self.cole_jornada!r}, cole_naturaleza = {self.cole_naturaleza!r}, cole_calendario = {self.cole_calendario!r}, \
                    cole_nombre_establecimiento = {self.cole_nombre_establecimiento!r}, cole_caracter = {self.cole_caracter!r}, \
                    cole_area_ubicacion = {self.cole_area_ubicacion!r}, cole_genero = {self.cole_genero!r}, prom_punt_global = {self.prom_punt_global!r}"

    class AnaliticaPuntajePeriodo(Base):
        __tablename__ = "analitica_puntaje_periodo"

        id = sa.Column(sa.Integer, primary_key=True)
        periodo = sa.Column(sa.Integer)
        cole_naturaleza = sa.Column(sa.String)
        cole_jornada = sa.Column(sa.String)
        prom_punt_global = sa.Column(sa.Float)
        numero_estudiantes = sa.Column(sa.Integer)

        def _repr_(self):
            return f"AnaliticaPuntajePeriodo(id={self.id!r}, periodo={self.periodo!r}, cole_naturaleza={self.cole_naturaleza!r}, \
                    cole_jornada = {self.cole_jornada!r}, prom_punt_global = {self.prom_punt_global!r}, numero_estudiantes = {self.numero_estudiantes!r}"

    class AnaliticaPuntajeGenero(Base):
        __tablename__ = "analitica_puntaje_genero"

        id = sa.Column(sa.Integer, primary_key=True)
        estu_genero = sa.Column(sa.String)
        cole_naturaleza = sa.Column(sa.String)
        cole_jornada = sa.Column(sa.String)
        prom_punt_global = sa.Column(sa.Float)
        numero_estudiantes = sa.Column(sa.Integer)

        def _repr_(self):
            return f"AnaliticaPuntajeGenero(id={self.id!r}, estu_genero={self.estu_genero!r}, cole_naturaleza={self.cole_naturaleza!r}, \
                    cole_jornada = {self.cole_jornada!r}, prom_punt_global = {self.prom_punt_global!r}, numero_estudiantes = {self.numero_estudiantes!r}"

    class AnaliticaPuntajeEstrato(Base):
        __tablename__ = "analitica_puntaje_estrato"

        id = sa.Column(sa.Integer, primary_key=True)
        fami_estratovivienda = sa.Column(sa.String)
        cole_naturaleza = sa.Column(sa.String)
        cole_jornada = sa.Column(sa.String)
        prom_punt_global = sa.Column(sa.Float)
        numero_estudiantes = sa.Column(sa.Integer)

        def _repr_(self):
            return f"AnaliticaPuntajeEstrato(id={self.id!r}, fami_estratovivienda={self.fami_estratovivienda!r}, cole_naturaleza={self.cole_naturaleza!r}, \
                    cole_jornada = {self.cole_jornada!r}, prom_punt_global = {self.prom_punt_global!r}, numero_estudiantes = {self.numero_estudiantes!r}"

    class AnaliticaPuntajeInternet(Base):
        __tablename__ = "analitica_puntaje_internet"

        id = sa.Column(sa.Integer, primary_key=True)
        fami_tieneinternet = sa.Column(sa.String)
        cole_naturaleza = sa.Column(sa.String)
        cole_jornada = sa.Column(sa.String)
        prom_punt_global = sa.Column(sa.Float)
        numero_estudiantes = sa.Column(sa.Integer)

        def _repr_(self):
            return f"AnaliticaPuntajeInternet(id={self.id!r}, fami_tieneinternet={self.fami_tieneinternet!r}, cole_naturaleza={self.cole_naturaleza!r}, \
                    cole_jornada = {self.cole_jornada!r}, prom_punt_global = {self.prom_punt_global!r}, numero_estudiantes = {self.numero_estudiantes!r}"

    class AnaliticaEducacionFamilia(Base):
        __tablename__ = "analitica_educacion_familia"

        id = sa.Column(sa.Integer, primary_key=True)
        nivel_educacion_maximo = sa.Column(sa.String)
        cole_naturaleza = sa.Column(sa.String)
        cole_jornada = sa.Column(sa.String)
        prom_punt_global = sa.Column(sa.Float)
        numero_estudiantes = sa.Column(sa.Integer)

        def _repr_(self):
            return f"AnaliticaEducacionFamilia(id={self.id!r}, nivel_educacion_maximo={self.nivel_educacion_maximo!r}, cole_naturaleza={self.cole_naturaleza!r}, \
                    cole_jornada = {self.cole_jornada!r}, prom_punt_global = {self.prom_punt_global!r}, numero_estudiantes = {self.numero_estudiantes!r}"

    conn = conectar_bd(env)

    Base.metadata.create_all(conn)

    try:
        with Session(conn) as session:
            session.bulk_insert_mappings(
                AnaliticaColegio, datos_colegio.to_dict(orient="records")
            )
            session.bulk_insert_mappings(
                AnaliticaPuntajePeriodo, puntaje_periodo.to_dict(orient="records")
            )
            session.bulk_insert_mappings(
                AnaliticaPuntajeGenero, puntaje_genero.to_dict(orient="records")
            )
            session.bulk_insert_mappings(
                AnaliticaPuntajeEstrato, puntaje_estrato.to_dict(orient="records")
            )
            session.bulk_insert_mappings(
                AnaliticaPuntajeInternet, puntaje_internet.to_dict(orient="records")
            )
            session.bulk_insert_mappings(
                AnaliticaEducacionFamilia,
                puntaje_educacion_familia.to_dict(orient="records"),
            )
            session.commit()
    finally:
        conn.dispose()


@flow(name="proyecto_grupal", log_prints=True)
def flujo_analitica():
    datos_colegio = obtener_datos_colegio("local")
    datos_estudiante = obtener_datos_estudiante("local")

    datos_estudiante = limpiar_datos_estudiantes(datos_estudiante)

    puntaje_periodo = promedio_puntaje_periodo(datos_colegio, datos_estudiante)
    puntaje_genero = promedio_puntaje_genero(datos_colegio, datos_estudiante)
    puntaje_estrato = promedio_puntaje_estrato(datos_colegio, datos_estudiante)
    puntaje_internet = promedio_puntaje_internet(datos_colegio, datos_estudiante)
    puntaje_educacion_familia = promedio_puntaje_educacion_familia(
        datos_colegio, datos_estudiante
    )

    cargar_tablas_analitica(
        "aws",
        datos_colegio,
        puntaje_periodo,
        puntaje_genero,
        puntaje_estrato,
        puntaje_internet,
        puntaje_educacion_familia,
    )

    print("ETL process finished")


if __name__ == "__main__":
    flujo_analitica()
