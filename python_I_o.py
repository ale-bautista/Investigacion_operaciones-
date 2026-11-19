# ==============================================================================
# ACTIVIDAD INTEGRADORA: INVESTIGACIÓN DE OPERACIONES EN PYTHON
# Programa Educativo: Ingeniería en Computación
# Integrantes:
#   - Alejandra Bautista Ávila
#   - Omar Sánchez Valencia
# ==============================================================================

import networkx as nx
import pandas as pd
from scipy.optimize import linprog

print("Librerías cargadas correctamente.\n")


# ==============================================================================
# PRÁCTICA 1: ALGORITMO DE EXPANSIÓN MÍNIMA (PRIM)
# Conceptos:
#   - Nodo: punto de conexión en la red (servidor, laboratorio o edificio).
#   - Arista: enlace de fibra óptica que une dos nodos.
#   - Peso: costo de instalación del enlace (en miles de USD).
#   - Árbol de Expansión Mínima (MST): subgrafo que conecta todos los nodos sin
#     ciclos y con la suma mínima de costos.
# ==============================================================================
print("=" * 70)
print("PRÁCTICA 1: ÁRBOL DE EXPANSIÓN MÍNIMA (ALGORITMO DE PRIM)")
print("=" * 70)

nodos_p1 = [
    "N1_Core",
    "N2_Sur",
    "N3_Norte",
    "N4_Este",
    "N5_Oeste",
    "N6_Cloud",
    "N7_Lab",
    "N8_Campus",
]

arcos_p1 = [
    ("N1_Core", "N2_Sur", 120),
    ("N1_Core", "N3_Norte", 95),
    ("N1_Core", "N4_Este", 140),
    ("N2_Sur", "N3_Norte", 80),
    ("N2_Sur", "N5_Oeste", 110),
    ("N3_Norte", "N6_Cloud", 130),
    ("N3_Norte", "N7_Lab", 75),
    ("N4_Este", "N6_Cloud", 85),
    ("N4_Este", "N8_Campus", 105),
    ("N5_Oeste", "N7_Lab", 90),
    ("N5_Oeste", "N8_Campus", 150),
    ("N6_Cloud", "N7_Lab", 115),
    ("N7_Lab", "N8_Campus", 65),
]

G1 = nx.Graph()
G1.add_nodes_from(nodos_p1)
G1.add_weighted_edges_from(arcos_p1)

print(f"Total de nodos: {G1.number_of_nodes()} | Enlaces candidatos: {G1.number_of_edges()}")

visitados = {"N1_Core"}
aristas_mst = []
paso = 1

while len(visitados) < len(G1.nodes()):
    candidatas = [
        (u, v, d["weight"])
        for u, v, d in G1.edges(data=True)
        if (u in visitados) != (v in visitados)
    ]
    u_min, v_min, w_min = min(candidatas, key=lambda x: x[2])
    nuevo_nodo = v_min if u_min in visitados else u_min

    visitados.add(nuevo_nodo)
    aristas_mst.append((u_min, v_min, w_min))
    print(f"Paso {paso}: Se agrega ({u_min} -- {v_min}) | Costo = {w_min} mil USD")
    paso += 1

mst_nx = nx.minimum_spanning_tree(G1, algorithm="prim")
costo_total_p1 = sum(d["weight"] for _, _, d in mst_nx.edges(data=True))
print(f"\nCosto mínimo total del árbol (Prim): {costo_total_p1} mil USD\n")


# ==============================================================================
# PRÁCTICA 2: RUTA CRÍTICA (PERT / CPM)
# Conceptos:
#   - ES (Inicio Temprano) y EF (Fin Temprano): tiempos más próximos posibles.
#   - LS (Inicio Tardío) y LF (Fin Tardío): límites sin retrasar el proyecto.
#   - Holgura (LS - ES): margen de atraso permitido; si es 0, es ruta crítica.
# ==============================================================================
print("=" * 70)
print("PRÁCTICA 2: RUTA CRÍTICA (CPM)")
print("=" * 70)

actividades_p2 = {
    "A": {"desc": "Análisis y arquitectura", "dur": 4, "pred": []},
    "B": {"desc": "Provisión VPC y seguridad", "dur": 3, "pred": ["A"]},
    "C": {"desc": "Diseño base de datos", "dur": 5, "pred": ["A"]},
    "D": {"desc": "Pipeline CI/CD", "dur": 3, "pred": ["B"]},
    "E": {"desc": "Microservicios auth", "dur": 6, "pred": ["B", "C"]},
    "F": {"desc": "Migración y seeds BD", "dur": 4, "pred": ["C"]},
    "G": {"desc": "Pruebas integración API", "dur": 5, "pred": ["D", "E"]},
    "H": {"desc": "Tuning y respaldo BD", "dur": 3, "pred": ["F"]},
    "I": {"desc": "Auditoría seguridad/carga", "dur": 4, "pred": ["G", "H"]},
    "J": {"desc": "Pase a prod y monitoreo", "dur": 2, "pred": ["I"]},
}

orden = list(actividades_p2.keys())

ES, EF = {}, {}
for act in orden:
    ES[act] = max((EF[p] for p in actividades_p2[act]["pred"]), default=0)
    EF[act] = ES[act] + actividades_p2[act]["dur"]

