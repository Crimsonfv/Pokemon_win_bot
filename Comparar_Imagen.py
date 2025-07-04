#!/usr/bin/env python3
"""
Comparar_Imagen.py - Detector de shinies para múltiples emuladores
Versión final optimizada para integración con main.py
"""

import cv2
import numpy as np
import time
import os
import json
import threading
from concurrent.futures import ThreadPoolExecutor

class MultiEmulatorShinyDetector:
    def __init__(self, reference_image_path=None, config_path="coordinates/emulator_coordinates.json"):
        """
        Detector de shinies para múltiples emuladores simultáneamente
        """
        self.reference_image = None
        self.emulator_windows = []
        self.capture_regions = []
        self.is_running = False
        self.config_path = config_path
        self.config = None
        
        # Cargar configuración de coordenadas
        self.load_coordinates_config()
        
        if reference_image_path and os.path.exists(reference_image_path):
            self.load_reference_image(reference_image_path)
    
    def load_coordinates_config(self):
        """Carga la configuración de coordenadas desde el archivo JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"✅ Configuración cargada desde {self.config_path}")
            self.update_capture_regions()
            return True
        except FileNotFoundError:
            print(f"⚠️  No se encontró {self.config_path}")
            print("💡 Ejecuta emulator_config_builder.py primero")
            self.config = None
            return False
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            self.config = None
            return False
    
    def update_capture_regions(self):
        """Actualiza las regiones de captura usando la configuración cargada"""
        self.capture_regions = []
        
        if not self.config or 'emulators' not in self.config:
            print("❌ No hay configuración de emuladores disponible")
            return
        
        for emu_config in self.config['emulators']:
            region_config = emu_config.get('pokemon_region', {})
            
            # Usar coordenadas directas del archivo de configuración
            region = {
                "top": region_config.get('y', 0),
                "left": region_config.get('x', 0),
                "width": region_config.get('width', 150),
                "height": region_config.get('height', 150),
                "emulator_id": emu_config.get('id', 0),
                "window_title": emu_config.get('name', f"Emulador_{emu_config.get('id', 0)}")
            }
            self.capture_regions.append(region)
        
        print(f"✅ {len(self.capture_regions)} regiones de captura configuradas")
    
    def load_reference_image(self, image_path=None):
        """Carga la imagen de referencia del Pokémon normal"""
        # Si no se especifica ruta, usar la de la configuración
        if image_path is None and self.config:
            image_path = self.config.get('reference_image', 'reference/treecko_normal.png')
        elif image_path is None:
            image_path = 'reference/treecko_normal.png'
            
        try:
            self.reference_image = cv2.imread(image_path)
            if self.reference_image is None:
                print(f"Error: No se pudo cargar la imagen {image_path}")
                return False
            print(f"✅ Imagen de referencia cargada: {image_path}")
            return True
        except Exception as e:
            print(f"Error cargando imagen de referencia: {e}")
            return False
    
    def capture_region_from_emulator(self, emulator_id, sct_instance=None):
        """
        Captura la región del Pokémon de un emulador específico
        NO guarda la imagen, solo la retorna en memoria
        """
        if emulator_id >= len(self.capture_regions):
            return None
            
        region = self.capture_regions[emulator_id]
        
        try:
            # Usar instancia de MSS específica del hilo o crear una nueva
            if sct_instance is None:
                import mss
                sct_instance = mss.mss()
            
            # Captura directa en memoria (SIN guardar archivo)
            screenshot = sct_instance.grab(region)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return img
        except Exception as e:
            print(f"Error capturando emulador {emulator_id}: {e}")
            return None
    
    def compare_images_histogram(self, img1, img2):
        """Compara imágenes usando histogramas de color"""
        if img1 is None or img2 is None:
            return 0.0
        
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        # Calcular histogramas
        hist1_b = cv2.calcHist([img1], [0], None, [256], [0, 256])
        hist1_g = cv2.calcHist([img1], [1], None, [256], [0, 256])
        hist1_r = cv2.calcHist([img1], [2], None, [256], [0, 256])
        
        hist2_b = cv2.calcHist([img2], [0], None, [256], [0, 256])
        hist2_g = cv2.calcHist([img2], [1], None, [256], [0, 256])
        hist2_r = cv2.calcHist([img2], [2], None, [256], [0, 256])
        
        # Comparar histogramas
        corr_b = cv2.compareHist(hist1_b, hist2_b, cv2.HISTCMP_CORREL)
        corr_g = cv2.compareHist(hist1_g, hist2_g, cv2.HISTCMP_CORREL)
        corr_r = cv2.compareHist(hist1_r, hist2_r, cv2.HISTCMP_CORREL)
        
        similarity = (corr_b + corr_g + corr_r) / 3.0
        return max(0.0, similarity)
    
    def check_emulator_for_shiny(self, emulator_id, similarity_threshold=0.85, sct_instance=None):
        """
        Verifica si hay shiny en un emulador específico
        Retorna solo datos, NO guarda screenshots automáticamente
        """
        if self.reference_image is None:
            return False, 0.0, None
        
        # Capturar imagen actual (solo en memoria)
        current_image = self.capture_region_from_emulator(emulator_id, sct_instance)
        
        if current_image is None:
            return False, 0.0, None
        
        # Comparar con referencia
        similarity = self.compare_images_histogram(self.reference_image, current_image)
        
        # Determinar si es shiny
        is_shiny = similarity < similarity_threshold
        
        return is_shiny, similarity, current_image
    
    def save_shiny_screenshot(self, image, emulator_id):
        """SOLO guarda screenshots cuando se encuentra un shiny"""
        timestamp = int(time.time())
        emulator_name = self.capture_regions[emulator_id]['window_title'].replace(' ', '_')
        filename = f"screenshots/SHINY_Emulator{emulator_id+1}_{emulator_name}_{timestamp}.png"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        cv2.imwrite(filename, image)
        print(f"🌟 SHINY SCREENSHOT GUARDADO: {filename}")
        return filename
    
    def monitor_single_emulator(self, emulator_id):
        """Monitorea un emulador específico en un hilo separado"""
        emulator_name = self.capture_regions[emulator_id]['window_title']
        check_count = 0
        
        # Crear instancia de MSS específica para este hilo
        import mss
        sct_local = mss.mss()
        
        print(f"🎮 Iniciando monitoreo de {emulator_name} (Emulador {emulator_id+1})")
        
        while self.is_running:
            try:
                is_shiny, similarity, image = self.check_emulator_for_shiny(emulator_id, sct_instance=sct_local)
                check_count += 1
                
                # Solo imprimir cada 20 verificaciones para no spam
                if check_count % 20 == 0:
                    print(f"Emulador {emulator_id+1}: Similitud {similarity:.3f} - {'SHINY!' if is_shiny else 'Normal'}")
                
                if is_shiny:
                    print(f"\n🌟🌟🌟 ¡SHINY ENCONTRADO EN EMULADOR {emulator_id+1}! 🌟🌟🌟")
                    print(f"Ventana: {emulator_name}")
                    print(f"Similitud: {similarity:.3f}")
                    
                    # Guardar screenshot SOLO del shiny
                    screenshot_path = self.save_shiny_screenshot(image, emulator_id)
                    
                    # Opcional: pausar detección o continuar
                    print("🎉 ¡Shiny capturado! Continuando monitoreo...")
                    # self.is_running = False  # Descomentar para parar todo
                    
                    time.sleep(5)  # Pausa breve después de encontrar shiny
                    
                time.sleep(0.5)  # Verificar cada 0.5 segundos
                
            except Exception as e:
                print(f"Error monitoreando emulador {emulator_id}: {e}")
                time.sleep(1)
        
        # Cerrar instancia de MSS del hilo
        sct_local.close()
        return False
    
    def start_monitoring_all_emulators(self):
        """Inicia el monitoreo de todos los emuladores simultáneamente"""
        if not self.capture_regions:
            print("Error: No hay regiones de captura configuradas")
            print("💡 Ejecuta emulator_config_builder.py primero")
            return
        
        if self.reference_image is None:
            print("Error: No hay imagen de referencia cargada")
            if self.config and 'reference_image' in self.config:
                print(f"💡 Intentando cargar: {self.config['reference_image']}")
                if not self.load_reference_image():
                    return
            else:
                print("💡 Ejecuta emulator_config_builder.py para configurar imagen de referencia")
                return
        
        print(f"\n🔍 Iniciando monitoreo de {len(self.capture_regions)} emuladores...")
        print("Presiona Ctrl+C para detener")
        
        # Mostrar información de configuración
        for i, region in enumerate(self.capture_regions):
            print(f"🎮 Emulador {i+1}: {region['window_title']}")
            print(f"   📍 Región: ({region['left']}, {region['top']}) {region['width']}x{region['height']}")
        
        self.is_running = True
        
        try:
            # Usar ThreadPoolExecutor para monitorear múltiples emuladores
            with ThreadPoolExecutor(max_workers=len(self.capture_regions)) as executor:
                # Crear un hilo para cada emulador
                futures = []
                for i in range(len(self.capture_regions)):
                    future = executor.submit(self.monitor_single_emulator, i)
                    futures.append(future)
                
                # Mantener ejecución hasta interrupción
                while self.is_running:
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\n⏹️ Monitoreo detenido por el usuario")
        finally:
            self.is_running = False
    
    def test_capture_regions(self):
        """Prueba la captura de cada región configurada"""
        if not self.capture_regions:
            print("❌ No hay regiones configuradas")
            return
        
        print("🧪 Probando captura de cada emulador...")
        
        # Crear instancia de MSS para testing
        import mss
        sct_test = mss.mss()
        
        for i in range(len(self.capture_regions)):
            print(f"\n📸 Capturando Emulador {i+1}...")
            img = self.capture_region_from_emulator(i, sct_test)
            
            if img is not None:
                print(f"✅ Captura exitosa: {img.shape[1]}x{img.shape[0]} pixels")
                
                # Mostrar preview opcional
                show_preview = input("¿Ver preview? (y/N): ").lower() == 'y'
                if show_preview:
                    cv2.imshow(f"Test Emulador {i+1}", img)
                    print("Presiona cualquier tecla para continuar...")
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
            else:
                print(f"❌ Error capturando Emulador {i+1}")
        
        # Cerrar instancia de testing
        sct_test.close()


# Ejemplo de uso standalone (opcional)
if __name__ == "__main__":
    detector = MultiEmulatorShinyDetector()
    
    print("=== DETECTOR DE SHINIES MULTI-EMULADOR ===")
    print("Este sistema usa coordenadas configuradas automáticamente")
    
    while True:
        print("\nOpciones:")
        print("1. 📋 Verificar configuración cargada")
        print("2. 🖼️  Cargar imagen de referencia")
        print("3. 🔍 Test de captura (verificar regiones)")
        print("4. 🌟 ¡INICIAR CAZA DE SHINIES!")
        print("5. ⚙️  Recargar configuración")
        print("6. Salir")
        
        choice = input("\nElige opción: ").strip()
        
        if choice == '1':
            if detector.config:
                print("✅ Configuración cargada:")
                print(f"   📁 Archivo: {detector.config_path}")
                print(f"   🎮 Emuladores: {len(detector.config.get('emulators', []))}")
                print(f"   🖼️  Referencia: {detector.config.get('reference_image', 'No configurada')}")
                
                for emu in detector.config.get('emulators', []):
                    region = emu.get('pokemon_region', {})
                    print(f"   🎯 {emu.get('name', 'Sin nombre')}: ({region.get('x', 0)}, {region.get('y', 0)}) {region.get('width', 0)}x{region.get('height', 0)}")
            else:
                print("❌ No hay configuración cargada")
                print("💡 Ejecuta: python emulator_config_builder.py")
                
        elif choice == '2':
            ref_path = input("Ruta de imagen de referencia (Enter para usar configurada): ").strip()
            if not ref_path:
                detector.load_reference_image()
            else:
                detector.load_reference_image(ref_path)
                
        elif choice == '3':
            detector.test_capture_regions()
                    
        elif choice == '4':
            detector.start_monitoring_all_emulators()
            
        elif choice == '5':
            detector.load_coordinates_config()
            detector.load_reference_image()
            
        elif choice == '6':
            break
            
        else:
            print("❌ Opción inválida")