from pathlib import Path
import csv


class ReporteBasicoWikipedia:
    """
    Genera reportes del grafo de Wikipedia y los exporta a la carpeta de resultados.

    Archivos generados:
    - reporte_basico.txt     : resumen general y top 10 por grados.
    - top_pagerank.csv       : ranking completo de PageRank.
    - distribucion_grados.csv: histograma de grados de entrada y salida.
    - analisis_categorias.txt: artículos top por categoría.
    """

    def __init__(self, carpeta_resultados: str | None = None):
        if carpeta_resultados is None:
            self.carpeta_resultados = (
                Path(__file__).resolve().parent.parent.parent / "results"
            )
        else:
            self.carpeta_resultados = Path(carpeta_resultados)

    # ─────────────────────────────────────────────────
    # Punto de entrada principal
    # ─────────────────────────────────────────────────

    def generar(self, grafo, puntajes_pagerank: dict | None = None) -> dict:
        """
        Genera todos los archivos de reporte.

        Args:
            grafo: GrafoWikipedia ya construido.
            puntajes_pagerank: dict {id: score}; si es None no se exporta PageRank.

        Returns:
            Diccionario con rutas de los archivos generados.
        """
        self.carpeta_resultados.mkdir(parents=True, exist_ok=True)

        resumen = grafo.resumen()
        top_entrada = grafo.top_por_grado_entrada(10)
        top_salida  = grafo.top_por_grado_salida(10)

        # ── Reporte de texto ──────────────────────────────────────────────
        ruta_txt = self.carpeta_resultados / "reporte_basico.txt"
        self._exportar_texto(ruta_txt, resumen, top_entrada, top_salida)

        archivos = {"reporte": ruta_txt}

        # ── Distribución de grados ────────────────────────────────────────
        ruta_dist = self.carpeta_resultados / "distribucion_grados.csv"
        self._exportar_distribucion(ruta_dist, grafo)
        archivos["distribucion"] = ruta_dist

        # ── PageRank ──────────────────────────────────────────────────────
        if puntajes_pagerank is not None:
            top_pr = grafo.top_pagerank(puntajes_pagerank, cantidad=50)
            ruta_pr = self.carpeta_resultados / "top_pagerank.csv"
            self._exportar_pagerank(ruta_pr, top_pr)
            archivos["pagerank"] = ruta_pr

            ruta_cat = self.carpeta_resultados / "analisis_categorias.txt"
            self._exportar_analisis_categorias(ruta_cat, grafo, puntajes_pagerank)
            archivos["categorias"] = ruta_cat

        return archivos

    # ─────────────────────────────────────────────────
    # Salida en consola
    # ─────────────────────────────────────────────────

    def imprimir_en_consola(self, grafo, puntajes_pagerank: dict | None = None):
        """Muestra un resumen completo del grafo en la consola."""
        resumen = grafo.resumen()

        print("\n" + "═" * 60)
        print("  RESUMEN DEL GRAFO DE WIKIPEDIA")
        print("═" * 60)
        print(f"  Artículos (nodos)  : {resumen['articulos']:,}")
        print(f"  Enlaces (aristas)  : {resumen['enlaces']:,}")
        print(f"  Grado entrada prom.: {resumen['promedio_entrada']}")
        print(f"  Grado salida prom. : {resumen['promedio_salida']}")
        print(f"  Máx grado entrada  : {resumen['max_grado_entrada']}")
        print(f"  Máx grado salida   : {resumen['max_grado_salida']}")
        print(f"  Nodos sin salida   : {resumen['nodos_sin_salida']:,}")
        print(f"  Nodos sin entrada  : {resumen['nodos_sin_entrada']:,}")
        print("═" * 60)

        self._imprimir_top(
            "Top 10 por GRADO DE ENTRADA (más referenciados)",
            grafo.top_por_grado_entrada(10),
            "entrada"
        )
        self._imprimir_top(
            "Top 10 por GRADO DE SALIDA (más enlazadores)",
            grafo.top_por_grado_salida(10),
            "salida"
        )

        if puntajes_pagerank:
            top_pr = grafo.top_pagerank(puntajes_pagerank, 10)
            print(f"\n{'─'*60}")
            print("Top 10 por PAGERANK")
            print(f"{'─'*60}")
            for pos, (art, score) in enumerate(top_pr, start=1):
                cats = ", ".join(list(art.categorias)[:3]) if art.categorias else "—"
                print(f"  {pos:2}. {art.nombre:<40} PR={score:.6f}  [{cats}]")

    # ─────────────────────────────────────────────────
    # Exportadores de archivo
    # ─────────────────────────────────────────────────

    def _exportar_texto(self, ruta, resumen, top_entrada, top_salida):
        lineas = [
            "=" * 60,
            "REPORTE BÁSICO - RED DE WIKIPEDIA",
            "=" * 60,
            "",
            "── RESUMEN GENERAL ──────────────────────────────────────",
            f"Artículos (nodos)   : {resumen['articulos']:,}",
            f"Enlaces (aristas)   : {resumen['enlaces']:,}",
            f"Grado entrada prom. : {resumen['promedio_entrada']}",
            f"Grado salida prom.  : {resumen['promedio_salida']}",
            f"Máx grado entrada   : {resumen['max_grado_entrada']}",
            f"Máx grado salida    : {resumen['max_grado_salida']}",
            f"Nodos sin salida    : {resumen['nodos_sin_salida']:,}",
            f"Nodos sin entrada   : {resumen['nodos_sin_entrada']:,}",
            "",
            "── TOP 10 POR GRADO DE ENTRADA ──────────────────────────",
        ]
        for i, art in enumerate(top_entrada, 1):
            cats = ", ".join(list(art.categorias)[:2]) if art.categorias else "—"
            lineas.append(f"  {i:2}. {art.nombre:<45} in={art.grado_entrada():>5}  [{cats}]")

        lineas += ["", "── TOP 10 POR GRADO DE SALIDA ───────────────────────────"]
        for i, art in enumerate(top_salida, 1):
            cats = ", ".join(list(art.categorias)[:2]) if art.categorias else "—"
            lineas.append(f"  {i:2}. {art.nombre:<45} out={art.grado_salida():>5}  [{cats}]")

        lineas.append("")
        ruta.write_text("\n".join(lineas), encoding="utf-8")

    def _exportar_distribucion(self, ruta, grafo):
        dist = grafo.distribucion_grados()
        todos_grados = sorted(
            set(dist["entrada"]) | set(dist["salida"])
        )
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["grado", "frecuencia_entrada", "frecuencia_salida"])
            for g in todos_grados:
                writer.writerow([g, dist["entrada"].get(g, 0), dist["salida"].get(g, 0)])

    def _exportar_pagerank(self, ruta, top_pr: list):
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["posicion", "id", "nombre", "pagerank", "grado_entrada",
                             "grado_salida", "categorias"])
            for pos, (art, score) in enumerate(top_pr, 1):
                cats = "|".join(sorted(art.categorias))
                writer.writerow([pos, art.id_articulo, art.nombre,
                                 f"{score:.8f}", art.grado_entrada(),
                                 art.grado_salida(), cats])

    def _exportar_analisis_categorias(self, ruta, grafo, puntajes: dict):
        """Agrupa los artículos de mayor PageRank por categoría."""
        from collections import defaultdict

        por_categoria: dict[str, list] = defaultdict(list)
        for nid, art in grafo.articulos.items():
            score = puntajes.get(nid, 0)
            for cat in art.categorias:
                por_categoria[cat].append((art, score))

        lineas = [
            "=" * 60,
            "ANÁLISIS POR CATEGORÍA (Top 5 por PageRank)",
            "=" * 60,
        ]
        for cat in sorted(por_categoria):
            top = sorted(por_categoria[cat], key=lambda x: x[1], reverse=True)[:5]
            lineas.append(f"\n[{cat}]")
            for pos, (art, score) in enumerate(top, 1):
                lineas.append(f"  {pos}. {art.nombre} (PR={score:.6f}, "
                              f"in={art.grado_entrada()}, out={art.grado_salida()})")

        ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")

    # ─────────────────────────────────────────────────
    # Helpers privados
    # ─────────────────────────────────────────────────

    def _imprimir_top(self, titulo, articulos, tipo_grado):
        print(f"\n{'─'*60}")
        print(titulo)
        print(f"{'─'*60}")
        for pos, art in enumerate(articulos, 1):
            valor = art.grado_entrada() if tipo_grado == "entrada" else art.grado_salida()
            cats = ", ".join(list(art.categorias)[:2]) if art.categorias else "—"
            print(f"  {pos:2}. {art.nombre:<45} {valor:>5}  [{cats}]")
