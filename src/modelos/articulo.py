class ArticuloWikipedia:
    """
    Modela un artículo de Wikipedia con sus categorías y enlaces asociados.

    Atributos:
        id_articulo (int): Identificador único del artículo.
        nombre (str): Nombre del artículo.
        categorias (set): Conjunto de categorías a las que pertenece.
        enlaces_salida (set): IDs de artículos a los que este artículo apunta.
        enlaces_entrada (set): IDs de artículos que apuntan a este artículo.
    """

    def __init__(self, id_articulo: int, nombre: str):
        self.id_articulo = id_articulo
        self.nombre = nombre
        self.categorias: set = set()
        self.enlaces_salida: set = set()
        self.enlaces_entrada: set = set()

    def agregar_categoria(self, categoria: str):
        """Asocia una categoría al artículo."""
        self.categorias.add(categoria)

    def agregar_enlace_salida(self, id_destino: int):
        """Registra un enlace que sale desde este artículo hacia otro."""
        self.enlaces_salida.add(id_destino)

    def agregar_enlace_entrada(self, id_origen: int):
        """Registra un enlace que llega a este artículo desde otro."""
        self.enlaces_entrada.add(id_origen)

    def grado_salida(self) -> int:
        """Retorna la cantidad de enlaces que salen de este artículo."""
        return len(self.enlaces_salida)

    def grado_entrada(self) -> int:
        """Retorna la cantidad de enlaces que apuntan hacia este artículo."""
        return len(self.enlaces_entrada)

    def __str__(self):
        return f"[{self.id_articulo}] {self.nombre}"

    def __repr__(self):
        return (
            f"ArticuloWikipedia(id={self.id_articulo}, nombre='{self.nombre}', "
            f"entrada={self.grado_entrada()}, salida={self.grado_salida()})"
        )
