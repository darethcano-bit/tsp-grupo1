# Problema del Agente Viajero (TSP) por fuerza bruta
# Matemática Computacional (1AMA0726) - UPC - Grupo 1
# Archivo app.py: página web hecha con Streamlit.
# Para probarla en la computadora:  streamlit run app.py

import json
import math
import random
import time
from pathlib import Path

import pandas as pd
import streamlit as st

import grafo as G

st.set_page_config(page_title="TSP por fuerza bruta - Grupo 1", page_icon="🗺️", layout="wide")

NOMBRES = ["Tipo de grafo", "Número de nodos", "Construcción", "Revisión",
           "Condiciones", "Rutas", "Resultado"]
COLORES = {"Azul": "#1f4fbf", "Verde": "#157347", "Morado": "#6b3fc0",
           "Turquesa": "#0f766e", "Naranja": "#c2570c"}
FONDOS = {"Blanco": ("#ffffff", "#eef1f5"), "Gris claro": ("#f4f5f7", "#e4e7eb"),
          "Celeste": ("#eef6fc", "#d9e9f6"), "Crema": ("#fbf8f1", "#efe7d6"),
          "Menta": ("#f1f8f4", "#dcede3")}

ss = st.session_state
INICIAL = {"paso": 1, "tipo": "No dirigido", "sorteado": None, "n": 6, "modo": "Generar al azar",
           "semilla": random.randint(100, 999), "grafo": None, "rutas": None, "costos": None,
           "ciclos": None, "resultado": None, "actual": 0, "elegido": 0, "reproduciendo": False,
           "version": 0, "color": "Azul", "fondo": "Blanco", "zip": None, "recien_creado": False}
for clave, valor in INICIAL.items():
    if clave not in ss:
        ss[clave] = valor
    else:
        ss[clave] = ss[clave]      # evita que Streamlit borre el valor al cambiar de paso
CARPETA = Path(__file__).parent


# ---------------------------------------------------------------
# Funciones de apoyo
# ---------------------------------------------------------------
def es_dirigido():
    if ss.tipo == "Aleatorio":
        return ss.sorteado
    return ss.tipo == "Dirigido"


def invalidar():
    # el grafo cambió: lo calculado ya no sirve
    ss.rutas = None
    ss.resultado = None
    ss.zip = None
    ss.actual = 0
    ss.elegido = 0
    ss.reproduciendo = False
    ss.version = ss.version + 1


def ir_a(paso):
    ss.paso = paso
    ss.reproduciendo = False


def siguiente():
    if ss.paso == 1 and ss.tipo == "Aleatorio" and ss.sorteado is None:
        ss.sorteado = random.choice([True, False])
    if ss.paso == 2:
        d = es_dirigido()
        if ss.grafo is None or ss.grafo.n != ss.n or ss.grafo.dirigido != d:
            ss.grafo = G.Grafo(ss.n, d)
            ss.grafo.ubicar_nodos()
            ss.recien_creado = True
            invalidar()
    if ss.paso == 3 and not ss.grafo.lista_aristas():
        ss.aviso = "El grafo todavía no tiene aristas."
        return
    ir_a(ss.paso + 1)


def atras():
    ir_a(ss.paso - 1)


def nuevo_grafo():
    for clave, valor in INICIAL.items():
        if clave not in ("color", "fondo"):
            ss[clave] = valor
    ss.semilla = random.randint(100, 999)


def matriz_tabla(M, guion):
    filas = []
    for fila in M:
        filas.append(["-" if (guion and x == 0) else G.num(x) for x in fila])
    return pd.DataFrame(filas, columns=[str(j) for j in range(len(M))],
                        index=[str(i) for i in range(len(M))])


def mapa(**opciones):
    fig = G.figura(ss.grafo, color=COLORES[ss.color], **opciones)
    st.pyplot(fig, width="stretch")
    G.plt.close(fig)


