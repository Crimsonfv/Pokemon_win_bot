import subprocess
import os
import sys
import time
import win32gui
import win32con

# Configuración
NUM_EMULATORS = 4
DELAY_BETWEEN_EMULATORS = 3  # segundos entre cada emulador

# Configuración de ventanas (más pequeñas)
WINDOW_WIDTH = 400  # Reducido de 800 a 600
WINDOW_HEIGHT = 400  # Reducido de 600 a 450
WINDOW_SPACING = 0 # Reducido de 60 a 40

# Rutas del emulador y ROM
EMULATOR_PATH = r'E:\Emulador-GBA\visualboyadvance-m'
ROM_PATH = r'E:\Emulador-GBA\juegos\Pokemon - Ruby Version (USA, Europe) (Rev 2).gba'

def verificar_archivos():
    """Verifica que el emulador y la ROM existan"""
    # Verificar que la ROM existe
    if not os.path.exists(ROM_PATH):
        print(f"Error: No se encuentra la ROM en {ROM_PATH}")
        return False

    # Verificar que el emulador existe
    if not os.path.exists(EMULATOR_PATH + '.exe'):
        print(f"Error: No se encuentra el emulador en {EMULATOR_PATH}.exe")
        return False
    
    print(f"✓ Emulador encontrado: {EMULATOR_PATH}")
    print(f"✓ ROM encontrada: {ROM_PATH}")
    return True

def calculate_position(index, cols=2):
    """Calcula la posición x,y para una ventana según su índice"""
    row = index // cols
    col = index % cols
    x = col * (WINDOW_WIDTH + WINDOW_SPACING)
    y = row * (WINDOW_HEIGHT + WINDOW_SPACING)
    return x, y

def find_windows_by_process_name(process_name):
    """Encuentra todas las ventanas de un proceso específico"""
    windows = []
    
    def enum_windows_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if process_name.lower() in window_text.lower() or "visual" in window_text.lower():
                windows.append(hwnd)
        return True
    
    win32gui.EnumWindows(enum_windows_callback, None)
    return windows

def position_emulator_windows():
    """Posiciona todas las ventanas del emulador encontradas"""
    print("Buscando y posicionando ventanas del emulador...")
    
    # Esperar un poco para que las ventanas aparezcan
    time.sleep(3)
    
    windows = find_windows_by_process_name("visual")
    
    if not windows:
        print("No se encontraron ventanas del emulador")
        return
    
    print(f"Encontradas {len(windows)} ventanas del emulador")
    
    for i, hwnd in enumerate(windows):
        if i >= NUM_EMULATORS:
            break
            
        x, y = calculate_position(i)
        try:
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, x, y, WINDOW_WIDTH, WINDOW_HEIGHT, 0)
            window_text = win32gui.GetWindowText(hwnd)
            print(f"✓ Ventana {i+1} '{window_text}' posicionada en ({x},{y}) - {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        except Exception as e:
            print(f"Error posicionando ventana {i+1}: {e}")

def abrir_emuladores():
    """Abre múltiples instancias del emulador"""
    
    # Verificar archivos antes de comenzar
    if not verificar_archivos():
        sys.exit(1)
    
    print(f"Iniciando {NUM_EMULATORS} emuladores con {DELAY_BETWEEN_EMULATORS}s de espera...")
    print(f"✓ Configuración: {WINDOW_WIDTH}x{WINDOW_HEIGHT} pixels por ventana")
    
    # Lista para guardar los procesos
    processes = []
    
    # Abrir múltiples emuladores
    for i in range(NUM_EMULATORS):
        try:
            print(f"Abriendo emulador {i+1}/{NUM_EMULATORS}...")
            
            # Calcular posición planeada
            x, y = calculate_position(i)
            print(f"  Posición planeada: ({x}, {y})")
            
            # Comando para abrir emulador con ROM
            cmd = [EMULATOR_PATH + '.exe', ROM_PATH]
            process = subprocess.Popen(cmd, shell=False)
            processes.append(process)
            
            print(f"✓ Emulador {i+1} iniciado (PID: {process.pid})")
            
            # Esperar antes del siguiente (excepto en el último)
            if i < NUM_EMULATORS - 1:
                print(f"Esperando {DELAY_BETWEEN_EMULATORS} segundos...")
                time.sleep(DELAY_BETWEEN_EMULATORS)
                
        except Exception as e:
            print(f"✗ Error al abrir emulador {i+1}: {e}")
    
    print(f"\n¡{len(processes)} emuladores iniciados exitosamente!")
    
    # Esperar a que los emuladores se carguen completamente
    print("Esperando 5 segundos para que los emuladores se carguen...")
    time.sleep(5)
    
    # Posicionar todas las ventanas
    position_emulator_windows()
    
    print("✓ Emuladores listos y posicionados!")
    
    return processes

# Función para cerrar emuladores
def cerrar_emuladores(processes):
    """Cierra todos los emuladores abiertos"""
    print("Cerrando todos los emuladores...")
    
    for i, process in enumerate(processes):
        try:
            process.terminate()
            print(f"✓ Emulador {i+1} cerrado")
        except:
            print(f"✗ Error cerrando emulador {i+1}")
    
    print("✓ Emuladores cerrados")

# Función adicional para reposicionar ventanas en cualquier momento
def reposicionar_ventanas():
    """Reposiciona las ventanas sin reiniciar emuladores"""
    print("Reposicionando ventanas existentes...")
    position_emulator_windows()

# Uso principal
if __name__ == "__main__":
    # Abrir emuladores
    procesos = abrir_emuladores()
    
    print("\nControles estándar de VBA-M:")
    print("  X=A, Z=B, A=L, S=R, Enter=Start, Backspace=Select")
    print("  Flechas=D-pad, Space=Turbo")
    print("  F1-F4=Save States, Shift+F1-F4=Load States")
    print("\nEmuladores abiertos. Presiona Ctrl+C para cerrarlos...")
    print("Tip: Puedes llamar reposicionar_ventanas() si se mueven")
    
    # Esperar hasta que el usuario quiera cerrar
    try:
        while True:
            time.sleep(1)
            
            # Verificar si algún emulador se cerró
            procesos_activos = []
            for i, process in enumerate(procesos):
                if process.poll() is None:  # Aún está ejecutándose
                    procesos_activos.append(process)
                else:
                    print(f"Emulador {i+1} se cerró")
            
            procesos = procesos_activos
            
            if not procesos:
                print("Todos los emuladores se cerraron")
                break
                
    except KeyboardInterrupt:
        cerrar_emuladores(procesos)