"""
Nombres de los integrantes del grupo:
- Paulette Bauer - 21.574.385-3
- Valentina Vergara - 21.833.059-2
- María Salas - 21.591.568-9
main.py — Punto de entrada del sistema de análisis de Wikipedia.

Ejecutar desde ambiente personalizado conda src/:
    python main.py


"""

import argparse
import sys
from pathlib import Path

# Asegurar que los módulos locales sean encontrables
sys.path.insert(0, str(Path(__file__).parent))

from loaders.cargador_wikipedia import CargadorWikipedia
from utilidades.reporte_basico import ReporteBasicoWikipedia


def parsear_argumentos():
    parser = argparse.ArgumentParser(
        description="Análisis de la red de artículos de Wikipedia"
    )
    parser.add_argument(
        "--categorias", type=int, default=50,
        help="Número de categorías a incluir en el subconjunto (default: 50)"
    )
    parser.add_argument(
        "--iteraciones", type=int, default=50,
        help="Iteraciones del algoritmo PageRank (default: 50)"
    )
    parser.add_argument(
        "--damping", type=float, default=0.85,
        help="Factor de amortiguación de PageRank (default: 0.85)"
    )
    parser.add_argument(
        "--origen", type=int, default=None,
        help="ID del nodo origen para BFS/DFS y camino simple"
    )
    parser.add_argument(
        "--destino", type=int, default=None,
        help="ID del nodo destino para camino simple"
    )
    return parser.parse_args()


def demostrar_recorridos(grafo, id_origen: int | None, id_destino: int | None):
    """Ejecuta BFS, DFS y búsqueda de camino entre nodos de ejemplo."""
    ids = list(grafo.articulos.keys())
    if not ids:
        return

    # Elegir nodos de ejemplo si no se especificaron
    origen = id_origen if id_origen in grafo.articulos else ids[0]
    destino = id_destino if id_destino in grafo.articulos else (
        ids[min(100, len(ids) - 1)]
    )

    art_origen  = grafo.obtener_articulo(origen)
    art_destino = grafo.obtener_articulo(destino)

    print(f"\n{'─'*60}")
    print("RECORRIDOS DEL GRAFO")
    print(f"{'─'*60}")
    print(f"Nodo origen : {art_origen}")
    print(f"Nodo destino: {art_destino}")

    # BFS
    bfs_resultado = grafo.bfs(origen)
    print(f"\nBFS desde '{art_origen.nombre}':")
    print(f"  Nodos alcanzables: {len(bfs_resultado):,}")
    primeros = [grafo.obtener_articulo(i).nombre for i in bfs_resultado[:5]]
    print(f"  Primeros 5: {primeros}")

    # DFS
    dfs_resultado = grafo.dfs(origen)
    print(f"\nDFS desde '{art_origen.nombre}':")
    print(f"  Nodos alcanzables: {len(dfs_resultado):,}")
    primeros = [grafo.obtener_articulo(i).nombre for i in dfs_resultado[:5]]
    print(f"  Primeros 5: {primeros}")

    # Camino simple
    camino = grafo.encontrar_camino_simple(origen, destino)
    print(f"\nCamino más corto: '{art_origen.nombre}' → '{art_destino.nombre}'")
    if camino:
        nombres_camino = [grafo.obtener_articulo(i).nombre for i in camino]
        print(f"  Longitud: {len(camino) - 1} saltos")
        print(f"  Ruta: {' → '.join(nombres_camino)}")
    else:
        print("  No existe camino entre estos nodos en el subgrafo.")


def main():
    args = parsear_argumentos()

    # ── 1. Cargar datos ───────────────────────────────────────────────────
    CargadorWikipedia.MAX_CATEGORIAS = args.categorias

    print("=" * 60)
    print("  SISTEMA DE ANÁLISIS DE RED DE WIKIPEDIA")
    print("=" * 60)

    cargador = CargadorWikipedia()
    grafo = cargador.cargar_grafo()

    # ── 2. Métricas básicas y recorridos ──────────────────────────────────
    reporte = ReporteBasicoWikipedia()
    reporte.imprimir_en_consola(grafo)

    demostrar_recorridos(grafo, args.origen, args.destino)

    # ── 3. PageRank ───────────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"Calculando PageRank ({args.iteraciones} iteraciones, d={args.damping})...")
    puntajes = grafo.pagerank(iteraciones=args.iteraciones, damping=args.damping)
    print("PageRank calculado.")

    reporte.imprimir_en_consola(grafo, puntajes_pagerank=puntajes)

    # ── 4. Exportar resultados ────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print("Exportando archivos de resultados...")
    archivos = reporte.generar(grafo, puntajes_pagerank=puntajes)

    print("\nArchivos generados:")
    for nombre, ruta in archivos.items():
        print(f"  [{nombre}] {ruta}")

    print(f"\n{'═'*60}")
    print("  Análisis completado exitosamente.")
    print(f"{'═'*60}\n")


if __name__ == "__main__":
    main()
