#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar y corregir nombres de departamentos y provincias
en los datasets de dengue comparándolos con la lista de referencia.
"""

import pandas as pd
import os
import difflib
from datetime import datetime

def normalizar_texto(texto):
    """Normaliza texto para comparación: minúsculas, sin acentos, sin espacios extra"""
    if pd.isna(texto) or texto == '':
        return ''
    
    # Convertir a string y normalizar
    texto = str(texto).strip().lower()
    
    # Reemplazar acentos y caracteres especiales
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u', 'ç': 'c',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'ã': 'a', 'õ': 'o', 'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o'
    }
    
    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)
    
    # Eliminar espacios extra
    texto = ' '.join(texto.split())
    
    return texto

def cargar_referencia():
    """Carga el archivo de referencia con los nombres correctos"""
    try:
        df_ref = pd.read_csv('/Users/ignaciosenestrari/Facu/tp-dengue/dataset-departamentos/lista-departamentos.csv')
        df_ref = df_ref.dropna(subset=['Nombre', 'Provincia'])
        df_ref['Nombre_normalizado'] = df_ref['Nombre'].apply(normalizar_texto)
        df_ref['Provincia_normalizada'] = df_ref['Provincia'].apply(normalizar_texto)
        print(f"[OK] Archivo de referencia cargado: {len(df_ref)} departamentos")
        return df_ref
    except Exception as e:
        print(f"[ERROR] Error al cargar archivo de referencia: {e}")
        return None

def cargar_dataset_dengue(archivo):
    """Carga un dataset de dengue específico"""
    try:
        df = pd.read_csv(archivo)
        df['departamento_nombre_normalizado'] = df['departamento_nombre'].apply(normalizar_texto)
        df['provincia_nombre_normalizado'] = df['provincia_nombre'].apply(normalizar_texto)
        df['fila_original'] = df.index + 2  # +2 porque pandas indexa desde 0 y CSV tiene header
        print(f"[OK] Dataset cargado: {len(df)} registros")
        return df
    except Exception as e:
        print(f"[ERROR] Error al cargar {archivo}: {e}")
        return None

def verificar_coincidencia_exacta(depto_norm, prov_norm, df_ref):
    """Verifica si existe una coincidencia exacta en la referencia"""
    match = df_ref[
        (df_ref['Nombre_normalizado'] == depto_norm) & 
        (df_ref['Provincia_normalizada'] == prov_norm)
    ]
    return not match.empty

def buscar_sugerencias_similares(nombre, df_ref, tipo):
    """Busca sugerencias similares en la referencia"""
    if tipo == 'departamento':
        nombres_disponibles = df_ref['Nombre'].unique()
    else:  # provincia
        nombres_disponibles = df_ref['Provincia'].unique()
    
    sugerencias = difflib.get_close_matches(
        nombre, 
        [normalizar_texto(n) for n in nombres_disponibles], 
        n=10, 
        cutoff=0.5
    )
    
    # Convertir de vuelta a nombres originales
    sugerencias_originales = []
    for sug in sugerencias:
        if tipo == 'departamento':
            match = df_ref[df_ref['Nombre_normalizado'] == sug]
            if not match.empty:
                sugerencias_originales.append(match.iloc[0]['Nombre'])
        else:
            match = df_ref[df_ref['Provincia_normalizada'] == sug]
            if not match.empty:
                sugerencias_originales.append(match.iloc[0]['Provincia'])
    
    return sugerencias_originales

def encontrar_discrepancias(df_dengue, df_ref):
    """Encuentra discrepancias entre el dataset de dengue y la referencia"""
    discrepancias = []
    
    # Usar combinaciones únicas de departamento + provincia como identificación
    departamentos_unicos = df_dengue[['departamento_nombre', 'departamento_nombre_normalizado', 
                                    'provincia_nombre', 'provincia_nombre_normalizado', 'fila_original']].drop_duplicates()
    
    print(f"[INFO] Analizando {len(departamentos_unicos)} combinaciones únicas de departamento+provincia...")
    
    for _, row in departamentos_unicos.iterrows():
        depto_nombre = row['departamento_nombre']
        depto_norm = row['departamento_nombre_normalizado']
        prov_nombre = row['provincia_nombre']
        prov_norm = row['provincia_nombre_normalizado']
        fila_original = row['fila_original']
        
        # Crear identificador único para esta combinación
        identificador = f"{depto_nombre}|{prov_nombre}"
        
        if not depto_norm and not prov_norm:
            discrepancias.append({
                'tipo': 'ambos_nombres_vacios',
                'identificador': identificador,
                'departamento_original': depto_nombre if pd.notna(depto_nombre) else '[VACIO]',
                'provincia_original': prov_nombre if pd.notna(prov_nombre) else '[VACIO]',
                'fila_original': fila_original,
                'sugerencias': []
            })
        elif not depto_norm:
            discrepancias.append({
                'tipo': 'departamento_vacio',
                'identificador': identificador,
                'departamento_original': '[VACIO]',
                'provincia_original': prov_nombre if pd.notna(prov_nombre) else '[VACIO]',
                'fila_original': fila_original,
                'sugerencias': buscar_sugerencias_similares(prov_norm, df_ref, 'provincia') if prov_norm else []
            })
        elif not prov_norm:
            discrepancias.append({
                'tipo': 'provincia_vacia',
                'identificador': identificador,
                'departamento_original': depto_nombre if pd.notna(depto_nombre) else '[VACIO]',
                'provincia_original': '[VACIO]',
                'fila_original': fila_original,
                'sugerencias': buscar_sugerencias_similares(depto_norm, df_ref, 'departamento')
            })
        else:
            # Verificar coincidencia exacta
            if verificar_coincidencia_exacta(depto_norm, prov_norm, df_ref):
                continue
            
            # Buscar si el departamento existe
            match_depto = df_ref[df_ref['Nombre_normalizado'] == depto_norm]
            
            if match_depto.empty:
                # Departamento no existe, buscar sugerencias
                sugerencias_depto = buscar_sugerencias_similares(depto_norm, df_ref, 'departamento')
                
                # Verificar si alguna sugerencia + provincia original forma una combinación válida
                encontro_coincidencia = False
                for sugerencia in sugerencias_depto:
                    if verificar_coincidencia_exacta(normalizar_texto(sugerencia), prov_norm, df_ref):
                        encontro_coincidencia = True
                        break
                
                if not encontro_coincidencia:
                    discrepancias.append({
                        'tipo': 'departamento_no_encontrado',
                        'identificador': identificador,
                        'departamento_original': depto_nombre,
                        'provincia_original': prov_nombre,
                        'fila_original': fila_original,
                        'sugerencias': sugerencias_depto
                    })
            else:
                # Departamento existe, verificar si la provincia coincide
                otros_matches = df_ref[df_ref['Nombre_normalizado'] == depto_norm]
                encontro_coincidencia_prov = False
                
                for _, otro_match in otros_matches.iterrows():
                    if otro_match['Provincia_normalizada'] == prov_norm:
                        encontro_coincidencia_prov = True
                        break
                
                if not encontro_coincidencia_prov:
                    discrepancias.append({
                        'tipo': 'provincia_no_coincide',
                        'identificador': identificador,
                        'departamento_original': depto_nombre,
                        'provincia_original': prov_nombre,
                        'provincia_correcta': match_depto.iloc[0]['Provincia'],
                        'fila_original': fila_original,
                        'sugerencias': buscar_sugerencias_similares(prov_norm, df_ref, 'provincia')
                    })
    
    return discrepancias

def mostrar_discrepancias(discrepancias):
    """Muestra las discrepancias encontradas"""
    if not discrepancias:
        print("\n✅ ¡No se encontraron discrepancias! Todos los nombres coinciden con la referencia.")
        return
    
    print(f"\n❌ Se encontraron {len(discrepancias)} discrepancias:")
    print("=" * 80)
    
    for i, disc in enumerate(discrepancias, 1):
        print(f"\n{i}. TIPO: {disc['tipo'].upper()}")
        print(f"   Fila CSV: {disc['fila_original']}")
        print(f"   Departamento: {disc['departamento_original']}")
        print(f"   Provincia: {disc['provincia_original']}")
        
        if disc['tipo'] == 'provincia_no_coincide':
            print(f"   Provincia correcta: {disc['provincia_correcta']}")
        
        if disc['sugerencias']:
            print(f"   Sugerencias: {', '.join(disc['sugerencias'][:5])}")

def corregir_discrepancias(df_dengue, discrepancias, df_ref):
    """Permite corregir las discrepancias encontradas"""
    if not discrepancias:
        return df_dengue
    
    print(f"\n🔧 Corrección de discrepancias:")
    print("=" * 50)
    
    for i, disc in enumerate(discrepancias, 1):
        print(f"\n--- Discrepancia {i}/{len(discrepancias)} ---")
        print(f"Tipo: {disc['tipo']}")
        print(f"Fila CSV: {disc['fila_original']}")
        print(f"Departamento: {disc['departamento_original']}")
        print(f"Provincia: {disc['provincia_original']}")
        
        if disc['tipo'] == 'provincia_no_coincide':
            print(f"Provincia correcta: {disc['provincia_correcta']}")
        
        if disc['sugerencias']:
            print(f"Sugerencias: {', '.join(disc['sugerencias'][:5])}")
        
        print("\nOpciones:")
        print("1. Corregir manualmente")
        print("2. Usar sugerencia")
        print("3. Eliminar registro")
        print("4. Saltar")
        
        while True:
            try:
                opcion = input("\nSeleccione una opción (1-4): ").strip()
                if opcion in ['1', '2', '3', '4']:
                    break
                else:
                    print("❌ Opción inválida. Ingrese 1, 2, 3 o 4.")
            except KeyboardInterrupt:
                print("\n\n⚠️ Operación cancelada por el usuario.")
                return df_dengue
        
        if opcion == '1':
            # Corrección manual
            nuevo_depto = input("Ingrese el nombre correcto del departamento: ").strip()
            nueva_prov = input("Ingrese el nombre correcto de la provincia: ").strip()
            
            if nuevo_depto and nueva_prov:
                # Filtrar registros que coincidan con esta combinación
                mask = (df_dengue['departamento_nombre'] == disc['departamento_original']) & \
                       (df_dengue['provincia_nombre'] == disc['provincia_original'])
                
                df_dengue.loc[mask, 'departamento_nombre'] = nuevo_depto
                df_dengue.loc[mask, 'provincia_nombre'] = nueva_prov
                df_dengue.loc[mask, 'departamento_nombre_normalizado'] = normalizar_texto(nuevo_depto)
                df_dengue.loc[mask, 'provincia_nombre_normalizado'] = normalizar_texto(nueva_prov)
                
                print("✅ Registros corregidos.")
            else:
                print("❌ No se ingresaron nombres válidos.")
        
        elif opcion == '2':
            # Usar sugerencia
            if disc['sugerencias']:
                print("\nSugerencias disponibles:")
                for j, sug in enumerate(disc['sugerencias'][:5], 1):
                    print(f"{j}. {sug}")
                
                while True:
                    try:
                        sug_idx = int(input("Seleccione el número de la sugerencia: ")) - 1
                        if 0 <= sug_idx < len(disc['sugerencias'][:5]):
                            break
                        else:
                            print("❌ Número inválido.")
                    except ValueError:
                        print("❌ Ingrese un número válido.")
                
                sugerencia = disc['sugerencias'][sug_idx]
                
                if disc['tipo'] == 'departamento_no_encontrado':
                    # Buscar la provincia correcta para esta sugerencia
                    match = df_ref[df_ref['Nombre'] == sugerencia]
                    if not match.empty:
                        provincia_correcta = match.iloc[0]['Provincia']
                        
                        # Filtrar registros que coincidan con esta combinación
                        mask = (df_dengue['departamento_nombre'] == disc['departamento_original']) & \
                               (df_dengue['provincia_nombre'] == disc['provincia_original'])
                        
                        df_dengue.loc[mask, 'departamento_nombre'] = sugerencia
                        df_dengue.loc[mask, 'provincia_nombre'] = provincia_correcta
                        df_dengue.loc[mask, 'departamento_nombre_normalizado'] = normalizar_texto(sugerencia)
                        df_dengue.loc[mask, 'provincia_nombre_normalizado'] = normalizar_texto(provincia_correcta)
                        
                        print(f"✅ Registros corregidos: {sugerencia}, {provincia_correcta}")
                    else:
                        print("❌ No se pudo encontrar la provincia para esta sugerencia.")
                else:
                    print("❌ No se puede usar sugerencia para este tipo de discrepancia.")
            else:
                print("❌ No hay sugerencias disponibles.")
        
        elif opcion == '3':
            # Eliminar registro
            confirmar = input("¿Está seguro de eliminar estos registros? (s/n): ").strip().lower()
            if confirmar == 's':
                # Filtrar registros que coincidan con esta combinación
                mask = (df_dengue['departamento_nombre'] == disc['departamento_original']) & \
                       (df_dengue['provincia_nombre'] == disc['provincia_original'])
                
                df_dengue = df_dengue[~mask]
                print("✅ Registros eliminados.")
            else:
                print("⏭️ Eliminación cancelada.")
        
        elif opcion == '4':
            print("⏭️ Saltando discrepancia.")
    
    return df_dengue

def crear_backup(archivo_original, año):
    """Crea un backup del archivo original"""
    try:
        # Crear directorio de backup si no existe
        backup_dir = "/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/backup automatico/dep y prov"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Nombre del archivo de backup
        nombre_archivo = os.path.basename(archivo_original)
        archivo_backup = os.path.join(backup_dir, f"backup_{nombre_archivo}")
        
        # Copiar archivo
        import shutil
        shutil.copy2(archivo_original, archivo_backup)
        print(f"✅ Backup creado: {archivo_backup}")
        return True
    except Exception as e:
        print(f"❌ Error al crear backup: {e}")
        return False

def guardar_dataset_corregido(df_dengue, archivo_original):
    """Guarda el dataset corregido"""
    try:
        # Eliminar columnas auxiliares antes de guardar
        df_guardar = df_dengue.drop(columns=['departamento_nombre_normalizado', 'provincia_nombre_normalizado', 'fila_original'])
        
        # Guardar archivo
        df_guardar.to_csv(archivo_original, index=False)
        print(f"✅ Dataset corregido guardado: {archivo_original}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar dataset: {e}")
        return False

def procesar_año(año):
    """Procesa un año específico"""
    archivo_dengue = f"/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/dengue-{año}.csv"
    
    if not os.path.exists(archivo_dengue):
        print(f"❌ No se encontró el archivo: {archivo_dengue}")
        return
    
    print(f"\n📊 Procesando año {año}...")
    print("=" * 50)
    
    # Cargar archivos
    df_ref = cargar_referencia()
    if df_ref is None:
        return
    
    df_dengue = cargar_dataset_dengue(archivo_dengue)
    if df_dengue is None:
        return
    
    # Crear backup
    if not crear_backup(archivo_dengue, año):
        return
    
    # Encontrar discrepancias
    discrepancias = encontrar_discrepancias(df_dengue, df_ref)
    
    # Mostrar discrepancias
    mostrar_discrepancias(discrepancias)
    
    if discrepancias:
        # Corregir discrepancias
        df_dengue_corregido = corregir_discrepancias(df_dengue, discrepancias, df_ref)
        
        # Guardar dataset corregido
        if guardar_dataset_corregido(df_dengue_corregido, archivo_dengue):
            print(f"\n🎉 Procesamiento del año {año} completado exitosamente!")
        else:
            print(f"\n❌ Error al guardar el dataset del año {año}")
    else:
        print(f"\n🎉 No se encontraron discrepancias en el año {año}!")

def main():
    """Función principal"""
    print("🔍 Verificador de Departamentos y Provincias - Datasets Dengue")
    print("=" * 70)
    
    while True:
        print("\nOPCIONES:")
        print("1. Procesar un año específico")
        print("2. Salir")
        
        try:
            opcion = input("\nSeleccione una opción (1-2): ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        
        if opcion == '1':
            # Mostrar años disponibles
            años_disponibles = []
            for año in range(2018, 2026):
                archivo = f"/Users/ignaciosenestrari/Facu/tp-dengue/dataset-dengue/dengue-{año}.csv"
                if os.path.exists(archivo):
                    años_disponibles.append(año)
            
            if not años_disponibles:
                print("❌ No se encontraron archivos de dengue para procesar.")
                continue
            
            print(f"\nAños disponibles: {', '.join(map(str, años_disponibles))}")
            
            while True:
                try:
                    año = int(input("Ingrese el año a procesar: ").strip())
                    if año in años_disponibles:
                        break
                    else:
                        print(f"❌ Año inválido. Años disponibles: {', '.join(map(str, años_disponibles))}")
                except ValueError:
                    print("❌ Ingrese un año válido.")
                except KeyboardInterrupt:
                    print("\n⏭️ Operación cancelada.")
                    break
            
            if año in años_disponibles:
                procesar_año(año)
        
        elif opcion == '2':
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida. Ingrese 1 o 2.")

if __name__ == "__main__":
    main()