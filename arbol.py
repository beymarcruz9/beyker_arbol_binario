"""
================================================================================
VISUALIZADOR INTERACTIVO DE ÁRBOLES BINARIOS Y N-ARIOS EN PYTHON
================================================================================
Características:
  - Soporte para Árbol Binario (ABB / BST) y Árboles N-arios (2, 3, 4... ramas por nodo).
  - Configuración dinámica de la cantidad de ramas o hijos máximos.
  - Inserción automática (balanceada / BST) o inserción manual seleccionando el nodo padre.
  - Generador de árboles completos con N ramas y cantidad configurable de nodos.
  - Recorridos animados paso a paso: Preorden (RID), Inorden (IRD), Postorden (IDR) y Por Niveles (BFS).
  - Controles de reproducción: Reproducir, Pausar, Siguiente Paso (clic a clic), Reiniciar y Velocidad.
  - Interacción directa en el Canvas: Clic para seleccionar nodo, ver detalles, recorrer subárbol,
    ver ruta a la raíz o agregar hijos a esa rama específica.
  - Búsqueda interactiva con iluminación del camino paso a paso.
  - Eliminación de nodos y limpieza de árbol.
  - Navegación con Zoom y Arrastre (Pan) con el ratón.
================================================================================
"""

import collections
import math
import random
import tkinter as tk
from tkinter import messagebox, ttk


class TreeNode:
    """Representa un nodo en el árbol (soporta binario y N-ario)."""
    _id_counter = 0

    def __init__(self, value, max_children=2):
        self.id = TreeNode._id_counter
        TreeNode._id_counter += 1
        self.value = value
        self.max_children = max_children  # None = ilimitado
        self.children = []  # Lista de nodos hijos (para N-ario)
        self.left = None    # Para árbol binario explícito
        self.right = None   # Para árbol binario explícito
        self.parent = None
        self.depth = 0
        self.unit_x = 0
        self.x = 0
        self.y = 0

    def get_children(self):
        """Retorna la lista de hijos reales del nodo."""
        if self.max_children == 2:
            res = []
            if self.left is not None:
                res.append(self.left)
            if self.right is not None:
                res.append(self.right)
            return res
        return self.children

    def add_child(self, child_node, branch_index=None):
        """Agrega un hijo respetando el límite de ramas/hijos."""
        child_node.parent = self
        if self.max_children == 2:
            if branch_index == 0:
                self.left = child_node
                return True
            elif branch_index == 1:
                self.right = child_node
                return True
            else:
                if self.left is None:
                    self.left = child_node
                    return True
                elif self.right is None:
                    self.right = child_node
                    return True
                else:
                    return False
        else:
            if self.max_children is not None and len(self.children) >= self.max_children:
                return False
            if branch_index is not None and 0 <= branch_index <= len(self.children):
                self.children.insert(branch_index, child_node)
            else:
                self.children.append(child_node)
            return True

    def remove_child(self, child_node):
        """Elimina un hijo directo."""
        if self.max_children == 2:
            if self.left == child_node:
                self.left = None
                child_node.parent = None
                return True
            if self.right == child_node:
                self.right = None
                child_node.parent = None
                return True
        else:
            if child_node in self.children:
                self.children.remove(child_node)
                child_node.parent = None
                return True
        return False

    def is_leaf(self):
        return len(self.get_children()) == 0

    def count_children(self):
        return len(self.get_children())


class TreeModel:
    """Modelo del árbol con operaciones de inserción, búsqueda y recorridos."""

    def __init__(self, max_children=2):
        self.root = None
        self.max_children = max_children
        self.is_bst_mode = True if max_children == 2 else False

    def clear(self):
        self.root = None

    def insert_bst(self, val):
        """Inserción en Árbol Binario de Búsqueda (ABB)."""
        new_node = TreeNode(val, max_children=2)
        if self.root is None:
            self.root = new_node
            return new_node, True

        curr = self.root
        while True:
            if val == curr.value:
                return curr, False  # Duplicado
            elif val < curr.value:
                if curr.left is None:
                    curr.left = new_node
                    new_node.parent = curr
                    return new_node, True
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = new_node
                    new_node.parent = curr
                    return new_node, True
                curr = curr.right

    def insert_level_order(self, val):
        """Inserción por niveles (anchura) llenando cada nodo según max_children."""
        new_node = TreeNode(val, max_children=self.max_children)
        if self.root is None:
            self.root = new_node
            return new_node, True

        queue = collections.deque([self.root])
        while queue:
            curr = queue.popleft()
            if self.max_children == 2:
                if curr.left is None:
                    curr.left = new_node
                    new_node.parent = curr
                    return new_node, True
                elif curr.right is None:
                    curr.right = new_node
                    new_node.parent = curr
                    return new_node, True
                else:
                    queue.append(curr.left)
                    queue.append(curr.right)
            else:
                if self.max_children is None or len(curr.children) < self.max_children:
                    curr.children.append(new_node)
                    new_node.parent = curr
                    return new_node, True
                for c in curr.children:
                    queue.append(c)
        return None, False

    def insert_child_of(self, parent_node, val):
        """Inserta un nuevo hijo directamente bajo el nodo especificado."""
        if parent_node is None:
            if self.root is None:
                self.root = TreeNode(val, max_children=self.max_children)
                return self.root, True
            return None, False

        new_node = TreeNode(val, max_children=self.max_children)
        success = parent_node.add_child(new_node)
        if success:
            return new_node, True
        return None, False

    def search(self, val):
        """Busca un valor y retorna (nodo_encontrado, ruta_de_nodos)."""
        if self.root is None:
            return None, []

        path = []
        if self.max_children == 2 and self.is_bst_mode:
            # Búsqueda eficiente en ABB
            curr = self.root
            while curr is not None:
                path.append(curr)
                if curr.value == val:
                    return curr, path
                elif val < curr.value:
                    curr = curr.left
                else:
                    curr = curr.right
            return None, path
        else:
            # Búsqueda por niveles (BFS) para N-ario
            queue = collections.deque([self.root])
            visited = []
            while queue:
                curr = queue.popleft()
                visited.append(curr)
                if curr.value == val:
                    return curr, visited
                for c in curr.get_children():
                    queue.append(c)
            return None, visited

    def delete_node(self, node_to_delete):
        """Elimina un nodo del árbol."""
        if not node_to_delete:
            return False

        if node_to_delete == self.root:
            children = node_to_delete.get_children()
            if not children:
                self.root = None
                return True
            elif len(children) == 1:
                self.root = children[0]
                self.root.parent = None
                return True
            else:
                # Si tiene varios hijos, reemplazamos por el sucesor
                succ = children[-1]
                while succ.get_children():
                    succ = succ.get_children()[0]
                node_to_delete.value = succ.value
                return self.delete_node(succ)

        parent = node_to_delete.parent
        children = node_to_delete.get_children()

        if not children:
            # Es hoja
            parent.remove_child(node_to_delete)
            return True
        elif len(children) == 1:
            child = children[0]
            # Conectar child al parent
            if self.max_children == 2:
                if parent.left == node_to_delete:
                    parent.left = child
                else:
                    parent.right = child
            else:
                idx = parent.children.index(node_to_delete)
                parent.children[idx] = child
            child.parent = parent
            return True
        else:
            # Múltiples hijos: buscar sucesor hoja
            succ = children[-1]
            while succ.get_children():
                succ = succ.get_children()[0]
            node_to_delete.value = succ.value
            return self.delete_node(succ)

    def get_path_to_root(self, node):
        """Obtiene la lista de nodos desde la raíz hasta el nodo indicado."""
        path = []
        curr = node
        while curr:
            path.append(curr)
            curr = curr.parent
        return list(reversed(path))

    # ==================== RECORRIDOS ====================
    def preorder(self, start_node=None):
        """Preorden: Raíz -> Hijos (de izquierda a derecha)."""
        res = []
        node = start_node if start_node else self.root
        if not node:
            return res

        def _rec(curr):
            if not curr:
                return
            res.append(curr)
            if self.max_children == 2:
                if curr.left:
                    _rec(curr.left)
                if curr.right:
                    _rec(curr.right)
            else:
                for c in curr.children:
                    _rec(c)

        _rec(node)
        return res

    def postorder(self, start_node=None):
        """Postorden: Hijos (de izquierda a derecha) -> Raíz."""
        res = []
        node = start_node if start_node else self.root
        if not node:
            return res

        def _rec(curr):
            if not curr:
                return
            if self.max_children == 2:
                if curr.left:
                    _rec(curr.left)
                if curr.right:
                    _rec(curr.right)
            else:
                for c in curr.children:
                    _rec(c)
            res.append(curr)

        _rec(node)
        return res

    def inorder(self, start_node=None):
        """Inorden: Izquierda -> Raíz -> Derecha (o Primer Hijo -> Raíz -> Resto de Hijos)."""
        res = []
        node = start_node if start_node else self.root
        if not node:
            return res

        if self.max_children == 2:
            def _rec_bin(curr):
                if not curr:
                    return
                if curr.left:
                    _rec_bin(curr.left)
                res.append(curr)
                if curr.right:
                    _rec_bin(curr.right)
            _rec_bin(node)
        else:
            def _rec_nary(curr):
                if not curr:
                    return
                children = curr.get_children()
                if children:
                    _rec_nary(children[0])
                res.append(curr)
                for c in children[1:]:
                    _rec_nary(c)
            _rec_nary(node)
        return res

    def level_order(self, start_node=None):
        """Recorrido por Niveles (Amplitud / BFS)."""
        res = []
        node = start_node if start_node else self.root
        if not node:
            return res

        queue = collections.deque([node])
        while queue:
            curr = queue.popleft()
            res.append(curr)
            for c in curr.get_children():
                queue.append(c)
        return res


