#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar columna UTA_ID a los archivos CSV de población.

Agrega la columna UTA_ID al principio de cada archivo CSV de población,
basándose en el Código UTA 2020 de lista-departamentos.csv.

Matching estricto: Nombre del partido + Provincia del archivo
"""

import os
import csv
import shutil
from datetime import datetime
from pathlib import Path

class AgregadorUTAID:
    def __init__(self):
        self.base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue")
        self.poblacion_path = self.base_path / "dataset-poblacion"
        self.departamentos_path = self.base_path / "dataset-departamentos" / "lista-departamentos.csv"
        self.backup_path = self.base_path / "dataset-poblacion" / "backup" / "automatico" / "revision partidos"
        
        # Crear directorio de backup si no existe
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        self.departamentos_data = {}
        self.errores = []
        self.procesados = []
        self.backup_counter = 1
        
    def cargar_departamentos(self):
        """Carga la lista de departamentos desde el archivo CSV"""
        print("Cargando lista de departamentos...")
        
        try:
            with open(self.departamentos_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    nombre = row['Nombre'].strip().lower()
                    provincia = row['Provincia'].strip().lower()
                    uta_id = row['Código UTA 2020'].strip()
                    
                    # Crear clave única: nombre + provincia
                    clave = f"{nombre}|{provincia}"
                    self.departamentos_data[clave] = uta_id
            
            print(f"✓ Cargados {len(self.departamentos_data)} departamentos")
            return True
        except Exception as e:
            print(f"✗ Error cargando departamentos: {e}")
            return False
    
    def crear_backup(self, archivo_path):
        """Crea un backup del archivo antes de modificarlo"""
        backup_dir = self.backup_path / f"back{self.backup_counter}"
        backup_dir.mkdir(exist_ok=True)
        
        archivo_nombre = archivo_path.name
        backup_file = backup_dir / archivo_nombre
        
        shutil.copy2(archivo_path, backup_file)
        print(f"✓ Backup creado: {backup_file}")
        return backup_file
    
    def obtener_uta_id(self, partido, provincia_archivo):
        """Obtiene el UTA_ID para un partido en una provincia específica"""
        clave = f"{partido.lower()}|{provincia_archivo.lower()}"
        return self.departamentos_data.get(clave)
    
    def procesar_archivo(self, archivo_path):
        """Procesa un archivo CSV agregando la columna UTA_ID"""
        archivo_nombre = archivo_path.stem.lower()
        errores_archivo = []
        filas_procesadas = 0
        filas_con_id = 0
        
        print(f"\nProcesando: {archivo_path.name}")
        
        try:
            # Leer archivo original
            with open(archivo_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                headers = reader.fieldnames
            
            # Verificar que existe la columna Partido o Departamento
            columna_partido = None
            if 'Partido' in headers:
                columna_partido = 'Partido'
            elif 'Departamento' in headers:
                columna_partido = 'Departamento'
            else:
                errores_archivo.append({
                    'archivo': archivo_path.name,
                    'error': 'No se encontró la columna "Partido" ni "Departamento"',
                    'tipo': 'columna_faltante'
                })
                return errores_archivo, 0, 0
            
            # Crear backup
            self.crear_backup(archivo_path)
            
            # Preparar nuevos datos
            nuevos_headers = ['UTA_ID'] + headers
            nuevas_filas = []
            
            for num_fila, row in enumerate(rows, start=2):  # Empezar en 2 porque la fila 1 es header
                partido = row.get(columna_partido, '').strip()
                filas_procesadas += 1
                
                if not partido:  # Saltar filas vacías
                    nueva_fila = [''] + [row.get(header, '') for header in headers]
                    nuevas_filas.append(nueva_fila)
                    continue
                
                # Obtener UTA_ID
                uta_id = self.obtener_uta_id(partido, archivo_nombre)
                
                if uta_id:
                    filas_con_id += 1
                    nueva_fila = [uta_id] + [row.get(header, '') for header in headers]
                    nuevas_filas.append(nueva_fila)
                else:
                    errores_archivo.append({
                        'archivo': archivo_path.name,
                        'fila': num_fila,
                        'partido': partido,
                        'provincia': archivo_nombre,
                        'error': 'No se encontró UTA_ID para este partido en esta provincia',
                        'tipo': 'uta_id_no_encontrado'
                    })
                    # Agregar fila sin UTA_ID
                    nueva_fila = [''] + [row.get(header, '') for header in headers]
                    nuevas_filas.append(nueva_fila)
            
            # Escribir archivo modificado
            with open(archivo_path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(nuevos_headers)
                writer.writerows(nuevas_filas)
            
            print(f"✓ Procesadas {filas_procesadas} filas, {filas_con_id} con UTA_ID")
            print(f"✓ Columna detectada: '{columna_partido}'")
            
            if errores_archivo:
                print(f"✗ {len(errores_archivo)} errores encontrados")
            else:
                print("✓ Sin errores")
            
            return errores_archivo, filas_procesadas, filas_con_id
            
        except Exception as e:
            print(f"✗ Error procesando archivo: {e}")
            return [{'archivo': archivo_path.name, 'error': str(e), 'tipo': 'error_procesamiento'}], 0, 0
    
    def procesar_todos_archivos(self):
        """Procesa todos los archivos CSV de población"""
        print("Iniciando procesamiento de archivos de población...")
        
        if not self.cargar_departamentos():
            return False
        
        archivos_csv = list(self.poblacion_path.glob("*.csv"))
        
        if not archivos_csv:
            print("✗ No se encontraron archivos CSV en dataset-poblacion")
            return False
        
        print(f"Encontrados {len(archivos_csv)} archivos CSV")
        
        total_filas = 0
        total_con_id = 0
        
        for archivo in archivos_csv:
            errores, filas, con_id = self.procesar_archivo(archivo)
            self.errores.extend(errores)
            total_filas += filas
            total_con_id += con_id
            
            self.procesados.append({
                'archivo': archivo.name,
                'filas_procesadas': filas,
                'filas_con_id': con_id,
                'errores': len(errores)
            })
        
        print(f"\n📊 RESUMEN GENERAL:")
        print(f"Total de archivos procesados: {len(archivos_csv)}")
        print(f"Total de filas procesadas: {total_filas}")
        print(f"Total de filas con UTA_ID: {total_con_id}")
        print(f"Total de errores: {len(self.errores)}")
        
        return True
    
    def mostrar_resumen_archivos(self):
        """Muestra un resumen por archivo"""
        if not self.procesados:
            print("\n⚠️  No hay archivos procesados. Ejecute primero el procesamiento.")
            return
        
        print(f"\n📋 RESUMEN POR ARCHIVO")
        print("=" * 80)
        
        for archivo_info in self.procesados:
            print(f"\n📄 {archivo_info['archivo']}")
            print(f"   Filas procesadas: {archivo_info['filas_procesadas']}")
            print(f"   Filas con UTA_ID: {archivo_info['filas_con_id']}")
            print(f"   Errores: {archivo_info['errores']}")
            
            if archivo_info['filas_procesadas'] > 0:
                porcentaje = (archivo_info['filas_con_id'] / archivo_info['filas_procesadas']) * 100
                print(f"   Éxito: {porcentaje:.1f}%")
    
    def mostrar_errores_detallados(self):
        """Muestra los errores de forma detallada"""
        if not self.errores:
            print("\n🎉 ¡Excelente! No se encontraron errores.")
            return
        
        print(f"\n❌ ERRORES DETALLADOS")
        print("=" * 80)
        
        # Agrupar errores por tipo
        por_tipo = {}
        for error in self.errores:
            tipo = error['tipo']
            if tipo not in por_tipo:
                por_tipo[tipo] = []
            por_tipo[tipo].append(error)
        
        for tipo, errores_tipo in por_tipo.items():
            print(f"\n🔍 {tipo.upper().replace('_', ' ')} ({len(errores_tipo)} errores)")
            print("-" * 50)
            
            for i, error in enumerate(errores_tipo, 1):
                print(f"\n{i}. Archivo: {error['archivo']}")
                
                if 'fila' in error:
                    print(f"   Fila: {error['fila']}")
                if 'partido' in error:
                    print(f"   Partido: {error['partido']}")
                if 'provincia' in error:
                    print(f"   Provincia: {error['provincia']}")
                
                print(f"   Error: {error['error']}")
    
    def mostrar_sugerencias_uta_id(self, partido, provincia):
        """Muestra sugerencias para partidos sin UTA_ID"""
        print(f"\n💡 SUGERENCIAS PARA: {partido} en {provincia}")
        print("-" * 50)
        
        # Buscar partidos similares
        sugerencias = []
        partido_lower = partido.lower()
        
        for clave, uta_id in self.departamentos_data.items():
            nombre_dept, prov_dept = clave.split('|')
            
            # Buscar coincidencias parciales
            if (partido_lower in nombre_dept or 
                nombre_dept in partido_lower or
                self.calcular_similitud(partido_lower, nombre_dept) > 0.7):
                sugerencias.append((nombre_dept, prov_dept, uta_id))
        
        if sugerencias:
            print("Partidos similares encontrados:")
            for i, (nombre, prov, uta_id) in enumerate(sugerencias[:5], 1):
                print(f"{i}. {nombre} (Provincia: {prov}, UTA_ID: {uta_id})")
        else:
            print("No se encontraron partidos similares.")
    
    def calcular_similitud(self, str1, str2):
        """Calcula similitud entre dos strings"""
        if str1 == str2:
            return 1.0
        
        chars1 = set(str1)
        chars2 = set(str2)
        intersection = chars1.intersection(chars2)
        union = chars1.union(chars2)
        
        return len(intersection) / len(union) if union else 0
    
    def exportar_errores(self):
        """Exporta los errores a un archivo CSV"""
        if not self.errores:
            print("\n⚠️  No hay errores para exportar.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_errores = self.backup_path / f"errores_uta_id_{timestamp}.csv"
        
        try:
            with open(archivo_errores, 'w', encoding='utf-8', newline='') as file:
                if self.errores:
                    fieldnames = self.errores[0].keys()
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.errores)
            
            print(f"✓ Errores exportados a: {archivo_errores}")
        except Exception as e:
            print(f"✗ Error exportando errores: {e}")
    
    def menu_principal(self):
        """Menú principal interactivo"""
        while True:
            print(f"\n{'='*60}")
            print("🆔 AGREGADOR DE UTA_ID A ARCHIVOS DE POBLACIÓN")
            print(f"{'='*60}")
            print("1. Procesar todos los archivos")
            print("2. Mostrar resumen por archivo")
            print("3. Mostrar errores detallados")
            print("4. Ver sugerencias para un partido")
            print("5. Exportar errores a CSV")
            print("6. Incrementar contador de backup")
            print("7. Salir")
            
            opcion = input("\nSeleccione una opción (1-7): ").strip()
            
            if opcion == '1':
                if self.procesar_todos_archivos():
                    print("\n✓ Procesamiento completado")
                    self.backup_counter += 1
                else:
                    print("\n✗ Error en el procesamiento")
            
            elif opcion == '2':
                self.mostrar_resumen_archivos()
            
            elif opcion == '3':
                self.mostrar_errores_detallados()
            
            elif opcion == '4':
                if not self.departamentos_data:
                    print("\n⚠️  Debe cargar los departamentos primero. Ejecute la opción 1.")
                    continue
                
                partido = input("Ingrese el nombre del partido: ").strip()
                provincia = input("Ingrese la provincia: ").strip()
                
                if partido and provincia:
                    self.mostrar_sugerencias_uta_id(partido, provincia)
                else:
                    print("✗ Debe ingresar tanto el partido como la provincia")
            
            elif opcion == '5':
                self.exportar_errores()
            
            elif opcion == '6':
                self.backup_counter += 1
                print(f"✓ Contador de backup incrementado a: back{self.backup_counter}")
            
            elif opcion == '7':
                print("\n👋 ¡Hasta luego!")
                break
            
            else:
                print("\n✗ Opción inválida")

def main():
    """Función principal"""
    print("🚀 Iniciando Agregador de UTA_ID")
    print("=" * 60)
    
    agregador = AgregadorUTAID()
    agregador.menu_principal()

if __name__ == "__main__":
    main()
