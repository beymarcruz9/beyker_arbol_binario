/**
 * ============================================================================
 * MODELO DE DATOS Y ALGORITMOS DE ÁRBOL (BINARIO Y N-ARIO)
 * ============================================================================
 */

class TreeNode {
  static idCounter = 0;

  constructor(value, maxChildren = 2) {
    this.id = TreeNode.idCounter++;
    this.value = value;
    this.maxChildren = maxChildren; // null = ilimitado
    this.children = [];
    this.left = null;  // Para binario explícito
    this.right = null; // Para binario explícito
    this.parent = null;

    // Métricas de visualización
    this.depth = 0;
    this.unitX = 0;
    this.x = 0;
    this.y = 0;
  }

  getChildren() {
    if (this.maxChildren === 2) {
      const res = [];
      if (this.left !== null) res.push(this.left);
      if (this.right !== null) res.push(this.right);
      return res;
    }
    return this.children;
  }

  countChildren() {
    return this.getChildren().length;
  }

  isLeaf() {
    return this.countChildren() === 0;
  }

  addChild(childNode) {
    childNode.parent = this;
    if (this.maxChildren === 2) {
      if (this.left === null) {
        this.left = childNode;
        return true;
      } else if (this.right === null) {
        this.right = childNode;
        return true;
      }
      return false; // Límite alcanzado
    } else {
      if (this.maxChildren !== null && this.children.length >= this.maxChildren) {
        return false;
      }
      this.children.push(childNode);
      return true;
    }
  }

  removeChild(childNode) {
    if (this.maxChildren === 2) {
      if (this.left === childNode) {
        this.left = null;
        childNode.parent = null;
        return true;
      }
      if (this.right === childNode) {
        this.right = null;
        childNode.parent = null;
        return true;
      }
    } else {
      const idx = this.children.indexOf(childNode);
      if (idx !== -1) {
        this.children.splice(idx, 1);
        childNode.parent = null;
        return true;
      }
    }
    return false;
  }
}

class TreeModel {
  constructor(maxChildren = 2) {
    this.root = null;
    this.maxChildren = maxChildren;
    this.isBstMode = maxChildren === 2;
  }

  clear() {
    this.root = null;
  }

  insertBst(val) {
    const newNode = new TreeNode(val, 2);
    if (!this.root) {
      this.root = newNode;
      return { node: newNode, ok: true };
    }

    let curr = this.root;
    while (true) {
      if (val === curr.value) {
        return { node: curr, ok: false }; // Duplicado
      } else if (val < curr.value) {
        if (!curr.left) {
          curr.left = newNode;
          newNode.parent = curr;
          return { node: newNode, ok: true };
        }
        curr = curr.left;
      } else {
        if (!curr.right) {
          curr.right = newNode;
          newNode.parent = curr;
          return { node: newNode, ok: true };
        }
        curr = curr.right;
      }
    }
  }

  insertLevelOrder(val) {
    const newNode = new TreeNode(val, this.maxChildren);
    if (!this.root) {
      this.root = newNode;
      return { node: newNode, ok: true };
    }

    const queue = [this.root];
    while (queue.length > 0) {
      const curr = queue.shift();
      if (this.maxChildren === 2) {
        if (!curr.left) {
          curr.left = newNode;
          newNode.parent = curr;
          return { node: newNode, ok: true };
        } else if (!curr.right) {
          curr.right = newNode;
          newNode.parent = curr;
          return { node: newNode, ok: true };
        } else {
          queue.push(curr.left);
          queue.push(curr.right);
        }
      } else {
        if (this.maxChildren === null || curr.children.length < this.maxChildren) {
          curr.children.push(newNode);
          newNode.parent = curr;
          return { node: newNode, ok: true };
        }
        for (const c of curr.children) {
          queue.push(c);
        }
      }
    }
    return { node: null, ok: false };
  }

  insertChildOf(parentNode, val) {
    if (!parentNode) {
      if (!this.root) {
        this.root = new TreeNode(val, this.maxChildren);
        return { node: this.root, ok: true };
      }
      return { node: null, ok: false };
    }

    const newNode = new TreeNode(val, this.maxChildren);
    const success = parentNode.addChild(newNode);
    return { node: success ? newNode : null, ok: success };
  }

  search(val) {
    if (!this.root) return { found: null, path: [] };

    const path = [];
    if (this.maxChildren === 2 && this.isBstMode && typeof val === 'number') {
      let curr = this.root;
      while (curr) {
        path.push(curr);
        if (curr.value === val) return { found: curr, path };
        if (val < curr.value) curr = curr.left;
        else curr = curr.right;
      }
      return { found: null, path };
    } else {
      const queue = [this.root];
      while (queue.length > 0) {
        const curr = queue.shift();
        path.push(curr);
        if (curr.value == val) return { found: curr, path };
        for (const c of curr.getChildren()) {
          queue.push(c);
        }
      }
      return { found: null, path };
    }
  }