# ---------------------------------------------------------------
# Barra lateral: logo, pasos y colores
# ---------------------------------------------------------------
with st.sidebar:
    st.image(str(CARPETA / "logo_upc.png"), width=70)
    st.markdown("**Universidad Peruana de Ciencias Aplicadas**  \nMatemática Computacional (1AMA0726)  \nGrupo 1")
    st.divider()
    for i, nombre in enumerate(NOMBRES, start=1):
        if i < ss.paso:
            st.markdown("✅ %d. %s" % (i, nombre))
        elif i == ss.paso:
            st.markdown('<span class="paso-actual">▶ %d. %s</span>' % (i, nombre), unsafe_allow_html=True)
        else:
            st.markdown("⚪ %d. %s" % (i, nombre))
    st.divider()
    st.markdown("**🎨 Colores de la página**")
    st.selectbox("Color principal", list(COLORES), key="color")
    st.selectbox("Fondo", list(FONDOS), key="fondo")

# Aplica los colores elegidos a botones, títulos y fondo
COLOR = COLORES[ss.color]
FONDO, FONDO_LATERAL = FONDOS[ss.fondo]
st.markdown("""<style>
.stApp, [data-testid="stHeader"] { background-color: %(f)s; }
[data-testid="stSidebar"] { background-color: %(fl)s; }
button[kind="primary"] { background-color: %(c)s !important; border-color: %(c)s !important; color: #ffffff !important; }
button[kind="primary"]:hover { filter: brightness(1.12); }
button[kind="secondary"]:hover, button[kind="secondary"]:focus { border-color: %(c)s !important; color: %(c)s !important; }
[data-testid="stSlider"] [role="slider"] { background-color: %(c)s !important; box-shadow: none !important; }
[data-testid="stSlider"] [data-baseweb="slider"] > div > div > div:first-child { background: %(c)s !important; }
[data-testid="stSliderThumbValue"] { color: %(c)s !important; }
h1, h1 span, [data-testid="stHeading"] h1 { color: %(c)s !important; }
h1 { border-bottom: 4px solid %(c)s; padding-bottom: 0.3rem; }
h3 { color: %(c)s; }
.paso-actual { color: %(c)s; font-weight: 700; }
</style>""" % {"c": COLOR, "f": FONDO, "fl": FONDO_LATERAL}, unsafe_allow_html=True)

st.title("Problema del Agente Viajero por fuerza bruta")
izq, der = st.columns([1, 1.8], gap="large")
aviso = ss.pop("aviso", None)


# ---------------------------------------------------------------
# Paso 1: tipo de grafo
# ---------------------------------------------------------------
def cambio_tipo():
    ss.sorteado = random.choice([True, False]) if ss.tipo == "Aleatorio" else None


def abrir_grafo():
    archivo = ss.get("archivo")
    if archivo is None:
        return
    try:
        datos = json.load(archivo)
        g = G.grafo_desde_diccionario(datos)
        if not (5 <= g.n <= 10):
            raise ValueError
    except (ValueError, KeyError, TypeError):
        ss.aviso = "El archivo no es un grafo válido."
        return
    ss.grafo = g
    ss.tipo = "Dirigido" if g.dirigido else "No dirigido"
    ss.sorteado = None
    ss.n = g.n
    ss.modo = "Ingresar a mano"
    invalidar()
    ir_a(4)


def paso1():
    with izq:
        st.subheader("Paso 1. ¿Qué tipo de grafo?")
        st.radio("Tipo de grafo", ["No dirigido", "Dirigido", "Aleatorio"], key="tipo",
                 on_change=cambio_tipo, label_visibility="collapsed",
                 captions=["Ida y vuelta cuestan lo mismo.",
                           "Con flechas: el sentido importa y la vuelta puede costar distinto.",
                           "El programa elige uno de los dos al azar."])
        if ss.tipo == "Aleatorio" and ss.sorteado is not None:
            st.info("Salió: **%s**" % ("dirigido" if ss.sorteado else "no dirigido"))
        st.divider()
        st.file_uploader("¿Guardaste un grafo antes? Ábrelo aquí (.json)", type=["json"],
                         key="archivo", on_change=abrir_grafo)
    with der:
        mapa()


