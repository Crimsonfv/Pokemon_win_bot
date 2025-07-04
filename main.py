#!/usr/bin/env python3
"""
main.py - Sistema completo de shiny hunting automatizado
Maneja: apertura de emuladores, navegación automática y detección de shinies
"""

from Control import *
from AbrirEmulador import verificar_archivos, abrir_emuladores, cerrar_emuladores
from Comparar_Imagen import MultiEmulatorShinyDetector
import time
import cv2
import numpy as np
import mss
import os
import sys

class GameNavigator:
    def __init__(self):
        """Navegador del juego integrado en main.py"""
        # Estados del juego (DEFINIR PRIMERO antes que todo)
        self.UNKNOWN = 0
        self.STARTER_SELECTION = 1    # Pantalla de Birch (imagen 2)
        self.TREECKO_CONFIRMED = 2    # Treecko seleccionado (imagen 3)
        self.IN_BATTLE = 3            # En combate (pantalla inicial)
        self.TREECKO_BATTLE_MENU = 4  # Menú de combate con Treecko visible
        
        # Inicializar otras variables
        self.sct = mss.mss()
        self.shiny_detector = None
        self.encounters = 0
        self.resets = 0  # ← CONTADOR DE REINICIOS
        self.start_time = time.time()
        self.shiny_found = False  # ← BANDERA PARA SHINY ENCONTRADO
        
        # Cargar templates DESPUÉS de definir constantes
        self.templates = self.load_templates()
        
    def clear_screen(self):
        """Limpia la pantalla de la terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def load_templates(self):
        """Carga imágenes template para detectar pantallas"""
        templates = {}
        template_files = {
            "template/starter_selection.png": self.STARTER_SELECTION,
            "template/treecko_confirmed.png": self.TREECKO_CONFIRMED,
            "template/in_battle.png": self.IN_BATTLE,
            "template/treecko_battle_menu.png": self.TREECKO_BATTLE_MENU  # ← NUEVA PANTALLA
        }
        
        for file_path, state in template_files.items():
            if os.path.exists(file_path):
                template = cv2.imread(file_path)
                if template is not None:
                    templates[state] = template
                    print(f"✅ Template cargado: {file_path}")
                else:
                    print(f"⚠️  Error cargando template: {file_path}")
            else:
                print(f"⚠️  Template no encontrado: {file_path}")
        
        if not templates:
            print("⚠️  No se cargaron templates - navegación será básica")
        
        return templates
    
    def capture_full_screen_region(self, region_coords):
        """Captura una región específica de la pantalla"""
        try:
            screenshot = self.sct.grab(region_coords)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return img
        except Exception as e:
            print(f"Error capturando pantalla: {e}")
            return None
    
    def detect_current_screen(self, screenshot):
        """Detecta en qué pantalla estamos usando template matching"""
        if screenshot is None or not self.templates:
            return self.UNKNOWN
        
        best_match = self.UNKNOWN
        best_confidence = 0.0
        
        for state, template in self.templates.items():
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            if max_val > 0.7 and max_val > best_confidence:
                best_confidence = max_val
                best_match = state
        
        return best_match
    
    def navigate_to_starter_selection(self):
        """Navega presionando A hasta llegar a selección de inicial"""
        print("🎮 Navegando a selección de inicial...")
        
        # Región de captura - ajustar según tu configuración de emulador principal
        capture_region = {"top": 50, "left": 50, "width": 800, "height": 600}
        
        for attempt in range(50):  # Máximo 50 intentos
            print(f"   Intento {attempt + 1}: Presionando A...")
            Press_A()
            time.sleep(1.5)  # Esperar a que cambie la pantalla
            
            # Verificar si llegamos a selección de inicial
            screenshot = self.capture_full_screen_region(capture_region)
            current_screen = self.detect_current_screen(screenshot)
            
            if current_screen == self.STARTER_SELECTION:
                print("✅ ¡Llegamos a la pantalla de selección de inicial!")
                return True
            
            print(f"   Estado actual: {current_screen} (buscando {self.STARTER_SELECTION})")
        
        print("❌ No se pudo llegar a selección de inicial después de 50 intentos")
        return False
    
    def select_treecko_and_continue(self):
        """Selecciona Treecko y continúa hasta el combate"""
        print("🦎 Seleccionando Treecko...")
        
        # Mover a la izquierda para seleccionar Treecko
        Press_Izquierda()
        time.sleep(0.8)
        
        # Confirmar selección de Treecko
        Press_A()
        time.sleep(2.0)
        
        print("🎮 Continuando hasta llegar al combate...")
        
        # Seguir presionando A hasta llegar al combate
        capture_region = {"top": 50, "left": 50, "width": 800, "height": 600}
        
        for attempt in range(30):  # Máximo 30 intentos para llegar al combate
            print(f"   Avanzando al combate - intento {attempt + 1}")
            Press_A()
            time.sleep(1.8)
            
            # Verificar si llegamos al combate
            screenshot = self.capture_full_screen_region(capture_region)
            current_screen = self.detect_current_screen(screenshot)
            
            if current_screen == self.IN_BATTLE:
                print("✅ ¡Llegamos al combate!")
                return True
            elif current_screen == self.TREECKO_CONFIRMED:
                print("   Treecko confirmado, continuando...")
                continue
        
        print("⚠️  No se detectó pantalla de combate, pero continuando con detección de shiny...")
        return True  # Asumir que llegamos al combate
    
    def check_for_shiny_in_battle(self):
        """Verifica si el Treecko en combate es shiny"""
        if self.shiny_detector is None:
            print("❌ Detector de shiny no inicializado")
            return False
        
        print("🔍 Verificando si el Treecko es shiny...")
        print("🐛 DEBUG: Probando detección paso a paso...")
        
        # PASO 1: Verificar que el detector esté bien configurado
        print(f"🔧 Detector configurado: {len(self.shiny_detector.capture_regions)} regiones")
        print(f"🖼️  Imagen de referencia: {'✅' if self.shiny_detector.reference_image is not None else '❌'}")
        
        if self.shiny_detector.reference_image is None:
            print("🔄 Intentando cargar imagen de referencia...")
            if not self.shiny_detector.load_reference_image():
                print("❌ No se pudo cargar imagen de referencia")
                return False
        
        # PASO 2: Esperar un momento para asegurar que Treecko esté visible
        print("⏱️  Esperando 3 segundos para asegurar que Treecko esté completamente visible...")
        time.sleep(3.0)
        
        print("📊 Explicación de similitudes:")
        print("   • 0.90-1.00 = Treecko NORMAL (muy parecido a referencia)")
        print("   • 0.00-0.85 = Posible SHINY (muy diferente a referencia)")  
        print("   • 0.000 = ERROR en captura/configuración")
        print()
        
        # PASO 3: Verificar cada emulador CON debug
        similarities = []
        
        for emulator_id in range(len(self.shiny_detector.capture_regions)):
            try:
                print(f"🔍 Analizando Emulador {emulator_id + 1}...")
                
                # Debug: mostrar región que se va a capturar
                region = self.shiny_detector.capture_regions[emulator_id]
                print(f"   📍 Región: ({region['left']}, {region['top']}) {region['width']}x{region['height']}")
                
                # Capturar imagen para debug
                import mss
                sct_debug = mss.mss()
                captured_img = self.shiny_detector.capture_region_from_emulator(emulator_id, sct_debug)
                
                if captured_img is not None:
                    print(f"   ✅ Captura exitosa: {captured_img.shape[1]}x{captured_img.shape[0]} pixels")
                    
                    # Guardar imagen capturada para debug
                    debug_filename = f"debug_capture_emulator{emulator_id+1}.png"
                    cv2.imwrite(debug_filename, captured_img)
                    print(f"   💾 Debug guardado: {debug_filename}")
                else:
                    print(f"   ❌ Error en captura")
                    continue
                
                # Hacer la comparación con umbral ajustado
                is_shiny, similarity, image = self.shiny_detector.check_emulator_for_shiny(emulator_id, similarity_threshold=0.90, sct_instance=sct_debug)
                similarities.append(similarity)
                
                # Mostrar resultado con interpretación
                if similarity == 0.000:
                    status = "❌ ERROR"
                    explanation = "(Problema en captura/coordenadas/referencia)"
                elif similarity >= 0.90:
                    status = "✅ NORMAL"
                    explanation = "(Muy parecido a referencia)"
                elif similarity < 0.85:
                    status = "🌟 POSIBLE SHINY"
                    explanation = "(Muy diferente a referencia)"
                else:
                    status = "🤔 DUDOSO" 
                    explanation = "(Similitud intermedia)"
                
                print(f"   📊 Similitud: {similarity:.3f} - {status} {explanation}")
                
                if is_shiny and similarity > 0.000:  # Solo considerar shiny si no hay error
                    print(f"\n🌟🌟🌟 ¡SHINY ENCONTRADO EN EMULADOR {emulator_id + 1}! 🌟🌟🌟")
                    print(f"Encuentros realizados: {self.encounters}")
                    print(f"Reinicios realizados: {self.resets}")
                    print(f"Tiempo total: {time.time() - self.start_time:.1f} segundos")
                    
                    # Guardar screenshot del shiny
                    if image is not None:
                        timestamp = int(time.time())
                        filename = f"screenshots/SHINY_MAIN_Emulator{emulator_id+1}_{timestamp}.png"
                        os.makedirs(os.path.dirname(filename), exist_ok=True)
                        cv2.imwrite(filename, image)
                        print(f"💾 Screenshot del shiny guardado: {filename}")
                    
                    print("\n" + "="*60)
                    print("🎉 ¡FELICITACIONES! ¡SHINY POKEMON ENCONTRADO!")
                    print("="*60)
                    print("🎮 Los emuladores permanecen ABIERTOS para que puedas:")
                    print("   • 🎯 Capturar el Pokemon shiny")
                    print("   • 🏷️  Darle nombre")
                    print("   • 💾 Guardar el juego")
                    print("   • 📸 Tomar más screenshots")
                    print("\n💡 Cuando termines:")
                    print("   • Presiona Ctrl+C en esta terminal para cerrar emuladores")
                    print("   • O simplemente cierra esta ventana")
                    print("="*60)
                    
                    # Marcar que se encontró shiny
                    self.shiny_found = True
                    
                    sct_debug.close()
                    return True
                
                sct_debug.close()
                
            except Exception as e:
                print(f"   ❌ Error procesando Emulador {emulator_id + 1}: {e}")
        
        # Análisis de resultados
        print()
        if all(sim == 0.000 for sim in similarities):
            print("⚠️  TODOS los emuladores muestran similitud 0.000")
            print("🐛 Esto indica problema de integración entre main.py y detector")
            print("💡 Revisa los archivos debug_capture_emulator*.png generados")
            print("💡 Compara con: python Comparar_Imagen.py → Opción 3")
        elif all(sim >= 0.95 for sim in similarities):
            print("   ✅ Detección funcionando correctamente - Todos NORMALES")
            print(f"   📊 Rango de similitudes: {min(similarities):.3f} - {max(similarities):.3f}")
        elif any(sim < 0.90 for sim in similarities):
            print("   🌟 ¡POSIBLE SHINY DETECTADO!")
        else:
            print("   🤔 Similitudes dudosas - revisar manualmente")
        
        return False
    
    def reset_for_next_attempt(self):
        """Reinicia el juego para el siguiente intento"""
        print("🔄 Reiniciando para el siguiente intento...")
        self.encounters += 1
        self.resets += 1  # ← INCREMENTAR CONTADOR
        
        # Mostrar estadísticas antes del reset
        elapsed_time = time.time() - self.start_time
        print(f"📊 Encuentro #{self.encounters} completado")
        print(f"📊 Reinicio #{self.resets}")
        print(f"⏱️  Tiempo transcurrido: {elapsed_time:.1f} segundos")
        if self.resets > 0:
            print(f"⏱️  Tiempo promedio por reinicio: {elapsed_time/self.resets:.1f} segundos")
        
        # Soft reset del juego
        print("🔄 Ejecutando SoftReset...")
        SoftReset()
        time.sleep(3.0)  # Pausa antes de limpiar pantalla
        
        # VOLVER A LIMPIAR PANTALLA
        self.clear_screen()
        
        # Mostrar header después de limpiar
        print("🎮 === SISTEMA COMPLETO DE SHINY HUNTING AUTOMATIZADO ===")
        print("="*60)
        print(f"🔄 REINICIO #{self.resets + 1} - ENCUENTRO #{self.encounters + 1}")
        print(f"⏱️  Tiempo total: {time.time() - self.start_time:.1f} segundos")
        print("💡 Umbral ajustado: Shiny si similitud < 0.90")
        print("="*60)
        
        time.sleep(5.0)  # Esperar a que se reinicie completamente
    
    def run_complete_shiny_hunt_cycle(self):
        """Ejecuta UN ciclo completo de shiny hunting"""
        print(f"\n🎯 === CICLO #{self.resets + 1} - BUSCANDO SHINY ===")
        
        # PASO 1: Navegar a selección de inicial
        if not self.navigate_to_starter_selection():
            print("❌ Error navegando a selección de inicial")
            return False
        
        # PASO 2: Seleccionar Treecko y llegar al combate
        if not self.select_treecko_and_continue():
            print("❌ Error seleccionando Treecko o llegando al combate")
            return False
        
        # PASO 3: Buscar hasta llegar al menú de combate con Treecko visible
        print("🎮 Esperando menú de combate con Treecko visible...")
        
        for attempt in range(100):  # Máximo 100 intentos
            # Verificar estado actual
            capture_region = {"top": 50, "left": 50, "width": 800, "height": 600}
            screenshot = self.capture_full_screen_region(capture_region)
            current_screen = self.detect_current_screen(screenshot)
            
            if current_screen == self.TREECKO_BATTLE_MENU:
                print(f"⚔️  ¡Menú de combate con Treecko visible!")
                
                # AHORA SÍ - VERIFICAR SI ES SHINY
                if self.check_for_shiny_in_battle():
                    print("🎉 ¡SHINY ENCONTRADO! Deteniendo búsqueda.")
                    return True  # Shiny encontrado - detener todo
                
                # NO ES SHINY - SOFTRESET INMEDIATO
                print("   No es shiny → Haciendo SoftReset...")
                self.reset_for_next_attempt()
                return False  # Continuar con siguiente ciclo
                
            elif current_screen == self.IN_BATTLE:
                print(f"   En combate - esperando menú completo...")
                Press_A()  # Continuar para llegar al menú
                time.sleep(1.0)
                
            else:
                # Seguir avanzando hasta llegar al combate
                print(f"   Avanzando - intento {attempt + 1}")
                Press_A()
                time.sleep(1.5)
        
        # Si llegamos aquí, no llegamos al menú de combate
        print("⚠️  No se llegó al menú de combate después de 100 intentos")
        self.reset_for_next_attempt()
        return False  # Continuar buscando
    



def main():
    """Función principal que maneja todo el flujo"""
    print("🎮 === SISTEMA COMPLETO DE SHINY HUNTING AUTOMATIZADO ===")
    print("="*60)
    
    # PASO 1: Verificar archivos y abrir emuladores
    print("🔧 Verificando archivos y abriendo emuladores...")
    if not verificar_archivos():
        print("❌ Error verificando archivos")
        return
    
    procesos_emuladores = abrir_emuladores()
    if not procesos_emuladores:
        print("❌ Error abriendo emuladores")
        return
    
    print("✅ Emuladores abiertos correctamente")
    
    # PASO 2: Inicializar navegador y detector de shiny
    print("🔧 Inicializando sistemas...")
    navigator = GameNavigator()
    
    # Inicializar detector de shiny
    try:
        navigator.shiny_detector = MultiEmulatorShinyDetector()
        print("✅ Detector de shiny inicializado")
    except Exception as e:
        print(f"❌ Error inicializando detector de shiny: {e}")
        print("💡 Asegúrate de tener configurado coordinates/emulator_coordinates.json")
        return
    
    # PASO 3: Esperar a que el usuario esté listo
    print("\n📋 PREPARACIÓN:")
    print("1. Asegúrate de que los emuladores estén en la pantalla inicial del juego")
    print("2. Verifica que el detector de shiny esté configurado correctamente")
    print("3. Los templates deben estar en la carpeta template/")
    
    input("\n⏸️  Presiona ENTER cuando todo esté listo para comenzar...")
    
    # PASO 4: Ejecutar ciclos de shiny hunting
    print("\n🚀 ¡INICIANDO SHINY HUNTING AUTOMATIZADO!")
    print("💡 Presiona Ctrl+C para detener en cualquier momento")
    
    try:
        while True:
            # Ejecutar un ciclo completo
            shiny_found = navigator.run_complete_shiny_hunt_cycle()
            
            if shiny_found:
                print("\n🎊 ¡SHINY HUNTING COMPLETADO EXITOSAMENTE!")
                print("🎮 Emuladores permanecen abiertos para que captures el Pokemon")
                print("💡 Presiona Ctrl+C cuando quieras cerrar los emuladores")
                
                # NO CERRAR EMULADORES - mantenerlos abiertos para capturar shiny
                try:
                    print("\n⏸️  Esperando... (Presiona Ctrl+C para cerrar emuladores)")
                    while True:
                        time.sleep(1)  # Mantener programa vivo pero sin hacer nada
                except KeyboardInterrupt:
                    print("\n👋 Usuario decidió cerrar emuladores")
                    break
            
            # Breve pausa entre ciclos (solo si no encontró shiny)
            time.sleep(2.0)
            
    except KeyboardInterrupt:
        print("\n⏹️  Shiny hunting interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante shiny hunting: {e}")
    finally:
        # PASO 5: Limpieza final - solo si el usuario quiere cerrar
        print("\n🔧 Cerrando emuladores...")
        try:
            cerrar_emuladores(procesos_emuladores)
            print("✅ Emuladores cerrados correctamente")
        except Exception as e:
            print(f"⚠️  Error cerrando emuladores: {e}")
        
        # Mostrar estadísticas finales
        total_time = time.time() - navigator.start_time
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"   🔄 Reinicios totales: {navigator.resets}")
        print(f"   ⚔️  Encuentros totales: {navigator.encounters}")
        print(f"   ⏱️  Tiempo total: {total_time:.1f} segundos")
        if navigator.resets > 0:
            print(f"   ⏱️  Tiempo promedio por reinicio: {total_time/navigator.resets:.1f} segundos")
        if navigator.encounters > 0:
            print(f"   ⏱️  Tiempo promedio por encuentro: {total_time/navigator.encounters:.1f} segundos")
        
        print("\n👋 ¡Gracias por usar el sistema de shiny hunting!")
        
        # Si encontramos shiny, recordar al usuario que ya puede capturarlo
        if navigator.shiny_found:
            print("🌟 ¡No olvides capturar tu Pokemon shiny antes de cerrar el juego!")
        
        print("💡 Tip: Siempre guarda el juego después de capturar un shiny")


if __name__ == "__main__":
    main()