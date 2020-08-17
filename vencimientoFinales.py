import re

VERANO = "ver"
PCUAT = "1c"
SCUAT = "2c"
INVIERNO = "inv"

VERANOS = ["v", "ver", "verano"]
INVIERNOS = ["i", "inv", "invierno"]


def parse_cuatri_y_anio(linea):
    # regex para parametros.
    r_entrada = r"^(?P<cuatri>[12]c|v(er(ano)?)?|i(nv(ierno)?)?)(?P<anio>20\d{2})$"
    entrada = re.search(r_entrada, linea)
    if not entrada:
        raise 

    cuatri = entrada.group("cuatri")
    anio = entrada.group("anio")

    return cuatri, anio

def get_vencimiento (cuatri, anio) :

    if cuatri in VERANOS:
        cuatri = VERANO
    elif cuatri in INVIERNOS:
        cuatri = INVIERNO

    cuatri_string = {
        PCUAT : "1er cuatri", 
        SCUAT : "2do cuatri",
        VERANO : "verano",
        INVIERNO : "invierno",
    }

    if cuatri == VERANO or cuatri == PCUAT:
        cuatri_limite = "Febrero/Marzo"
        mes_extension = "Abril"
    else:
        cuatri_limite = "Julio/Agosto"
        mes_extension = "Septiembre"

    anio_limite = int(anio) + 4

    mje = f"""Materia aprobada en {cuatri_string[cuatri]} de {anio}.
    
Última fecha en la cual podés rendir:
*{cuatri_limite} de {anio_limite}.*

Puede extenderse a {mes_extension} si lo aprueba el CD para ese año. Consultar en el Depto. de Estudiantes (Pab. 2)."""

    if anio_limite == 2020:
        mje += "\n\n*Según resolución N°430/20 de CD se extiende la validez de los trabajos prácticos que vencen en 2020 hasta 2021.*"

    return mje