# ---------------------------------------------------------------
# Paso 2: número de nodos
# ---------------------------------------------------------------
def paso2():
    with izq:
        st.subheader("Paso 2. ¿Cuántos nodos?")
        st.write("Tipo de grafo: **%s**" % ("dirigido" if es_dirigido() else "no dirigido"))
        st.slider("Número de nodos", 5, 10, key="n")
        f = math.factorial(ss.n - 1)
        if es_dirigido():
            st.info("Rutas que se revisarán: (n − 1)! = %d! = **%s**\n\n"
                    "En un grafo dirigido, 0-1-2-0 y 0-2-1-0 son rutas distintas." % (ss.n - 1, f"{f:,}".replace(",", " ")))
        else:
            st.info("Rutas que se revisarán: (n − 1)!/2 = %d!/2 = **%s**\n\n"
                    "Se divide entre 2 porque recorrer el ciclo al revés cuesta lo mismo." % (ss.n - 1, f"{f // 2:,}".replace(",", " ")))
    with der:
        mapa()


# ---------------------------------------------------------------
# Paso 3: construcción del grafo
# ---------------------------------------------------------------
def generar():
    ss.grafo.generar_aleatorio(int(ss.semilla))
    invalidar()


def otro_grafo():
    ss.semilla = random.randint(100, 999)
    generar()


def borrar_todas():
    for (a, b, p) in ss.grafo.lista_aristas():
        ss.grafo.quitar_arista(a, b)
    ss.grafo.semilla = None
    invalidar()


def reubicar():
    ss.grafo.ubicar_nodos()
    invalidar()


def agregar_arista():
    g = ss.grafo
    a, b = ss.origen, ss.destino
    if a == b:
        ss.aviso = "El origen y el destino deben ser nodos distintos."
        return
    peso = ss["peso_%d_%d" % (a, b)]
    if peso <= 0:
        ss.aviso = "El peso debe ser mayor que 0."
        return
    g.agregar_arista(a, b, int(peso) if float(peso).is_integer() else peso)
    if g.dirigido and ss.get("con_regreso"):
        vuelta = ss["vuelta_%d_%d" % (a, b)]
        if vuelta > 0:
            g.agregar_arista(b, a, int(vuelta) if float(vuelta).is_integer() else vuelta)
    invalidar()
    ss.aviso_ok = "Arista %d %s %d guardada." % (a, "→" if g.dirigido else "–", b)


