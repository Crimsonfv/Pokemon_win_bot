#!/usr/bin/env python3
"""
Script para tomar screenshots automáticamente de todos los emuladores
y prepararlos para configuración de coordenadas
"""

import win32gui
import win32con
import mss
import cv2
import numpy as np
import os
import time
from datetime import datetime

class EmulatorScreenshotTaker:
    def __init__(self):
        self.sct = mss.mss()
        self.emulator_windows = []
        self.screenshots_taken = []
        
        # Crear directorio para screenshots
        os.makedirs("img_treecko", exist_ok=True)
        
    def find_emulator_windows(self):
        """Encuentra automáticamente todas las ventanas de emuladores"""
        windows = []
        
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                try:
                    window_text = win32gui.GetWindowText(hwnd)
                    # Buscar ventanas que contengan palabras clave de emuladores
                    keywords = ["visual", "vba", "gba", "boy advance", "pokemon"]
                    
                    if any(keyword in window_text.lower() for keyword in keywords):
                        # Obtener información de la ventana
                        rect = win32gui.GetWindowRect(hwnd)
                        
                        # Filtrar ventanas muy pequeñas (probablemente no son emuladores)
                        width = rect[2] - rect[0]
                        height = rect[3] - rect[1]
                        
                        if width > 200 and height > 200:  # Mínimo tamaño razonable
                            window_info = {
                                'hwnd': hwnd,
                                'title': window_text,
                                'rect': rect,  # (left, top, right, bottom)
                                'width': width,
                                'height': height
                            }
                            windows.append(window_info)
                except Exception as e:
                    pass  # Ignorar ventanas que no se pueden procesar
            return True
        
        win32gui.EnumWindows(enum_windows_callback, None)
        
        # Ordenar ventanas por posición (izquierda a derecha, arriba a abajo)
        windows.sort(key=lambda w: (w['rect'][1], w['rect'][0]))
        
        self.emulator_windows = windows
        return windows
    
    def take_window_screenshot(self, window_info, output_path):
        """Toma screenshot de una ventana específica"""
        try:
            # Coordenadas de la ventana
            left, top, right, bottom = window_info['rect']
            
            # Región para MSS
            region = {
                "top": top,
                "left": left,
                "width": right - left,
                "height": bottom - top
            }
            
            # Tomar screenshot
            screenshot = self.sct.grab(region)
            
            # Convertir a formato OpenCV
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            # Guardar imagen
            cv2.imwrite(output_path, img)
            
            print(f"✅ Screenshot guardado: {output_path}")
            print(f"   📏 Tamaño: {img.shape[1]}x{img.shape[0]} pixels")
            
            return img, True
            
        except Exception as e:
            print(f"❌ Error tomando screenshot: {e}")
            return None, False
    
    def preview_screenshot(self, img, window_title, emulator_id):
        """Muestra preview del screenshot tomado"""
        if img is None:
            return
            
        # Redimensionar para preview si es muy grande
        height, width = img.shape[:2]
        if width > 800:
            scale = 800 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            preview_img = cv2.resize(img, (new_width, new_height))
        else:
            preview_img = img.copy()
        
        # Mostrar preview
        window_name = f"Preview Emulador {emulator_id} - {window_title[:30]}..."
        cv2.imshow(window_name, preview_img)
        
        print(f"👁️  Preview mostrado. Presiona cualquier tecla para continuar...")
        cv2.waitKey(0)
        cv2.destroyWindow(window_name)
    
    def take_all_screenshots(self, show_preview=True):
        """Toma screenshots de todos los emuladores encontrados"""
        if not self.emulator_windows:
            print("❌ No se encontraron ventanas de emuladores")
            print("💡 Asegúrate de que los emuladores estén abiertos y visibles")
            return False
        
        print(f"\n📸 TOMANDO SCREENSHOTS DE {len(self.emulator_windows)} EMULADORES")
        print("="*60)
        
        self.screenshots_taken = []
        
        for i, window in enumerate(self.emulator_windows, 1):
            print(f"\n🎮 Procesando Emulador {i}:")
            print(f"   📝 Título: {window['title']}")
            print(f"   📍 Posición: ({window['rect'][0]}, {window['rect'][1]})")
            print(f"   📏 Tamaño: {window['width']}x{window['height']}")
            
            # Nombre del archivo
            safe_title = "".join(c for c in window['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')[:20]  # Limitar longitud
            
            filename = f"emulador{i}_{safe_title}_treecko.png"
            output_path = os.path.join("img_treecko", filename)
            
            # Tomar screenshot
            img, success = self.take_window_screenshot(window, output_path)
            
            if success:
                screenshot_info = {
                    'emulator_id': i,
                    'filename': filename,
                    'path': output_path,
                    'window_info': window,
                    'image': img
                }
                self.screenshots_taken.append(screenshot_info)
                
                # Mostrar preview si está habilitado
                if show_preview:
                    self.preview_screenshot(img, window['title'], i)
            else:
                print(f"❌ Error procesando Emulador {i}")
        
        return len(self.screenshots_taken) > 0
    
    def verify_screenshots(self):
        """Verifica que todos los screenshots se tomaron correctamente"""
        print(f"\n🔍 VERIFICACIÓN DE SCREENSHOTS")
        print("="*40)
        
        if not self.screenshots_taken:
            print("❌ No hay screenshots para verificar")
            return False
        
        all_good = True
        
        for screenshot in self.screenshots_taken:
            path = screenshot['path']
            
            if os.path.exists(path):
                # Verificar que el archivo no esté corrupto
                try:
                    img = cv2.imread(path)
                    if img is not None:
                        height, width = img.shape[:2]
                        print(f"✅ {screenshot['filename']}: {width}x{height}")
                    else:
                        print(f"❌ {screenshot['filename']}: Archivo corrupto")
                        all_good = False
                except:
                    print(f"❌ {screenshot['filename']}: Error leyendo archivo")
                    all_good = False
            else:
                print(f"❌ {screenshot['filename']}: Archivo no encontrado")
                all_good = False
        
        if all_good:
            print(f"\n✅ Todos los {len(self.screenshots_taken)} screenshots están correctos")
        else:
            print(f"\n❌ Algunos screenshots tienen problemas")
        
        return all_good
    
    def list_screenshots(self):
        """Lista todos los screenshots disponibles"""
        print(f"\n📋 SCREENSHOTS DISPONIBLES:")
        print("="*40)
        
        screenshots_dir = "img_treecko"
        if not os.path.exists(screenshots_dir):
            print("❌ Directorio img_treecko no encontrado")
            return
        
        files = [f for f in os.listdir(screenshots_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        
        if not files:
            print("📁 No hay screenshots en img_treecko/")
            return
        
        for i, filename in enumerate(files, 1):
            path = os.path.join(screenshots_dir, filename)
            try:
                img = cv2.imread(path)
                if img is not None:
                    height, width = img.shape[:2]
                    size_mb = os.path.getsize(path) / (1024 * 1024)
                    print(f"📸 {i}. {filename}")
                    print(f"    📏 {width}x{height} - {size_mb:.2f}MB")
                else:
                    print(f"❌ {i}. {filename} (corrupto)")
            except:
                print(f"❌ {i}. {filename} (error)")
    
    def cleanup_old_screenshots(self):
        """Limpia screenshots antiguos opcionalmente"""
        print(f"\n🧹 LIMPIEZA DE SCREENSHOTS ANTIGUOS")
        print("="*40)
        
        screenshots_dir = "img_treecko"
        if not os.path.exists(screenshots_dir):
            return
        
        files = [f for f in os.listdir(screenshots_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        
        if not files:
            print("📁 No hay archivos para limpiar")
            return
        
        print(f"📁 Encontrados {len(files)} archivos:")
        for filename in files:
            print(f"   📸 {filename}")
        
        choice = input("\n❓ ¿Eliminar archivos antiguos? (y/N): ").lower()
        
        if choice == 'y':
            deleted = 0
            for filename in files:
                try:
                    os.remove(os.path.join(screenshots_dir, filename))
                    print(f"🗑️  Eliminado: {filename}")
                    deleted += 1
                except:
                    print(f"❌ Error eliminando: {filename}")
            
            print(f"✅ {deleted} archivos eliminados")
        else:
            print("🔄 Conservando archivos existentes")


def main():
    print("📸 CAPTURADOR AUTOMÁTICO DE SCREENSHOTS")
    print("="*50)
    print("Este script toma screenshots automáticamente de todos")
    print("los emuladores abiertos para configurar coordenadas.")
    print("="*50)
    
    capturer = EmulatorScreenshotTaker()
    
    while True:
        print("\n📋 OPCIONES:")
        print("1. 🔍 Buscar emuladores")
        print("2. 📸 Tomar screenshots de todos los emuladores")
        print("3. 👁️  Tomar screenshots con preview")
        print("4. 🔍 Verificar screenshots tomados")
        print("5. 📋 Listar screenshots existentes")
        print("6. 🧹 Limpiar screenshots antiguos")
        print("7. 🚀 Continuar con configuración de coordenadas")
        print("8. ❌ Salir")
        
        choice = input("\nElige opción: ").strip()
        
        if choice == '1':
            print("\n🔍 Buscando emuladores...")
            windows = capturer.find_emulator_windows()
            
            if windows:
                print(f"✅ Encontrados {len(windows)} emuladores:")
                for i, window in enumerate(windows, 1):
                    print(f"   {i}. {window['title']} - {window['width']}x{window['height']}")
            else:
                print("❌ No se encontraron emuladores")
                print("💡 Asegúrate de que estén abiertos y visibles")
        
        elif choice == '2':
            capturer.take_all_screenshots(show_preview=False)
            
        elif choice == '3':
            capturer.take_all_screenshots(show_preview=True)
            
        elif choice == '4':
            capturer.verify_screenshots()
            
        elif choice == '5':
            capturer.list_screenshots()
            
        elif choice == '6':
            capturer.cleanup_old_screenshots()
            
        elif choice == '7':
            if capturer.verify_screenshots():
                print("\n🚀 Screenshots listos!")
                print("💡 Ahora puedes ejecutar:")
                print("   python emulator_config_builder.py")
                break
            else:
                print("❌ Primero debes tomar screenshots válidos")
                
        elif choice == '8':
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main()