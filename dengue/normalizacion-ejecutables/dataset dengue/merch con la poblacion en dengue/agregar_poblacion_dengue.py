#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar columna de población a los archivos CSV de dengue.

Agrega la columna "poblacion" al final de cada archivo CSV de dengue,
obteniendo los valores de los archivos de población según provincia, departamento y año.
"""

import os
import csv
import shutil
from datetime import datetime
from pathlib import Path

class AgregadorPoblacionDengue:
    def __init__(self):
        self.base_path = Path("/Users/ignaciosenestrari/Facu/tp-dengue")
        self.dengue_path = self.base_path / "dataset-dengue"
        self.poblacion_path = self.base_path / "dataset-poblacion"
        self.backup_path = self.base_path / "dataset-dengue" / "backup" / "backup automatico" / "poblacion"
        
        # Crear directorio de backup si no existe
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        self.poblacion_data = {}
        self.errores = []
        self.procesados = []
        self.backup_counter = 1
        
    def cargar_archivo_poblacion(self, provincia):
        """Carga los datos de población de una provincia específica"""
        archivo_poblacion = self.poblacion_path / f"{provincia}.csv"
        
        if not archivo_poblacion.exists():
            return None
        
        try:
            with open(archivo_poblacion, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                
                # Detectar columna de departamento/partido
                columna_departamento = None
                if 'Partido' in headers:
                    columna_departamento = 'Partido'
                elif 'Departamento' in headers:
                    columna_departamento = 'Departamento'
                else:
                    return None
                
                # Cargar datos
                datos = {}
                for row in reader:
                    departamento = row.get(columna_departamento, '').strip().lower()
                    if departamento:
                        datos[departamento] = row
                
                return {
                    'datos': datos,
                    'columna_departamento': columna_departamento,
                    'headers': headers
                }
                
        except Exception as e:
            print(f"✗ Error cargando archivo de población {provincia}: {e}")
            return None
    
    def crear_backup(self, archivo_path):
        """Crea un backup del archivo antes de modificarlo"""
        backup_dir = self.backup_path / f"back{self.backup_counter}"
        backup_dir.mkdir(exist_ok=True)
        
        archivo_nombre = archivo_path.name
        backup_file = backup_dir / archivo_nombre
        
        shutil.copy2(archivo_path, backup_file)
        print(f"✓ Backup creado: {backup_file}")
        return backup_file
    
    def obtener_poblacion(self, provincia, departamento, año):
        """Obtiene la población para un departamento en una provincia y año específicos"""
        # Cargar datos de la provincia si no están cargados
        if provincia not in self.poblacion_data:
            self.poblacion_data[provincia] = self.cargar_archivo_poblacion(provincia)
        
        if not self.poblacion_data[provincia]:
            return None
        
        datos_provincia = self.poblacion_data[provincia]['datos']
        departamento_lower = departamento.strip().lower()
        
        if departamento_lower not in datos_provincia:
            return None
        
        # Obtener valor del año
        fila_departamento = datos_provincia[departamento_lower]
        return fila_departamento.get(str(año), '').strip()
    
    def procesar_archivo_dengue(self, archivo_path):
        """Procesa un archivo CSV de dengue agregando la columna población"""
        errores_archivo = []
        filas_procesadas = 0
        filas_con_poblacion = 0
        
        print(f"\nProcesando: {archivo_path.name}")
        
        try:
            # Leer archivo original
            with open(archivo_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                rows = list(reader)
                headers = reader.fieldnames
            
            # Verificar columnas necesarias
            columnas_requeridas = ['provincia_nombre', 'departamento_nombre', 'ano']
            columnas_faltantes = [col for col in columnas_requeridas if col not in headers]
            
            if columnas_faltantes:
                errores_archivo.append({
                    'archivo': archivo_path.name,
                    'error': f'Columnas faltantes: {", ".join(columnas_faltantes)}',
                    'tipo': 'columnas_faltantes'
                })
                return errores_archivo, 0, 0
            
            # Crear backup
            self.crear_backup(archivo_path)
            
            # Preparar nuevos datos
            nuevos_headers = headers + ['poblacion']
            nuevas_filas = []
            
            for num_fila, row in enumerate(rows, start=2):  # Empezar en 2 porque la fila 1 es header
                provincia = row.get('provincia_nombre', '').strip()
                departamento = row.get('departamento_nombre', '').strip()
                año = row.get('ano', '').strip()
                filas_procesadas += 1
                
                if not provincia or not departamento or not año:
                    nueva_fila = [row.get(header, '') for header in headers] + ['']
                    nuevas_filas.append(nueva_fila)
                    continue
                
                # Obtener población
                poblacion = self.obtener_poblacion(provincia, departamento, año)
                
                if poblacion:
                    filas_con_poblacion += 1
                    nueva_fila = [row.get(header, '') for header in headers] + [poblacion]
                    nuevas_filas.append(nueva_fila)
                else:
                    errores_archivo.append({
                        'archivo': archivo_path.name,
                        'fila': num_fila,
                        'provincia': provincia,
                        'departamento': departamento,
                        'ano': año,
                        'error': 'No se encontró población para esta combinación',
                        'tipo': 'poblacion_no_encontrada'
                    })
                    # Agregar fila sin población
                    nueva_fila = [row.get(header, '') for header in headers] + ['']
                    nuevas_filas.append(nueva_fila)
            
            # Escribir archivo modificado
            with open(archivo_path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(nuevos_headers)
                writer.writerows(nuevas_filas)
            
            print(f"✓ Procesadas {filas_procesadas} filas, {filas_con_poblacion} con población")
            
            if errores_archivo:
                print(f"✗ {len(errores_archivo)} errores encontrados")
            else:
                print("✓ Sin errores")
            
            return errores_archivo, filas_procesadas, filas_con_poblacion
            
        except Exception as e:
            print(f"✗ Error procesando archivo: {e}")
            return [{'archivo': archivo_path.name, 'error': str(e), 'tipo': 'error_procesamiento'}], 0, 0
    
    def procesar_todos_archivos(self):
        """Procesa todos los archivos CSV de dengue"""
        print("Iniciando procesamiento de archivos de dengue...")
        
        archivos_csv = list(self.dengue_path.glob("dengue-*.csv"))
        
        if not archivos_csv:
            print("✗ No se encontraron archivos CSV de dengue")
            return False
        
        print(f"Encontrados {len(archivos_csv)} archivos CSV de dengue")
        
        total_filas = 0
        total_con_poblacion = 0
        
        for archivo in archivos_csv:
            errores, filas, con_poblacion = self.procesar_archivo_dengue(archivo)
            self.errores.extend(errores)
            total_filas += filas
            total_con_poblacion += con_poblacion
            
            self.procesados.append({
                'archivo': archivo.name,
                'filas_procesadas': filas,
                'filas_con_poblacion': con_poblacion,
                'errores': len(errores)
            })
        
        print(f"\n📊 RESUMEN GENERAL:")
        print(f"Total de archivos procesados: {len(archivos_csv)}")
        print(f"Total de filas procesadas: {total_filas}")
        print(f"Total de filas con población: {total_con_poblacion}")
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
            print(f"   Filas con población: {archivo_info['filas_con_poblacion']}")
            print(f"   Errores: {archivo_info['errores']}")
            
            if archivo_info['filas_procesadas'] > 0:
                porcentaje = (archivo_info['filas_con_poblacion'] / archivo_info['filas_procesadas']) * 100
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
                if 'provincia' in error:
                    print(f"   Provincia: {error['provincia']}")
                if 'departamento' in error:
                    print(f"   Departamento: {error['departamento']}")
                if 'ano' in error:
                    print(f"   Año: {error['ano']}")
                
                print(f"   Error: {error['error']}")
    
    def mostrar_estadisticas_provincias(self):
        """Muestra estadísticas de provincias procesadas"""
        if not self.errores:
            print("\n⚠️  No hay errores para analizar. Ejecute primero el procesamiento.")
            return
        
        print(f"\n📊 ESTADÍSTICAS POR PROVINCIA")
        print("=" * 60)
        
        # Agrupar errores por provincia
        por_provincia = {}
        for error in self.errores:
            if 'provincia' in error:
                provincia = error['provincia']
                if provincia not in por_provincia:
                    por_provincia[provincia] = 0
                por_provincia[provincia] += 1
        
        if por_provincia:
            for provincia, cantidad in sorted(por_provincia.items()):
                print(f"   {provincia}: {cantidad} errores")
        else:
            print("   No hay errores por provincia para mostrar")
    
    def verificar_archivo_poblacion(self, provincia):
        """Verifica si existe un archivo de población para una provincia"""
        archivo_poblacion = self.poblacion_path / f"{provincia}.csv"
        
        if archivo_poblacion.exists():
            print(f"✓ Archivo de población existe: {archivo_poblacion.name}")
            
            # Mostrar información del archivo
            try:
                with open(archivo_poblacion, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    headers = reader.fieldnames
                    
                    columna_departamento = None
                    if 'Partido' in headers:
                        columna_departamento = 'Partido'
                    elif 'Departamento' in headers:
                        columna_departamento = 'Departamento'
                    
                    print(f"   Columna de departamento: {columna_departamento}")
                    print(f"   Columnas de años: {[h for h in headers if h.isdigit()]}")
                    
            except Exception as e:
                print(f"   Error leyendo archivo: {e}")
        else:
            print(f"✗ Archivo de población NO existe: {provincia}.csv")
    
    def menu_principal(self):
        """Menú principal interactivo"""
        while True:
            print(f"\n{'='*60}")
            print("👥 AGREGADOR DE POBLACIÓN A ARCHIVOS DE DENGUE")
            print(f"{'='*60}")
            print("1. Procesar todos los archivos de dengue")
            print("2. Mostrar resumen por archivo")
            print("3. Mostrar errores detallados")
            print("4. Mostrar estadísticas por provincia")
            print("5. Verificar archivo de población")
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
                self.mostrar_estadisticas_provincias()
            
            elif opcion == '5':
                provincia = input("Ingrese el nombre de la provincia: ").strip()
                if provincia:
                    self.verificar_archivo_poblacion(provincia)
                else:
                    print("✗ Debe ingresar el nombre de la provincia")
            
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
    print("🚀 Iniciando Agregador de Población a Dengue")
    print("=" * 60)
    
    agregador = AgregadorPoblacionDengue()
    agregador.menu_principal()

if __name__ == "__main__":
    main()
