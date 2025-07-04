#!/usr/bin/env python3
"""
Configurador simplificado que usa tu coordinate_selector.py existente
"""

import json
import os

class SimpleConfigBuilder:
    def __init__(self):
        self.config = {
            "emulators": [],
            "reference_image": "reference/treecko_normal.png", 
            "similarity_threshold": 0.85
        }
        
        # Crear directorios
        os.makedirs("coordinates", exist_ok=True)
        os.makedirs("reference", exist_ok=True)
    
    def configure_emulator_manually(self, emulator_id):
        """Configura un emulador pidiendo coordenadas manualmente"""
        
        print(f"\n🎯 CONFIGURANDO EMULADOR {emulator_id}")
        print("="*40)
        
        # Verificar que existe el screenshot
        screenshot_path = f"img_treecko/emulador{emulator_id}_*.png"
        
        # Buscar archivos que coincidan
        import glob
        matching_files = glob.glob(f"img_treecko/*emulador{emulator_id}*.png") + glob.glob(f"img_treecko/emulador{emulator_id}*.png")
        
        if not matching_files:
            print(f"❌ No se encontró screenshot para emulador {emulator_id}")
            print(f"📁 Busca archivos como: img_treecko/emulador{emulator_id}_*.png")
            return None
        
        screenshot_file = matching_files[0]
        print(f"📁 Usando: {screenshot_file}")
        
        print(f"\n📝 INSTRUCCIONES:")
        print(f"1. Ejecuta: python coordinate_selector.py {screenshot_file}")
        print(f"2. Selecciona SOLO la región del Treecko")
        print(f"3. Anota las coordenadas que aparecen")
        print(f"4. Vuelve aquí e ingrésalas")
        
        input("Presiona ENTER cuando hayas ejecutado coordinate_selector.py...")
        
        # Pedir coordenadas manualmente
        print(f"\n📋 Ingresa las coordenadas del Emulador {emulator_id}:")
        try:
            x = int(input("X (esquina superior izquierda): "))
            y = int(input("Y (esquina superior izquierda): ")) 
            width = int(input("Ancho: "))
            height = int(input("Alto: "))
            
            emulator_config = {
                "id": emulator_id,
                "name": f"Emulador_{emulator_id}",
                "screenshot_path": screenshot_file,
                "pokemon_region": {
                    "x": x,
                    "y": y,
                    "width": width, 
                    "height": height
                }
            }
            
            print(f"✅ Emulador {emulator_id} configurado:")
            print(f"   📍 Posición: ({x}, {y})")
            print(f"   📏 Tamaño: {width}x{height}")
            
            return emulator_config
            
        except ValueError:
            print("❌ Error: Coordenadas inválidas")
            return None
    
    def setup_all_emulators(self):
        """Configura todos los emuladores"""
        print("🎮 CONFIGURACIÓN DE COORDENADAS")
        print("="*50)
        
        # Verificar screenshots disponibles
        import glob
        screenshots = glob.glob("img_treecko/*.png")
        
        if not screenshots:
            print("❌ No se encontraron screenshots en img_treecko/")
            print("💡 Ejecuta auto_screenshot_emulators.py primero")
            return False
        
        print(f"📁 Encontrados {len(screenshots)} screenshots:")
        for img in screenshots:
            print(f"   📸 {img}")
        
        # Preguntar cuántos emuladores
        try:
            num_emulators = int(input(f"\n¿Cuántos emuladores configurar? (máximo {len(screenshots)}): "))
        except ValueError:
            num_emulators = min(4, len(screenshots))
            print(f"Usando {num_emulators} emuladores por defecto")
        
        # Configurar cada emulador
        for i in range(1, num_emulators + 1):
            emulator_config = self.configure_emulator_manually(i)
            
            if emulator_config:
                self.config["emulators"].append(emulator_config)
                print(f"✅ Emulador {i} añadido a la configuración")
            else:
                print(f"❌ Error configurando Emulador {i}")
                retry = input("¿Reintentar? (y/n): ").lower() == 'y'
                if retry:
                    i -= 1  # Reintentar
        
        return len(self.config["emulators"]) > 0
    
    def create_reference_image(self):
        """Ayuda a crear imagen de referencia"""
        print("\n🖼️  IMAGEN DE REFERENCIA")
        print("="*30)
        
        ref_path = "reference/treecko_normal.png"
        
        if os.path.exists(ref_path):
            print(f"✅ Ya existe: {ref_path}")
            replace = input("¿Reemplazar? (y/N): ").lower() == 'y'
            if not replace:
                return True
        
        print("📝 Para crear la imagen de referencia:")
        print("1. Toma un screenshot PEQUEÑO solo del Treecko normal")
        print("2. Puede ser un recorte de cualquiera de tus capturas")
        print("3. Debe mostrar claramente el sprite del Treecko NORMAL")
        print(f"4. Guárdalo como: {ref_path}")
        
        input("Presiona ENTER cuando hayas guardado la imagen...")
        
        if os.path.exists(ref_path):
            print("✅ Imagen de referencia detectada")
            return True
        else:
            print("❌ No se encontró la imagen de referencia")
            return False
    
    def save_config(self):
        """Guarda la configuración"""
        try:
            config_path = "coordinates/emulator_coordinates.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 CONFIGURACIÓN GUARDADA")
            print("="*30)
            print(f"📁 Archivo: {config_path}")
            print(f"🎮 Emuladores: {len(self.config['emulators'])}")
            print(f"🖼️  Referencia: {self.config['reference_image']}")
            
            # Mostrar resumen
            for emu in self.config['emulators']:
                region = emu['pokemon_region']
                print(f"🎯 {emu['name']}: ({region['x']}, {region['y']}) {region['width']}x{region['height']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error guardando: {e}")
            return False
    
    def load_config(self):
        """Carga configuración existente"""
        try:
            config_path = "coordinates/emulator_coordinates.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            print(f"✅ Configuración cargada desde {config_path}")
            print(f"🎮 Emuladores configurados: {len(self.config.get('emulators', []))}")
            return True
            
        except FileNotFoundError:
            print("📄 No hay configuración previa")
            return False
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            return False