def paso3():
    g = ss.grafo
    with izq:
        st.subheader("Paso 3. Construye el grafo")
        st.radio("Modo", ["Generar al azar", "Ingresar a mano"], key="modo", horizontal=True,
                 label_visibility="collapsed")
        if ss.modo == "Generar al azar":
            st.number_input("Semilla", min_value=0, step=1, key="semilla")
            c1, c2 = st.columns(2)
            c1.button("Generar", on_click=generar, width="stretch")
            c2.button("Otro grafo", on_click=otro_grafo, width="stretch")
            st.caption("Los nodos se ubican como ciudades y cada uno tiene como máximo 3 conexiones. "
                       "El peso es la distancia en el mapa. La misma semilla siempre da el mismo grafo.")
            if ss.recien_creado:
                ss.recien_creado = False
                generar()
                st.rerun()
        else:
            nodos = list(range(g.n))
            c1, c2 = st.columns(2)
            c1.selectbox("Desde", nodos, key="origen")
            c2.selectbox("Hasta", nodos, key="destino", index=1)
            a, b = ss.origen, ss.destino
            sugerido = float(g.matriz[a][b] if g.matriz[a][b] else g.distancia(a, b)) if a != b else 1.0
            st.number_input("Peso de %d %s %d (km); viene sugerida la distancia del mapa" %
                            (a, "→" if g.dirigido else "–", b),
                            min_value=0.0, value=sugerido, step=1.0, key="peso_%d_%d" % (a, b))
            if g.dirigido:
                st.checkbox("Agregar también el regreso %d → %d" % (b, a), key="con_regreso")
                if ss.get("con_regreso"):
                    st.number_input("Peso de %d → %d (km)" % (b, a), min_value=0.0, value=sugerido,
                                    step=1.0, key="vuelta_%d_%d" % (a, b))
            c1, c2 = st.columns(2)
            c1.button("Agregar arista", type="primary", on_click=agregar_arista, width="stretch")
            c2.button("Reubicar nodos", on_click=reubicar, width="stretch")

        st.markdown("**Aristas del grafo** (puedes cambiar el peso o marcar Eliminar)")
        aristas = g.lista_aristas()
        tabla = pd.DataFrame([{"Desde": a, "Hasta": b, "Peso (km)": float(p), "Eliminar": False}
                              for (a, b, p) in aristas],
                             columns=["Desde", "Hasta", "Peso (km)", "Eliminar"])
        editada = st.data_editor(tabla, hide_index=True, width="stretch",
                                 disabled=["Desde", "Hasta"], key="tabla_%d" % ss.version,
                                 column_config={"Peso (km)": st.column_config.NumberColumn(min_value=0.01, step=1.0)})
        cambios = False
        for k in range(len(editada)):
            a, b = int(editada.iloc[k]["Desde"]), int(editada.iloc[k]["Hasta"])
            peso = editada.iloc[k]["Peso (km)"]
            if editada.iloc[k]["Eliminar"]:
                g.quitar_arista(a, b)
                cambios = True
            elif pd.notna(peso) and peso > 0 and peso != g.matriz[a][b]:
                g.agregar_arista(a, b, int(peso) if float(peso).is_integer() else float(peso))
                cambios = True
        if cambios:
            invalidar()
            st.rerun()
        st.button("Borrar todas las aristas", on_click=borrar_todas)
        if ss.get("aviso_ok"):
            st.success(ss.pop("aviso_ok"))
    with der:
        mapa(origen=None)
        if g.semilla is not None:
            st.caption("Grafo generado con la semilla %s." % g.semilla)


# ---------------------------------------------------------------
# Paso 4: revisión
# ---------------------------------------------------------------
def paso4():
    g = ss.grafo
    with izq:
        st.subheader("Paso 4. Revisa el grafo")
        st.caption("Este mismo grafo se mantiene en el mapa durante todo el análisis.")
        st.markdown("**Matriz de costos** (fila = desde, columna = hasta)")
        st.dataframe(matriz_tabla(g.matriz, True), width="stretch")
        st.markdown("**Grados**")
        if g.dirigido:
            entrada, salida = g.grados()
            st.dataframe(pd.DataFrame([entrada, salida], index=["Entra", "Sale"],
                                      columns=[str(v) for v in range(g.n)]), width="stretch")
        else:
            st.dataframe(pd.DataFrame([g.grados()], index=["Grado"],
                                      columns=[str(v) for v in range(g.n)]), width="stretch")
        c1, c2 = st.columns(2)
        c1.download_button("Guardar grafo (.json)", json.dumps(g.a_diccionario(), indent=2),
                           file_name="grafo_tsp.json", mime="application/json", width="stretch")
        tipo = "dirigido" if g.dirigido else "no dirigido"
        c2.download_button("Descargar imagen", G.figura_png(G.figura(g, titulo="Grafo %s con %d nodos" % (tipo, g.n),
                                                                     blanco_y_negro=True)),
                           file_name="grafo_inicial.png", mime="image/png", width="stretch")
    with der:
        mapa()


