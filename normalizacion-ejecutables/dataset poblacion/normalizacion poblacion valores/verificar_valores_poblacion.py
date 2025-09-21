#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar valores extraños, nulos, vacíos y desconocidos 
en todos los datasets de población.

Autor: Sistema de Normalización
Fecha: 2025
"""

import os
import pandas as pd
import shutil
from datetime import datetime
import re
import sys

class VerificadorPoblacion:
    def __init__(self):
        self.directorio_poblacion = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-poblacion"
        self.directorio_backup = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-poblacion/backup/automatico/revision valores"
        self.problemas_encontrados = []
        self.archivos_procesados = []
        
    def crear_backup(self):
        """Crea un backup de todos los archivos CSV antes de la verificación"""
        print("🔄 Creando backup de seguridad...")
        
        # Crear timestamp para el backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(self.directorio_backup, f"backup_{timestamp}")
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copiar todos los archivos CSV
            archivos_csv = [f for f in os.listdir(self.directorio_poblacion) if f.endswith('.csv')]
            
            for archivo in archivos_csv:
                origen = os.path.join(self.directorio_poblacion, archivo)
                destino = os.path.join(backup_dir, archivo)
                shutil.copy2(origen, destino)
                print(f"  ✅ Backup creado: {archivo}")
            
            print(f"📁 Backup completo guardado en: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return None
    
    def es_valor_extraño(self, valor):
        """
        Verifica si un valor es extraño, nulo, vacío o desconocido
        """
        if pd.isna(valor):
            return True, "Valor nulo (NaN)"
        
        if valor == "" or valor == " " or str(valor).strip() == "":
            return True, "Valor vacío"
        
        valor_str = str(valor).strip().lower()
        
        # Valores desconocidos comunes
        valores_desconocidos = [
            'desconocido', 'sin datos', 'n/a', 'na', 'null', 'none', 
            '?', '??', '???', 'no disponible', 'no disponible', 
            'sin informacion', 'sin información', 'pendiente',
            'tbd', 'por definir', 'por determinar'
        ]
        
        if valor_str in valores_desconocidos:
            return True, f"Valor desconocido: '{valor}'"
        
        # Verificar si es un número válido
        try:
            # Intentar convertir a float
            num_valor = float(valor)
            
            # Verificar si es un entero (población debería ser entera)
            if not num_valor.is_integer():
                return True, f"Valor no entero: '{valor}'"
            
            # Verificar si es negativo
            if num_valor < 0:
                return True, f"Valor negativo: '{valor}'"
                
        except (ValueError, TypeError):
            # No es un número válido
            return True, f"Valor no numérico: '{valor}'"
        
        return False, ""
    
    def verificar_archivo(self, archivo_path):
        """
        Verifica un archivo CSV específico
        """
        print(f"\n🔍 Verificando: {os.path.basename(archivo_path)}")
        
        try:
            # Leer el archivo CSV
            df = pd.read_csv(archivo_path, encoding='utf-8')
            
            problemas_archivo = []
            
            # Verificar cada fila y columna (excepto la primera columna que son nombres)
            for idx, row in df.iterrows():
                for col_idx, (col_name, valor) in enumerate(row.items()):
                    # Saltar la primera columna (nombres de departamentos/comunas/partidos)
                    if col_idx == 0:
                        continue
                    
                    es_extraño, motivo = self.es_valor_extraño(valor)
                    
                    if es_extraño:
                        problema = {
                            'archivo': os.path.basename(archivo_path),
                            'linea': idx + 2,  # +2 porque pandas cuenta desde 0 y el header es línea 1
                            'columna': col_name,
                            'valor': valor,
                            'motivo': motivo
                        }
                        problemas_archivo.append(problema)
            
            if problemas_archivo:
                self.problemas_encontrados.extend(problemas_archivo)
                print(f"  ⚠️  Encontrados {len(problemas_archivo)} problemas")
            else:
                print(f"  ✅ Sin problemas encontrados")
            
            self.archivos_procesados.append(os.path.basename(archivo_path))
            
        except Exception as e:
            print(f"  ❌ Error procesando archivo: {e}")
            problema_error = {
                'archivo': os.path.basename(archivo_path),
                'linea': 'N/A',
                'columna': 'N/A',
                'valor': 'N/A',
                'motivo': f"Error al procesar archivo: {e}"
            }
            self.problemas_encontrados.append(problema_error)
    
    def mostrar_problemas(self):
        """
        Muestra todos los problemas encontrados de forma organizada
        """
        if not self.problemas_encontrados:
            print("\n🎉 ¡Excelente! No se encontraron problemas en ningún archivo.")
            return
        
        print(f"\n📊 RESUMEN DE PROBLEMAS ENCONTRADOS")
        print(f"{'='*60}")
        print(f"Total de problemas: {len(self.problemas_encontrados)}")
        print(f"Archivos con problemas: {len(set(p['archivo'] for p in self.problemas_encontrados))}")
        
        # Agrupar por archivo
        problemas_por_archivo = {}
        for problema in self.problemas_encontrados:
            archivo = problema['archivo']
            if archivo not in problemas_por_archivo:
                problemas_por_archivo[archivo] = []
            problemas_por_archivo[archivo].append(problema)
        
        # Mostrar problemas por archivo
        for archivo, problemas in problemas_por_archivo.items():
            print(f"\n📁 {archivo} ({len(problemas)} problemas)")
            print("-" * 50)
            
            for problema in problemas:
                print(f"  Línea {problema['linea']}, Columna '{problema['columna']}':")
                print(f"    Valor: '{problema['valor']}'")
                print(f"    Problema: {problema['motivo']}")
                print()
    
    def procesar_interactivo(self):
        """
        Procesa los problemas de forma interactiva
        """
        if not self.problemas_encontrados:
            return
        
        print(f"\n🔧 MODO INTERACTIVO")
        print(f"{'='*40}")
        
        for i, problema in enumerate(self.problemas_encontrados, 1):
            print(f"\nProblema {i}/{len(self.problemas_encontrados)}")
            print(f"Archivo: {problema['archivo']}")
            print(f"Línea: {problema['linea']}")
            print(f"Columna: {problema['columna']}")
            print(f"Valor actual: '{problema['valor']}'")
            print(f"Problema: {problema['motivo']}")
            
            while True:
                print("\nOpciones:")
                print("1. Saltar este problema")
                print("2. Ver más detalles del archivo")
                print("3. Terminar verificación")
                
                opcion = input("\nSelecciona una opción (1-3): ").strip()
                
                if opcion == "1":
                    break
                elif opcion == "2":
                    self.mostrar_detalles_archivo(problema['archivo'])
                elif opcion == "3":
                    print("👋 Verificación terminada por el usuario.")
                    return
                else:
                    print("❌ Opción inválida. Por favor selecciona 1, 2 o 3.")
    
    def mostrar_detalles_archivo(self, nombre_archivo):
        """
        Muestra detalles del archivo específico
        """
        archivo_path = os.path.join(self.directorio_poblacion, nombre_archivo)
        
        try:
            df = pd.read_csv(archivo_path, encoding='utf-8')
            print(f"\n📋 Detalles del archivo: {nombre_archivo}")
            print(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
            print(f"Columnas: {list(df.columns)}")
            print(f"Primeras 5 filas:")
            print(df.head().to_string())
            
        except Exception as e:
            print(f"❌ Error mostrando detalles: {e}")
    
    def ejecutar_verificacion(self):
        """
        Ejecuta la verificación completa
        """
        print("🚀 INICIANDO VERIFICACIÓN DE VALORES EN DATASETS DE POBLACIÓN")
        print("="*70)
        
        # Crear backup
        backup_dir = self.crear_backup()
        if not backup_dir:
            print("❌ No se pudo crear el backup. Abortando verificación.")
            return
        
        # Verificar que el directorio existe
        if not os.path.exists(self.directorio_poblacion):
            print(f"❌ Directorio no encontrado: {self.directorio_poblacion}")
            return
        
        # Obtener todos los archivos CSV
        archivos_csv = [f for f in os.listdir(self.directorio_poblacion) 
                       if f.endswith('.csv') and not f.startswith('.')]
        
        if not archivos_csv:
            print("❌ No se encontraron archivos CSV en el directorio.")
            return
        
        print(f"\n📁 Encontrados {len(archivos_csv)} archivos CSV para verificar")
        
        # Verificar cada archivo
        for archivo in sorted(archivos_csv):
            archivo_path = os.path.join(self.directorio_poblacion, archivo)
            self.verificar_archivo(archivo_path)
        
        # Mostrar resumen
        self.mostrar_problemas()
        
        # Procesar interactivamente si hay problemas
        if self.problemas_encontrados:
            self.procesar_interactivo()
        
        print(f"\n✅ Verificación completada.")
        print(f"📁 Backup disponible en: {backup_dir}")

def main():
    """
    Función principal
    """
    verificador = VerificadorPoblacion()
    
    try:
        verificador.ejecutar_verificacion()
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificación interrumpida por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
