# 🌟 Pokemon Shiny Hunting Bot - Sistema Automatizado

Bot completamente automatizado para cazar Pokemon shinies en emuladores de Game Boy Advance (Pokémon Ruby/Sapphire). El sistema abre múltiples emuladores, navega automáticamente hasta encontrar Pokemon, detecta shinies usando comparación de imágenes y te permite capturarlos sin perder el progreso.

## ✨ Características

- 🎮 **Múltiples emuladores simultáneos** - Hasta 4 emuladores para 4x probabilidades
- 🤖 **Navegación completamente automática** - Desde menú inicial hasta combate
- 🔍 **Detección inteligente de shinies** - Usando análisis de histogramas de color
- 💾 **Screenshots automáticos** - Solo guarda imágenes de shinies encontrados
- 📊 **Estadísticas en tiempo real** - Contador de encuentros, tiempo transcurrido
- 🎯 **Preservación de shinies** - Para cuando encuentra shiny para que puedas capturarlo
- 🧹 **Interface limpia** - Terminal que se actualiza automáticamente

## 📋 Requisitos

### Software Necesario
- **Python 3.8 o superior**
- **Visual Boy Advance-M** (emulador GBA)
- **ROM de Pokémon Ruby/Sapphire**
- **Windows** (el sistema está optimizado para Windows)

### Librerías Python
```bash
opencv-python
mss
numpy
pillow
pyautogui
pywin32
```

## 🚀 Instalación

### Paso 1: Configurar Entorno Virtual
```bash
# Crear entorno virtual
python -m venv pokemon_venv

# Activar entorno virtual (Windows)
pokemon_venv\Scripts\activate

# Instalar dependencias
pip install opencv-python mss numpy pillow pyautogui pywin32
```

### Paso 2: Descargar Archivos del Proyecto
Asegúrate de tener estos archivos en tu carpeta del proyecto:
```
pokemon-bot/
├── main.py
├── Control.py
├── AbrirEmulador.py
├── Comparar_Imagen.py
├── coordinate_selector.py
├── emulator_config_builder.py
├── auto_screenshot_emulators.py
└── README.md
```

### Paso 3: Configurar Emulador y ROM
1. **Instalar Visual Boy Advance-M**
2. **Configurar ruta del emulador** en `AbrirEmulador.py`:
   ```python
   EMULATOR_PATH = r'C:\ruta\a\tu\emulador\visualboyadvance-m'
   ```
3. **Configurar ruta de la ROM** en `AbrirEmulador.py`:
   ```python
   ROM_PATH = r'C:\ruta\a\tu\rom\Pokemon - Ruby Version.gba'
   ```

## ⚙️ Configuración Inicial

### Paso 1: Crear Estructura de Directorios
```bash
mkdir template
mkdir coordinates
mkdir reference
mkdir screenshots
mkdir img_treecko
```

### Paso 2: Configurar Screenshots de Emuladores
```bash
# Abrir emuladores
python main.py
# Detener con Ctrl+C después de que abran

# Tomar screenshots automáticamente
python auto_screenshot_emulators.py
# Opción 3: Tomar screenshots con preview
```

### Paso 3: Configurar Coordenadas de Detección
```bash
python emulator_config_builder.py
```

**Proceso detallado:**
1. **Selecciona "1"** → Configurar coordenadas de emuladores
2. Para cada emulador:
   ```bash
   # Te dirá: "Ejecuta: python coordinate_selector.py img_treecko/emulador1_*.png"
   python coordinate_selector.py img_treecko/emulador1_treecko.png
   ```
3. **En coordinate_selector:**
   - Haz click y arrastra para seleccionar SOLO el sprite del Treecko
   - Anota las coordenadas que aparecen: `(X, Y, Ancho, Alto)`
   - Presiona ESC para cerrar
4. **Vuelve al configurador** e ingresa las coordenadas anotadas
5. **Repite para los 4 emuladores**
6. **Selecciona "2"** → Configurar imagen de referencia
7. **Crea:** `reference/treecko_normal.png` (screenshot pequeño del Treecko normal)
8. **Selecciona "3"** → Guardar configuración

### Paso 4: Crear Templates de Navegación

Necesitas crear 3 imágenes template en la carpeta `template/`:

#### `template/starter_selection.png`
Screenshot de la pantalla donde Birch está en problemas (selección de inicial)

#### `template/treecko_confirmed.png`  
Screenshot de la pantalla donde Treecko está seleccionado

#### `template/treecko_battle_menu.png`
Screenshot del menú de combate con Treecko completamente visible (esta es la clave)

**Ejemplo de captura para treecko_battle_menu.png:**
```
┌─────────────────────────┐
│ TREECKO     Lv. 5      │  ← Esta pantalla
│ HP: 19/19              │
│                        │
│ What should TREECKO do?│
│ ┌───────┬──────────────┐│
│ │FIGHT  │ BAG          ││
│ │POKEMON│ RUN          ││
│ └───────┴──────────────┘│
└─────────────────────────┘
```

## 🎮 Uso del Sistema

### Iniciar Shiny Hunting
```bash
# Activar entorno virtual
pokemon_venv\Scripts\activate

# Ejecutar sistema completo
python main.py
```

### Flujo Automático
1. **✅ Abre 4 emuladores automáticamente**
2. **✅ Navega presionando A hasta selección de inicial**
3. **✅ Selecciona Treecko (mueve izquierda + A)**
4. **✅ Continúa hasta llegar al combate**
5. **✅ Detecta si el Treecko es shiny**
6. **✅ Si NO es shiny → SoftReset y repite**
7. **✅ Si ES shiny → Para y deja emuladores abiertos**