# ---------------------------------------------------------------
# Paso 5: condiciones necesarias
# ---------------------------------------------------------------
def paso5():
    g = ss.grafo
    condiciones = g.condiciones()
    malos = []
    with izq:
        st.subheader("Paso 5. ¿Puede existir un ciclo hamiltoniano?")
        st.caption("Si una condición falla, no hay ciclo. Si todas se cumplen, puede haberlo o no: "
                   "lo confirma la fuerza bruta.")
        for (texto, cumple, detalle, nodos) in condiciones:
            if cumple:
                st.success("**%s.** %s" % (texto, detalle))
            else:
                st.error("**%s.** %s" % (texto, detalle))
            malos = malos + nodos
        P, potencia = g.matriz_de_caminos()
        st.markdown("**Matriz de caminos** (1 = hay camino; se sumaron A … A^%d)" % potencia)
        st.dataframe(matriz_tabla(P, False), width="stretch")
    with der:
        mapa(malos=malos)
        if malos:
            st.caption("Borde punteado: nodo que no cumple una condición.")


# ---------------------------------------------------------------
# Paso 6: revisión de rutas
# ---------------------------------------------------------------
def mover(i):
    ss.actual = max(0, min(len(ss.rutas) - 1, i))
    ss.reproduciendo = False


def siguiente_ciclo():
    for i in ss.ciclos:
        if i > ss.actual:
            mover(i)
            return
    ss.aviso = "No hay más ciclos después de esta ruta."


def alternar_reproduccion():
    ss.reproduciendo = not ss.reproduciendo


def elegir_ciclo():
    filas = ss.lista_ciclos.selection.rows
    if filas:
        mover(ss.ciclos[filas[0]])


def paso6():
    g = ss.grafo
    if ss.rutas is None:
        with st.spinner("Calculando todas las rutas..."):
            ss.rutas, ss.costos, ss.ciclos = G.revisar_rutas(g)
    rutas, costos, ciclos = ss.rutas, ss.costos, ss.ciclos
    ruta = rutas[ss.actual]
    costo, pesos, faltan = g.evaluar(ruta)
    with izq:
        st.subheader("Paso 6. Revisión de las rutas una por una")
        st.caption("Ruta %s de %s" % (f"{ss.actual + 1:,}".replace(",", " "), f"{len(rutas):,}".replace(",", " ")))
        st.markdown("### " + G.ruta_texto(ruta))
        if not faltan:
            st.success("✓ Es ciclo hamiltoniano  \nCosto = %s = **%s**" % (" + ".join(G.num(p) for p in pesos), G.num(costo)))
        else:
            flecha = "→" if g.dirigido else "–"
            st.error("✗ No es ciclo. No existe: " + ", ".join("%d %s %d" % (a, flecha, b) for a, b in faltan))
        mejor = G.mejor_hasta(costos, ciclos, ss.actual)
        if mejor is None:
            st.caption("Mejor hasta aquí: todavía ninguno.")
        else:
            st.caption("Mejor hasta aquí: ruta %d, %s, costo %s" % (mejor + 1, G.ruta_texto(rutas[mejor]), G.num(costos[mejor])))
        c = st.columns(2)
        c[0].button("◀ Anterior", on_click=mover, args=(ss.actual - 1,), width="stretch")
        c[1].button("Siguiente ▶", on_click=mover, args=(ss.actual + 1,), width="stretch")
        c = st.columns(2)
        c[0].button("⏮ Primera", on_click=mover, args=(0,), width="stretch")
        c[1].button("Última ⏭", on_click=mover, args=(len(rutas) - 1,), width="stretch")
        c = st.columns(2)
        c[0].button("Siguiente ciclo", on_click=siguiente_ciclo, width="stretch")
        c[1].button("⏸ Pausar" if ss.reproduciendo else "▶ Reproducir", on_click=alternar_reproduccion,
                    width="stretch")
        st.markdown("**Ciclos hamiltonianos: %d de %s rutas**" % (len(ciclos), f"{len(rutas):,}".replace(",", " ")))
        if ciclos:
            lista = pd.DataFrame([{"Ruta": i + 1, "Ciclo": G.ruta_texto(rutas[i]).replace(" ", ""),
                                   "Costo": G.num(costos[i])} for i in ciclos[:2000]])
            st.dataframe(lista, hide_index=True, width="stretch", height=min(250, 38 + 35 * len(lista)),
                         on_select=elegir_ciclo, selection_mode="single-row", key="lista_ciclos")
            st.caption("Haz clic en una fila para ver ese ciclo en el mapa.")
        else:
            st.caption("Ninguna ruta forma un ciclo hamiltoniano.")
    with der:
        mapa(ruta=ruta)
        st.caption("Línea gruesa: ruta y orden de visita. Línea punteada: arista que no existe.")


