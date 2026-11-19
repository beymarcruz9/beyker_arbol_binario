/**
 * ============================================================================
 * LÓGICA DE INTERACCIÓN MÓVIL, CANVAS, GESTOS TÁCTILES Y TEMAS
 * ============================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  // Inicialización del modelo
  const tree = new TreeModel(2);
  let selectedNode = null;
  let layoutData = { positions: new Map() };

  // Estado de transformación del Canvas (Zoom y Pan)
  let scale = 1.0;
  let panX = 0;
  let panY = 0;
  let isDragging = false;
  let touchStartDist = 0;
  let lastTouchX = 0;
  let lastTouchY = 0;
  let tapStartTime = 0;

  // Estado de animación de recorridos
  let traversalQueue = [];
  let traversalIndex = 0;
  let traversalTypeName = '';
  let isPlaying = false;
  let animationTimer = null;
  let visitedSet = new Set();
  let activeNode = null;
  let hapticsEnabled = true;

  // Elementos del DOM
  const canvas = document.getElementById('tree-canvas');
  const ctx = canvas.getContext('2d');
  const canvasContainer = document.getElementById('canvas-container');

  const nodeInput = document.getElementById('node-input');
  const btnInsert = document.getElementById('btn-insert');
  const btnSearch = document.getElementById('btn-search');
  const btnClearQuick = document.getElementById('btn-clear-quick');
  const btnGenerateQuick = document.getElementById('btn-generate-quick');

  const selectedCard = document.getElementById('selected-card');
  const selectedVal = document.getElementById('selected-val');
  const selectedDetails = document.getElementById('selected-details');
  const btnCloseSel = document.getElementById('btn-close-sel');
  const btnDeleteSel = document.getElementById('btn-delete-sel');
  const btnAddChildSel = document.getElementById('btn-add-child-sel');
  const btnTraverseSub = document.getElementById('btn-traverse-sub');

  const traversalBanner = document.getElementById('traversal-banner');
  const traversalTitle = document.getElementById('traversal-title');
  const traversalProgress = document.getElementById('traversal-progress');
  const traversalChips = document.getElementById('traversal-chips');
  const btnPlayPause = document.getElementById('btn-play-pause');
  const iconPlay = document.getElementById('icon-play');
  const iconPause = document.getElementById('icon-pause');
  const btnStepNext = document.getElementById('btn-step-next');
  const btnStop = document.getElementById('btn-stop');
  const traversalSpeed = document.getElementById('traversal-speed');

  const btnMenu = document.getElementById('btn-menu');
  const drawer = document.getElementById('drawer');
  const drawerBackdrop = document.getElementById('drawer-backdrop');
  const btnCloseDrawer = document.getElementById('btn-close-drawer');
  const badgeMode = document.getElementById('badge-mode');
  const chkBstMode = document.getElementById('chk-bst-mode');

  const btnZoomIn = document.getElementById('btn-zoom-in');
  const btnZoomOut = document.getElementById('btn-zoom-out');
  const btnZoomReset = document.getElementById('btn-zoom-reset');
  const btnCenterView = document.getElementById('btn-center-view');
  const btnThemeQuick = document.getElementById('btn-theme-quick');

  const modalGenerate = document.getElementById('modal-generate');
  const modalBackdrop = document.getElementById('modal-backdrop');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const btnModalCancel = document.getElementById('btn-modal-cancel');
  const btnModalConfirm = document.getElementById('btn-modal-confirm');
  const modalBranchSelect = document.getElementById('modal-branch-select');
  const modalCountInput = document.getElementById('modal-count-input');
  const modalValuesSelect = document.getElementById('modal-values-select');

  const btnExportImg = document.getElementById('btn-export-img');
  const btnHapticsToggle = document.getElementById('btn-haptics-toggle');
  const hapticsStatus = document.getElementById('haptics-status');

  // Ajustar tamaño del Canvas a la pantalla móvil (Retina / High-DPI display)
  function resizeCanvas() {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvasContainer.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;
    ctx.scale(dpr, dpr);
    render();
  }
  window.addEventListener('resize', resizeCanvas);

  // ================= DIBUJADO Y RENDERIZADO =================
  function render() {
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.width / dpr;
    const h = canvas.height / dpr;

    ctx.save();
    ctx.clearRect(0, 0, w, h);

    if (!tree.root) {
      ctx.restore();
      ctx.save();
      ctx.font = '600 15px var(--font-sans)';
      ctx.fillStyle = getComputedStyle(document.body).getPropertyValue('--text-secondary').trim() || '#64748b';
      ctx.textAlign = 'center';
      ctx.fillText('🌳 Árbol vacío', w / 2, h / 2 - 12);
      ctx.font = '400 12px var(--font-sans)';
      ctx.fillText('Escribe un número arriba o presiona Llenar', w / 2, h / 2 + 12);
      ctx.restore();
      return;
    }

    // Calcular distribución
    layoutData = tree.calculateLayout(w, h);

    // Aplicar transformaciones táctiles (Pan y Zoom)
    ctx.translate(panX + w / 2, panY + 40);
    ctx.scale(scale, scale);
    ctx.translate(-w / 2, -40);

    // Obtener variables de colores actuales según el tema
    const style = getComputedStyle(document.body);
    const colorEdge = style.getPropertyValue('--edge-color').trim() || '#475569';
    const colorEdgeActive = style.getPropertyValue('--edge-active').trim() || '#f59e0b';
    const colorRoot = document.getElementById('picker-root').value || style.getPropertyValue('--node-root').trim();
    const colorL1 = document.getElementById('picker-l1').value || style.getPropertyValue('--node-l1').trim();
    const colorL2 = document.getElementById('picker-l2').value || style.getPropertyValue('--node-l2').trim();
    const colorActive = document.getElementById('picker-active').value || style.getPropertyValue('--node-active').trim();
    const colorVisited = style.getPropertyValue('--node-visited').trim() || '#fed7aa';
    const colorSelected = style.getPropertyValue('--node-selected').trim() || '#a5f3fc';

    // 1. Dibujar líneas de conexión (Ramas)
    function drawEdges(node) {
      const pos = layoutData.positions.get(node);
      if (!pos) return;

      for (const child of node.getChildren()) {
        const cPos = layoutData.positions.get(child);
        if (cPos) {
          const isEdgeActive = (visitedSet.has(node) && visitedSet.has(child)) ||
                               (activeNode === node || activeNode === child);

          ctx.beginPath();
          ctx.moveTo(pos.x, pos.y);
          ctx.lineTo(cPos.x, cPos.y);
          ctx.strokeStyle = isEdgeActive ? colorEdgeActive : colorEdge;
          ctx.lineWidth = isEdgeActive ? 3.5 : 2.2;
          ctx.lineCap = 'round';
          ctx.stroke();

          drawEdges(child);
        }
      }
    }
    drawEdges(tree.root);

    // 2. Dibujar nodos
    const radius = 22;

    function drawNodes(node) {
      const pos = layoutData.positions.get(node);
      if (!pos) return;

      let fill = colorRoot;
      let stroke = '#1d4ed8';
      let textColor = '#ffffff';

      // Asignación de color según profundidad
      if (node.depth === 1) { fill = colorL1; stroke = '#be185d'; }
      else if (node.depth === 2) { fill = colorL2; stroke = '#b45309'; }
      else if (node.depth >= 3) { fill = '#10b981'; stroke = '#047857'; }

      // Estado activo / visitado / seleccionado
      if (node === activeNode) {
        fill = colorActive;
        stroke = '#ca8a04';
        textColor = '#713f12';
      } else if (node === selectedNode) {
        fill = colorSelected;
        stroke = '#0891b2';
        textColor = '#0e7490';
      } else if (visitedSet.has(node)) {
        fill = colorVisited;
        stroke = '#ea580c';
        textColor = '#7c2d12';
      }

      // Anillo de brillo pulsante en nodo activo
      if (node === activeNode) {
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, radius + 6, 0, Math.PI * 2);
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 2.5;
        ctx.setLineDash([4, 4]);
        ctx.stroke();
        ctx.setLineDash([]);
      }

      // Sombra sutil del nodo
      ctx.beginPath();
      ctx.arc(pos.x + 1.5, pos.y + 2, radius, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(0, 0, 0, 0.12)';
      ctx.fill();

      // Círculo del nodo
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
      ctx.fillStyle = fill;
      ctx.fill();
      ctx.strokeStyle = stroke;
      ctx.lineWidth = (node === activeNode || node === selectedNode) ? 3.5 : 2;
      ctx.stroke();

      // Texto del valor
      ctx.font = '700 13px var(--font-sans)';
      ctx.fillStyle = textColor;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(String(node.value), pos.x, pos.y);

      for (const child of node.getChildren()) {
        drawNodes(child);
      }
    }
    drawNodes(tree.root);

    ctx.restore();
  }

  // ================= GESTOS TÁCTILES MÓVILES (PINCH-TO-ZOOM, PAN & TAP) =================
  canvasContainer.addEventListener('touchstart', (e) => {
    if (e.touches.length === 1) {
      isDragging = true;
      lastTouchX = e.touches[0].clientX;
      lastTouchY = e.touches[0].clientY;
      tapStartTime = Date.now();
    } else if (e.touches.length === 2) {
      isDragging = false;
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      touchStartDist = Math.hypot(dx, dy);
    }
  }, { passive: true });

  canvasContainer.addEventListener('touchmove', (e) => {
    if (e.touches.length === 1 && isDragging) {
      const dx = e.touches[0].clientX - lastTouchX;
      const dy = e.touches[0].clientY - lastTouchY;
      panX += dx;
      panY += dy;
      lastTouchX = e.touches[0].clientX;
      lastTouchY = e.touches[0].clientY;
      render();
    } else if (e.touches.length === 2) {
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      const dist = Math.hypot(dx, dy);
      if (touchStartDist > 0) {
        const factor = dist / touchStartDist;
        scale = Math.max(0.4, Math.min(2.5, scale * factor));
        touchStartDist = dist;
        render();
      }
    }
  }, { passive: true });

  canvasContainer.addEventListener('touchend', (e) => {
    if (isDragging && e.changedTouches.length === 1) {
      const duration = Date.now() - tapStartTime;
      const distMoved = Math.hypot(e.changedTouches[0].clientX - lastTouchX, e.changedTouches[0].clientY - lastTouchY);
      if (duration < 250 && distMoved < 15) {
        handleTap(e.changedTouches[0].clientX, e.changedTouches[0].clientY);
      }
    }
    isDragging = false;
  });

  // Soporte de ratón para escritorio / testing en PC
  let isMouseDown = false;
  let mouseStartX = 0, mouseStartY = 0;
  canvasContainer.addEventListener('mousedown', (e) => {
    isMouseDown = true;
    mouseStartX = e.clientX;
    mouseStartY = e.clientY;
    lastTouchX = e.clientX;
    lastTouchY = e.clientY;
    tapStartTime = Date.now();
  });

  window.addEventListener('mousemove', (e) => {
    if (!isMouseDown) return;
    panX += e.clientX - lastTouchX;
    panY += e.clientY - lastTouchY;
    lastTouchX = e.clientX;
    lastTouchY = e.clientY;
    render();
  });

  window.addEventListener('mouseup', (e) => {
    if (isMouseDown) {
      const duration = Date.now() - tapStartTime;
      const distMoved = Math.hypot(e.clientX - mouseStartX, e.clientY - mouseStartY);
      if (duration < 250 && distMoved < 10) {
        handleTap(e.clientX, e.clientY);
      }
    }
    isMouseDown = false;
  });

  canvasContainer.addEventListener('wheel', (e) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    scale = Math.max(0.4, Math.min(2.5, scale * factor));
    render();
  }, { passive: false });

  // Detección de toque en nodo
  function handleTap(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.width / dpr;

    // Convertir de coordenadas de pantalla a espacio de árbol
    const screenX = clientX - rect.left;
    const screenY = clientY - rect.top;

    const treeX = (screenX - (panX + w / 2)) / scale + w / 2;
    const treeY = (screenY - (panY + 40)) / scale + 40;

    let clicked = null;
    const radius = 25;

    for (const [node, pos] of layoutData.positions.entries()) {
      const d = Math.hypot(treeX - pos.x, treeY - pos.y);
      if (d <= radius) {
        clicked = node;
        break;
      }
    }

    if (clicked) {
      triggerHaptic(20);
      selectedNode = (selectedNode === clicked) ? null : clicked;
    } else {
      selectedNode = null;
    }
    updateSelectedCard();
    render();
  }

  function updateSelectedCard() {
    if (!selectedNode) {
      selectedCard.classList.add('hidden');
      return;
    }
    selectedVal.textContent = String(selectedNode.value);
    const maxStr = tree.maxChildren !== null ? String(tree.maxChildren) : '∞';
    const childrenCount = selectedNode.countChildren();
    selectedDetails.textContent = `Nivel ${selectedNode.depth} • ${childrenCount}/${maxStr} ramas ocupadas • Padre: ${selectedNode.parent ? selectedNode.parent.value : 'Raíz'}`;
    selectedCard.classList.remove('hidden');
  }

  function triggerHaptic(duration = 25) {
    if (hapticsEnabled && navigator.vibrate) {
      try { navigator.vibrate(duration); } catch (_) {}
    }
  }

  function showToast(msg) {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-msg');
    toastMsg.textContent = msg;
    toast.classList.remove('hidden');
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => toast.classList.add('hidden'), 2200);
  }

  // ================= INSERCIÓN Y ACCIONES BÁSICAS =================
  function parseVal(str) {
    const s = str.trim();
    if (!s) return null;
    const n = Number(s);
    return isNaN(n) ? s : n;
  }

  btnInsert.addEventListener('click', () => {
    const val = parseVal(nodeInput.value);
    if (val === null) {
      showToast('⚠️ Ingresa un número o valor');
      nodeInput.focus();
      return;
    }

    stopAnimation();

    let result;
    if (selectedNode) {
      const maxC = tree.maxChildren;
      if (maxC !== null && selectedNode.countChildren() >= maxC) {
        showToast(`El nodo ${selectedNode.value} ya tiene el máximo de ${maxC} ramas.`);
        return;
      }
      result = tree.insertChildOf(selectedNode, val);
    } else {
      if (tree.maxChildren === 2 && tree.isBstMode && typeof val === 'number') {
        result = tree.insertBst(val);
      } else {
        result = tree.insertLevelOrder(val);
      }
    }

    if (!result.ok) {
      showToast(`El valor '${val}' ya existe o no se pudo insertar.`);
    } else {
      showToast(`Nodo '${val}' insertado correctamente`);
      nodeInput.value = '';
      selectedNode = result.node;
      updateSelectedCard();
      triggerHaptic(30);
    }
    render();
  });

  nodeInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') btnInsert.click();
  });

  btnSearch.addEventListener('click', () => {
    const val = parseVal(nodeInput.value);
    if (val === null) {
      showToast('Ingresa el valor a buscar');
      return;
    }
    stopAnimation();

    const { found, path } = tree.search(val);
    if (path.length === 0) {
      showToast('Árbol vacío');
      return;
    }

    traversalQueue = path;
    traversalIndex = 0;
    traversalTypeName = `Búsqueda de '${val}'`;
    visitedSet.clear();
    startAnimation(true, found);
  });

  btnClearQuick.addEventListener('click', () => {
    if (confirm('¿Eliminar todos los nodos del árbol?')) {
      stopAnimation();
      tree.clear();
      selectedNode = null;
      updateSelectedCard();
      showToast('Árbol limpiado');
      render();
    }
  });

  // Acciones de la tarjeta seleccionada
  btnCloseSel.addEventListener('click', () => {
    selectedNode = null;
    updateSelectedCard();
    render();
  });

  btnDeleteSel.addEventListener('click', () => {
    if (!selectedNode) return;
    const v = selectedNode.value;
    stopAnimation();
    tree.deleteNode(selectedNode);
    selectedNode = null;
    updateSelectedCard();
    showToast(`Nodo '${v}' eliminado`);
    render();
  });

  btnAddChildSel.addEventListener('click', () => {
    nodeInput.focus();
    showToast(`Escribe el valor del nuevo hijo para '${selectedNode.value}'`);
  });

  btnTraverseSub.addEventListener('click', () => {
    if (!selectedNode) return;
    startTraversal('preorder', selectedNode);
  });

  // ================= RECORRIDOS ANIMADOS INTERACTIVOS =================
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const type = btn.dataset.traversal;
      startTraversal(type, selectedNode);
    });
  });

  function startTraversal(type, startNode = null) {
    if (!tree.root) {
      showToast('El árbol no tiene nodos para recorrer');
      return;
    }
    stopAnimation();

    if (type === 'preorder') {
      traversalQueue = tree.preorder(startNode);
      traversalTypeName = 'Preorden (RID)';
    } else if (type === 'inorder') {
      traversalQueue = tree.inorder(startNode);
      traversalTypeName = 'Inorden (IRD)';
    } else if (type === 'postorder') {
      traversalQueue = tree.postorder(startNode);
      traversalTypeName = 'Postorden (IDR)';
    } else if (type === 'levelorder') {
      traversalQueue = tree.levelOrder(startNode);
      traversalTypeName = 'Por Niveles (BFS)';
    }

    traversalIndex = 0;
    visitedSet.clear();
    startAnimation();
  }

  function startAnimation(isSearch = false, targetNode = null) {
    isPlaying = true;
    iconPlay.classList.add('hidden');
    iconPause.classList.remove('hidden');
    traversalTitle.textContent = traversalTypeName;
    renderChips();
    animateStep(isSearch, targetNode);
  }

  function animateStep(isSearch = false, targetNode = null) {
    if (!isPlaying) return;

    if (traversalIndex >= traversalQueue.length) {
      isPlaying = false;
      iconPlay.classList.remove('hidden');
      iconPause.classList.add('hidden');
      activeNode = null;
      if (isSearch) {
        showToast(targetNode ? `¡Encontrado nodo '${targetNode.value}'!` : 'Nodo no encontrado');
      } else {
        showToast(`Recorrido ${traversalTypeName} completado`);
      }
      render();
      return;
    }

    const curr = traversalQueue[traversalIndex];
    activeNode = curr;
    visitedSet.add(curr);
    triggerHaptic(20);

    traversalProgress.textContent = `Paso ${traversalIndex + 1} / ${traversalQueue.length}`;
    updateChipsState();
    render();

    traversalIndex++;

    if (isSearch && curr === targetNode) {
      isPlaying = false;
      iconPlay.classList.remove('hidden');
      iconPause.classList.add('hidden');
      showToast(`¡Nodo '${targetNode.value}' encontrado!`);
      return;
    }

    const delay = Number(traversalSpeed.value);
    animationTimer = setTimeout(() => animateStep(isSearch, targetNode), delay);
  }

  function renderChips() {
    traversalChips.innerHTML = '';
    traversalQueue.forEach((n, idx) => {
      const chip = document.createElement('span');
      chip.className = 'traversal-chip';
      chip.id = `chip-step-${idx}`;
      chip.textContent = String(n.value);
      traversalChips.appendChild(chip);
    });
  }

  function updateChipsState() {
    document.querySelectorAll('.traversal-chip').forEach((c, idx) => {
      if (idx === traversalIndex) {
        c.className = 'traversal-chip active';
        c.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
      } else if (idx < traversalIndex) {
        c.className = 'traversal-chip visited';
      } else {
        c.className = 'traversal-chip';
      }
    });
  }

  btnPlayPause.addEventListener('click', () => {
    if (!traversalQueue.length) {
      startTraversal('preorder');
      return;
    }
    if (isPlaying) {
      isPlaying = false;
      clearTimeout(animationTimer);
      iconPlay.classList.remove('hidden');
      iconPause.classList.add('hidden');
    } else {
      if (traversalIndex >= traversalQueue.length) {
        traversalIndex = 0;
        visitedSet.clear();
      }
      isPlaying = true;
      iconPlay.classList.add('hidden');
      iconPause.classList.remove('hidden');
      animateStep();
    }
  });

  btnStepNext.addEventListener('click', () => {
    if (!traversalQueue.length) {
      startTraversal('preorder');
      return;
    }
    isPlaying = false;
    clearTimeout(animationTimer);
    iconPlay.classList.remove('hidden');
    iconPause.classList.add('hidden');

    if (traversalIndex >= traversalQueue.length) {
      traversalIndex = 0;
      visitedSet.clear();
    }
    isPlaying = true;
    animateStep();
    isPlaying = false;
  });

  btnStop.addEventListener('click', stopAnimation);

  function stopAnimation() {
    isPlaying = false;
    clearTimeout(animationTimer);
    traversalQueue = [];
    traversalIndex = 0;
    visitedSet.clear();
    activeNode = null;
    iconPlay.classList.remove('hidden');
    iconPause.classList.add('hidden');
    traversalTitle.textContent = 'Recorrido: Inactivo';
    traversalProgress.textContent = 'Paso 0 / 0';
    traversalChips.innerHTML = '<span class="chip-placeholder">Haz clic en Preorden, Inorden, Postorden o Niveles</span>';
    render();
  }

  // ================= ZOOM Y PAN CONTROLES =================
  btnZoomIn.addEventListener('click', () => {
    scale = Math.min(2.5, scale * 1.2);
    render();
  });

  btnZoomOut.addEventListener('click', () => {
    scale = Math.max(0.4, scale / 1.2);
    render();
  });

  btnZoomReset.addEventListener('click', () => {
    scale = 1.0;
    panX = 0;
    panY = 0;
    render();
  });

  btnCenterView.addEventListener('click', () => {
    scale = 1.0;
    panX = 0;
    panY = 0;
    render();
    showToast('Vista centrada');
  });

  // ================= DRAWER Y CONFIGURACIÓN =================
  btnMenu.addEventListener('click', () => {
    drawer.classList.remove('hidden');
    drawerBackdrop.classList.remove('hidden');
  });

  function closeDrawer() {
    drawer.classList.add('hidden');
    drawerBackdrop.classList.add('hidden');
  }
  btnCloseDrawer.addEventListener('click', closeDrawer);
  drawerBackdrop.addEventListener('click', closeDrawer);

  // Selector de ramas (Grado del árbol)
  document.querySelectorAll('.branch-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.branch-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const b = Number(btn.dataset.branches);
      tree.maxChildren = b === 0 ? null : b;
      tree.isBstMode = b === 2 && chkBstMode.checked;
      badgeMode.textContent = b === 0 ? 'N-ario Libre' : `${b === 2 ? 'Binario' : b === 3 ? 'Ternario' : b === 4 ? 'Cuaternario' : 'Quinario'} (${b} ramas)`;
      showToast(`Modo cambiado a: ${badgeMode.textContent}`);
      render();
    });
  });

  chkBstMode.addEventListener('change', () => {
    tree.isBstMode = chkBstMode.checked;
    showToast(chkBstMode.checked ? 'Modo ABB activado (Menores a la izquierda, mayores a la derecha)' : 'Inserción normal por niveles activada');
  });

  // Temas de colores
  document.querySelectorAll('.theme-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.theme-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      const themeClass = card.dataset.theme;
      document.body.className = themeClass;
      render();
      showToast(`Tema aplicado: ${card.querySelector('span').textContent}`);
    });
  });

  // Cambio rápido de tema desde el header
  const quickThemes = ['theme-modern', 'theme-dark', 'theme-cyberpunk', 'theme-sunset', 'theme-forest', 'theme-pastel'];
  let currentThemeIdx = 0;
  btnThemeQuick.addEventListener('click', () => {
    currentThemeIdx = (currentThemeIdx + 1) % quickThemes.length;
    document.body.className = quickThemes[currentThemeIdx];
    document.querySelectorAll('.theme-card').forEach(c => {
      c.classList.toggle('active', c.dataset.theme === quickThemes[currentThemeIdx]);
    });
    render();
  });

  // Pickers de colores individuales
  ['picker-root', 'picker-l1', 'picker-l2', 'picker-active'].forEach(id => {
    document.getElementById(id).addEventListener('input', render);
  });

  // Toggle de vibración
  btnHapticsToggle.addEventListener('click', () => {
    hapticsEnabled = !hapticsEnabled;
    hapticsStatus.textContent = `Vibración Táctil: ${hapticsEnabled ? 'ON' : 'OFF'}`;
    triggerHaptic(50);
  });

  // Exportar como PNG
  btnExportImg.addEventListener('click', () => {
    const link = document.createElement('a');
    link.download = 'arbol-binario.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
    showToast('Imagen PNG descargada con éxito');
  });

  // ================= MODAL GENERADOR =================
  btnGenerateQuick.addEventListener('click', () => {
    modalGenerate.classList.remove('hidden');
    modalBackdrop.classList.remove('hidden');
  });

  function closeModal() {
    modalGenerate.classList.add('hidden');
    modalBackdrop.classList.add('hidden');
  }
  btnCloseModal.addEventListener('click', closeModal);
  btnModalCancel.addEventListener('click', closeModal);
  modalBackdrop.addEventListener('click', closeModal);

  btnModalConfirm.addEventListener('click', () => {
    const branches = Number(modalBranchSelect.value);
    const count = Math.max(1, Math.min(40, Number(modalCountInput.value) || 7));
    const isRandom = modalValuesSelect.value === 'random';

    tree.maxChildren = branches;
    tree.isBstMode = false;
    tree.clear();

    const values = [];
    if (isRandom) {
      const set = new Set();
      while (set.size < count) set.add(Math.floor(Math.random() * 95) + 5);
      values.push(...Array.from(set));
    } else {
      for (let i = 1; i <= count; i++) values.push(i * 10);
    }

    values.forEach(v => tree.insertLevelOrder(v));

    selectedNode = null;
    updateSelectedCard();
    badgeMode.textContent = `${branches === 2 ? 'Binario' : branches === 3 ? 'Ternario' : 'N-ario'} (${branches} ramas)`;
    closeModal();
    showToast(`Árbol generado con ${count} nodos y ${branches} ramas por nodo`);
    render();
  });

  // ================= EJEMPLOS PREDEFINIDOS =================
  document.getElementById('ex-photo').addEventListener('click', () => {
    loadPhotoExample();
    closeDrawer();
  });

  document.getElementById('ex-ternary').addEventListener('click', () => {
    loadTernaryExample();
    closeDrawer();
  });

  document.getElementById('ex-quaternary').addEventListener('click', () => {
    loadQuaternaryExample();
    closeDrawer();
  });

  function loadPhotoExample() {
    stopAnimation();
    tree.maxChildren = 2;
    tree.isBstMode = true;
    tree.clear();

    // 10 -> [6, 15]
    // 6 -> [3, 7]
    // 15 -> [12, 18]
    const r = new TreeNode(10, 2);
    tree.root = r;

    const n6 = new TreeNode(6, 2);
    const n15 = new TreeNode(15, 2);
    r.left = n6; n6.parent = r;
    r.right = n15; n15.parent = r;

    const n3 = new TreeNode(3, 2);
    const n7 = new TreeNode(7, 2);
    n6.left = n3; n3.parent = n6;
    n6.right = n7; n7.parent = n6;

    const n12 = new TreeNode(12, 2);
    const n18 = new TreeNode(18, 2);
    n15.left = n12; n12.parent = n15;
    n15.right = n18; n18.parent = n15;

    selectedNode = null;
    updateSelectedCard();
    badgeMode.textContent = 'Binario (2 ramas)';
    showToast('Árbol de la imagen cargado');
    render();
  }

  function loadTernaryExample() {
    stopAnimation();
    tree.maxChildren = 3;
    tree.isBstMode = false;
    tree.clear();

    const r = new TreeNode(10, 3);
    tree.root = r;

    [5, 15, 25].forEach(v => {
      const c = new TreeNode(v, 3);
      r.addChild(c);
      if (v === 5) [2, 4].forEach(sub => c.addChild(new TreeNode(sub, 3)));
      if (v === 15) [12, 14, 16].forEach(sub => c.addChild(new TreeNode(sub, 3)));
      if (v === 25) [22, 28].forEach(sub => c.addChild(new TreeNode(sub, 3)));
    });

    selectedNode = null;
    updateSelectedCard();
    badgeMode.textContent = 'Ternario (3 ramas)';
    showToast('Árbol ternario cargado');
    render();
  }

  function loadQuaternaryExample() {
    stopAnimation();
    tree.maxChildren = 4;
    tree.isBstMode = false;
    tree.clear();

    const r = new TreeNode('A', 4);
    tree.root = r;

    ['B1', 'B2', 'B3', 'B4'].forEach(v => {
      const c = new TreeNode(v, 4);
      r.addChild(c);
      if (v === 'B1') ['C1', 'C2'].forEach(sub => c.addChild(new TreeNode(sub, 4)));
      if (v === 'B4') ['C3', 'C4', 'C5'].forEach(sub => c.addChild(new TreeNode(sub, 4)));
    });

    selectedNode = null;
    updateSelectedCard();
    badgeMode.textContent = 'Cuaternario (4 ramas)';
    showToast('Árbol cuaternario cargado');
    render();
  }

  // Carga inicial
  resizeCanvas();
  loadPhotoExample();
});
