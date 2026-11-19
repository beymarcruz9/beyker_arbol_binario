# 📱 Árbol Binario & N-Ario - Versión Móvil y Proyecto APK

Esta versión ha sido completamente rediseñada y optimizada para dispositivos móviles (teléfonos y tablets), con soporte de gestos táctiles, personalización de colores, múltiples ramas y generación de formato **APK**.

---

## ⚡ ¿Cómo Probar la App en tu Celular de Inmediato? (Sin esperas)

1. Abre una terminal en esta carpeta (`mobile_app`) y ejecuta:
   ```bash
   python server.py
   ```
2. La terminal te mostrará una dirección URL local (por ejemplo `http://192.168.1.15:8080`).
3. Abre esa dirección en el navegador **Google Chrome** de tu teléfono móvil (conectado al mismo Wi-Fi).
4. **Instalar en el celular:** Toca los tres puntos de Chrome (⋮) y selecciona **"Agregar a la pantalla principal"** o **"Instalar aplicación"**. ¡Se instalará con ícono y pantalla completa como una app nativa!

---

## 📦 ¿Cómo Generar el Archivo `.apk` con Android Studio?

El proyecto nativo de Android ya está listo en la carpeta `android_project/`:

1. Abre **Android Studio** (instalado en tu equipo).
2. Haz clic en **File > Open** y selecciona la carpeta:
   `c:\Users\USUARIO\Documents\BEYKER\SISTEMAS\ESTRUCTURA DE DATOS\arbol_binario\mobile_app\android_project`
3. En el menú superior de Android Studio, haz clic en:
   **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
4. En cuestión de segundos, Android Studio compilará y te mostrará el archivo listo:
   `app-debug.apk`
5. Pasa ese archivo `.apk` a tu celular e instálalo directamente.

---

## 🌟 Novedades y Mejoras Implementadas

### 🎨 1. Opciones Avanzadas de Colores y Temas
- **Temas Predefinidos:**
  - `Modern Light`: Diseño limpio con tonos claros.
  - `OLED Dark`: Modo oscuro puro de bajo consumo para pantallas AMOLED.
  - `Cyberpunk Neon`: Tonos cian, fucsia y púrpura de alto contraste.
  - `Sunset Gold`: Tonos cálidos atardecer.
  - `Emerald Forest`: Tonos verdes naturales y menta.
  - `Pastel Candy`: Colores suaves tipo pastel.
- **Selectores de Color Personalizados:**
  - Puedes cambiar independientemente el color de la Raíz, Nivel 1, Nivel 2 y del nodo activo en el recorrido.

### 🌿 2. Cantidad de Ramas o Hijos (Grado Configurable)
- Selector de ramas por nodo:
  - `2 (Binario)`
  - `3 (Ternario)`
  - `4 (Cuaternario)`
  - `5 (Quinario)`
  - `Sin Límite (N-ario general)`
- **Modo ABB (Árbol Binario de Búsqueda):** Activable o desactivable con un interruptor.
- **Inserción Táctil:** Toca cualquier nodo para seleccionarlo y agrega hijos directamente a esa rama.
- **Generador Masivo:** Crea árboles completos con la cantidad de ramas y nodos que elijas.

### 🎬 3. Recorridos Interactivos Táctiles ("Al hacer clic pueda recorrer")
- **Barra de navegación inferior móvil:**
  - Preorden (RID)
  - Inorden (IRD)
  - Postorden (IDR)
  - Por Niveles (BFS)
- **Animación con Brillo y Pulso:** Los nodos se van iluminando dinámicamente con anillos luminosos.
- **Controles Multimedia:** Play, Pause, Siguiente Paso (clic a clic) y control de velocidad.
- **Lista de Chips Deslizables:** Muestra en tiempo real cada paso del recorrido y se desplaza automáticamente.
- **Retroalimentación Táctil (Vibración):** Vibra suavemente en tu teléfono al visitar cada nodo.

### 🖐️ 4. Gestos Táctiles Móviles
- **Pinch-to-Zoom:** Acerca o aleja pellizcando la pantalla con dos dedos.
- **Arrastre (Pan):** Desplaza el lienzo con un dedo para explorar árboles grandes.
- **Toque Directo:** Toca cualquier nodo para ver sus detalles (nivel, hijos ocupados, padre) y opciones rápidas.
- **Exportar Imagen:** Botón para guardar el árbol como imagen PNG en tu galería.
