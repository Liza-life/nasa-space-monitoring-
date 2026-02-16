"""
Gerar dados CORRIGIDOS para Power BI - VALORES GARANTIDOS
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

print("=" * 60)
print("GERANDO DADOS CORRIGIDOS - VALORES GARANTIDOS")
print("=" * 60)

np.random.seed(42)
output_dir = Path('data/powerbi_export')
output_dir.mkdir(parents=True, exist_ok=True)

# Gerar 100 asteroides
n_asteroids = 100
dates = pd.date_range(start=datetime.now(), periods=30, freq='D')

data = []

for i in range(n_asteroids):
    # Diâmetro em km
    diameter_min = np.random.uniform(0.01, 2.0)
    diameter_max = diameter_min + np.random.uniform(0.1, 1.0)
    diameter_avg = (diameter_min + diameter_max) / 2
    
    # IMPORTANTE: Distância em LUNAR DISTANCES (valores pequenos!)
    miss_distance_lunar = np.random.choice([
        np.random.uniform(0.3, 0.9),    # 10% muito próximo
        np.random.uniform(0.9, 2.5),    # 20% próximo  
        np.random.uniform(2.5, 6.0),    # 30% médio
        np.random.uniform(6.0, 20.0)    # 40% longe
    ], p=[0.1, 0.2, 0.3, 0.4])
    
    # Converter LD para outras unidades
    miss_distance_km = miss_distance_lunar * 384400  # 1 LD = 384.400 km
    miss_distance_astronomical = miss_distance_lunar * 0.00257  # 1 LD = 0.00257 AU
    
    velocity_kms = np.random.uniform(5, 40)
    velocity_kmh = velocity_kms * 3600
    
    is_hazardous = np.random.choice([True, False], p=[0.15, 0.85])
    
    volume = (4/3) * np.pi * (diameter_avg / 2) ** 3
    
    # Calcular risco
    risk_score = (
        (1 / max(miss_distance_lunar, 0.1)) * 20 +
        (diameter_avg * 100) * 0.3 +
        (velocity_kms / 50) * 20 +
        (int(is_hazardous) * 30)
    )
    risk_score = min(100, max(0, risk_score))
    
    # Classificar ameaça
    if is_hazardous and miss_distance_lunar < 1.0:
        threat_level = 'High'
    elif is_hazardous and miss_distance_lunar < 5.0:
        threat_level = 'Medium'
    elif miss_distance_lunar < 2.0:
        threat_level = 'Low'
    else:
        threat_level = 'Minimal'
    
    # Classificar tamanho
    if diameter_avg < 0.025:
        size_category = 'Small (<25m)'
    elif diameter_avg < 0.14:
        size_category = 'Medium (25-140m)'
    elif diameter_avg < 1.0:
        size_category = 'Large (140m-1km)'
    else:
        size_category = 'Very Large (>1km)'
    
    approach_date = np.random.choice(dates)
    days_until = (approach_date - pd.Timestamp.now()).days
    
    data.append({
        'asteroid_id': f'2024{i+1:03d}',
        'name': f'({2024}) {chr(65 + (i % 26))}{chr(65 + ((i//26) % 26))}{i+1}',
        'close_approach_date': approach_date,
        'miss_distance_km': round(miss_distance_km, 2),
        'miss_distance_lunar': round(miss_distance_lunar, 4),  # VALORES PEQUENOS!
        'miss_distance_astronomical': round(miss_distance_astronomical, 6),
        'relative_velocity_kms': round(velocity_kms, 2),
        'relative_velocity_kmh': round(velocity_kmh, 2),
        'diameter_min_km': round(diameter_min, 4),
        'diameter_max_km': round(diameter_max, 4),
        'diameter_avg_km': round(diameter_avg, 4),
        'estimated_volume_km3': round(volume, 6),
        'is_potentially_hazardous': is_hazardous,
        'threat_level': threat_level,
        'size_category': size_category,
        'risk_score': round(risk_score, 2),
        'days_until_approach': days_until
    })

df = pd.DataFrame(data)

print(f"\n✅ Gerados {len(df)} asteroides")
print(f"\n🔍 VERIFICAÇÃO DE VALORES:")
print(f"  miss_distance_lunar - Mínimo: {df['miss_distance_lunar'].min():.4f} LD")
print(f"  miss_distance_lunar - Máximo: {df['miss_distance_lunar'].max():.4f} LD")
print(f"  miss_distance_lunar - Médio: {df['miss_distance_lunar'].mean():.4f} LD")

# Salvar FATO
fact_path = output_dir / 'fact_asteroid_approaches.csv'
df.to_csv(fact_path, index=False, encoding='utf-8-sig')
print(f"\n✅ Salvo: {fact_path}")

# Dimensão Asteroides
dim_asteroids = df[['asteroid_id', 'name', 'diameter_min_km', 'diameter_max_km', 
                     'diameter_avg_km', 'size_category', 'is_potentially_hazardous']].drop_duplicates()
dim_path = output_dir / 'dim_asteroids.csv'
dim_asteroids.to_csv(dim_path, index=False, encoding='utf-8-sig')
print(f"✅ Salvo: {dim_path}")

# Dimensão Calendário
date_range = pd.date_range(start=dates[0], end=dates[-1], freq='D')
dim_calendar = pd.DataFrame({
    'date': date_range,
    'year': date_range.year,
    'month': date_range.month,
    'month_name': date_range.strftime('%B'),
    'day': date_range.day,
    'day_of_week': date_range.dayofweek,
    'day_name': date_range.strftime('%A'),
    'week_of_year': date_range.isocalendar().week,
    'quarter': date_range.quarter,
    'is_weekend': date_range.dayofweek.isin([5, 6])
})
calendar_path = output_dir / 'dim_calendar.csv'
dim_calendar.to_csv(calendar_path, index=False, encoding='utf-8-sig')
print(f"✅ Salvo: {calendar_path}")

# Dimensão Ameaça
dim_threat = pd.DataFrame({
    'threat_level': ['Minimal', 'Low', 'Medium', 'High'],
    'threat_order': [1, 2, 3, 4],
    'threat_color': ['#44ff44', '#ffdd44', '#ff9944', '#ff4444'],
    'threat_description': [
        'Distância segura, sem preocupação',
        'Próximo mas sem risco significativo',
        'Atenção recomendada',
        'Potencialmente perigoso - monitoramento crítico'
    ]
})
threat_path = output_dir / 'dim_threat_classification.csv'
dim_threat.to_csv(threat_path, index=False, encoding='utf-8-sig')
print(f"✅ Salvo: {threat_path}")

# Estatísticas Diárias
daily_stats = df.groupby(df['close_approach_date'].dt.date).agg({
    'asteroid_id': 'count',
    'is_potentially_hazardous': 'sum',
    'miss_distance_lunar': ['min', 'mean'],
    'relative_velocity_kms': 'mean',
    'risk_score': 'mean',
    'diameter_avg_km': 'mean'
}).reset_index()

daily_stats.columns = [
    'date', 'total_approaches', 'hazardous_count',
    'closest_distance_ld', 'avg_distance_ld',
    'avg_velocity_kms', 'avg_risk_score', 'avg_diameter_km'
]
stats_path = output_dir / 'daily_statistics.csv'
daily_stats.to_csv(stats_path, index=False, encoding='utf-8-sig')
print(f"✅ Salvo: {stats_path}")

print("\n" + "=" * 60)
print("✅ DADOS GERADOS COM SUCESSO!")
print("=" * 60)
print(f"\n📊 Distribuição de Ameaças:")
print(df['threat_level'].value_counts())
print(f"\n📏 Valores de miss_distance_lunar:")
print(df['miss_distance_lunar'].describe())
print("\n" + "=" * 60)
