from pathlib import Path

from modelos.grafo import GrafoWikipedia


class CargadorWikipedia:
    """
    Carga desde el dataset los datos necesarios para construir el grafo de Wikipedia.

    Criterio de filtrado aplicado
    ──────────────────────────────
    El dataset completo tiene ~1.79 millones de artículos y ~28.5 millones de
    aristas, lo que supera la memoria práctica para un análisis interactivo.

    Estrategia elegida: **subgrafo por categorías**.
    Se seleccionan las primeras MAX_CATEGORIAS categorías (ordenadas por ID),
    se identifican todos los artículos que pertenecen al menos a una de ellas,
    y luego se carga únicamente el subconjunto de aristas entre esos artículos.

    Esto garantiza:
    - Nodos conectados semánticamente (mismas temáticas).
    - Tamaño manejable (~30 000–80 000 nodos según MAX_CATEGORIAS).
    - Estructura de grafo real, no un muestreo aleatorio.
    """

    # ── Parámetros de filtrado ─────────────────────────────────────────────
    MAX_CATEGORIAS = 50          # Cuántas categorías incluir
    MAX_ENLACES_POR_NODO = 500   # Cap de aristas por nodo (evita hubs extremos)
    # ──────────────────────────────────────────────────────────────────────

    def __init__(self, ruta_dataset: str | None = None):
        if ruta_dataset is None:
            self.ruta_dataset = Path(__file__).resolve().parent.parent.parent / "dataset"
        else:
            self.ruta_dataset = Path(ruta_dataset)

    # ─────────────────────────────────────────────────
    # Loaders individuales
    # ─────────────────────────────────────────────────

    def cargar_nombres_articulos(self) -> dict[int, str]:
        """
        Lee wiki-topcats_pagenames.txt.
        Cada línea i (base 1) corresponde al artículo con id i.
        """
        ruta = self.ruta_dataset / "wiki-topcats_pagenames.txt"
        nombres: dict[int, str] = {}

        with open(ruta, "r", encoding="utf-8") as f:
            for indice, linea in enumerate(f, start=1):
                nombres[indice] = linea.strip()

        return nombres

    def cargar_nombres_categorias(self) -> dict[int, str]:
        """
        Lee wiki-topcats_Category_names.txt.
        Cada línea i (base 1) corresponde a la categoría con id i.
        """
        ruta = self.ruta_dataset / "wiki-topcats_Category_names.txt"
        categorias: dict[int, str] = {}

        with open(ruta, "r", encoding="utf-8") as f:
            for indice, linea in enumerate(f, start=1):
                categorias[indice] = linea.strip()

        return categorias

    def _leer_matriz_market(self, ruta_archivo: Path):
        """
        Generador que parsea un archivo Matrix Market (formato .mtx).
        Omite cabeceras (líneas con %) y la línea de dimensiones (3 tokens).
        Produce pares (fila, columna) como enteros.
        """
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("%"):
                    continue
                partes = linea.split()
                if len(partes) == 3:
                    # Línea de dimensiones: "filas columnas nnz"
                    continue
                if len(partes) >= 2:
                    yield int(partes[0]), int(partes[1])

    # ─────────────────────────────────────────────────
    # Construcción del grafo con filtrado
    # ─────────────────────────────────────────────────

    def cargar_grafo(self) -> GrafoWikipedia:
        """
        Carga y construye el grafo aplicando el filtrado por categorías.

        Pasos:
        1. Cargar nombres de artículos y categorías.
        2. Seleccionar las primeras MAX_CATEGORIAS categorías.
        3. Identificar qué artículos pertenecen a esas categorías.
        4. Agregar esos artículos como nodos al grafo.
        5. Asociar las categorías a cada nodo.
        6. Cargar aristas solo entre nodos presentes, con cap por nodo.
        """
        print("Cargando nombres de artículos...")
        nombres = self.cargar_nombres_articulos()

        print("Cargando nombres de categorías...")
        categorias_nombres = self.cargar_nombres_categorias()

        # ── Paso 2: seleccionar categorías objetivo ───────────────────────
        ids_categorias_objetivo = set(
            sorted(categorias_nombres.keys())[:self.MAX_CATEGORIAS]
        )
        print(f"Categorías seleccionadas: {len(ids_categorias_objetivo)}")

        # ── Paso 3: artículos en esas categorías ──────────────────────────
        # wiki-topcats_Categories.mtx: (id_articulo, id_categoria)
        print("Identificando artículos por categoría...")
        articulos_seleccionados: dict[int, set[str]] = {}  # id → set de nombres de cat.

        ruta_cat = self.ruta_dataset / "wiki-topcats_Categories.mtx"
        for id_articulo, id_categoria in self._leer_matriz_market(ruta_cat):
            if id_categoria in ids_categorias_objetivo:
                if id_articulo not in articulos_seleccionados:
                    articulos_seleccionados[id_articulo] = set()
                nombre_cat = categorias_nombres.get(id_categoria, f"cat_{id_categoria}")
                articulos_seleccionados[id_articulo].add(nombre_cat)

        print(f"Artículos en subconjunto: {len(articulos_seleccionados)}")

        # ── Paso 4 y 5: crear nodos y asociar categorías ──────────────────
        grafo = GrafoWikipedia()
        for id_art, cats in articulos_seleccionados.items():
            nombre = nombres.get(id_art, f"articulo_{id_art}")
            grafo.agregar_articulo(id_art, nombre)
            articulo = grafo.obtener_articulo(id_art)
            for cat in cats:
                articulo.agregar_categoria(cat)

        # ── Paso 6: cargar aristas ────────────────────────────────────────
        print("Cargando aristas del subconjunto...")
        ruta_enlaces = self.ruta_dataset / "wiki-topcats.mtx"
        conteo_salida: dict[int, int] = {}

        for origen, destino in self._leer_matriz_market(ruta_enlaces):
            if origen not in articulos_seleccionados:
                continue
            if destino not in articulos_seleccionados:
                continue
            # Cap de aristas por nodo para evitar hubs extremos
            conteo_salida.setdefault(origen, 0)
            if conteo_salida[origen] >= self.MAX_ENLACES_POR_NODO:
                continue
            grafo.agregar_enlace(origen, destino)
            conteo_salida[origen] += 1

        print(f"Grafo listo: {grafo.cantidad_articulos()} nodos, "
              f"{grafo.cantidad_enlaces()} aristas.")

        return grafo