  deleteNode(nodeToDelete) {
    if (!nodeToDelete) return false;

    if (nodeToDelete === this.root) {
      const children = nodeToDelete.getChildren();
      if (children.length === 0) {
        this.root = null;
        return true;
      } else if (children.length === 1) {
        this.root = children[0];
        this.root.parent = null;
        return true;
      } else {
        let succ = children[children.length - 1];
        while (succ.getChildren().length > 0) {
          succ = succ.getChildren()[0];
        }
        nodeToDelete.value = succ.value;
        return this.deleteNode(succ);
      }
    }

    const parent = nodeToDelete.parent;
    const children = nodeToDelete.getChildren();

    if (children.length === 0) {
      parent.removeChild(nodeToDelete);
      return true;
    } else if (children.length === 1) {
      const child = children[0];
      if (this.maxChildren === 2) {
        if (parent.left === nodeToDelete) parent.left = child;
        else parent.right = child;
      } else {
        const idx = parent.children.indexOf(nodeToDelete);
        parent.children[idx] = child;
      }
      child.parent = parent;
      return true;
    } else {
      let succ = children[children.length - 1];
      while (succ.getChildren().length > 0) {
        succ = succ.getChildren()[0];
      }
      nodeToDelete.value = succ.value;
      return this.deleteNode(succ);
    }
  }

  // ================= RECORRIDOS =================
  preorder(startNode = null) {
    const res = [];
    const node = startNode || this.root;
    if (!node) return res;

    function rec(curr) {
      if (!curr) return;
      res.push(curr);
      if (curr.maxChildren === 2) {
        if (curr.left) rec(curr.left);
        if (curr.right) rec(curr.right);
      } else {
        for (const c of curr.children) rec(c);
      }
    }
    rec(node);
    return res;
  }

  inorder(startNode = null) {
    const res = [];
    const node = startNode || this.root;
    if (!node) return res;

    if (this.maxChildren === 2) {
      function recBin(curr) {
        if (!curr) return;
        if (curr.left) recBin(curr.left);
        res.push(curr);
        if (curr.right) recBin(curr.right);
      }
      recBin(node);
    } else {
      function recNary(curr) {
        if (!curr) return;
        const children = curr.getChildren();
        if (children.length > 0) recNary(children[0]);
        res.push(curr);
        for (let i = 1; i < children.length; i++) {
          recNary(children[i]);
        }
      }
      recNary(node);
    }
    return res;
  }

  postorder(startNode = null) {
    const res = [];
    const node = startNode || this.root;
    if (!node) return res;

    function rec(curr) {
      if (!curr) return;
      if (curr.maxChildren === 2) {
        if (curr.left) rec(curr.left);
        if (curr.right) rec(curr.right);
      } else {
        for (const c of curr.children) rec(c);
      }
      res.push(curr);
    }
    rec(node);
    return res;
  }

  levelOrder(startNode = null) {
    const res = [];
    const node = startNode || this.root;
    if (!node) return res;

    const queue = [node];
    while (queue.length > 0) {
      const curr = queue.shift();
      res.push(curr);
      for (const c of curr.getChildren()) {
        queue.push(c);
      }
    }
    return res;
  }

  // ================= CÁLCULO DE POSICIONES EN CANVAS =================
  calculateLayout(canvasWidth, canvasHeight, minNodeDist = 58) {
    if (!this.root) return { positions: new Map(), bounds: { minX: 0, maxX: 0, minY: 0, maxY: 0 } };

    // 1. Calcular profundidades
    let maxDepth = 0;
    function calcDepth(n, d) {
      n.depth = d;
      if (d > maxDepth) maxDepth = d;
      for (const c of n.getChildren()) {
        calcDepth(c, d + 1);
      }
    }
    calcDepth(this.root, 0);

    // 2. Asignar X relativa unitaria
    if (this.maxChildren === 2) {
      let idx = 0;
      function assignBinX(n) {
        if (!n) return;
        if (n.left) assignBinX(n.left);
        n.unitX = idx++;
        if (n.right) assignBinX(n.right);
      }
      assignBinX(this.root);
    } else {
      let leafIdx = 0;
      function assignNaryX(n) {
        const children = n.getChildren();
        if (children.length === 0) {
          n.unitX = leafIdx++;
        } else {
          for (const c of children) assignNaryX(c);
          n.unitX = (children[0].unitX + children[children.length - 1].unitX) / 2.0;
        }
      }
      assignNaryX(this.root);
    }

    // 3. Espaciado dinámico
    const allUnits = [];
    function collect(n) {
      allUnits.push(n.unitX);
      for (const c of n.getChildren()) collect(c);
    }
    collect(this.root);

    const minUnit = Math.min(...allUnits);
    const maxUnit = Math.max(...allUnits);
    const unitSpan = Math.max(1, maxUnit - minUnit);

    const spacingX = Math.max(minNodeDist, Math.min(110, (canvasWidth - 80) / unitSpan));
    const spacingY = Math.max(75, Math.min(100, (canvasHeight - 140) / Math.max(1, maxDepth)));

    const startX = Math.max(50, (canvasWidth - unitSpan * spacingX) / 2) - minUnit * spacingX;
    const startY = 70;

    const positions = new Map();
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;

    function assignPixels(n) {
      const px = startX + n.unitX * spacingX;
      const py = startY + n.depth * spacingY;
      n.x = px;
      n.y = py;
      positions.set(n, { x: px, y: py });

      if (px < minX) minX = px;
      if (px > maxX) maxX = px;
      if (py < minY) minY = py;
      if (py > maxY) maxY = py;

      for (const c of n.getChildren()) assignPixels(c);
    }
    assignPixels(this.root);

    return { positions, bounds: { minX, maxX, minY, maxY } };
  }
}