duracion_total = max(EF.values())

LS, LF = {}, {}
for act in reversed(orden):
    sucesoras = [x for x in orden if act in actividades_p2[x]["pred"]]
    LF[act] = min((LS[s] for s in sucesoras), default=duracion_total)
    LS[act] = LF[act] - actividades_p2[act]["dur"]

filas_cpm = []
for act in orden:
    holgura = LS[act] - ES[act]
    filas_cpm.append(
        {
            "Actividad": act,
            "Descripción": actividades_p2[act]["desc"],
            "Duración": actividades_p2[act]["dur"],
            "ES": ES[act],
            "EF": EF[act],
            "LS": LS[act],
            "LF": LF[act],
            "Holgura": holgura,
            "Crítica": "SÍ" if holgura == 0 else "NO",
        }
    )

tabla_cpm = pd.DataFrame(filas_cpm)
print(tabla_cpm.to_string(index=False))

ruta_critica = [act for act in orden if (LS[act] - ES[act]) == 0]
print("\nRuta crítica:", " -> ".join(ruta_critica))
print(f"Duración total del proyecto: {duracion_total} días\n")


# ==============================================================================
# PRÁCTICA 3: ALGORITMO DE DIJKSTRA
# Conceptos:
#   - Relajación de distancias: actualizar la distancia acumulada hacia un nodo
#     vecino cuando se encuentra un camino con menor latencia que el conocido.
# ==============================================================================
print("=" * 70)
print("PRÁCTICA 3: ALGORITMO DE DIJKSTRA (RUTA DE MÍNIMA LATENCIA)")
print("=" * 70)

nodos_p3 = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
arcos_p3 = [
    ("R1", "R2", 8),
    ("R1", "R3", 14),
    ("R2", "R3", 4),
    ("R2", "R4", 15),
    ("R3", "R5", 9),
    ("R3", "R6", 18),
    ("R4", "R6", 6),
    ("R4", "R7", 12),
    ("R5", "R6", 5),
    ("R5", "R8", 16),
    ("R6", "R7", 3),
    ("R6", "R8", 10),
    ("R7", "R8", 7),
]

G3 = nx.Graph()
G3.add_nodes_from(nodos_p3)
G3.add_weighted_edges_from(arcos_p3)

origen, destino = "R1", "R8"
distancias = {n: float("inf") for n in G3.nodes()}
distancias[origen] = 0
previos = {n: None for n in G3.nodes()}
no_visitados = set(G3.nodes())
iteracion = 1

while no_visitados:
    actual = min(no_visitados, key=lambda n: distancias[n])
    no_visitados.remove(actual)

    for vecino in G3.neighbors(actual):
        peso = G3[actual][vecino]["weight"]
        nueva_dist = distancias[actual] + peso
        if nueva_dist < distancias[vecino]:
            distancias[vecino] = nueva_dist
            previos[vecino] = actual

    print(f"Iteración {iteracion} (visitando {actual}): {distancias}")
    iteracion += 1

camino = []
nodo_actual = destino
while nodo_actual is not None:
    camino.append(nodo_actual)
    nodo_actual = previos[nodo_actual]
camino.reverse()

latencia_nx = nx.dijkstra_path_length(G3, origen, destino, weight="weight")
print(f"\nRuta óptima ({origen} -> {destino}): {' -> '.join(camino)}")
print(f"Latencia total mínima: {distancias[destino]} ms (Validación NetworkX: {latencia_nx} ms)\n")


# ==============================================================================
# PRÁCTICA 4: PROGRAMACIÓN LINEAL
# Conceptos:
#   - Variables de decisión (x1, x2): cantidades a determinar.
#   - Función objetivo (Z): expresión lineal a maximizar o minimizar.
#   - Restricciones: límites físicos de RAM, ancho de banda y cuota máxima.
# ==============================================================================
print("=" * 70)
print("PRÁCTICA 4: PROGRAMACIÓN LINEAL (ASIGNACIÓN DE CAPACIDAD vCPU)")
print("=" * 70)

c = [-45.0, -30.0]
A_ub = [
    [4.0, 2.0],
    [2.0, 3.0],
    [1.0, 0.0],
]
b_ub = [60.0, 48.0, 12.0]
limites = [(0, None), (0, None)]

resultado = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=limites, method="highs")

x1_opt, x2_opt = resultado.x
z_opt = -resultado.fun

print(f"Estado del solver: {resultado.message}")
print(f"x1* (Horas-vCPU Análisis de Datos): {x1_opt:.2f} mil horas")
print(f"x2* (Horas-vCPU Servicios Web):     {x2_opt:.2f} mil horas")
print(f"Ganancia máxima total (Z*):         ${z_opt:.2f} USD")

ram_usada = 4 * x1_opt + 2 * x2_opt
red_usada = 2 * x1_opt + 3 * x2_opt
print(f"\nConsumo de RAM: {ram_usada:.1f} / 60.0 GB-h (Holgura: {60.0 - ram_usada:.1f})")
print(f"Consumo de Red: {red_usada:.1f} / 48.0 Gbps (Holgura: {48.0 - red_usada:.1f})")
print(f"Cuota Análisis: {x1_opt:.1f} / 12.0 mil h (Holgura: {12.0 - x1_opt:.1f})")