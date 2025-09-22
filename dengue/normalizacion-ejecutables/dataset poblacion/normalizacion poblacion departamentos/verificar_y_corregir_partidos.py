#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar y corregir la consistencia entre archivos de población
y la lista de departamentos.

Verifica que:
1. Cada partido en los CSV de población exista en lista-departamentos.csv
2. La provincia del partido coincida con el nombre del archivo CSV
"""

import os
import csv
import shutil
from datetime import datetime
from pathlib import Path

class VerificadorPartidos:
    def __init__(self):
        self.base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue")
        self.poblacion_path = self.base_path / "dataset-poblacion"
        self.departamentos_path = self.base_path / "dataset-departamentos" / "lista-departamentos.csv"
        self.backup_path = self.base_path / "dataset-poblacion" / "backup" / "automatico" / "revision partidos"
        
        # Crear directorio de backup si no existe
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        self.departamentos_data = {}
        self.errores = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def cargar_departamentos(self):
        """Carga la lista de departamentos desde el archivo CSV"""
        print("Cargando lista de departamentos...")
        
        try:
            with open(self.departamentos_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    nombre = row['Nombre'].strip().lower()
                    provincia = row['Provincia'].strip().lower()
                    
                    # Permitir múltiples provincias para el mismo nombre de partido
                    if nombre not in self.departamentos_data:
                        self.departamentos_data[nombre] = []
                    self.departamentos_data[nombre].append(provincia)
            
            # Mostrar estadísticas de partidos duplicados
            duplicados = {nombre: provincias for nombre, provincias in self.departamentos_data.items() if len(provincias) > 1}
            if duplicados:
                print(f"✓ Cargados {len(self.departamentos_data)} departamentos")
                print(f"📊 {len(duplicados)} partidos existen en múltiples provincias:")
                for nombre, provincias in list(duplicados.items())[:5]:  # Mostrar solo los primeros 5
                    print(f"   • {nombre}: {', '.join(provincias)}")
                if len(duplicados) > 5:
                    print(f"   ... y {len(duplicados) - 5} más")
            else:
                print(f"✓ Cargados {len(self.departamentos_data)} departamentos")
            
            return True
        except Exception as e:
            print(f"✗ Error cargando departamentos: {e}")
            return False
    
    def crear_backup(self, archivo_path):
        """Crea un backup del archivo antes de modificarlo"""
        backup_dir = self.backup_path / f"backup_{self.timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        archivo_nombre = archivo_path.name
        backup_file = backup_dir / archivo_nombre
        
        shutil.copy2(archivo_path, backup_file)
        print(f"✓ Backup creado: {backup_file}")
        return backup_file
    
    def verificar_archivo(self, archivo_path):
        """Verifica un archivo CSV de población"""
        archivo_nombre = archivo_path.stem.lower()
        errores_archivo = []
        
        print(f"\nVerificando: {archivo_path.name}")
        
        try:
            with open(archivo_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for num_fila, row in enumerate(reader, start=2):  # Empezar en 2 porque la fila 1 es header
                    partido = row.get('Partido', '').strip().lower()
                    
                    if not partido:  # Saltar filas vacías
                        continue
                    
                    # Verificar si el partido existe en la lista de departamentos
                    if partido not in self.departamentos_data:
                        errores_archivo.append({
                            'archivo': archivo_path.name,
                            'fila': num_fila,
                            'partido': partido,
                            'tipo': 'partido_no_existe',
                            'provincia_archivo': archivo_nombre
                        })
                    else:
                        # Verificar si el partido existe en la provincia del archivo
                        provincias_partido = self.departamentos_data[partido]
                        if archivo_nombre not in provincias_partido:
                            errores_archivo.append({
                                'archivo': archivo_path.name,
                                'fila': num_fila,
                                'partido': partido,
                                'tipo': 'provincia_incorrecta',
                                'provincia_archivo': archivo_nombre,
                                'provincias_correctas': provincias_partido
                            })
            
            if errores_archivo:
                print(f"✗ Encontrados {len(errores_archivo)} errores")
                self.errores.extend(errores_archivo)
            else:
                print("✓ Sin errores")
                
        except Exception as e:
            print(f"✗ Error procesando archivo: {e}")
    
    def verificar_todos_archivos(self):
        """Verifica todos los archivos CSV de población"""
        print("Iniciando verificación de archivos de población...")
        
        if not self.cargar_departamentos():
            return False
        
        archivos_csv = list(self.poblacion_path.glob("*.csv"))
        
        if not archivos_csv:
            print("✗ No se encontraron archivos CSV en dataset-poblacion")
            return False
        
        print(f"Encontrados {len(archivos_csv)} archivos CSV")
        
        for archivo in archivos_csv:
            self.verificar_archivo(archivo)
        
        return True
    
    def mostrar_resumen(self):
        """Muestra un resumen de los errores encontrados"""
        if not self.errores:
            print("\n🎉 ¡Excelente! No se encontraron errores.")
            return
        
        print(f"\n📊 RESUMEN DE ERRORES")
        print(f"Total de errores: {len(self.errores)}")
        
        # Agrupar por tipo de error
        por_tipo = {}
        for error in self.errores:
            tipo = error['tipo']
            if tipo not in por_tipo:
                por_tipo[tipo] = 0
            por_tipo[tipo] += 1
        
        print("\nErrores por tipo:")
        for tipo, cantidad in por_tipo.items():
            if tipo == 'partido_no_existe':
                print(f"  • Partidos que no existen: {cantidad}")
            elif tipo == 'provincia_incorrecta':
                print(f"  • Provincias incorrectas: {cantidad}")
    
    def mostrar_errores_detallados(self):
        """Muestra los errores de forma detallada"""
        if not self.errores:
            return
        
        print(f"\n📋 ERRORES DETALLADOS")
        print("=" * 80)
        
        for i, error in enumerate(self.errores, 1):
            print(f"\n{i}. Archivo: {error['archivo']}")
            print(f"   Fila: {error['fila']}")
            print(f"   Partido: {error['partido']}")
            
            if error['tipo'] == 'partido_no_existe':
                print(f"   Error: El partido no existe en la lista de departamentos")
            elif error['tipo'] == 'provincia_incorrecta':
                print(f"   Error: El partido no existe en esta provincia")
                print(f"   Provincia del archivo: {error['provincia_archivo']}")
                print(f"   Provincias donde existe: {', '.join(error['provincias_correctas'])}")
    
    def obtener_sugerencias(self, partido):
        """Obtiene sugerencias para un partido que no existe"""
        sugerencias = []
        partido_lower = partido.lower()
        
        for dept_nombre, dept_provincias in self.departamentos_data.items():
            # Buscar coincidencias parciales
            if (partido_lower in dept_nombre or 
                dept_nombre in partido_lower or
                self.calcular_similitud(partido_lower, dept_nombre) > 0.7):
                sugerencias.append((dept_nombre, dept_provincias))
        
        return sugerencias[:5]  # Máximo 5 sugerencias
    
    def calcular_similitud(self, str1, str2):
        """Calcula similitud entre dos strings"""
        # Algoritmo simple de similitud
        if str1 == str2:
            return 1.0
        
        # Contar caracteres comunes
        chars1 = set(str1)
        chars2 = set(str2)
        intersection = chars1.intersection(chars2)
        union = chars1.union(chars2)
        
        return len(intersection) / len(union) if union else 0
    
    def corregir_error(self, error_index):
        """Corrige un error específico"""
        if error_index < 0 or error_index >= len(self.errores):
            print("✗ Índice de error inválido")
            return False
        
        error = self.errores[error_index]
        archivo_path = self.poblacion_path / error['archivo']
        
        print(f"\n🔧 Corrigiendo error en {error['archivo']}, fila {error['fila']}")
        print(f"Partido: {error['partido']}")
        
        if error['tipo'] == 'partido_no_existe':
            print("\nOpciones:")
            print("1. Cambiar nombre del partido")
            print("2. Eliminar la fila")
            print("3. Ver sugerencias")
            print("4. Cancelar")
            
            opcion = input("\nSeleccione una opción (1-4): ").strip()
            
            if opcion == '1':
                nuevo_nombre = input("Ingrese el nuevo nombre del partido: ").strip()
                if nuevo_nombre:
                    return self.cambiar_nombre_partido(archivo_path, error['fila'], error['partido'], nuevo_nombre)
            elif opcion == '2':
                return self.eliminar_fila(archivo_path, error['fila'])
            elif opcion == '3':
                sugerencias = self.obtener_sugerencias(error['partido'])
                if sugerencias:
                    print("\nSugerencias:")
                    for i, (nombre, provincias) in enumerate(sugerencias, 1):
                        print(f"{i}. {nombre} (Provincias: {', '.join(provincias)})")
                    
                    try:
                        sel = int(input("Seleccione una sugerencia (0 para cancelar): "))
                        if 1 <= sel <= len(sugerencias):
                            nombre_sugerido = sugerencias[sel-1][0]
                            return self.cambiar_nombre_partido(archivo_path, error['fila'], error['partido'], nombre_sugerido)
                    except ValueError:
                        pass
            elif opcion == '4':
                return False
        
        elif error['tipo'] == 'provincia_incorrecta':
            print(f"\nProvincia del archivo: {error['provincia_archivo']}")
            print(f"Provincias donde existe el partido: {', '.join(error['provincias_correctas'])}")
            print("\nOpciones:")
            print("1. Cambiar nombre del partido")
            print("2. Eliminar la fila")
            print("3. Cancelar")
            
            opcion = input("\nSeleccione una opción (1-3): ").strip()
            
            if opcion == '1':
                nuevo_nombre = input("Ingrese el nuevo nombre del partido: ").strip()
                if nuevo_nombre:
                    return self.cambiar_nombre_partido(archivo_path, error['fila'], error['partido'], nuevo_nombre)
            elif opcion == '2':
                return self.eliminar_fila(archivo_path, error['fila'])
            elif opcion == '3':
                return False
        
        return False
    
    def cambiar_nombre_partido(self, archivo_path, fila, nombre_actual, nombre_nuevo):
        """Cambia el nombre de un partido en un archivo"""
        try:
            # Crear backup
            self.crear_backup(archivo_path)
            
            # Leer archivo
            with open(archivo_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Modificar línea específica
            if fila <= len(lines):
                # Encontrar la columna Partido en el header
                header = lines[0].strip().split(',')
                try:
                    partido_index = header.index('Partido')
                except ValueError:
                    print("✗ No se encontró la columna 'Partido'")
                    return False
                
                # Modificar la línea
                line_parts = lines[fila-1].strip().split(',')
                if partido_index < len(line_parts):
                    line_parts[partido_index] = nombre_nuevo
                    lines[fila-1] = ','.join(line_parts) + '\n'
                    
                    # Escribir archivo modificado
                    with open(archivo_path, 'w', encoding='utf-8') as file:
                        file.writelines(lines)
                    
                    print(f"✓ Partido cambiado de '{nombre_actual}' a '{nombre_nuevo}'")
                    return True
                else:
                    print("✗ Error: índice de columna fuera de rango")
                    return False
            else:
                print("✗ Error: número de fila fuera de rango")
                return False
                
        except Exception as e:
            print(f"✗ Error modificando archivo: {e}")
            return False
    
    def eliminar_fila(self, archivo_path, fila):
        """Elimina una fila de un archivo"""
        try:
            # Crear backup
            self.crear_backup(archivo_path)
            
            # Leer archivo
            with open(archivo_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Eliminar línea específica
            if 1 < fila <= len(lines):  # No eliminar header
                del lines[fila-1]
                
                # Escribir archivo modificado
                with open(archivo_path, 'w', encoding='utf-8') as file:
                    file.writelines(lines)
                
                print(f"✓ Fila {fila} eliminada")
                return True
            else:
                print("✗ Error: no se puede eliminar esa fila")
                return False
                
        except Exception as e:
            print(f"✗ Error eliminando fila: {e}")
            return False
    
    def menu_principal(self):
        """Menú principal interactivo"""
        while True:
            print(f"\n{'='*60}")
            print("🔍 VERIFICADOR Y CORRECTOR DE PARTIDOS")
            print(f"{'='*60}")
            print("1. Verificar todos los archivos")
            print("2. Mostrar resumen de errores")
            print("3. Mostrar errores detallados")
            print("4. Corregir error específico")
            print("5. Salir")
            
            opcion = input("\nSeleccione una opción (1-5): ").strip()
            
            if opcion == '1':
                if self.verificar_todos_archivos():
                    print("\n✓ Verificación completada")
                else:
                    print("\n✗ Error en la verificación")
            
            elif opcion == '2':
                self.mostrar_resumen()
            
            elif opcion == '3':
                self.mostrar_errores_detallados()
            
            elif opcion == '4':
                if not self.errores:
                    print("\n⚠️  No hay errores para corregir. Ejecute primero la verificación.")
                    continue
                
                print(f"\nErrores disponibles (1-{len(self.errores)}):")
                for i, error in enumerate(self.errores, 1):
                    print(f"{i}. {error['archivo']} - Fila {error['fila']} - {error['partido']}")
                
                try:
                    error_index = int(input(f"\nSeleccione el error a corregir (1-{len(self.errores)}): ")) - 1
                    if self.corregir_error(error_index):
                        # Remover error de la lista si se corrigió exitosamente
                        del self.errores[error_index]
                        print("✓ Error corregido y removido de la lista")
                except ValueError:
                    print("✗ Opción inválida")
            
            elif opcion == '5':
                print("\n👋 ¡Hasta luego!")
                break
            
            else:
                print("\n✗ Opción inválida")

def main():
    """Función principal"""
    print("🚀 Iniciando Verificador y Corregidor de Partidos")
    print("=" * 60)
    
    verificador = VerificadorPartidos()
    verificador.menu_principal()

if __name__ == "__main__":
    main()
