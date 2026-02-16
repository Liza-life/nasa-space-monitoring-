# 🚀 NASA Space Monitoring Platform
### Plataforma de Monitoramento Espacial com Dados da NASA

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow.svg)](https://powerbi.microsoft.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Sistema completo de Engenharia de Dados** para coleta, processamento e visualização de dados de asteroides próximos à Terra (NEOs) utilizando APIs da NASA.

---

## 📸 Screenshots

### Página 1: Visão Geral
![Visão Geral](screenshots/pagina1.png)

### Página 2: Análise Detalhada  
![Análise Detalhada](screenshots/pagina2.png)

### Página 3: Alertas e Monitoramento
![Alertas](screenshots/pagina3.png)

---

## 🎯 Sobre o Projeto

Este projeto foi desenvolvido para demonstrar competências em **Engenharia de Dados** e **Business Intelligence**, incluindo:

- ✅ **Pipeline ETL completo** (Extract, Transform, Load)
- ✅ **Arquitetura Medallion** (Bronze → Silver → Gold)
- ✅ **Data Warehouse dimensional**
- ✅ **Dashboard interativo** no Power BI
- ✅ **Análise de dados espaciais em tempo real**

### 🌟 Destaques

- 📊 **3 páginas de dashboard** com diferentes níveis de análise
- 🎨 **Identidade visual NASA** (cores oficiais)
- 📈 **15+ visualizações interativas**
- 🚨 **Sistema de alertas** para asteroides de alto risco
- 💡 **Insights automáticos** e recomendações

---

## 🏗️ Arquitetura

```
┌─────────────┐
│  NASA APIs  │ (NeoWs - Near Earth Objects)
└──────┬──────┘
       │ Python + Requests
       ▼
┌─────────────┐
│  Bronze     │ (Dados Brutos - JSON/Parquet)
│  Layer      │ data/raw/
└──────┬──────┘
       │ Pandas + Transformações
       ▼
┌─────────────┐
│  Silver     │ (Dados Limpos e Validados)
│  Layer      │ data/processed/
└──────┬──────┘
       │ Enriquecimento + Métricas
       ▼
┌─────────────┐
│  Gold       │ (Dados Analíticos - DuckDB)
│  Layer      │ data/warehouse/
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Power BI   │ (Dashboard Interativo)
│  Dashboard  │ 3 Páginas de Análise
└─────────────┘
```

---

## 🛠️ Tecnologias Utilizadas

### Data Engineering
- **Python 3.9+** - Linguagem principal
- **Pandas** - Manipulação de dados
- **DuckDB** - Data Warehouse embarcado
- **Requests** - Consumo de APIs
- **PyArrow** - Formato Parquet

### Business Intelligence
- **Power BI Desktop** - Visualização de dados
- **DAX** - Linguagem de medidas
- **Power Query** - Transformação visual

### DevOps & Qualidade
- **Git/GitHub** - Versionamento
- **Python Virtual Environments** - Isolamento
- **Logging** - Monitoramento

---

## 📊 Funcionalidades do Dashboard

### 📄 Página 1: Visão Geral
- KPIs principais (Total, Perigosos, Distância, Velocidade)
- Distribuição por nível de ameaça
- Timeline de aproximações
- Análise de risco (Distância vs Velocidade)

### 📄 Página 2: Análise Detalhada
- Top 10 asteroides por risco
- Distribuição por tamanho
- Análise de velocidades
- Periculosidade por categoria

### 📄 Página 3: Alertas e Monitoramento
- Alertas de alto risco
- Matriz de risco por período
- Evolução temporal do risco
- Insights e recomendações

---

## 🚀 Como Usar

### Pré-requisitos

```bash
Python 3.9+
Power BI Desktop
NASA API Key (gratuita)
```

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/Liza-life/nasa-space-monitoring.git
cd nasa-space-monitoring

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure a API Key
cp .env.example .env
# Edite .env e adicione sua NASA_API_KEY
```

### Obter API Key da NASA

1. Acesse: https://api.nasa.gov/
2. Preencha o formulário
3. Receba a chave por email (instantâneo)
4. **GRÁTIS** - 1.000 requisições/hora

### Executar o Pipeline

```bash
# 1. Coletar dados da NASA
python src/ingestion/neo_ingestion.py

# 2. Processar e transformar
python src/transformation/neo_transformer.py

# 3. Exportar para Power BI
python export_to_powerbi.py

# 4. Abrir dashboard
# Abra o arquivo nasa_dashboard.pbix no Power BI Desktop
```

---

## 📈 Métricas do Projeto

- **100 asteroides** monitorados
- **3 níveis de ameaça** classificados
- **30 dias** de dados futuros
- **15+ visualizações** interativas
- **10+ medidas DAX** criadas
- **3 páginas** de análise

---

## 🎓 Aprendizados

Este projeto demonstra conhecimentos em:

### Engenharia de Dados
- ✅ Coleta de dados via APIs REST
- ✅ Processamento e limpeza de dados
- ✅ Modelagem dimensional (Star Schema)
- ✅ Pipeline ETL automatizado
- ✅ Arquitetura de Data Lake/Warehouse

### Business Intelligence
- ✅ Criação de dashboards executivos
- ✅ Storytelling com dados
- ✅ Design de experiência do usuário
- ✅ Medidas e cálculos DAX
- ✅ Formatação e identidade visual

### Boas Práticas
- ✅ Código limpo e documentado
- ✅ Estrutura de projeto organizada
- ✅ Versionamento com Git
- ✅ Tratamento de erros
- ✅ Logging estruturado

---

## 📁 Estrutura do Projeto

```
nasa-space-monitoring/
├── 📄 README.md                    # Este arquivo
├── 📄 requirements.txt             # Dependências Python
├── 📄 .env.example                 # Template de configuração
├── 📄 .gitignore                   # Arquivos ignorados
│
├── 📂 src/                         # Código-fonte
│   ├── ingestion/                  # Coleta de dados
│   │   ├── base_client.py         # Cliente base API
│   │   └── neo_ingestion.py       # Ingestão NEO
│   ├── transformation/             # Processamento
│   │   └── neo_transformer.py     # Transformações
│   └── dashboard/                  # Dashboard Streamlit (extra)
│
├── 📂 data/                        # Dados (não versionado)
│   ├── raw/                        # Bronze layer
│   ├── processed/                  # Silver layer
│   ├── analytics/                  # Gold layer
│   └── powerbi_export/             # CSVs para Power BI
│
├── 📂 docs/                        # Documentação
│   ├── QUICKSTART.md              # Guia rápido
│   ├── ARCHITECTURE.md            # Arquitetura detalhada
│   └── EXAMPLES.md                # Exemplos de uso
│
├── 📂 notebooks/                   # Jupyter notebooks
│   └── 01_exploratory_analysis.ipynb
│
└── 📂 screenshots/                 # Prints do dashboard
    ├── pagina1.png
    ├── pagina2.png
    └── pagina3.png
```

---

## 🤝 Contribuições

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Autor

**Lizandra Ruiz**

- LinkedIn: [linkedin.com/in/lizandra-ruiz-890268381/](https://www.linkedin.com/in/lizandra-ruiz-890268381/)
- GitHub: [@Liza-life](https://github.com/Liza-life)
- Email: lizandraruiz.life@gmail.com

---

## 🙏 Agradecimentos

- **NASA** - Pelos dados públicos incríveis através da API NeoWs
- **Comunidade Python** - Pelas ferramentas fantásticas
- **Você** - Por visitar este projeto! ⭐

---

## 📚 Referências

- [NASA Open APIs](https://api.nasa.gov/)
- [NeoWs API Documentation](https://api.nasa.gov/neo/)
- [Power BI Documentation](https://docs.microsoft.com/power-bi/)
- [Python Pandas](https://pandas.pydata.org/)

---

**⭐ Se você gostou deste projeto, considere dar uma estrela no GitHub!**

---

*Projeto desenvolvido como demonstração de competências em Engenharia de Dados e Business Intelligence - 2026*
