"""
Verificar distribuição de ameaças nos dados processados
"""

import pandas as pd
from pathlib import Path

# Carregar dados processados
processed_dir = Path('data/processed/neo')
processed_files = list(processed_dir.glob('neo_processed_*.parquet'))

if processed_files:
    latest_file = max(processed_files, key=lambda p: p.stat().st_mtime)
    print(f"Carregando: {latest_file.name}\n")
    
    df = pd.read_parquet(latest_file)
    
    print("=" * 60)
    print("ANÁLISE DOS DADOS")
    print("=" * 60)
    
    print(f"\nTotal de registros: {len(df)}")
    print(f"Asteroides únicos: {df['asteroid_id'].nunique()}")
    
    print("\n--- DISTRIBUIÇÃO DE AMEAÇAS ---")
    threat_dist = df['threat_level'].value_counts()
    print(threat_dist)
    
    print("\n--- ASTEROIDES POTENCIALMENTE PERIGOSOS ---")
    hazardous = df['is_potentially_hazardous'].value_counts()
    print(hazardous)
    
    print("\n--- ESTATÍSTICAS DE DISTÂNCIA ---")
    print(f"Distância mínima: {df['miss_distance_lunar'].min():.2f} LD")
    print(f"Distância média: {df['miss_distance_lunar'].mean():.2f} LD")
    print(f"Distância máxima: {df['miss_distance_lunar'].max():.2f} LD")
    
    print("\n--- ASTEROIDES MAIS PRÓXIMOS (Top 5) ---")
    closest = df.nsmallest(5, 'miss_distance_lunar')[
        ['name', 'miss_distance_lunar', 'is_potentially_hazardous', 'threat_level', 'risk_score']
    ]
    print(closest.to_string(index=False))
    
    print("\n--- ASTEROIDES COM MAIOR RISCO (Top 5) ---")
    highest_risk = df.nsmallest(5, 'miss_distance_lunar')[
        ['name', 'risk_score', 'miss_distance_lunar', 'diameter_avg_km', 'threat_level']
    ]
    print(highest_risk.to_string(index=False))
    
    print("\n" + "=" * 60)
    
    # Verificar se há asteroides perigosos
    if df['is_potentially_hazardous'].sum() == 0:
        print("\n⚠️ ATENÇÃO: Nenhum asteroide perigoso nos últimos 7 dias!")
        print("Isso é NORMAL - significa que não há ameaças iminentes.")
        print("\nPara ter dados mais variados, você pode:")
        print("1. Coletar dados de um período maior (30 dias)")
        print("2. Ou usar dados simulados para demonstração")
    
else:
    print("❌ Nenhum arquivo processado encontrado!")