class TreeVisualizerApp(tk.Tk):
    """Interfaz gráfica moderna para visualizar y recorrer árboles en Python."""

    # Paleta de colores atractiva y consistente con la captura
    COLOR_BG = "#f4f6f9"
    COLOR_CARD = "#ffffff"
    COLOR_PRIMARY = "#2563eb"       # Azul
    COLOR_SUCCESS = "#16a34a"       # Verde (Insertar)
    COLOR_DANGER = "#dc2626"        # Rojo (Eliminar)
    COLOR_WARNING = "#f59e0b"       # Ámbar / Dorado
    COLOR_TEXT_MAIN = "#1f2937"
    COLOR_TEXT_MUTED = "#6b7280"
    COLOR_BORDER = "#d1d5db"

    # Colores temáticos por ramas/niveles
    NODE_COLORS = [
        {"fill": "#60a5fa", "outline": "#2563eb", "text": "#ffffff"},  # Raíz: Azul cielo
        {"fill": "#f472b6", "outline": "#db2777", "text": "#ffffff"},  # Nivel 1 Izq: Rosa
        {"fill": "#c084fc", "outline": "#9333ea", "text": "#ffffff"},  # Nivel 1 Der: Púrpura
        {"fill": "#fbbf24", "outline": "#d97706", "text": "#1f2937"},  # Nivel 2: Dorado
        {"fill": "#34d399", "outline": "#059669", "text": "#ffffff"},  # Nivel 3: Esmeralda
        {"fill": "#38bdf8", "outline": "#0284c7", "text": "#ffffff"},  # Nivel 4: Cian
        {"fill": "#fb7185", "outline": "#e11d48", "text": "#ffffff"},  # Nivel 5: Coral
    ]

    COLOR_HIGHLIGHT = {"fill": "#fde047", "outline": "#ca8a04", "text": "#1f2937"}  # Activo
    COLOR_VISITED = {"fill": "#fed7aa", "outline": "#ea580c", "text": "#1f2937"}    # Ya visitado
    COLOR_SELECTED = {"fill": "#a5f3fc", "outline": "#0891b2", "text": "#083344"}   # Seleccionado

    def __init__(self):
        super().__init__()

        self.title("Beyker - Árbol Binario y N-Ario Interactivo")
        self.geometry("1120x760")
        self.minsize(960, 680)
        self.configure(bg=self.COLOR_BG)

        # Modelo del árbol
        self.tree = TreeModel(max_children=2)
        self.selected_node = None
        self.node_positions = {}  # node -> (x, y)
        self.node_canvas_items = {}  # node -> dict de ids en canvas
        self.line_canvas_items = {}  # (parent, child) -> line_id

        # Estado de animación del recorrido
        self.traversal_sequence = []
        self.traversal_index = 0
        self.traversal_type_name = ""
        self.is_playing = False
        self.animation_job = None
        self.visited_set = set()

        # Variables de control
        self.var_input_val = tk.StringVar()
        self.var_branch_count = tk.StringVar(value="2 (Binario)")
        self.var_insert_mode = tk.StringVar(value="auto")  # 'auto' o 'selected'
        self.var_status = tk.StringVar(value="Listo. Ingrese valores o cargue un ejemplo.")
        self.var_speed = tk.IntVar(value=650)  # ms entre pasos
        self.var_traversal_display = tk.StringVar(value="Ningún recorrido activo. Haga clic en Preorden, Inorden, Postorden o Por Niveles.")

        # Variables para Zoom y Pan
        self.zoom_scale = 1.0
        self.pan_start_x = 0
        self.pan_start_y = 0

        self._configure_styles()
        self._build_ui()

        # Cargar ejemplo inicial tipo imagen
        self.cargar_ejemplo_foto()

    def _configure_styles(self):
        """Configuración de estilos TTK modernos."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TFrame", background=self.COLOR_BG)
        style.configure("Card.TFrame", background=self.COLOR_CARD, relief="ridge", borderwidth=1)
        style.configure("TLabel", background=self.COLOR_BG, foreground=self.COLOR_TEXT_MAIN, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground=self.COLOR_TEXT_MAIN)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10, "italic"), foreground=self.COLOR_TEXT_MUTED)
        style.configure("Badge.TLabel", font=("Segoe UI", 9, "bold"), foreground=self.COLOR_PRIMARY)

        # Botones con diseño personalizado
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("Green.TButton", font=("Segoe UI", 10, "bold"), padding=6, background=self.COLOR_SUCCESS)
        style.configure("Blue.TButton", font=("Segoe UI", 10, "bold"), padding=6, background=self.COLOR_PRIMARY)
        style.configure("Red.TButton", font=("Segoe UI", 10, "bold"), padding=6, background=self.COLOR_DANGER)

    def _build_ui(self):
        """Construye los componentes de la interfaz de usuario."""
        # ================= ENCABEZADO =================
        header_frame = tk.Frame(self, bg=self.COLOR_BG, pady=8)
        header_frame.pack(fill="x", padx=20)

        lbl_title = tk.Label(
            header_frame,
            text="BEYKER - ÁRBOL BINARIO Y N-ARIO DE BÚSQUEDA",
            font=("Segoe UI", 18, "bold"),
            bg=self.COLOR_BG,
            fg="#111827"
        )
        lbl_title.pack()

        lbl_sub = tk.Label(
            header_frame,
            text="Configura la cantidad de ramas o hijos por nodo, inserta valores e interactúa con recorridos animados.",
            font=("Segoe UI", 10),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT_MUTED
        )
        lbl_sub.pack(pady=(2, 0))

        # ================= PANEL DE CONTROL SUPERIOR =================
        ctrl_card = tk.Frame(self, bg=self.COLOR_CARD, relief="groove", bd=1, padx=14, pady=10)
        ctrl_card.pack(fill="x", padx=20, pady=(4, 8))

        # Fila 1: Configuración de Ramas y Entrada de Valor
        row1 = tk.Frame(ctrl_card, bg=self.COLOR_CARD)
        row1.pack(fill="x", pady=3)

        tk.Label(row1, text="Ramas / Hijos máx.:", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD).pack(side="left")
        
        self.cb_branches = ttk.Combobox(
            row1,
            textvariable=self.var_branch_count,
            values=["2 (Binario)", "3 (Ternario)", "4 (Cuaternario)", "5 (Quinario)", "Sin Límite (N-ario)"],
            state="readonly",
            width=16,
            font=("Segoe UI", 9)
        )
        self.cb_branches.pack(side="left", padx=(6, 18))
        self.cb_branches.bind("<<ComboboxSelected>>", self._on_branch_config_changed)

        tk.Label(row1, text="Ingrese un número o texto:", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD).pack(side="left")

        self.entry_val = tk.Entry(
            row1,
            textvariable=self.var_input_val,
            font=("Segoe UI", 11),
            width=10,
            bd=2,
            relief="solid"
        )
        self.entry_val.pack(side="left", padx=8)
        self.entry_val.bind("<Return>", lambda e: self.accion_insertar())
        self.entry_val.focus()

        # Botón Insertar (Verde)
        btn_insertar = tk.Button(
            row1,
            text="Insertar",
            bg="#22c55e",
            fg="white",
            activebackground="#16a34a",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=3,
            relief="raised",
            bd=1,
            cursor="hand2",
            command=self.accion_insertar
        )
        btn_insertar.pack(side="left", padx=4)

        # Botón Buscar (Azul)
        btn_buscar = tk.Button(
            row1,
            text="Buscar",
            bg="#3b82f6",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=3,
            relief="raised",
            bd=1,
            cursor="hand2",
            command=self.accion_buscar
        )
        btn_buscar.pack(side="left", padx=4)

        # Botón Eliminar (Rojo)
        btn_eliminar = tk.Button(
            row1,
            text="Eliminar",
            bg="#ef4444",
            fg="white",
            activebackground="#b91c1c",
            activeforeground="white",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=3,
            relief="raised",
            bd=1,
            cursor="hand2",
            command=self.accion_eliminar
        )
        btn_eliminar.pack(side="left", padx=4)

        # Separador vertical
        sep = ttk.Separator(row1, orient="vertical")
        sep.pack(side="left", fill="y", padx=10)

        # Botón Llenar Árbol Completo / Masivo
        btn_llenar = tk.Button(
            row1,
            text="⚡ Generar Árbol N-ario",
            bg="#8b5cf6",
            fg="white",
            activebackground="#6d28d9",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=3,
            relief="raised",
            bd=1,
            cursor="hand2",
            command=self.abrir_dialogo_generar
        )
        btn_llenar.pack(side="left", padx=4)

        # Botón Limpiar
        btn_limpiar = tk.Button(
            row1,
            text="🗑 Limpiar",
            bg="#9ca3af",
            fg="white",
            activebackground="#6b7280",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=3,
            relief="raised",
            bd=1,
            cursor="hand2",
            command=self.accion_limpiar
        )
        btn_limpiar.pack(side="right", padx=4)

        # Fila 2: Botones de Recorridos (como en la foto)
        row2 = tk.Frame(ctrl_card, bg=self.COLOR_CARD)
        row2.pack(fill="x", pady=(8, 2))

        tk.Label(row2, text="Recorridos:", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD, fg="#374151").pack(side="left", padx=(0, 6))

        # Botones de recorrido con estilo limpio
        traversal_buttons = [
            ("Preorden (RID)", lambda: self.iniciar_recorrido("preorden")),
            ("Inorden (IRD)", lambda: self.iniciar_recorrido("inorden")),
            ("Postorden (IDR)", lambda: self.iniciar_recorrido("postorden")),
            ("Por Niveles (BFS)", lambda: self.iniciar_recorrido("niveles")),
        ]

        for text, cmd in traversal_buttons:
            b = tk.Button(
                row2,
                text=text,
                bg="#f3f4f6",
                fg="#1f2937",
                activebackground="#e5e7eb",
                font=("Segoe UI", 9, "bold"),
                padx=10,
                pady=3,
                relief="groove",
                bd=1,
                cursor="hand2",
                command=cmd
            )
            b.pack(side="left", padx=3)

        # Menú de Cargar Ejemplos
        mb_ejemplos = tk.Menubutton(
            row2,
            text="Cargar ejemplo ▼",
            bg="#e0e7ff",
            fg="#3730a3",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=3,
            relief="raised",
            bd=1,
            cursor="hand2"
        )
        menu_ejemplos = tk.Menu(mb_ejemplos, tearoff=0)
        menu_ejemplos.add_command(label="Árbol Binario (de la foto: 10, 6, 15...)", command=self.cargar_ejemplo_foto)
        menu_ejemplos.add_command(label="Árbol Ternario (3 ramas por nodo)", command=self.cargar_ejemplo_ternario)
        menu_ejemplos.add_command(label="Árbol Cuaternario (4 ramas por nodo)", command=self.cargar_ejemplo_cuaternario)
        menu_ejemplos.add_command(label="Árbol de Búsqueda Binaria Equilibrado", command=self.cargar_ejemplo_bst)
        mb_ejemplos["menu"] = menu_ejemplos
        mb_ejemplos.pack(side="left", padx=(10, 4))

        # Indicador de nodo seleccionado actual
        self.lbl_selected_info = tk.Label(
            row2,
            text="Ningún nodo seleccionado (haz clic en un nodo para seleccionarlo)",
            font=("Segoe UI", 9, "italic"),
            bg=self.COLOR_CARD,
            fg="#64748b"
        )
        self.lbl_selected_info.pack(side="right", padx=6)

        # ================= ÁREA CENTRAL (CANVAS + CONTROLES DE RECORRIDO) =================
        main_body = tk.Frame(self, bg=self.COLOR_BG)
        main_body.pack(fill="both", expand=True, padx=20, pady=4)

        # Marco del canvas con borde elegante
        canvas_outer = tk.Frame(main_body, bg=self.COLOR_CARD, relief="solid", bd=1)
        canvas_outer.pack(fill="both", expand=True)

        # Canvas interactivo
        self.canvas = tk.Canvas(
            canvas_outer,
            bg="#ffffff",
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack(side="left", fill="both", expand=True)

        # Scrollbars para árboles grandes
        self.scroll_y = ttk.Scrollbar(canvas_outer, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.scroll_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scroll_x.pack(fill="x", padx=20, pady=(0, 4))
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)

        # Eventos del Canvas: Selección con clic, Panning y Zoom
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<Configure>", lambda e: self.redibujar_arbol())
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

        # ================= BARRA DE CONTROLES DE RECORRIDO =================
        anim_bar = tk.Frame(self, bg=self.COLOR_CARD, relief="groove", bd=1, padx=12, pady=6)
        anim_bar.pack(fill="x", padx=20, pady=(0, 4))

        tk.Label(anim_bar, text="Control del Recorrido:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_CARD).pack(side="left", padx=(0, 6))

        self.btn_play_pause = tk.Button(
            anim_bar,
            text="⏸ Pausar",
            bg="#f3f4f6",
            fg="#1f2937",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=2,
            relief="groove",
            bd=1,
            cursor="hand2",
            command=self.toggle_play_pause
        )
        self.btn_play_pause.pack(side="left", padx=3)

        self.btn_next_step = tk.Button(
            anim_bar,
            text="⏭ Siguiente Paso (Clic)",
            bg="#e0f2fe",
            fg="#0369a1",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=2,
            relief="groove",
            bd=1,
            cursor="hand2",
            command=self.avanzar_paso_manual
        )
        self.btn_next_step.pack(side="left", padx=3)

        self.btn_stop_anim = tk.Button(
            anim_bar,
            text="⏹ Detener",
            bg="#fee2e2",
            fg="#b91c1c",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=2,
            relief="groove",
            bd=1,
            cursor="hand2",
            command=self.detener_animacion
        )
        self.btn_stop_anim.pack(side="left", padx=3)

        # Control de velocidad
        tk.Label(anim_bar, text="Velocidad:", font=("Segoe UI", 9), bg=self.COLOR_CARD).pack(side="left", padx=(14, 4))
        self.scale_speed = tk.Scale(
            anim_bar,
            from_=150,
            to=1200,
            orient="horizontal",
            variable=self.var_speed,
            showvalue=False,
            length=110,
            bg=self.COLOR_CARD,
            highlightthickness=0
        )
        self.scale_speed.pack(side="left", padx=2)
        tk.Label(anim_bar, text="(Rápido ─ Lento)", font=("Segoe UI", 8), bg=self.COLOR_CARD, fg=self.COLOR_TEXT_MUTED).pack(side="left")

        # Botón de ayuda / instrucciones rápidas
        btn_ayuda = tk.Button(
            anim_bar,
            text="❓ Ayuda",
            bg="#f1f5f9",
            fg="#475569",
            font=("Segoe UI", 8, "bold"),
            padx=6,
            pady=1,
            relief="groove",
            bd=1,
            cursor="hand2",
            command=self.mostrar_ayuda
        )
        btn_ayuda.pack(side="right", padx=2)

        # ================= PANEL DE RESULTADOS Y SECUENCIA =================
        result_box = tk.Frame(self, bg=self.COLOR_CARD, relief="groove", bd=1, padx=12, pady=6)
        result_box.pack(fill="x", padx=20, pady=(0, 4))

        tk.Label(
            result_box,
            text="Secuencia de Recorrido:",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_CARD,
            fg="#1f2937"
        ).pack(anchor="w")

        self.lbl_traversal = tk.Label(
            result_box,
            textvariable=self.var_traversal_display,
            font=("Consolas", 10, "bold"),
            bg="#f8fafc",
            fg="#0f172a",
            relief="solid",
            bd=1,
            padx=8,
            pady=5,
            anchor="w",
            wraplength=1040,
            justify="left"
        )
        self.lbl_traversal.pack(fill="x", pady=(3, 0))

        # ================= BARRA DE ESTADO INFERIOR =================
        status_bar = tk.Frame(self, bg=self.COLOR_BG, padx=20, pady=2)
        status_bar.pack(fill="x")

        lbl_status = tk.Label(
            status_bar,
            textvariable=self.var_status,
            font=("Segoe UI", 9),
            bg=self.COLOR_BG,
            fg="#4b5563",
            anchor="w"
        )
        lbl_status.pack(side="left")

    # ================= GESTIÓN DE CONFIGURACIÓN DE RAMAS =================
    def _on_branch_config_changed(self, event=None):
        val = self.var_branch_count.get()
        if "2" in val:
            self.tree.max_children = 2
            self.tree.is_bst_mode = True
            self.var_status.set("Modo: Árbol Binario (máximo 2 ramas/hijos por nodo). Inserción ABB activada.")
        elif "3" in val:
            self.tree.max_children = 3
            self.tree.is_bst_mode = False
            self.var_status.set("Modo: Árbol Ternario (máximo 3 ramas/hijos por nodo).")
        elif "4" in val:
            self.tree.max_children = 4
            self.tree.is_bst_mode = False
            self.var_status.set("Modo: Árbol Cuaternario (máximo 4 ramas/hijos por nodo).")
        elif "5" in val:
            self.tree.max_children = 5
            self.tree.is_bst_mode = False
            self.var_status.set("Modo: Árbol Quinario (máximo 5 ramas/hijos por nodo).")
        else:
            self.tree.max_children = None
            self.tree.is_bst_mode = False
            self.var_status.set("Modo: Árbol N-ario General (sin límite de ramas/hijos por nodo).")

        self.actualizar_info_seleccion()
        self.redibujar_arbol()

    def parse_value(self, raw_str):
        """Convierte a entero si es posible, de lo contrario deja como cadena limpia."""
        s = raw_str.strip()
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            return s

    # ================= ACCIONES PRINCIPALES =================
    def accion_insertar(self):
        """Inserta un valor en el árbol."""
        val = self.parse_value(self.var_input_val.get())
        if val is None:
            messagebox.showwarning("Dato requerido", "Por favor ingrese un número o texto para insertar.")
            self.entry_val.focus()
            return

        self.detener_animacion()

        # Si el usuario seleccionó un nodo específico, insertamos como hijo de ese nodo
        if self.selected_node is not None:
            max_c = self.tree.max_children
            curr_c = self.selected_node.count_children()
            if max_c is not None and curr_c >= max_c:
                res = messagebox.askyesno(
                    "Límite de ramas alcanzado",
                    f"El nodo '{self.selected_node.value}' ya tiene el máximo permitido de {max_c} ramas/hijos.\n\n"
                    "¿Desea insertarlo automáticamente en la siguiente posición libre por niveles?"
                )
                if not res:
                    return
                new_node, ok = self.tree.insert_level_order(val)
            else:
                new_node, ok = self.tree.insert_child_of(self.selected_node, val)
        else:
            # Inserción general
            if self.tree.max_children == 2 and self.tree.is_bst_mode and isinstance(val, (int, float)):
                new_node, ok = self.tree.insert_bst(val)
            else:
                new_node, ok = self.tree.insert_level_order(val)

        if not ok:
            messagebox.showinfo("Información", f"El valor '{val}' ya existe en el árbol o no se pudo insertar.")
        else:
            self.var_status.set(f"Nodo '{val}' insertado correctamente.")
            self.var_input_val.set("")

        self.selected_node = new_node
        self.actualizar_info_seleccion()
        self.redibujar_arbol()
        self.entry_val.focus()

    def accion_buscar(self):
        """Busca un valor y anima el camino recorrido."""
        val = self.parse_value(self.var_input_val.get())
        if val is None:
            messagebox.showwarning("Búsqueda", "Ingrese el número o texto que desea buscar.")
            return

        if not self.tree.root:
            messagebox.showinfo("Árbol vacío", "El árbol no tiene nodos.")
            return

        self.detener_animacion()
        found_node, path = self.tree.search(val)

        if not path:
            self.var_status.set(f"Nodo '{val}' no encontrado.")
            return

        # Animar búsqueda paso a paso
        self.traversal_sequence = path
        self.traversal_index = 0
        self.traversal_type_name = f"Búsqueda de '{val}'"
        self.visited_set.clear()
        self.is_playing = True
        self.var_status.set(f"Buscando nodo '{val}'...")
        self._animar_paso(es_busqueda=True, nodo_objetivo=found_node)

    def accion_eliminar(self):
        """Elimina el nodo seleccionado o el valor ingresado."""
        if self.selected_node:
            target = self.selected_node
        else:
            val = self.parse_value(self.var_input_val.get())
            if val is None:
                messagebox.showwarning("Eliminar", "Seleccione un nodo en pantalla o ingrese un valor para eliminar.")
                return
            found, _ = self.tree.search(val)
            if not found:
                messagebox.showinfo("No encontrado", f"El valor '{val}' no existe en el árbol.")
                return
            target = found

        val_deleted = target.value
        self.detener_animacion()
        self.tree.delete_node(target)
        self.selected_node = None
        self.actualizar_info_seleccion()
        self.var_status.set(f"Nodo '{val_deleted}' eliminado del árbol.")
        self.redibujar_arbol()

    def accion_limpiar(self):
        """Limpia todo el árbol."""
        if messagebox.askyesno("Limpiar Árbol", "¿Está seguro de que desea eliminar todos los nodos del árbol?"):
            self.detener_animacion()
            self.tree.clear()
            self.selected_node = None
            self.actualizar_info_seleccion()
            self.var_status.set("Árbol limpiado completamente.")
            self.var_traversal_display.set("Árbol vacío.")
            self.redibujar_arbol()

    # ================= GENERADOR Y EJEMPLOS =================
    def abrir_dialogo_generar(self):
        """Abre un diálogo para generar un árbol completo con N ramas."""
        dlg = tk.Toplevel(self)
        dlg.title("Generar Árbol N-ario")
        dlg.geometry("380x300")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        dlg.configure(bg=self.COLOR_BG)

        tk.Label(
            dlg,
            text="Generador de Árboles",
            font=("Segoe UI", 12, "bold"),
            bg=self.COLOR_BG
        ).pack(pady=(12, 4))

        tk.Label(
            dlg,
            text="Crea un árbol automáticamente con la cantidad de\nramas e hijos que elijas.",
            font=("Segoe UI", 9),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT_MUTED
        ).pack(pady=(0, 12))

        f_inputs = tk.Frame(dlg, bg=self.COLOR_BG)
        f_inputs.pack(padx=20, pady=4)

        # Cantidad de ramas por nodo
        tk.Label(f_inputs, text="Ramas por nodo (Grado):", font=("Segoe UI", 9, "bold"), bg=self.COLOR_BG).grid(row=0, column=0, sticky="w", pady=6)
        sp_branches = tk.Spinbox(f_inputs, from_=2, to=6, width=6, font=("Segoe UI", 9))
        sp_branches.delete(0, "end")
        curr_b = 2 if self.tree.max_children is None else self.tree.max_children
        sp_branches.insert(0, str(curr_b))
        sp_branches.grid(row=0, column=1, padx=8, pady=6)

        # Cantidad total de nodos
        tk.Label(f_inputs, text="Cantidad total de nodos:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_BG).grid(row=1, column=0, sticky="w", pady=6)
        sp_nodes = tk.Spinbox(f_inputs, from_=3, to=31, width=6, font=("Segoe UI", 9))
        sp_nodes.delete(0, "end")
        sp_nodes.insert(0, "7")
        sp_nodes.grid(row=1, column=1, padx=8, pady=6)

        # Tipo de valores
        tk.Label(f_inputs, text="Tipo de valores:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_BG).grid(row=2, column=0, sticky="w", pady=6)
        var_tipo = tk.StringVar(value="ordenados")
        cb_tipo = ttk.Combobox(f_inputs, textvariable=var_tipo, values=["ordenados", "aleatorios"], state="readonly", width=12)
        cb_tipo.grid(row=2, column=1, padx=8, pady=6)

        def generar():
            try:
                branches = int(sp_branches.get())
                count = int(sp_nodes.get())
            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos.")
                return

            if count < 1 or count > 50:
                messagebox.showerror("Límite", "Por favor elija entre 1 y 50 nodos para una visualización clara.")
                return

            self.tree.max_children = branches
            self.tree.is_bst_mode = False
            self.tree.clear()

            # Configurar combo en la interfaz
            if branches == 2:
                self.var_branch_count.set("2 (Binario)")
            elif branches == 3:
                self.var_branch_count.set("3 (Ternario)")
            elif branches == 4:
                self.var_branch_count.set("4 (Cuaternario)")
            elif branches == 5:
                self.var_branch_count.set("5 (Quinario)")
            else:
                self.var_branch_count.set("Sin Límite (N-ario)")

            if var_tipo.get() == "aleatorios":
                valores = random.sample(range(1, 100), count)
            else:
                valores = [10 * (i + 1) for i in range(count)]

            for v in valores:
                self.tree.insert_level_order(v)

            self.selected_node = None
            self.actualizar_info_seleccion()
            self.var_status.set(f"Árbol generado con éxito: {count} nodos y {branches} ramas por nodo.")
            self.redibujar_arbol()
            dlg.destroy()

        btn_generar = tk.Button(
            dlg,
            text="Generar y Dibujar Árbol",
            bg="#22c55e",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=4,
            relief="raised",
            cursor="hand2",
            command=generar
        )
        btn_generar.pack(pady=16)

    def cargar_ejemplo_foto(self):
        """Carga exactamente el árbol binario mostrado en la imagen del usuario: 10, 6, 15, 3, 7, 12, 18."""
        self.detener_animacion()
        self.tree = TreeModel(max_children=2)
        self.tree.is_bst_mode = True
        self.var_branch_count.set("2 (Binario)")

        # Raíz 10
        r = TreeNode(10, 2)
        self.tree.root = r

        # Nivel 1: 6 a la izquierda, 15 a la derecha
        n6 = TreeNode(6, 2)
        n15 = TreeNode(15, 2)
        r.left = n6
        n6.parent = r
        r.right = n15
        n15.parent = r

        # Hijos de 6: 3 y 7
        n3 = TreeNode(3, 2)
        n7 = TreeNode(7, 2)
        n6.left = n3
        n3.parent = n6
        n6.right = n7
        n7.parent = n6

        # Hijos de 15: 12 y 18
        n12 = TreeNode(12, 2)
        n18 = TreeNode(18, 2)
        n15.left = n12
        n12.parent = n15
        n15.right = n18
        n18.parent = n15

        self.selected_node = None
        self.actualizar_info_seleccion()
        self.var_status.set("Árbol de ejemplo cargado correctamente (Árbol de la imagen).")
        self.var_traversal_display.set("Listo para recorrer. Haz clic en 'Preorden', 'Inorden', 'Postorden' o 'Por Niveles'.")
        self.redibujar_arbol()

    def cargar_ejemplo_ternario(self):
        """Carga un árbol con 3 ramas por nodo."""
        self.detener_animacion()
        self.tree = TreeModel(max_children=3)
        self.var_branch_count.set("3 (Ternario)")

        r = TreeNode(10, 3)
        self.tree.root = r

        # 3 hijos de la raíz
        for v in [5, 15, 25]:
            child = TreeNode(v, 3)
            r.add_child(child)
            # Agregar 2 o 3 hijos a cada rama
            if v == 5:
                for sub in [2, 4]:
                    child.add_child(TreeNode(sub, 3))
            elif v == 15:
                for sub in [12, 14, 16]:
                    child.add_child(TreeNode(sub, 3))
            elif v == 25:
                for sub in [22, 28]:
                    child.add_child(TreeNode(sub, 3))

        self.selected_node = None
        self.actualizar_info_seleccion()
        self.var_status.set("Árbol ternario cargado (3 ramas por nodo).")
        self.redibujar_arbol()

    def cargar_ejemplo_cuaternario(self):
        """Carga un árbol con 4 ramas por nodo."""
        self.detener_animacion()
        self.tree = TreeModel(max_children=4)
        self.var_branch_count.set("4 (Cuaternario)")

        r = TreeNode("A", 4)
        self.tree.root = r
        for v in ["B1", "B2", "B3", "B4"]:
            c = TreeNode(v, 4)
            r.add_child(c)
            if v == "B1":
                for sub in ["C1", "C2"]:
                    c.add_child(TreeNode(sub, 4))
            elif v == "B4":
                for sub in ["C3", "C4", "C5"]:
                    c.add_child(TreeNode(sub, 4))

        self.selected_node = None
        self.actualizar_info_seleccion()
        self.var_status.set("Árbol cuaternario cargado (4 ramas por nodo).")
        self.redibujar_arbol()

    def cargar_ejemplo_bst(self):
        """Carga un árbol binario de búsqueda con varios elementos."""
        self.detener_animacion()
        self.tree = TreeModel(max_children=2)
        self.var_branch_count.set("2 (Binario)")
        for val in [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 65]:
            self.tree.insert_bst(val)

        self.selected_node = None
        self.actualizar_info_seleccion()
        self.var_status.set("Árbol Binario de Búsqueda (ABB) equilibrado cargado.")
        self.redibujar_arbol()

    # ================= MOTOR DE RECORRIDOS ANIMADOS =================
    def iniciar_recorrido(self, tipo):
        """Inicia el recorrido animado paso a paso con iluminación nodo por nodo."""
        if not self.tree.root:
            messagebox.showinfo("Árbol vacío", "El árbol no contiene nodos para recorrer.")
            return

        self.detener_animacion()

        # Obtener lista según el tipo
        start_node = self.selected_node if self.selected_node else self.tree.root

        if tipo == "preorden":
            self.traversal_sequence = self.tree.preorder(start_node)
            self.traversal_type_name = "Preorden (RID: Raíz ➔ Hijos)"
        elif tipo == "inorden":
            self.traversal_sequence = self.tree.inorder(start_node)
            self.traversal_type_name = "Inorden (IRD: Izq ➔ Raíz ➔ Der)"
        elif tipo == "postorden":
            self.traversal_sequence = self.tree.postorder(start_node)
            self.traversal_type_name = "Postorden (IDR: Hijos ➔ Raíz)"
        elif tipo == "niveles":
            self.traversal_sequence = self.tree.level_order(start_node)
            self.traversal_type_name = "Por Niveles (BFS / Anchura)"

        if not self.traversal_sequence:
            return

        self.traversal_index = 0
        self.visited_set.clear()
        self.is_playing = True
        self.btn_play_pause.config(text="⏸ Pausar")

        origen_txt = f" desde nodo '{start_node.value}'" if start_node != self.tree.root else ""
        self.var_status.set(f"Iniciando recorrido {self.traversal_type_name}{origen_txt}...")

        # Ejecutar primer paso
        self._animar_paso()

    def _animar_paso(self, es_busqueda=False, nodo_objetivo=None):
        """Ejecuta un paso de la animación y programa el siguiente."""
        if not self.is_playing:
            return

        if self.traversal_index >= len(self.traversal_sequence):
            # Finalizado
            self.is_playing = False
            self.btn_play_pause.config(text="▶ Reiniciar")
            if es_busqueda:
                if nodo_objetivo:
                    self.var_status.set(f"¡Éxito! Nodo '{nodo_objetivo.value}' encontrado en el nivel {nodo_objetivo.depth}.")
                else:
                    self.var_status.set("El valor buscado NO se encuentra en el árbol.")
            else:
                self.var_status.set(f"Recorrido {self.traversal_type_name} finalizado con éxito ({len(self.traversal_sequence)} nodos visitados).")
            return

        curr_node = self.traversal_sequence[self.traversal_index]
        self.visited_set.add(curr_node)

        # Actualizar visualización del texto de recorrido
        visitados_vals = [str(n.value) for n in self.traversal_sequence[:self.traversal_index + 1]]
        seq_str = "  ➔  ".join(visitados_vals)
        total = len(self.traversal_sequence)
        self.var_traversal_display.set(f"[{self.traversal_type_name}] Paso {self.traversal_index + 1} de {total}:\n{seq_str}")

        # Mensaje de estado
        if es_busqueda:
            if curr_node == nodo_objetivo:
                self.var_status.set(f"¡Encontrado! El nodo '{curr_node.value}' coincide con la búsqueda.")
            else:
                self.var_status.set(f"Buscando... Comparando con nodo '{curr_node.value}' (Nivel {curr_node.depth})")
        else:
            self.var_status.set(f"Visitando nodo '{curr_node.value}' | Paso {self.traversal_index + 1} de {total} ({self.traversal_type_name})")

        # Redibujar canvas con nodo activo iluminado
        self.redibujar_arbol(nodo_activo=curr_node, es_busqueda=es_busqueda, nodo_objetivo=nodo_objetivo)

        self.traversal_index += 1

        # Si encontramos el objetivo en búsqueda, detenerse aquí
        if es_busqueda and curr_node == nodo_objetivo:
            self.is_playing = False
            self.btn_play_pause.config(text="▶ Reiniciar")
            return

        # Programar siguiente paso si está en modo automático
        delay = self.var_speed.get()
        self.animation_job = self.after(delay, lambda: self._animar_paso(es_busqueda, nodo_objetivo))

    def avanzar_paso_manual(self):
        """Permite avanzar un paso a la vez haciendo clic."""
        if not self.traversal_sequence:
            # Si no hay recorrido, iniciar por defecto preorden
            self.iniciar_recorrido("preorden")
            return

        self.is_playing = False
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None
        self.btn_play_pause.config(text="▶ Reanudar")

        if self.traversal_index >= len(self.traversal_sequence):
            self.traversal_index = 0
            self.visited_set.clear()

        # Avanzar exactamente 1 paso
        self.is_playing = True
        self._animar_paso()
        self.is_playing = False

    def toggle_play_pause(self):
        """Pausa o reanuda la animación del recorrido."""
        if not self.traversal_sequence:
            self.iniciar_recorrido("preorden")
            return

        if self.is_playing:
            self.is_playing = False
            if self.animation_job:
                self.after_cancel(self.animation_job)
                self.animation_job = None
            self.btn_play_pause.config(text="▶ Reanudar")
            self.var_status.set("Recorrido en pausa. Usa 'Siguiente Paso' o 'Reanudar'.")
        else:
            if self.traversal_index >= len(self.traversal_sequence):
                self.traversal_index = 0
                self.visited_set.clear()
            self.is_playing = True
            self.btn_play_pause.config(text="⏸ Pausar")
            self._animar_paso()

    def detener_animacion(self):
        """Detiene y limpia el estado de la animación."""
        self.is_playing = False
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None
        self.traversal_sequence = []
        self.traversal_index = 0
        self.visited_set.clear()
        self.btn_play_pause.config(text="▶ Iniciar")
        self.redibujar_arbol()

    # ================= DIBUJADO Y DISTRIBUCIÓN DEL ÁRBOL =================
    def calcular_coordenadas(self, canvas_w, canvas_h):
        """
        Calcula coordenadas estéticas (X, Y) para todos los nodos del árbol.
        - Para árboles binarios utiliza distribución in-order para garantizar la orientación izquierda/derecha.
        - Para árboles N-arios utiliza distribución basada en hojas y baricentros.
        """
        if not self.tree.root:
            return {}

        root = self.tree.root

        # 1. Asignar profundidades
        max_depth = 0

        def calc_depth(n, d):
            nonlocal max_depth
            n.depth = d
            if d > max_depth:
                max_depth = d
            for c in n.get_children():
                calc_depth(c, d + 1)

        calc_depth(root, 0)

        # 2. Asignar posiciones unitarias X
        if self.tree.max_children == 2:
            # Distribución simétrica para árbol binario
            in_order_idx = 0

            def assign_binary_x(n):
                nonlocal in_order_idx
                if not n:
                    return
                if n.left:
                    assign_binary_x(n.left)
                n.unit_x = in_order_idx
                in_order_idx += 1
                if n.right:
                    assign_binary_x(n.right)

            assign_binary_x(root)
            total_units = max(1, in_order_idx - 1)
        else:
            # Distribución para árbol N-ario
            leaf_idx = 0

            def assign_nary_x(n):
                nonlocal leaf_idx
                children = n.get_children()
                if not children:
                    n.unit_x = leaf_idx
                    leaf_idx += 1
                else:
                    for c in children:
                        assign_nary_x(c)
                    n.unit_x = (children[0].unit_x + children[-1].unit_x) / 2.0

            assign_nary_x(root)
            total_units = max(1, leaf_idx - 1)

        # 3. Escalar a coordenadas de píxeles
        spacing_x = max(65, min(120, (canvas_w - 140) / total_units)) if total_units > 0 else 90
        spacing_y = max(75, min(100, (canvas_h - 150) / max(1, max_depth))) if max_depth > 0 else 85

        # Centrar horizontalmente
        all_units = []

        def collect_units(n):
            all_units.append(n.unit_x)
            for c in n.get_children():
                collect_units(c)

        collect_units(root)
        min_u = min(all_units)
        max_u = max(all_units)
        span_px = (max_u - min_u) * spacing_x

        start_x = max(70, (canvas_w - span_px) / 2) - min_u * spacing_x
        start_y = 65

        positions = {}

        def assign_pixels(n):
            px = start_x + n.unit_x * spacing_x
            py = start_y + n.depth * spacing_y
            n.x = px
            n.y = py
            positions[n] = (px, py)
            for c in n.get_children():
                assign_pixels(c)

        assign_pixels(root)
        return positions

    def redibujar_arbol(self, nodo_activo=None, es_busqueda=False, nodo_objetivo=None):
        """Redibuja completamente el árbol en el canvas interactivo con los estilos adecuados."""
        self.canvas.delete("all")
        self.node_canvas_items.clear()
        self.line_canvas_items.clear()

        if not self.tree.root:
            # Mensaje en canvas vacío
            w = self.canvas.winfo_width() or 800
            h = self.canvas.winfo_height() or 500
            self.canvas.create_text(
                w / 2, h / 2 - 20,
                text="🌳 Árbol vacío",
                font=("Segoe UI", 16, "bold"),
                fill="#94a3b8"
            )
            self.canvas.create_text(
                w / 2, h / 2 + 15,
                text="Escribe un número arriba y haz clic en 'Insertar' o prueba 'Cargar ejemplo'.",
                font=("Segoe UI", 10),
                fill="#94a3b8"
            )
            return

        w = max(self.canvas.winfo_width(), 850)
        h = max(self.canvas.winfo_height(), 520)

        self.node_positions = self.calcular_coordenadas(w, h)

        # Ajustar scrollregion para abarcar todo el árbol
        if self.node_positions:
            all_xs = [pos[0] for pos in self.node_positions.values()]
            all_ys = [pos[1] for pos in self.node_positions.values()]
            min_x, max_x = min(all_xs) - 80, max(all_xs) + 80
            min_y, max_y = min(all_ys) - 60, max(all_ys) + 100
            self.canvas.configure(scrollregion=(min(0, min_x), min(0, min_y), max(w, max_x), max(h, max_y)))

        # 1. DIBUJAR LÍNEAS / RAMAS (Conexiones padre -> hijo)
        def draw_edges(node):
            p_pos = self.node_positions.get(node)
            if not p_pos:
                return
            px, py = p_pos

            for child in node.get_children():
                c_pos = self.node_positions.get(child)
                if c_pos:
                    cx, cy = c_pos

                    # Color de línea: resaltada si ambos nodos están en el camino activo
                    is_active_edge = (
                        (node in self.visited_set and child in self.visited_set) or
                        (node == nodo_activo or child == nodo_activo)
                    )
                    edge_color = "#f59e0b" if is_active_edge else "#374151"
                    edge_width = 3 if is_active_edge else 2

                    line_id = self.canvas.create_line(
                        px, py, cx, cy,
                        fill=edge_color,
                        width=edge_width,
                        capstyle=tk.ROUND,
                        smooth=True
                    )
                    self.line_canvas_items[(node, child)] = line_id
                    draw_edges(child)

        draw_edges(self.tree.root)

        # 2. DIBUJAR NODOS (Círculos con texto y bordes estéticos)
        radius = 23

        def draw_nodes(node):
            pos = self.node_positions.get(node)
            if not pos:
                return
            x, y = pos

            # Determinar estilo de color
            if node == nodo_activo:
                if es_busqueda and node == nodo_objetivo:
                    # Encontrado en búsqueda: Verde brillante
                    fill_c = "#86efac"
                    outline_c = "#15803d"
                    text_c = "#14532d"
                else:
                    # Nodo actualmente visitado: Amarillo dorado brillante
                    fill_c = self.COLOR_HIGHLIGHT["fill"]
                    outline_c = self.COLOR_HIGHLIGHT["outline"]
                    text_c = self.COLOR_HIGHLIGHT["text"]
                outline_w = 4
            elif node == self.selected_node:
                # Nodo seleccionado por el usuario: Cian / Azul turquesa
                fill_c = self.COLOR_SELECTED["fill"]
                outline_c = self.COLOR_SELECTED["outline"]
                text_c = self.COLOR_SELECTED["text"]
                outline_w = 3
            elif node in self.visited_set:
                # Nodo ya visitado en el recorrido: Naranja suave / pastel
                fill_c = self.COLOR_VISITED["fill"]
                outline_c = self.COLOR_VISITED["outline"]
                text_c = self.COLOR_VISITED["text"]
                outline_w = 2.5
            else:
                # Color temático por profundidad o rama (como en la imagen del usuario)
                color_idx = node.depth % len(self.NODE_COLORS)
                cfg = self.NODE_COLORS[color_idx]
                fill_c = cfg["fill"]
                outline_c = cfg["outline"]
                text_c = cfg["text"]
                outline_w = 2

            # Anillo exterior para nodo activo (Efecto de brillo)
            if node == nodo_activo:
                self.canvas.create_oval(
                    x - radius - 5, y - radius - 5,
                    x + radius + 5, y + radius + 5,
                    outline="#f59e0b",
                    width=2,
                    dash=(3, 3)
                )

            # Sombra suave detrás del círculo
            self.canvas.create_oval(
                x - radius + 2, y - radius + 2,
                x + radius + 2, y + radius + 2,
                fill="#cbd5e1",
                outline=""
            )

            # Círculo principal del nodo
            circle_id = self.canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill=fill_c,
                outline=outline_c,
                width=outline_w
            )

            # Texto del valor dentro del círculo
            text_id = self.canvas.create_text(
                x, y,
                text=str(node.value),
                font=("Segoe UI", 11, "bold"),
                fill=text_c
            )

            # Guardar IDs asociados al nodo
            self.node_canvas_items[node] = (circle_id, text_id)

            for child in node.get_children():
                draw_nodes(child)

        draw_nodes(self.tree.root)

    # ================= INTERACCIÓN CON EL RATÓN =================
    def _on_canvas_click(self, event):
        """Detecta si el usuario hizo clic en un nodo para seleccionarlo."""
        # Convertir a coordenadas del canvas (considerando scroll)
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)

        self.pan_start_x = event.x
        self.pan_start_y = event.y

        clicked_node = None
        radius = 25

        for node, (nx, ny) in self.node_positions.items():
            dist = math.hypot(cx - nx, cy - ny)
            if dist <= radius:
                clicked_node = node
                break

        if clicked_node is not None:
            # Alternar selección
            if self.selected_node == clicked_node:
                self.selected_node = None
            else:
                self.selected_node = clicked_node

            self.actualizar_info_seleccion()
            self.redibujar_arbol()
        else:
            # Clic en fondo: deseleccionar
            if self.selected_node:
                self.selected_node = None
                self.actualizar_info_seleccion()
                self.redibujar_arbol()

    def _on_canvas_drag(self, event):
        """Permite arrastrar (panning) el canvas para explorar árboles grandes."""
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.canvas.xview_scroll(-1 if dx > 0 else (1 if dx < 0 else 0), "units")
        self.canvas.yview_scroll(-1 if dy > 0 else (1 if dy < 0 else 0), "units")

    def _on_mousewheel(self, event):
        """Scroll vertical con rueda del ratón."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def actualizar_info_seleccion(self):
        """Actualiza el texto descriptivo del nodo seleccionado."""
        if not self.selected_node:
            self.lbl_selected_info.config(
                text="Ningún nodo seleccionado (haz clic en un nodo para seleccionarlo)",
                fg="#64748b"
            )
            return

        n = self.selected_node
        hijos_cnt = n.count_children()
        max_c = self.tree.max_children
        max_str = str(max_c) if max_c is not None else "∞"
        hijos_vals = [str(c.value) for c in n.get_children()]
        hijos_str = ", ".join(hijos_vals) if hijos_vals else "Ninguno (Hoja)"
        padre_str = str(n.parent.value) if n.parent else "Raíz"

        txt = f"Nodo Seleccionado: '{n.value}'  |  Nivel: {n.depth}  |  Ramas/Hijos: {hijos_cnt}/{max_str} ({hijos_str})  |  Padre: {padre_str}"
        self.lbl_selected_info.config(text=txt, fg="#0369a1")

    def mostrar_ayuda(self):
        """Muestra instrucciones completas de uso."""
        msg = (
            "GUÍA RÁPIDA DE USO:\n\n"
            "1. INSERTAR VALORES:\n"
            "   - Escribe un número o texto y pulsa 'Insertar' o la tecla Enter.\n"
            "   - Si seleccionas un nodo haciendo clic sobre él, el nuevo valor se insertará como su hijo directo.\n\n"
            "2. CONFIGURAR RAMAS / HIJOS:\n"
            "   - En el menú superior puedes elegir cuántas ramas/hijos puede tener cada nodo: 2 (Binario), 3 (Ternario), 4, 5 o Sin Límite.\n"
            "   - También puedes pulsar '⚡ Generar Árbol N-ario' para crear automáticamente un árbol completo.\n\n"
            "3. RECORRIDOS ANIMADOS:\n"
            "   - Haz clic en Preorden (RID), Inorden (IRD), Postorden (IDR) o Por Niveles.\n"
            "   - El visualizador iluminará paso a paso cada nodo y mostrará la secuencia con flechas abajo.\n"
            "   - Usa 'Pausar', 'Siguiente Paso (Clic)' y la barra de velocidad para controlar la animación.\n\n"
            "4. BUSCAR Y ELIMINAR:\n"
            "   - 'Buscar' ilumina el camino hasta encontrar el nodo en verde.\n"
            "   - 'Eliminar' remueve el nodo seleccionado o el valor del campo de texto.\n\n"
            "5. NAVEGACIÓN:\n"
            "   - Haz clic y arrastra en el área en blanco para mover la vista (pan).\n"
            "   - Usa la rueda del ratón para desplazarte verticalmente."
        )
        messagebox.showinfo("Instrucciones y Ayuda", msg)


if __name__ == "__main__":
    app = TreeVisualizerApp()
    app.mainloop()
