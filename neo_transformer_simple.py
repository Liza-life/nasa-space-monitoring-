"""
Data Transformation Module - Bronze to Silver Layer (SIMPLIFIED)
Clean, validate, and enrich raw asteroid data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

print("=" * 60)
print("NEO DATA TRANSFORMATION - SIMPLIFIED VERSION")
print("=" * 60)

# Configurar caminhos
input_dir = Path("data/raw/neo")
output_dir = Path("data/processed/neo")
output_dir.mkdir(parents=True, exist_ok=True)

# Encontrar arquivo mais recente
raw_files = list(input_dir.glob("neo_approaches_*.parquet"))

if not raw_files:
    print("❌ Nenhum arquivo raw encontrado!")
    print("Execute primeiro: python src/ingestion/neo_ingestion.py")
    exit(1)

latest_file = max(raw_files, key=lambda p: p.stat().st_mtime)
print(f"\n📂 Carregando: {latest_file.name}")

# Carregar dados
df_raw = pd.read_parquet(latest_file)
print(f"✅ Carregados {len(df_raw)} registros")

# ==================================================
# LIMPEZA DE DADOS
# ==================================================
print("\n🧹 Limpando dados...")

df_clean = df_raw.copy()

# Remover duplicatas
initial_count = len(df_clean)
df_clean = df_clean.drop_duplicates(
    subset=['asteroid_id', 'close_approach_date'],
    keep='first'
)
print(f"  ✓ Removidas {initial_count - len(df_clean)} duplicatas")

# Preencher valores nulos com mediana
df_clean['diameter_min_km'] = df_clean['diameter_min_km'].fillna(
    df_clean['diameter_min_km'].median()
)
df_clean['diameter_max_km'] = df_clean['diameter_max_km'].fillna(
    df_clean['diameter_max_km'].median()
)

# Converter datas (sem timezone)
df_clean['close_approach_date'] = pd.to_datetime(df_clean['close_approach_date']).dt.tz_localize(None)

# Remover registros inválidos
df_clean = df_clean[
    (df_clean['diameter_min_km'] > 0) &
    (df_clean['diameter_max_km'] > 0) &
    (df_clean['relative_velocity_kms'] > 0) &
    (df_clean['miss_distance_km'] > 0)
]

print(f"  ✓ {len(df_clean)} registros válidos")

# ==================================================
# ENRIQUECIMENTO DE DADOS
# ==================================================
print("\n✨ Enriquecendo dados...")

# Diâmetro médio
df_clean['diameter_avg_km'] = (
    df_clean['diameter_min_km'] + df_clean['diameter_max_km']
) / 2

# Volume estimado (esfera)
df_clean['estimated_volume_km3'] = (
    4/3 * np.pi * (df_clean['diameter_avg_km'] / 2) ** 3
)

# Dias até aproximação
df_clean['days_until_approach'] = (
    df_clean['close_approach_date'] - pd.Timestamp.now().tz_localize(None)
).dt.days

# Classificação por tamanho
def classify_size(diameter_km):
    if diameter_km < 0.025:
        return 'Small (<25m)'
    elif diameter_km < 0.14:
        return 'Medium (25-140m)'
    elif diameter_km < 1.0:
        return 'Large (140m-1km)'
    else:
        return 'Very Large (>1km)'

df_clean['size_category'] = df_clean['diameter_avg_km'].apply(classify_size)

# Score de risco (0-100)
df_clean['risk_score'] = (
    (1 / df_clean['miss_distance_lunar']).clip(0, 10) * 20 +  # Proximidade
    (df_clean['diameter_avg_km'] * 100).clip(0, 30) +  # Tamanho
    (df_clean['relative_velocity_kms'] / 50).clip(0, 20) +  # Velocidade
    (df_clean['is_potentially_hazardous'].astype(int) * 30)  # Flag perigoso
).clip(0, 100)

# Nível de ameaça
def classify_threat(row):
    if row['is_potentially_hazardous'] and row['miss_distance_lunar'] < 1.0:
        return 'High'
    elif row['is_potentially_hazardous'] and row['miss_distance_lunar'] < 5.0:
        return 'Medium'
    elif row['miss_distance_lunar'] < 2.0:
        return 'Low'
    else:
        return 'Minimal'

df_clean['threat_level'] = df_clean.apply(classify_threat, axis=1)

# Componentes de data
df_clean['year'] = df_clean['close_approach_date'].dt.year
df_clean['month'] = df_clean['close_approach_date'].dt.month
df_clean['day'] = df_clean['close_approach_date'].dt.day
df_clean['day_of_week'] = df_clean['close_approach_date'].dt.dayofweek
df_clean['week_of_year'] = df_clean['close_approach_date'].dt.isocalendar().week

print(f"  ✓ Adicionados {len(df_clean.columns) - len(df_raw.columns)} novos campos")

# ==================================================
# SALVAR DADOS PROCESSADOS
# ==================================================
print("\n💾 Salvando dados processados...")

timestamp = datetime.now().strftime("%Y%m%d")
output_filename = f"neo_processed_{timestamp}.parquet"
output_path = output_dir / output_filename

df_clean.to_parquet(output_path, index=False, engine='pyarrow')
print(f"  ✓ Salvo: {output_path}")

# ==================================================
# RELATÓRIO DE QUALIDADE
# ==================================================
print("\n📊 RELATÓRIO DE QUALIDADE")
print("=" * 60)

quality_report = {
    'timestamp': datetime.now().isoformat(),
    'total_records': len(df_clean),
    'unique_asteroids': df_clean['asteroid_id'].nunique(),
    'date_range': {
        'min': df_clean['close_approach_date'].min().isoformat(),
        'max': df_clean['close_approach_date'].max().isoformat()
    },
    'hazardous_count': int(df_clean['is_potentially_hazardous'].sum()),
    'hazardous_percentage': f"{(df_clean['is_potentially_hazardous'].sum() / len(df_clean)) * 100:.2f}%",
    'threat_distribution': df_clean['threat_level'].value_counts().to_dict(),
    'size_distribution': df_clean['size_category'].value_counts().to_dict(),
    'statistics': {
        'avg_distance_lunar': float(df_clean['miss_distance_lunar'].mean()),
        'min_distance_lunar': float(df_clean['miss_distance_lunar'].min()),
        'avg_velocity_kms': float(df_clean['relative_velocity_kms'].mean()),
        'avg_diameter_km': float(df_clean['diameter_avg_km'].mean())
    }
}

print(f"Total de registros: {quality_report['total_records']}")
print(f"Asteroides únicos: {quality_report['unique_asteroids']}")
print(f"Perigosos: {quality_report['hazardous_count']} ({quality_report['hazardous_percentage']})")
print(f"\nDistribuição de Ameaças:")
for level, count in quality_report['threat_distribution'].items():
    print(f"  {level}: {count}")

# Salvar relatório
report_path = output_dir / f"neo_processed_{timestamp}_quality_report.json"
with open(report_path, 'w') as f:
    json.dump(quality_report, f, indent=2, default=str)
print(f"\n✅ Relatório salvo: {report_path}")

print("\n" + "=" * 60)
print("✅ TRANSFORMAÇÃO CONCLUÍDA COM SUCESSO!")
print("=" * 60)
print(f"\nPróximo passo: python export_to_powerbi.py")
