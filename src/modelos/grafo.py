from collections import deque

from modelos.articulo import ArticuloWikipedia


class GrafoWikipedia:
    """
    Representa un grafo dirigido de artículos de Wikipedia y sus enlaces.

    Internamente almacena un diccionario {id_articulo: ArticuloWikipedia}.
    Todas las operaciones estructurales se delegan a los objetos ArticuloWikipedia,
    lo que mantiene una responsabilidad única por clase.
    """

    def __init__(self):
        # Diccionario principal: id_articulo -> ArticuloWikipedia
        self.articulos: dict[int, ArticuloWikipedia] = {}

    # ─────────────────────────────────────────────────
    # Construcción del grafo
    # ─────────────────────────────────────────────────

    def agregar_articulo(self, id_articulo: int, nombre: str):
        """Agrega un nodo al grafo si no existe todavía."""
        if id_articulo not in self.articulos:
            self.articulos[id_articulo] = ArticuloWikipedia(id_articulo, nombre)

    def obtener_articulo(self, id_articulo: int):
        """Retorna el ArticuloWikipedia con el id dado, o None si no existe."""
        return self.articulos.get(id_articulo)

    def agregar_enlace(self, id_origen: int, id_destino: int):
        """
        Agrega una arista dirigida origen → destino.
        Ignora self-loops y enlaces a nodos que no están en el grafo.
        """
        if id_origen == id_destino:
            return
        if id_origen not in self.articulos or id_destino not in self.articulos:
            return

        self.articulos[id_origen].agregar_enlace_salida(id_destino)
        self.articulos[id_destino].agregar_enlace_entrada(id_origen)

    # ─────────────────────────────────────────────────
    # Métricas básicas
    # ─────────────────────────────────────────────────

    def cantidad_articulos(self) -> int:
        """Número total de nodos en el grafo."""
        return len(self.articulos)

    def cantidad_enlaces(self) -> int:
        """Número total de aristas en el grafo (suma de grados de salida)."""
        return sum(a.grado_salida() for a in self.articulos.values())

    def top_por_grado_entrada(self, cantidad: int = 10) -> list:
        """Retorna los artículos con mayor grado de entrada (más referenciados)."""
        return sorted(
            self.articulos.values(),
            key=lambda a: a.grado_entrada(),
            reverse=True
        )[:cantidad]

    def top_por_grado_salida(self, cantidad: int = 10) -> list:
        """Retorna los artículos con mayor grado de salida (más enlazadores)."""
        return sorted(
            self.articulos.values(),
            key=lambda a: a.grado_salida(),
            reverse=True
        )[:cantidad]

    def distribucion_grados(self) -> dict:
        """
        Calcula la distribución de grados de entrada y salida.
        Retorna un dict con listas de frecuencias agrupadas.
        """
        from collections import Counter
        entrada_counter = Counter(a.grado_entrada() for a in self.articulos.values())
        salida_counter = Counter(a.grado_salida() for a in self.articulos.values())
        return {
            "entrada": dict(sorted(entrada_counter.items())),
            "salida":  dict(sorted(salida_counter.items())),
        }

    def resumen(self) -> dict:
        """Retorna un diccionario con las métricas principales del grafo."""
        grados_entrada = [a.grado_entrada() for a in self.articulos.values()]
        grados_salida  = [a.grado_salida()  for a in self.articulos.values()]

        n = self.cantidad_articulos()
        promedio_entrada = sum(grados_entrada) / n if n else 0
        promedio_salida  = sum(grados_salida)  / n if n else 0

        nodos_sin_salida  = sum(1 for g in grados_salida  if g == 0)
        nodos_sin_entrada = sum(1 for g in grados_entrada if g == 0)

        return {
            "articulos":          n,
            "enlaces":            self.cantidad_enlaces(),
            "promedio_entrada":   round(promedio_entrada, 2),
            "promedio_salida":    round(promedio_salida, 2),
            "max_grado_entrada":  max(grados_entrada, default=0),
            "max_grado_salida":   max(grados_salida,  default=0),
            "nodos_sin_salida":   nodos_sin_salida,
            "nodos_sin_entrada":  nodos_sin_entrada,
        }

    # ─────────────────────────────────────────────────
    # Recorridos
    # ─────────────────────────────────────────────────

    def bfs(self, id_inicio: int) -> list:
        """
        Recorrido BFS desde un nodo origen.
        Retorna la lista de IDs visitados en orden BFS.
        """
        if id_inicio not in self.articulos:
            return []

        visitados = {id_inicio}
        cola = deque([id_inicio])
        recorrido = []

        while cola:
            actual = cola.popleft()
            recorrido.append(actual)

            for vecino in self.articulos[actual].enlaces_salida:
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append(vecino)

        return recorrido

    def dfs(self, id_inicio: int) -> list:
        """
        Recorrido DFS iterativo desde un nodo origen.
        Retorna la lista de IDs visitados en orden DFS.
        """
        if id_inicio not in self.articulos:
            return []

        visitados = set()
        pila = [id_inicio]
        recorrido = []

        while pila:
            actual = pila.pop()

            if actual in visitados:
                continue

            visitados.add(actual)
            recorrido.append(actual)

            # Invertimos para mantener orden natural de visita
            vecinos = sorted(self.articulos[actual].enlaces_salida, reverse=True)
            for vecino in vecinos:
                if vecino not in visitados:
                    pila.append(vecino)

        return recorrido

    def encontrar_camino_simple(self, id_origen: int, id_destino: int) -> list:
        """
        Busca el camino más corto entre dos nodos usando BFS.
        Retorna la lista de IDs del camino, o [] si no existe.
        """
        if id_origen not in self.articulos or id_destino not in self.articulos:
            return []

        cola = deque([id_origen])
        padres: dict[int, int | None] = {id_origen: None}

        while cola:
            actual = cola.popleft()

            if actual == id_destino:
                break

            for vecino in self.articulos[actual].enlaces_salida:
                if vecino not in padres:
                    padres[vecino] = actual
                    cola.append(vecino)

        if id_destino not in padres:
            return []

        # Reconstruir camino
        camino = []
        actual = id_destino
        while actual is not None:
            camino.append(actual)
            actual = padres[actual]

        camino.reverse()
        return camino

    # ─────────────────────────────────────────────────
    # PageRank
    # ─────────────────────────────────────────────────

    def pagerank(self, iteraciones: int = 50, damping: float = 0.85) -> dict:
        """
        Implementación del algoritmo PageRank simplificado.

        Fórmula:
            PR(u) = (1 - d) / N  +  d * Σ [ PR(v) / grado_salida(v) ]
                                      v → u

        Donde:
            d = factor de amortiguación (damping)
            N = número total de nodos
            v → u = todos los nodos que enlazan hacia u

        Los nodos sin salida (dangling nodes) distribuyen su puntaje
        uniformemente entre todos los nodos para evitar sumideros de probabilidad.

        Args:
            iteraciones: Número de iteraciones del algoritmo.
            damping:     Factor de amortiguación (típicamente 0.85).

        Returns:
            Diccionario {id_articulo: puntaje_pagerank}.
        """
        n = self.cantidad_articulos()
        if n == 0:
            return {}

        # Inicializar con distribución uniforme
        puntajes = {nid: 1.0 / n for nid in self.articulos}

        for _ in range(iteraciones):
            nuevos_puntajes = {}

            # Aporte de dangling nodes (sin enlaces de salida)
            suma_dangling = sum(
                puntajes[nid]
                for nid, art in self.articulos.items()
                if art.grado_salida() == 0
            )
            aporte_dangling = damping * suma_dangling / n

            # Calcular nuevo puntaje para cada nodo
            for nid in self.articulos:
                nuevos_puntajes[nid] = (1.0 - damping) / n + aporte_dangling

            # Propagar puntajes a través de los enlaces
            for nid, articulo in self.articulos.items():
                gs = articulo.grado_salida()
                if gs == 0:
                    continue
                aporte = damping * puntajes[nid] / gs
                for vecino in articulo.enlaces_salida:
                    if vecino in nuevos_puntajes:
                        nuevos_puntajes[vecino] += aporte

            puntajes = nuevos_puntajes

        return puntajes

    def top_pagerank(self, puntajes: dict, cantidad: int = 10) -> list:
        """
        Retorna los `cantidad` artículos con mayor puntaje PageRank.

        Args:
            puntajes: Diccionario {id: puntaje} retornado por pagerank().
            cantidad: Cuántos artículos incluir en el top.

        Returns:
            Lista de tuplas (ArticuloWikipedia, puntaje) ordenada de mayor a menor.
        """
        items = [
            (self.articulos[nid], score)
            for nid, score in puntajes.items()
            if nid in self.articulos
        ]
        items.sort(key=lambda x: x[1], reverse=True)
        return items[:cantidad]
