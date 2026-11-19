# 🌳 Beyker - Visualizador y Simulador de Árboles (Escritorio & Móvil APK)

**Beyker** es una aplicación interactiva para la creación, visualización, manipulación y recorrido animado paso a paso de **Árboles Binarios (ABB)** y **Árboles N-Arios (Grado Configurable)**.

Desarrollada con soporte multiplataforma:
- 💻 **Versión de Escritorio:** Desarrollada en **Python (Tkinter)**.
- 📱 **Versión Móvil & APK:** Diseñada para **Smartphones y Tablets (PWA & Android Studio APK)** con soporte de gestos táctiles y paleta de colores personalizable.

---

## 🌟 Características Principales de Beyker

### 🌿 1. Cantidad de Ramas o Hijos Configurable (Grado N)
- Elige dinámicamente el límite de ramas por nodo:
  - `2 (Binario)`
  - `3 (Ternario)`
  - `4 (Cuaternario)`
  - `5 (Quinario)`
  - `Sin Límite (N-ario general)`
- **Inserción Directa en Ramas:** Haz clic o toca cualquier nodo para seleccionarlo y agregarle un hijo directamente.
- **Inserción Automática:** Inserción por niveles (balanceada) o modo ABB (Árbol Binario de Búsqueda).
- **Generador Masivo:** Crea árboles completos indicando la cantidad de ramas y nodos deseados.

### 🎬 2. Recorridos Interactivos Paso a Paso ("Al hacer clic pueda recorrer")
- **Preorden (RID):** Raíz ➔ Hijos (de izquierda a derecha).
- **Inorden (IRD):** Izquierda ➔ Raíz ➔ Derecha (o Primer Hijo ➔ Raíz ➔ Resto).
- **Postorden (IDR):** Hijos ➔ Raíz.
- **Por Niveles (BFS):** Nivel por nivel de arriba hacia abajo.
- **Animación con Iluminación:** Los nodos se iluminan en color dorado con anillos de brillo y efecto de pulso.
- **Controles Multimedia:** Reproducir, Pausar, Siguiente Paso (clic a clic) y control de velocidad.
- **Secuencia en Tiempo Real:** Muestra la ruta completa recorrida con flechas y chips interactivos.

### 🎨 3. Temas y Personalización de Colores (Versión Móvil)
- 6 Temas visuales integrados: `Modern Light`, `OLED Dark`, `Cyberpunk Neon`, `Sunset Gold`, `Emerald Forest` y `Pastel Candy`.
- Selectores de color personalizados para la Raíz, Nivel 1, Nivel 2 y Nodo Activo.

---

## 🚀 Cómo Ejecutar

### 💻 Versión de Escritorio (Python)
Desde PowerShell o tu terminal:
```bash
python arbol.py
```

### 📱 Versión Móvil (PC o Celular vía Wi-Fi)
```bash
cd mobile_app
python server.py
```
Abre la dirección que te indique en el navegador de tu computadora o en el Google Chrome de tu teléfono móvil.

### 📦 Generar Archivo `.apk` para Android
Abre la carpeta `mobile_app/android_project/` en **Android Studio** y selecciona:
`Build > Build Bundle(s) / APK(s) > Build APK(s)`.

---

## 👤 Autor
Desarrollado por **Beyker** (`beymarcruz9`).
