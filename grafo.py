# Problema del Agente Viajero (TSP) por fuerza bruta
# Matemática Computacional (1AMA0726) - UPC - Grupo 1
# Archivo grafo.py: toda la parte matemática y los dibujos.

import io
import itertools
import json
import math
import random
import zipfile
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

KM = 30              # 1 unidad del mapa = 30 km
GRADO_MAX = 3


def num(x):
    # escribe el número con coma decimal
    if float(x).is_integer():
        return str(int(x))
    return str(round(x, 2)).replace(".", ",")


def ruta_texto(ruta):
    texto = ""
    for i in range(len(ruta)):
        texto = texto + str(ruta[i])
        if i < len(ruta) - 1:
            texto = texto + " - "
    return texto


def cerca_del_segmento(p, a, b, limite):
    # True si el punto p está muy cerca del segmento ab
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    x = a[0] + t * dx
    y = a[1] + t * dy
    return math.hypot(p[0] - x, p[1] - y) < limite


def se_cruzan(p1, p2, q1, q2):
    # True si los segmentos p1p2 y q1q2 se cruzan
    def giro(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return (giro(q1, q2, p1) * giro(q1, q2, p2) < 0 and
            giro(p1, p2, q1) * giro(p1, p2, q2) < 0)


# ---------------------------------------------------------------
# Clase Grafo: toda la parte matemática
# ---------------------------------------------------------------
class Grafo:

    def __init__(self, n, dirigido):
        self.n = n
        self.dirigido = dirigido
        self.matriz = []
        for i in range(n):
            self.matriz.append([0] * n)
        self.pos = []
        self.semilla = None

    def agregar_arista(self, a, b, peso):
        self.matriz[a][b] = peso
        if not self.dirigido:
            self.matriz[b][a] = peso

    def quitar_arista(self, a, b):
        self.matriz[a][b] = 0
        if not self.dirigido:
            self.matriz[b][a] = 0

    def lista_aristas(self):
        lista = []
        for a in range(self.n):
            for b in range(self.n):
                if self.matriz[a][b] > 0:
                    if self.dirigido or a < b:
                        lista.append((a, b, self.matriz[a][b]))
        return lista

    def distancia(self, a, b):
        x1, y1 = self.pos[a]
        x2, y2 = self.pos[b]
        return max(1, round(math.hypot(x1 - x2, y1 - y2) * KM))

    def ubicar_nodos(self):
        # coloca los nodos dispersos, separados al menos "minimo"
        minimo = 0.3
        while True:
            self.pos = []
            intentos = 0
            while len(self.pos) < self.n and intentos < 3000:
                x = random.uniform(0.06, 1.44)
                y = random.uniform(0.07, 0.93)
                lejos = True
                for (px, py) in self.pos:
                    if math.hypot(x - px, y - py) < minimo:
                        lejos = False
                if lejos:
                    self.pos.append((x, y))
                intentos = intentos + 1
            if len(self.pos) == self.n:
                return
            minimo = minimo * 0.9

    def generar_aleatorio(self, semilla):
        random.seed(semilla)
        self.semilla = semilla
        self.matriz = []
        for i in range(self.n):
            self.matriz.append([0] * self.n)
        self.ubicar_nodos()

        grado = [0] * self.n
        calles = []

        def se_puede(a, b):
            if (a, b) in calles or (b, a) in calles:
                return False
            if grado[a] >= GRADO_MAX or grado[b] >= GRADO_MAX:
                return False
            for v in range(self.n):
                if v != a and v != b and cerca_del_segmento(self.pos[v], self.pos[a], self.pos[b], 0.09):
                    return False
            for (u, w) in calles:
                if u not in (a, b) and w not in (a, b):
                    if se_cruzan(self.pos[a], self.pos[b], self.pos[u], self.pos[w]):
                        return False
            return True

        # pares ordenados de más cerca a más lejos
        pares = []
        for a in range(self.n):
            for b in range(a + 1, self.n):
                pares.append((self.distancia(a, b) + random.uniform(0, 8), a, b))
        pares.sort()

        for (d, a, b) in pares:
            if d <= 0.85 * KM and random.random() < 0.8 and se_puede(a, b):
                calles.append((a, b))
                grado[a] = grado[a] + 1
                grado[b] = grado[b] + 1

        # intentar que cada nodo tenga al menos 2 conexiones
        for v in range(self.n):
            vecinos = list(range(self.n))
            vecinos.remove(v)
            vecinos.sort(key=lambda u: self.distancia(v, u))
            for u in vecinos:
                if grado[v] < 2 and se_puede(v, u):
                    calles.append((v, u))
                    grado[v] = grado[v] + 1
                    grado[u] = grado[u] + 1

        for (a, b) in calles:
            d = self.distancia(a, b)
            if not self.dirigido:
                self.agregar_arista(a, b, d)
            else:
                r = random.random()
                if r < 0.7:                       # doble sentido
                    self.agregar_arista(a, b, d)
                    self.agregar_arista(b, a, max(1, d + random.randint(-3, 3)))
                elif r < 0.85:                    # solo de a hacia b
                    self.agregar_arista(a, b, d)
                else:                             # solo de b hacia a
                    self.agregar_arista(b, a, d)

    def grados(self):
        # no dirigido: grado de cada nodo
        # dirigido: (grados de entrada, grados de salida)
        entrada = [0] * self.n
        salida = [0] * self.n
        for a in range(self.n):
            for b in range(self.n):
                if self.matriz[a][b] > 0:
                    salida[a] = salida[a] + 1
                    entrada[b] = entrada[b] + 1
        if self.dirigido:
            return entrada, salida
        return salida

    def matriz_de_caminos(self):
        # P = A or A^2 or A^3 ... (producto booleano) hasta que no cambie
        A = []
        for i in range(self.n):
            fila = []
            for j in range(self.n):
                fila.append(1 if self.matriz[i][j] > 0 else 0)
            A.append(fila)
        P = [fila[:] for fila in A]
        potencia = 1
        while True:
            nueva = [fila[:] for fila in P]
            for i in range(self.n):
                for j in range(self.n):
                    for k in range(self.n):
                        if P[i][k] == 1 and A[k][j] == 1:
                            nueva[i][j] = 1
            if nueva == P:
                return P, potencia
            P = nueva
            potencia = potencia + 1

    def condiciones(self):
        # devuelve una lista de (texto, cumple, detalle, nodos_que_fallan)
        P, pot = self.matriz_de_caminos()
        sin_camino = None
        for i in range(self.n):
            for j in range(self.n):
                if i != j and P[i][j] == 0 and sin_camino is None:
                    sin_camino = (i, j)
        resultado = []
        if not self.dirigido:
            if sin_camino is None:
                resultado.append(("El grafo es conexo", True, "Todos los nodos están comunicados", []))
            else:
                resultado.append(("El grafo es conexo", False,
                                  "No hay camino entre %d y %d" % sin_camino, []))
            g = self.grados()
            malos = [v for v in range(self.n) if g[v] < 2]
            detalle = "Todos tienen grado 2 o más"
            if malos:
                detalle = ", ".join("nodo %d (grado %d)" % (v, g[v]) for v in malos)
            resultado.append(("Todo nodo tiene grado >= 2", len(malos) == 0, detalle, malos))
        else:
            if sin_camino is None:
                resultado.append(("Es fuertemente conexo", True,
                                  "Desde cada nodo se llega a todos siguiendo las flechas", []))
            else:
                resultado.append(("Es fuertemente conexo", False,
                                  "No se puede ir de %d a %d" % sin_camino, []))
            entrada, salida = self.grados()
            malos = [v for v in range(self.n) if entrada[v] < 1 or salida[v] < 1]
            detalle = "Todos tienen al menos una flecha que entra y una que sale"
            if malos:
                detalle = ", ".join("nodo %d (entra %d, sale %d)" % (v, entrada[v], salida[v])
                                    for v in malos)
            resultado.append(("Entrada >= 1 y salida >= 1", len(malos) == 0, detalle, malos))
        return resultado

    def rutas_candidatas(self):
        # no dirigido: (n-1)!/2 rutas (p[0] < p[-1] evita repetir el ciclo al revés)
        # dirigido: (n-1)! rutas porque el sentido importa
        rutas = []
        for p in itertools.permutations(range(1, self.n)):
            if self.dirigido or p[0] < p[-1]:
                rutas.append((0,) + p + (0,))
        return rutas

    def evaluar(self, ruta):
        # devuelve (costo, lista de pesos, aristas que faltan)
        costo = 0
        pesos = []
        faltan = []
        for i in range(len(ruta) - 1):
            a = ruta[i]
            b = ruta[i + 1]
            if self.matriz[a][b] == 0:
                faltan.append((a, b))
            else:
                costo = costo + self.matriz[a][b]
                pesos.append(self.matriz[a][b])
        return costo, pesos, faltan

    def a_diccionario(self):
        return {"n": self.n, "dirigido": self.dirigido, "posiciones": [list(p) for p in self.pos],
                "aristas": [list(a) for a in self.lista_aristas()], "semilla": self.semilla}


def grafo_desde_diccionario(datos):
    g = Grafo(int(datos["n"]), bool(datos["dirigido"]))
    g.pos = [tuple(p) for p in datos["posiciones"]]
    for (a, b, peso) in datos["aristas"]:
        g.agregar_arista(int(a), int(b), peso)
    g.semilla = datos.get("semilla")
    return g


# ---------------------------------------------------------------
# Fuerza bruta completa y resultado
# ---------------------------------------------------------------
def revisar_rutas(g):
    # devuelve todas las rutas, el costo de cada una (None si no es ciclo)
    # y las posiciones de las rutas que sí son ciclo
    rutas = g.rutas_candidatas()
    costos = []
    ciclos = []
    for i in range(len(rutas)):
        costo, pesos, faltan = g.evaluar(rutas[i])
        if faltan:
            costos.append(None)
        else:
            costos.append(costo)
            ciclos.append(i)
    return rutas, costos, ciclos


def calcular_resultado(g, rutas, costos, ciclos):
    if ciclos:
        minimo = min(costos[i] for i in ciclos)
        optimos = [i for i in ciclos if costos[i] == minimo]
        return {"hay_ciclo": True, "minimo": minimo, "opciones": optimos}
    # si no hay ciclos: cuántas aristas faltan como mínimo y cuáles
    menor = None
    for ruta in rutas:
        faltan = len(g.evaluar(ruta)[2])
        if menor is None or faltan < menor:
            menor = faltan
    opciones = []
    for ruta in rutas:
        faltan = g.evaluar(ruta)[2]
        if len(faltan) == menor:
            if not g.dirigido:
                faltan = [tuple(sorted(a)) for a in faltan]
            faltan = sorted(faltan)
            if faltan not in opciones:
                opciones.append(faltan)
    return {"hay_ciclo": False, "minimo": menor, "opciones": opciones}


def mejor_hasta(costos, ciclos, actual):
    mejor = None
    for j in ciclos:
        if j > actual:
            break
        if mejor is None or costos[j] < costos[mejor]:
            mejor = j
    return mejor


# ---------------------------------------------------------------
# Dibujo del grafo con matplotlib
# ---------------------------------------------------------------
def _flecha(ax, g, a, b, color, grosor, flecha, texto, color_texto, punteada=False, zorder=2):
    (x1, y1), (x2, y2) = g.pos[a], g.pos[b]
    y1, y2 = 1 - y1, 1 - y2
    d = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / d, (y2 - y1) / d
    sep = 0.012 if (g.dirigido and g.matriz[b][a] > 0 and g.matriz[a][b] > 0) else 0
    sx, sy = uy * sep, -ux * sep
    ini = (x1 + ux * 0.047 + sx, y1 + uy * 0.047 + sy)
    fin = (x2 - ux * 0.047 + sx, y2 - uy * 0.047 + sy)
    ax.annotate("", xy=fin, xytext=ini, zorder=zorder,
                arrowprops=dict(arrowstyle="-|>" if flecha else "-", color=color, lw=grosor,
                                linestyle="--" if punteada else "-", mutation_scale=14,
                                shrinkA=0, shrinkB=0))
    if texto is not None:
        ax.text((ini[0] + fin[0]) / 2 + sx * 2, (ini[1] + fin[1]) / 2 + sy * 2, texto,
                ha="center", va="center", fontsize=9.5, color=color_texto, weight="bold", zorder=6,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=color_texto, lw=0.8))


