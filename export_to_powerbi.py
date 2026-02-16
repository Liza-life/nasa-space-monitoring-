"""
Script para exportar dados do projeto NASA para Power BI
Gera arquivos CSV otimizados para importação
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

# Configurar caminhos
processed_dir = Path('data/processed/neo')
output_dir = Path('data/powerbi_export')
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("EXPORTANDO DADOS PARA POWER BI")
print("=" * 60)

# Encontrar arquivo mais recente
processed_files = list(processed_dir.glob('neo_processed_*.parquet'))

if not processed_files:
    print("❌ Nenhum arquivo processado encontrado!")
    print("Execute primeiro: python src/transformation/neo_transformer.py")
    exit(1)

latest_file = max(processed_files, key=lambda p: p.stat().st_mtime)
print(f"\n📂 Carregando: {latest_file.name}")

# Carregar dados
df = pd.read_parquet(latest_file)
print(f"✅ {len(df)} registros carregados")

# ==================================================
# TABELA FATO: Aproximações de Asteroides
# ==================================================
print("\n📊 Criando Tabela FATO: Aproximações de Asteroides")

fact_approaches = df[[
    'asteroid_id',
    'name',
    'close_approach_date',
    'miss_distance_km',
    'miss_distance_lunar',
    'miss_distance_astronomical',
    'relative_velocity_kms',
    'relative_velocity_kmh',
    'diameter_min_km',
    'diameter_max_km',
    'diameter_avg_km',
    'estimated_volume_km3',
    'is_potentially_hazardous',
    'threat_level',
    'size_category',
    'risk_score',
    'days_until_approach'
]].copy()

# Formatar datas
fact_approaches['close_approach_date'] = pd.to_datetime(fact_approaches['close_approach_date'])

# Salvar
fact_path = output_dir / 'fact_asteroid_approaches.csv'
fact_approaches.to_csv(fact_path, index=False, encoding='utf-8-sig')
print(f"✅ Salvo: {fact_path}")
print(f"   Registros: {len(fact_approaches)}")

# ==================================================
# DIMENSÃO: Asteroides
# ==================================================
print("\n🌑 Criando Dimensão: Asteroides")

dim_asteroids = df.groupby('asteroid_id').agg({
    'name': 'first',
    'diameter_min_km': 'first',
    'diameter_max_km': 'first',
    'diameter_avg_km': 'first',
    'size_category': 'first',
    'is_potentially_hazardous': 'first'
}).reset_index()

dim_path = output_dir / 'dim_asteroids.csv'
dim_asteroids.to_csv(dim_path, index=False, encoding='utf-8-sig')
print(f"✅ Salvo: {dim_path}")
print(f"   Asteroides únicos: {len(dim_asteroids)}")

# ==================================================
# DIMENSÃO: Calendário
# ==================================================
print("\n📅 Criando Dimensão: Calendário")

# Criar range de datas
min_date = df['close_approach_date'].min()
max_date = df['close_approach_date'].max()
date_range = pd.date_range(start=min_date, end=max_date, freq='D')

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
print(f"   Dias: {len(dim_calendar)}")

# ==================================================
# DIMENSÃO: Classificação de Ameaça
# ==================================================
print("\n⚠️ Criando Dimensão: Classificação de Ameaça")

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

# ==================================================
# TABELA AUXILIAR: Estatísticas Diárias
# ==================================================
print("\n📈 Criando Tabela: Estatísticas Diárias")

daily_stats = df.groupby(df['close_approach_date'].dt.date).agg({
    'asteroid_id': 'count',
    'is_potentially_hazardous': 'sum',
    'miss_distance_lunar': ['min', 'mean'],
    'relative_velocity_kms': 'mean',
    'risk_score': 'mean',
    'diameter_avg_km': 'mean'
}).reset_index()

daily_stats.columns = [
    'date',
    'total_approaches',
    'hazardous_count',
    'closest_distance_ld',
    'avg_distance_ld',
    'avg_velocity_kms',
    'avg_risk_score',
    'avg_diameter_km'
]

stats_path = output_dir / 'daily_statistics.csv'
daily_stats.to_csv(stats_path, index=False, encoding='utf-8-sig')
print(f"✅ Salvo: {stats_path}")

# ==================================================
# SUMÁRIO DE EXPORTAÇÃO
# ==================================================
print("\n" + "=" * 60)
print("✅ EXPORTAÇÃO CONCLUÍDA!")
print("=" * 60)
print(f"\n📁 Arquivos salvos em: {output_dir.absolute()}")
print("\nArquivos criados:")
print("  1. fact_asteroid_approaches.csv    (Tabela principal)")
print("  2. dim_asteroids.csv               (Dimensão Asteroides)")
print("  3. dim_calendar.csv                (Dimensão Calendário)")
print("  4. dim_threat_classification.csv   (Dimensão Ameaça)")
print("  5. daily_statistics.csv            (Estatísticas agregadas)")

print("\n" + "=" * 60)
print("PRÓXIMOS PASSOS - POWER BI")
print("=" * 60)
print("\n1. Abra o Power BI Desktop")
print("2. Clique em 'Obter Dados' → 'Texto/CSV'")
print("3. Importe todos os 5 arquivos CSV")
print("4. Siga o guia de relacionamentos e medidas")
print("\n" + "=" * 60)
