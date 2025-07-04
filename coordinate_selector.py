#!/usr/bin/env python3
"""
Script para seleccionar coordenadas de la región del Pokémon en capturas de emuladores.
Uso: python3 coordinate_selector.py imagen.png
"""

import cv2
import sys
import os

class CoordinateSelector:
    def __init__(self):
        self.selecting = False
        self.start_point = (0, 0)
        self.end_point = (0, 0)
        self.image = None
        self.clone = None
        
    def mouse_callback(self, event, x, y, flags, param):
        """Callback para manejar eventos del mouse"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.selecting = True
            self.start_point = (x, y)
            self.end_point = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.selecting:
                self.end_point = (x, y)
                # Actualizar imagen con rectángulo temporal
                temp_image = self.clone.copy()
                cv2.rectangle(temp_image, self.start_point, self.end_point, (0, 255, 0), 2)
                cv2.imshow("Selector de coordenadas", temp_image)
                
        elif event == cv2.EVENT_LBUTTONUP:
            self.selecting = False
            self.end_point = (x, y)
            
            # Calcular coordenadas finales
            x1, y1 = self.start_point
            x2, y2 = self.end_point
            
            # Asegurar que x1,y1 sea la esquina superior izquierda
            top_left_x = min(x1, x2)
            top_left_y = min(y1, y2)
            bottom_right_x = max(x1, x2)
            bottom_right_y = max(y1, y2)
            
            width = bottom_right_x - top_left_x
            height = bottom_right_y - top_left_y
            
            # Mostrar coordenadas
            print("\n" + "="*50)
            print("🎯 COORDENADAS DETECTADAS:")
            print("="*50)
            print(f"Esquina superior izquierda: ({top_left_x}, {top_left_y})")
            print(f"Esquina inferior derecha: ({bottom_right_x}, {bottom_right_y})")
            print(f"Ancho: {width} pixels")
            print(f"Alto: {height} pixels")
            print("\n📋 Para usar en tu código:")
            print(f"pokemon_region = ({top_left_x}, {top_left_y}, {width}, {height})")
            print("="*50)
            
            # Mostrar región seleccionada
            if width > 0 and height > 0:
                cropped = self.image[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
                cv2.imshow("Región seleccionada - Presiona cualquier tecla", cropped)
                
                # Guardar región seleccionada
                filename = f"region_selected_{top_left_x}_{top_left_y}_{width}_{height}.png"
                cv2.imwrite(filename, cropped)
                print(f"💾 Región guardada como: {filename}")
            
            # Dibujar rectángulo final
            cv2.rectangle(self.image, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 255, 0), 2)
            cv2.imshow("Selector de coordenadas", self.image)

    def select_region(self, image_path):
        """Función principal para seleccionar región"""
        if not os.path.exists(image_path):
            print(f"❌ Error: No se encuentra la imagen {image_path}")
            return
            
        # Cargar imagen
        self.image = cv2.imread(image_path)
        if self.image is None:
            print(f"❌ Error: No se pudo cargar la imagen {image_path}")
            return
            
        self.clone = self.image.copy()
        
        print("🎮 SELECTOR DE COORDENADAS DEL POKÉMON")
        print("="*50)
        print("📝 Instrucciones:")
        print("1. Haz click y arrastra para seleccionar la región del Pokémon")
        print("2. Suelta el mouse para confirmar la selección")
        print("3. Presiona ESC para salir")
        print("4. Presiona 'r' para reiniciar selección")
        print("="*50)
        
        # Crear ventana y configurar callback
        cv2.namedWindow("Selector de coordenadas", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Selector de coordenadas", self.mouse_callback)
        cv2.imshow("Selector de coordenadas", self.image)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC para salir
                break
            elif key == ord('r'):  # 'r' para reiniciar
                self.image = self.clone.copy()
                cv2.imshow("Selector de coordenadas", self.image)
                print("🔄 Selección reiniciada")
                
        cv2.destroyAllWindows()

def main():
    if len(sys.argv) != 2:
        print("🎯 Uso: python3 coordinate_selector.py <imagen.png>")
        print("\n📋 Ejemplos:")
        print("  python3 coordinate_selector.py emulador1_batalla.png")
        print("  python3 coordinate_selector.py emulador2_batalla.png")
        return
    
    image_path = sys.argv[1]
    selector = CoordinateSelector()
    selector.select_region(image_path)
    
    print("\n✅ Selector cerrado. ¡Usa las coordenadas mostradas en tu bot!")

if __name__ == "__main__":
    main()