def figura(g, ruta=None, faltantes=None, malos=None, origen=None, titulo="", pie="",
           color="#1f4fbf", blanco_y_negro=False):
    if blanco_y_negro:
        color = "black"
    rojo = "black" if blanco_y_negro else "#c62828"
    gris = "0.55"
    gris_claro = "0.8"
    fig, ax = plt.subplots(figsize=(9, 6.4))
    fig.patch.set_facecolor("white")
    for k in range(16):
        ax.plot([k * 0.1, k * 0.1], [0, 1], color="0.92", lw=0.8, zorder=0)
    for k in range(11):
        ax.plot([0, 1.5], [k * 0.1, k * 0.1], color="0.92", lw=0.8, zorder=0)
    ax.plot([0, 0.5], [-0.035, -0.035], color="0.35", lw=1.5)
    ax.text(0.25, -0.07, "%d km" % (KM // 2), ha="center", va="center", fontsize=8, color="0.35")
    if g is not None:
        for (a, b, peso) in g.lista_aristas():
            c = gris_claro if ruta else gris
            _flecha(ax, g, a, b, c, 1.2, g.dirigido, num(peso), "0.45" if ruta else "0.2")
        if ruta:
            for i in range(len(ruta) - 1):
                a, b = ruta[i], ruta[i + 1]
                if g.matriz[a][b] > 0:
                    _flecha(ax, g, a, b, color, 3, True, num(g.matriz[a][b]), color, zorder=3)
                else:
                    _flecha(ax, g, a, b, rojo, 1.6, True, "falta", rojo, punteada=True, zorder=3)
        for (a, b) in (faltantes or []):
            _flecha(ax, g, a, b, rojo, 1.6, g.dirigido, "nueva", rojo, punteada=True, zorder=3)
        orden = {}
        if ruta:
            for k, v in enumerate(ruta[:-1]):
                orden[v] = k + 1
        for v in range(g.n):
            x, y = g.pos[v][0], 1 - g.pos[v][1]
            relleno = color if v == origen else "white"
            borde = rojo if (malos and v in malos) else "black"
            if malos and v in malos:
                ax.add_patch(plt.Circle((x, y), 0.055, fc="none", ec=rojo, lw=1.5, ls="--", zorder=4))
            ax.add_patch(plt.Circle((x, y), 0.045, fc=relleno, ec=borde, lw=1.8, zorder=5))
            ax.text(x, y, str(v), ha="center", va="center", fontsize=13, weight="bold",
                    color="white" if v == origen else "black", zorder=6)
            if v == 0:
                ax.text(x, y - 0.07, "inicio", ha="center", va="center", fontsize=7, color="0.4", zorder=6)
            if v in orden:
                ax.text(x + 0.05, y + 0.045, str(orden[v]), ha="center", va="center", fontsize=8.5,
                        color=color, weight="bold", zorder=7,
                        bbox=dict(boxstyle="circle,pad=0.2", fc="white", ec=color, lw=0.8))
    else:
        ax.text(0.75, 0.5, "Aquí aparecerá el mapa del grafo", ha="center", va="center",
                fontsize=14, color="0.5")
    ax.set_xlim(-0.03, 1.53)
    ax.set_ylim(-0.1, 1.03)
    ax.set_aspect("equal")
    ax.axis("off")
    if titulo:
        ax.set_title(titulo, fontsize=12, weight="bold")
    if pie:
        fig.text(0.5, 0.04, pie, ha="center", fontsize=10)
    fig.tight_layout()
    return fig


def figura_png(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return buffer.getvalue()


# ---------------------------------------------------------------
# Reporte y archivo de resultados
# ---------------------------------------------------------------
def reporte(g, rutas, costos, resultado):
    flecha = "->" if g.dirigido else "-"
    L = ["PROBLEMA DEL AGENTE VIAJERO - FUERZA BRUTA",
         "Matemática Computacional (1AMA0726) - Grupo 1",
         "Fecha: " + datetime.now().strftime("%d/%m/%Y %H:%M"), "",
         "Tipo: " + ("dirigido" if g.dirigido else "no dirigido"), "Nodos: %d" % g.n]
    if g.semilla is not None:
        L.append("Semilla: %s" % g.semilla)
    L += ["", "ARISTAS"]
    for (a, b, peso) in g.lista_aristas():
        L.append("  %d %s %d : %s km" % (a, flecha, b, num(peso)))
    L += ["", "MATRIZ DE COSTOS (0 = no hay arista)"]
    for fila in g.matriz:
        L.append("  " + " ".join("%4s" % num(x) for x in fila))
    L += ["", "CONDICIONES"]
    for (texto, cumple, detalle, malos) in g.condiciones():
        L.append("  [%s] %s: %s" % ("SÍ" if cumple else "NO", texto, detalle))
    L += ["", "RUTAS REVISADAS: %d" % len(rutas)]
    omitidas = 0
    for i in range(len(rutas)):
        costo, pesos, faltan = g.evaluar(rutas[i])
        texto = ruta_texto(rutas[i]).replace(" ", "")
        if not faltan:
            L.append("%7d  %s  CICLO  %s = %s" % (i + 1, texto, " + ".join(num(p) for p in pesos), num(costo)))
        elif len(rutas) <= 5040 or i < 300:
            L.append("%7d  %s  no es ciclo (falta %s)" % (i + 1, texto, ", ".join("%d%s%d" % (a, flecha, b) for a, b in faltan)))
        else:
            omitidas = omitidas + 1
    if omitidas:
        L.append("  ... %d rutas más que no son ciclo (se revisaron, pero no se listan)." % omitidas)
    L += ["", "RESULTADO"]
    if resultado["hay_ciclo"]:
        L.append("  Costo mínimo: %s km" % num(resultado["minimo"]))
        for i in resultado["opciones"]:
            L.append("  Ciclo óptimo: %s (ruta %d)" % (ruta_texto(rutas[i]), i + 1))
    else:
        L.append("  No existe ciclo hamiltoniano.")
        L.append("  Mínimo de aristas que faltan: %d" % resultado["minimo"])
        for op in resultado["opciones"]:
            L.append("  Opción: agregar " + ", ".join("%d%s%d" % (a, flecha, b) for a, b in op))
    return "\n".join(L) + "\n"


def archivo_zip(g, rutas, costos, resultado, elegido):
    tipo = "dirigido" if g.dirigido else "no dirigido"
    inicial = figura_png(figura(g, titulo="Grafo %s con %d nodos" % (tipo, g.n), blanco_y_negro=True))
    if resultado["hay_ciclo"]:
        ruta = rutas[resultado["opciones"][elegido]]
        costo, pesos, f = g.evaluar(ruta)
        final = figura_png(figura(g, ruta=ruta, titulo="Ciclo de costo mínimo: " + ruta_texto(ruta),
                                  pie="Costo = %s = %s km" % (" + ".join(num(p) for p in pesos), num(costo)),
                                  blanco_y_negro=True))
    else:
        op = resultado["opciones"][elegido]
        flecha = "->" if g.dirigido else "-"
        final = figura_png(figura(g, faltantes=op, titulo="No hay ciclo: aristas que faltan",
                                  pie="Agregar " + ", ".join("%d%s%d" % (a, flecha, b) for a, b in op),
                                  blanco_y_negro=True))
    carpeta = "TSP_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(carpeta + "/1_grafo_inicial.png", inicial)
        z.writestr(carpeta + "/2_resultado.png", final)
        z.writestr(carpeta + "/reporte.txt", reporte(g, rutas, costos, resultado))
        z.writestr(carpeta + "/grafo.json", json.dumps(g.a_diccionario(), indent=2))
    return carpeta + ".zip", buffer.getvalue()
