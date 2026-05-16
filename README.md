# Wikipedia en Grafos — Programación Científica

Sistema en Python orientado a objetos para modelar y analizar la red de artículos de Wikipedia como un **grafo dirigido**. Implementa métricas estructurales, recorridos BFS/DFS y el algoritmo PageRank.

---

## Estructura del Proyecto

```
wiki_proyecto/
├── dataset/                       # Archivos del dataset (colocar aquí)
│   ├── wiki-topcats.mtx           # Aristas del grafo
│   ├── wiki-topcats_Categories.mtx
│   ├── wiki-topcats_Category_names.txt
│   └── wiki-topcats_pagenames.txt
├── results/                       # Archivos de salida generados automáticamente
├── src/
│   ├── main.py                    # Punto de entrada
│   ├── modelos/
│   │   ├── articulo.py            # Clase ArticuloWikipedia
│   │   └── grafo.py               # Clase GrafoWikipedia
│   ├── loaders/
│   │   └── cargador_wikipedia.py  # Carga y filtrado del dataset
│   └── utilidades/
│       └── reporte_basico.py      # Generación de reportes
└── README.md
```

---

## Requisitos

- Python 3.10 o superior
- Sin librerías externas obligatorias (usa solo la biblioteca estándar)

---

## Ejecución

```bash
cd src
python main.py
```

### Opciones de línea de comandos

| Argumento       | Default | Descripción                                         |
|-----------------|---------|-----------------------------------------------------|
| `--categorias`  | 50      | Número de categorías a incluir en el subconjunto    |
| `--iteraciones` | 50      | Iteraciones del algoritmo PageRank                  |
| `--damping`     | 0.85    | Factor de amortiguación de PageRank                 |
| `--origen`      | auto    | ID de nodo origen para BFS/DFS                      |
| `--destino`     | auto    | ID de nodo destino para búsqueda de camino          |

**Ejemplo con parámetros personalizados:**

```bash
python main.py --categorias 100 --iteraciones 100 --origen 302 --destino 500
```

---

## Criterio de Filtrado

El dataset completo (~1.79M nodos, ~28.5M aristas) se filtra así:

1. Se seleccionan las primeras **N categorías** (configurable con `--categorias`).
2. Se identifican todos los artículos que pertenecen a al menos una de esas categorías.
3. Solo se cargan aristas entre artículos del subconjunto.
4. Se aplica un cap de 500 aristas de salida por nodo para evitar hubs extremos.

Con 50 categorías se obtiene un grafo de ~5 000–20 000 nodos, manejable en memoria.

---

## Archivos Generados (carpeta `results/`)

| Archivo                    | Contenido                                              |
|----------------------------|--------------------------------------------------------|
| `reporte_basico.txt`       | Resumen del grafo y top 10 por grados de entrada/salida |
| `distribucion_grados.csv`  | Histograma de grados de entrada y salida               |
| `top_pagerank.csv`         | Top 50 artículos por puntaje PageRank                  |
| `analisis_categorias.txt`  | Top 5 artículos por PageRank para cada categoría       |

---

## Diseño Orientado a Objetos

```
ArticuloWikipedia
  - id_articulo, nombre, categorias
  - enlaces_salida, enlaces_entrada
  - grado_entrada(), grado_salida()

GrafoWikipedia
  - articulos: dict[int, ArticuloWikipedia]
  - agregar_articulo(), agregar_enlace()
  - bfs(), dfs(), encontrar_camino_simple()
  - pagerank(), top_pagerank()

CargadorWikipedia
  - cargar_grafo()  ← aplica filtrado por categorías

ReporteBasicoWikipedia
  - generar()           ← exporta todos los archivos
  - imprimir_en_consola()
```

---

## Algoritmo PageRank

Implementación iterativa con manejo de *dangling nodes*:

```
PR(u) = (1 - d) / N  +  d * Σ [ PR(v) / grado_salida(v) ]
                              v → u
```

Donde `d = 0.85` (por defecto) y los nodos sin salida distribuyen su puntaje uniformemente.