def main():
    print("⚙️  CONFIGURADOR SIMPLE DE EMULADORES")
    print("="*45)
    print("Este script usa tu coordinate_selector.py existente")
    print("="*45)
    
    builder = SimpleConfigBuilder()
    
    # Intentar cargar configuración existente
    builder.load_config()
    
    while True:
        print("\n📋 OPCIONES:")
        print("1. 🎯 Configurar coordenadas de emuladores")
        print("2. 🖼️  Configurar imagen de referencia")  
        print("3. 💾 Guardar configuración")
        print("4. 📋 Ver configuración actual")
        print("5. 🔄 Cargar configuración")
        print("6. ✅ Finalizar y continuar con detección")
        print("7. ❌ Salir")
        
        choice = input("\nElige opción: ").strip()
        
        if choice == '1':
            builder.setup_all_emulators()
            
        elif choice == '2':
            builder.create_reference_image()
            
        elif choice == '3':
            builder.save_config()
            
        elif choice == '4':
            if builder.config['emulators']:
                print("\n📋 CONFIGURACIÓN ACTUAL:")
                print("="*30)
                for emu in builder.config['emulators']:
                    region = emu['pokemon_region']
                    print(f"🎮 {emu['name']}")
                    print(f"   📍 ({region['x']}, {region['y']}) {region['width']}x{region['height']}")
            else:
                print("❌ No hay emuladores configurados")
                
        elif choice == '5':
            builder.load_config()
            
        elif choice == '6':
            if builder.config['emulators']:
                builder.save_config()
                print("\n🚀 ¡CONFIGURACIÓN COMPLETA!")
                print("💡 Ahora ejecuta: python Comparar_Imagen.py")
                break
            else:
                print("❌ Configura al menos un emulador primero")
                
        elif choice == '7':
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main()