### Cuando Encuentra Shiny
```
🌟🌟🌟 ¡SHINY ENCONTRADO EN EMULADOR X! 🌟🌟🌟
🎮 Los emuladores permanecen ABIERTOS para que puedas:
   • 🎯 Capturar el Pokemon shiny
   • 🏷️  Darle nombre
   • 💾 Guardar el juego
   • 📸 Tomar más screenshots

💡 Presiona Ctrl+C cuando termines de capturar
```

## 🔧 Configuración Avanzada

### Ajustar Umbrales de Detección
En `main.py`, puedes modificar:
```python
similarity_threshold=0.90  # Cambiar si detecta muchos falsos positivos/negativos
```

**Guía de umbrales:**
- `0.95` = Muy estricto (solo shinies muy diferentes)
- `0.90` = Balanceado (recomendado)
- `0.85` = Más sensible (puede detectar falsos positivos)

### Ajustar Velocidad
En `main.py`, puedes modificar delays:
```python
time.sleep(1.5)  # Tiempo entre presionar botones
time.sleep(1.0)  # Tiempo para esperar cambios de pantalla
```

### Cambiar Número de Emuladores
En `AbrirEmulador.py`:
```python
NUM_EMULATORS = 4  # Cambiar a 1, 2, 3, o 4
```

## 🐛 Troubleshooting

### Problema: Similitud 0.000 en todos los emuladores
**Causa:** Coordenadas mal configuradas
**Solución:**
```bash
python Comparar_Imagen.py
# Opción 3: Test de captura
# Verifica que capture correctamente el área del Treecko
```

### Problema: No detecta la pantalla de selección inicial
**Causa:** Template `starter_selection.png` incorrecto
**Solución:**
1. Toma screenshot exacto de la pantalla de Birch
2. Guárdalo como `template/starter_selection.png`

### Problema: Hace SoftReset antes de verificar shiny
**Causa:** Template `treecko_battle_menu.png` incorrecto  
**Solución:**
1. Toma screenshot del menú de combate con Treecko visible
2. Guárdalo como `template/treecko_battle_menu.png`

### Problema: No encuentra emuladores
**Causa:** Rutas incorrectas en `AbrirEmulador.py`
**Solución:**
```python
# Verificar estas rutas en AbrirEmulador.py
EMULATOR_PATH = r'C:\tu\ruta\correcta\visualboyadvance-m'
ROM_PATH = r'C:\tu\ruta\correcta\Pokemon.gba'
```

### Problema: Falsos positivos (detecta shinies que no lo son)
**Causa:** Umbral muy bajo
**Solución:**
```python
# En main.py, cambiar:
similarity_threshold=0.95  # Más estricto
```

### Problema: No detecta shinies reales
**Causa:** Umbral muy alto
**Solución:**
```python
# En main.py, cambiar:
similarity_threshold=0.85  # Más sensible
```

## 📁 Estructura de Archivos Final

```
pokemon-bot/
├── main.py                           # Script principal
├── Control.py                        # Controles de botones
├── AbrirEmulador.py                  # Manejo de emuladores
├── Comparar_Imagen.py                # Detección de shinies
├── coordinate_selector.py            # Selector de coordenadas
├── emulator_config_builder.py        # Configurador
├── auto_screenshot_emulators.py      # Capturador automático
├── README.md                         # Esta documentación
├── template/                         # Templates de navegación
│   ├── starter_selection.png         # Pantalla de selección inicial
│   ├── treecko_confirmed.png         # Treecko confirmado
│   └── treecko_battle_menu.png       # Menú de combate
├── coordinates/                      # Configuración de coordenadas
│   └── emulator_coordinates.json     # Coordenadas automáticas
├── reference/                        # Imagen de referencia
│   └── treecko_normal.png            # Treecko normal para comparación
├── screenshots/                      # Screenshots de shinies
│   └── SHINY_*.png                   # Solo shinies encontrados
└── img_treecko/                      # Screenshots de configuración
    ├── emulador1_treecko.png         # Para configurar coordenadas
    ├── emulador2_treecko.png
    ├── emulador3_treecko.png
    └── emulador4_treecko.png
```

## 📊 Estadísticas y Monitoreo

El sistema muestra estadísticas en tiempo real:
```
📊 ESTADÍSTICAS:
   🔄 Reinicios totales: 45
   ⚔️  Encuentros totales: 45  
   ⏱️  Tiempo total: 1250.3 segundos
   ⏱️  Tiempo promedio por reinicio: 27.8 segundos
```

## 🎯 Tips para Optimizar

### Mejores Prácticas
1. **Calibra bien las coordenadas** - Es lo más importante
2. **Usa templates de alta calidad** - Screenshots nítidos
3. **Ajusta umbrales gradualmente** - Empieza con 0.90
4. **Monitorea las primeras ejecuciones** - Verifica que funcione bien
5. **Guarda la configuración** - Haz backup de `coordinates/` y `template/`

### Para Múltiples Computadores
1. **Copia toda la carpeta del proyecto**
2. **Reconfigura rutas** en `AbrirEmulador.py`
3. **Recalibra coordenadas** (resoluciones pueden diferir)
4. **Reajusta templates** si es necesario

## 🎉 ¡Feliz Shiny Hunting!

¿Dudas o problemas? Revisa la sección de Troubleshooting o configura paso a paso siguiendo esta guía.

**¡Que encuentres muchos shinies!** 🌟✨