# ---------------------------------------------------------------
# Paso 7: resultado
# ---------------------------------------------------------------
def cambio_elegido():
    ss.zip = None


def paso7():
    g = ss.grafo
    if ss.resultado is None:
        ss.resultado = G.calcular_resultado(g, ss.rutas, ss.costos, ss.ciclos)
    R = ss.resultado
    rutas = ss.rutas
    flecha = "→" if g.dirigido else "-"
    with izq:
        st.subheader("Paso 7. Resultado")
        st.caption("Rutas revisadas: %s. Ciclos hamiltonianos: %d." % (f"{len(rutas):,}".replace(",", " "), len(ss.ciclos)))
        if R["hay_ciclo"]:
            etiquetas = ["%s (ruta %d)" % (G.ruta_texto(rutas[i]), i + 1) for i in R["opciones"]]
            st.metric("Costo mínimo", "%s km" % G.num(R["minimo"]))
            if len(etiquetas) > 1:
                st.radio("Hay %d ciclos con el costo mínimo. Elige uno:" % len(etiquetas),
                         range(len(etiquetas)), format_func=lambda k: etiquetas[k], key="elegido",
                         on_change=cambio_elegido)
            ruta = rutas[R["opciones"][ss.elegido]]
            costo, pesos, f = g.evaluar(ruta)
            st.markdown("### " + G.ruta_texto(ruta))
            st.write("%s = %s" % (" + ".join(G.num(p) for p in pesos), G.num(costo)))
        else:
            st.error("No existe ciclo hamiltoniano.")
            st.write("Como mínimo %s." % ("falta 1 arista" if R["minimo"] == 1 else "faltan %d aristas" % R["minimo"]))
            etiquetas = ["Agregar " + ", ".join("%d%s%d" % (a, flecha, b) for a, b in op) for op in R["opciones"]]
            st.radio("Opciones (elige una para verla en el mapa):", range(len(etiquetas)),
                     format_func=lambda k: etiquetas[k], key="elegido", on_change=cambio_elegido)
        st.divider()
        st.caption("Descarga una carpeta comprimida con la imagen del grafo, la imagen del resultado "
                   "(en blanco y negro), un reporte con todas las rutas y el grafo para volver a abrirlo.")
        if ss.zip is None:
            ss.zip = G.archivo_zip(g, rutas, ss.costos, R, ss.elegido)
        nombre, datos = ss.zip
        st.download_button("Exportar resultados (.zip)", datos, file_name=nombre, mime="application/zip",
                           type="primary", width="stretch")
    with der:
        if R["hay_ciclo"]:
            mapa(ruta=rutas[R["opciones"][ss.elegido]], titulo="Ciclo hamiltoniano de costo mínimo")
        else:
            mapa(faltantes=R["opciones"][ss.elegido], titulo="Aristas que faltan para formar un ciclo")


# ---------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------
[paso1, paso2, paso3, paso4, paso5, paso6, paso7][ss.paso - 1]()

with izq:
    if aviso:
        st.warning(aviso)
    st.divider()
    c1, c2 = st.columns(2)
    c1.button("◀ Atrás", on_click=atras, disabled=ss.paso == 1, width="stretch")
    if ss.paso < 7:
        c2.button("Ver resultado ▶" if ss.paso == 6 else "Siguiente ▶", on_click=siguiente, type="primary",
                  width="stretch")
    else:
        c2.button("Nuevo grafo", on_click=nuevo_grafo, type="primary", width="stretch")

if ss.paso == 6 and ss.reproduciendo:
    if ss.actual >= len(ss.rutas) - 1:
        ss.reproduciendo = False
    else:
        time.sleep(0.5)
        ss.actual = ss.actual + 1
        st.rerun()
