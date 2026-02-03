# Acesso Completo ao Sistema MR. HEALTH Data Platform

**Data da Validacao:** 2026-02-03
**Status:** TODOS OS COMPONENTES FUNCIONANDO

---

## Resumo Executivo

| Componente | Status | Acesso |
|------------|--------|--------|
| GCP Project | ATIVO | `sixth-foundry-485810-e5` |
| GCS Bucket | ATIVO | 19 arquivos CSV + 4 referencias |
| Cloud Functions | 2 ATIVAS | csv-processor, pg-reference-extractor |
| Cloud Scheduler | 1 ATIVO | pg-reference-extraction (01:00 BRT) |
| BigQuery Bronze | 6 tabelas | 178 orders, 496 items |
| BigQuery Silver | 6 tabelas | 15 orders processados |
| BigQuery Gold | 9 tabelas | Star schema completo |
| K3s Cluster | RUNNING | 1 node Ready |
| PostgreSQL | RUNNING | 30 produtos, 3 unidades |
| **Portainer** | **RUNNING** | http://<YOUR-K3S-IP>:30777 |
| **Airflow** | **RUNNING** | http://<YOUR-K3S-IP>:30180 |
| **Superset** | **RUNNING** | http://<YOUR-K3S-IP>:30188 |
| Local CSVs | 16 arquivos | 163 pedidos, 496 itens |

---

## 1. Dados Locais (CSVs)

### Caminho
```
output/csv_sales/2026/02/{01,02}/unit_{001,002,003}/
  - pedido.csv
  - item_pedido.csv

output/reference_data/
  - pais.csv (1 registro)
  - estado.csv (3 registros)
  - unidade.csv (3 registros)
  - produto.csv (30 registros)
```

### Estatisticas
- **Total de Pedidos:** 163
- **Total de Itens:** 496
- **Faturamento Local:** R$ 24.672,43
- **Periodo:** 2026-02-01 a 2026-02-02
- **Unidades:** 1, 2, 3

### Como Verificar
```bash
# Ver estrutura
ls -la output/csv_sales/2026/02/

# Contar pedidos
py -c "import glob; print(len(glob.glob('output/csv_sales/**/pedido.csv', recursive=True)))"

# Abrir no Python
py -c "import pandas as pd; print(pd.read_csv('output/csv_sales/2026/02/01/unit_001/pedido.csv', sep=';').head())"
```

---

## 2. Google Cloud Platform

### Console
**URL:** https://console.cloud.google.com/?project=sixth-foundry-485810-e5

### Autenticacao
```bash
# Verificar conta autenticada
gcloud auth list
# Ativo: arthurmgraf@gmail.com

# Definir projeto
gcloud config set project sixth-foundry-485810-e5
```

---

## 3. Cloud Storage (GCS)

### Bucket
**Nome:** `mrhealth-datalake-485810`
**URL Console:** https://console.cloud.google.com/storage/browser/mrhealth-datalake-485810

### Estrutura
```
gs://mrhealth-datalake-485810/
├── raw/
│   ├── csv_sales/
│   │   ├── 2026/01/27/unit_{001,002,003}/  (6 CSVs)
│   │   ├── 2026/01/28/unit_{001,002,003}/  (6 CSVs)
│   │   └── test/, final/, test2/, test3/  (testes)
│   └── reference_data/
│       ├── pais.csv
│       ├── estado.csv
│       ├── unidade.csv
│       └── produto.csv
└── quarantine/
```

### Como Verificar
```bash
# Listar bucket
gcloud storage ls gs://mrhealth-datalake-485810/

# Listar raw/csv_sales
gcloud storage ls --recursive gs://mrhealth-datalake-485810/raw/csv_sales/

# Ver conteudo de um arquivo
gcloud storage cat gs://mrhealth-datalake-485810/raw/csv_sales/2026/01/27/unit_001/pedido.csv | head -5
```

---

## 4. Cloud Functions

### csv-processor
- **Status:** ACTIVE
- **Runtime:** Python 3.11
- **Trigger:** Eventarc (upload no bucket `mrhealth-datalake-485810`)
- **URL:** https://csv-processor-f7wgmun2nq-uc.a.run.app
- **Console:** https://console.cloud.google.com/functions/details/us-central1/csv-processor?project=sixth-foundry-485810-e5

### pg-reference-extractor
- **Status:** ACTIVE
- **Runtime:** Python 3.11
- **Trigger:** HTTP (invocado pelo Scheduler)
- **URL:** https://pg-reference-extractor-f7wgmun2nq-uc.a.run.app
- **Console:** https://console.cloud.google.com/functions/details/us-central1/pg-reference-extractor?project=sixth-foundry-485810-e5

### Como Verificar
```bash
# Listar funcoes
gcloud functions list --project=sixth-foundry-485810-e5

# Ver detalhes
gcloud functions describe csv-processor --project=sixth-foundry-485810-e5 --region=us-central1

# Ver logs
gcloud functions logs read csv-processor --project=sixth-foundry-485810-e5 --region=us-central1 --limit=20
```

---

## 5. Cloud Scheduler

### pg-reference-extraction
- **Status:** ENABLED
- **Horario:** `0 1 * * *` (01:00 BRT diariamente)
- **Timezone:** America/Sao_Paulo
- **Console:** https://console.cloud.google.com/cloudscheduler?project=sixth-foundry-485810-e5

### Como Verificar
```bash
gcloud scheduler jobs list --project=sixth-foundry-485810-e5 --location=us-central1
```

---

## 6. BigQuery

### Console
**URL:** https://console.cloud.google.com/bigquery?project=sixth-foundry-485810-e5

### Datasets (NOMES REAIS)
> **Atencao:** Os datasets reais sao `mrhealth_*`, nao `case_ficticio_*`

| Dataset | Tabelas | Descricao |
|---------|---------|-----------|
| `mrhealth_bronze` | 6 | Dados brutos ingeridos |
| `mrhealth_silver` | 6 | Dados limpos e dedupados |
| `mrhealth_gold` | 9 | Star schema + agregacoes |
| `mrhealth_monitoring` | 0 | (vazio) |

### Tabelas por Layer

**BRONZE (mrhealth_bronze)**
| Tabela | Linhas |
|--------|--------|
| orders | 178 |
| order_items | 496 |
| products | 30 |
| units | 3 |
| states | 3 |
| countries | 1 |

**SILVER (mrhealth_silver)**
| Tabela | Linhas |
|--------|--------|
| orders | 15 |
| order_items | 0 |
| products | 30 |
| units | 3 |
| states | 3 |
| countries | 1 |

**GOLD (mrhealth_gold)**
| Tabela | Linhas |
|--------|--------|
| dim_date | 1.095 |
| dim_product | 30 |
| dim_unit | 3 |
| dim_geography | 3 |
| fact_sales | 15 |
| fact_order_items | 0 |
| agg_daily_sales | 1 |
| agg_unit_performance | 1 |
| agg_product_performance | 0 |

### Queries de Validacao
```sql
-- Bronze
SELECT COUNT(*) FROM `sixth-foundry-485810-e5.mrhealth_bronze.orders`;

-- Silver
SELECT COUNT(*) FROM `sixth-foundry-485810-e5.mrhealth_silver.orders`;

-- Gold Star Schema
SELECT
  d.full_date,
  p.nome_produto,
  u.nome_unidade,
  f.valor_total
FROM `sixth-foundry-485810-e5.mrhealth_gold.fact_sales` f
JOIN `sixth-foundry-485810-e5.mrhealth_gold.dim_date` d ON f.date_key = d.date_key
JOIN `sixth-foundry-485810-e5.mrhealth_gold.dim_product` p ON f.product_key = p.product_key
JOIN `sixth-foundry-485810-e5.mrhealth_gold.dim_unit` u ON f.unit_key = u.unit_key
LIMIT 10;

-- Agregacao diaria
SELECT * FROM `sixth-foundry-485810-e5.mrhealth_gold.agg_daily_sales`;
```

### Como Verificar via Python
```python
from google.cloud import bigquery
client = bigquery.Client(project='sixth-foundry-485810-e5')

# Listar datasets
for ds in client.list_datasets():
    print(ds.dataset_id)

# Contar linhas
result = client.query("SELECT COUNT(*) FROM mrhealth_bronze.orders").result()
print(list(result)[0][0])
```

---

## 7. K3s (Kubernetes) + PostgreSQL

### Servidor SSH
```
Host: <YOUR-K3S-IP>
User: <YOUR-SSH-USER>
Password: <STORED-IN-SECRET-MANAGER>
```

> **IMPORTANTE:** Nunca armazene credenciais em documentação. Use Secret Manager ou variáveis de ambiente.

### Acessar via SSH
```bash
ssh <YOUR-SSH-USER>@<YOUR-K3S-IP>
```

### Status do Cluster
```bash
# Nodes
kubectl get nodes
# Esperado: k3s-master Ready

# PostgreSQL pod
kubectl get pods -n mrhealth-db
# Esperado: postgresql-xxx Running

# Servico
kubectl get svc -n mrhealth-db
# Esperado: postgresql NodePort 30432
```

### Acessar PostgreSQL

**Opcao 1: Via kubectl exec (do servidor SSH)**
```bash
kubectl exec -n mrhealth-db deployment/postgresql -- \
  psql -U mrhealth_admin -d mrhealth -c "SELECT * FROM produto LIMIT 5;"
```

**Opcao 2: Via SSH tunnel (da sua maquina local)**
```bash
# Terminal 1: Criar tunel
ssh -L 5432:localhost:30432 <YOUR-SSH-USER>@<YOUR-K3S-IP>

# Terminal 2: Conectar via psql ou DBeaver
psql -h localhost -p 5432 -U mrhealth_admin -d mrhealth
```

### Tabelas no PostgreSQL
| Tabela | Linhas |
|--------|--------|
| produto | 30 |
| unidade | 3 |
| estado | 3 |
| pais | 1 |

### Queries de Validacao
```sql
-- Listar tabelas
\dt

-- Ver produtos
SELECT * FROM produto ORDER BY id_produto;

-- Ver unidades com geografia
SELECT u.nome_unidade, e.nome_estado, p.nome_pais
FROM unidade u
JOIN estado e ON u.id_estado = e.id_estado
JOIN pais p ON e.id_pais = p.id_pais;
```

---

## 8. Portainer (Interface Visual para Kubernetes)

**Status:** RUNNING
**URL:** http://<YOUR-K3S-IP>:30777
**URL HTTPS:** https://<YOUR-K3S-IP>:30779

### Primeiro Acesso
1. Abra http://<YOUR-K3S-IP>:30777 no navegador
2. Crie uma conta de administrador (username + senha)
3. Selecione "Kubernetes" como ambiente
4. Clique em "Connect"

### O que voce pode ver no Portainer
- **Namespaces:** mrhealth-db, portainer, kube-system, platypus-jobs
- **Deployments:** postgresql, airflow-webserver, airflow-scheduler, superset, portainer
- **Pods:** Status, logs, terminal
- **Services:** NodePort 30432 (PostgreSQL), 30180 (Airflow), 30188 (Superset), 30777 (Portainer)
- **Persistent Volumes:** postgresql-pvc, airflow-postgres-pvc, superset-pvc

### Verificar via CLI
```bash
# Status do Portainer
ssh <YOUR-SSH-USER>@<YOUR-K3S-IP> 'kubectl get pods -n portainer'

# Logs
ssh <YOUR-SSH-USER>@<YOUR-K3S-IP> 'kubectl logs -n portainer deployment/portainer --tail=10'
```

---

## 9. Airflow e Superset (Kubernetes)

**Status:** RUNNING NO KUBERNETES (namespace mrhealth-db)

Airflow e Superset agora rodam no cluster K3s junto com o PostgreSQL do projeto.

### URLs de Acesso
| Ferramenta | URL | Login |
|------------|-----|-------|
| **Airflow** | http://<YOUR-K3S-IP>:30180 | `admin` / `admin` |
| **Superset** | http://<YOUR-K3S-IP>:30188 | `admin` / `admin` |

### Componentes no Kubernetes
```
Namespace: mrhealth-db
├── airflow-postgres      (PostgreSQL para metadata do Airflow)
├── airflow-webserver     (Interface web - porta 30180)
├── airflow-scheduler     (Agendador de DAGs)
├── superset              (Dashboards - porta 30188)
└── postgresql            (Banco de dados do projeto Mr. Health)
```

### Verificar Status
```bash
# Via SSH
ssh <YOUR-SSH-USER>@<YOUR-K3S-IP> 'kubectl get pods -n mrhealth-db'

# Logs do Airflow
ssh <YOUR-SSH-USER>@<YOUR-K3S-IP> 'kubectl logs -n mrhealth-db deployment/airflow-webserver --tail=20'

# Logs do Superset
ssh <YOUR-SSH-USER>@<YOUR-K3S-IP> 'kubectl logs -n mrhealth-db deployment/superset --tail=20'
```

### Reiniciar Servicos
```bash
# Reiniciar Airflow
ssh <YOUR-SSH-USER>@<YOUR-K3S-IP> 'kubectl rollout restart deployment airflow-webserver airflow-scheduler -n mrhealth-db'

# Reiniciar Superset
ssh <YOUR-SSH-USER>@<YOUR-K3S-IP> 'kubectl rollout restart deployment superset -n mrhealth-db'
```

### Manifestos Kubernetes
Os arquivos de configuracao estao em:
```
k8s/
├── airflow/
│   ├── configmap.yaml
│   ├── postgres.yaml
│   ├── webserver.yaml
│   └── scheduler.yaml
├── superset/
│   ├── configmap.yaml
│   └── deployment.yaml
└── postgresql/
    └── (arquivos existentes)
```

---

## 10. Diagramas

### Arquivos Gerados
```
diagrams/generated/
├── architecture/
│   ├── infrastructure_v3_technical.excalidraw
│   └── infrastructure_v3_logo_flow.excalidraw
├── data-flow/
│   ├── medallion_pipeline_v3_technical.excalidraw
│   └── medallion_pipeline_v3_logo_flow.excalidraw
└── data-model/
    └── star_schema_v3_technical.excalidraw
```

### Como Visualizar
1. Acesse https://excalidraw.com
2. Clique em "Open" (icone de pasta)
3. Selecione qualquer arquivo `.excalidraw`
4. Exporte como PNG/SVG para apresentacoes

---

## 11. Codigo Python

### Scripts Principais
| Script | Funcao |
|--------|--------|
| `scripts/generate_fake_sales.py` | Gera CSVs de teste |
| `scripts/upload_fake_data_to_gcs.py` | Upload para GCS |
| `scripts/seed_postgresql.py` | Popula PostgreSQL |
| `scripts/build_silver_layer.py` | Transforma Bronze->Silver |
| `scripts/build_gold_layer.py` | Transforma Silver->Gold |
| `scripts/build_aggregations.py` | Cria tabelas de agregacao |

### Cloud Functions
| Funcao | Arquivo |
|--------|---------|
| csv-processor | `cloud_functions/csv_processor/main.py` |
| pg-reference-extractor | `cloud_functions/pg_reference_extractor/main.py` |
| data-generator | `cloud_functions/data_generator/main.py` |

### SQL
```
sql/
├── postgresql/
│   ├── create_tables.sql
│   └── create_readonly_user.sql
├── bronze/
│   └── create_tables.sql
├── silver/
│   ├── 01_reference_tables.sql
│   ├── 02_orders.sql
│   └── 03_order_items.sql
└── gold/
    ├── 01_dim_date.sql
    ├── 02_dim_product.sql
    ├── 03_dim_unit.sql
    ├── 04_dim_geography.sql
    ├── 05_fact_sales.sql
    ├── 06_fact_order_items.sql
    ├── 07_agg_daily_sales.sql
    ├── 08_agg_unit_performance.sql
    └── 09_agg_product_performance.sql
```

---

## 12. Links Rapidos

| O que | URL/Comando |
|-------|-------------|
| GCP Console | https://console.cloud.google.com/?project=sixth-foundry-485810-e5 |
| BigQuery | https://console.cloud.google.com/bigquery?project=sixth-foundry-485810-e5 |
| Cloud Storage | https://console.cloud.google.com/storage/browser/mrhealth-datalake-485810 |
| Cloud Functions | https://console.cloud.google.com/functions?project=sixth-foundry-485810-e5 |
| Cloud Scheduler | https://console.cloud.google.com/cloudscheduler?project=sixth-foundry-485810-e5 |
| SSH K3s | `ssh <YOUR-SSH-USER>@<YOUR-K3S-IP>` |
| **Portainer** | http://<YOUR-K3S-IP>:30777 |
| **Airflow** | http://<YOUR-K3S-IP>:30180 (use $AIRFLOW_ADMIN_USER/$AIRFLOW_ADMIN_PASSWORD) |
| **Superset** | http://<YOUR-K3S-IP>:30188 (use credentials from Secret Manager) |
| Diagramas | https://excalidraw.com + arquivos em `diagrams/generated/` |

---

## 13. Fluxo de Dados End-to-End

```
PostgreSQL (K3s)          CSV Generator
   │                          │
   │ 01:00 BRT               │ Local ou Cloud Function
   ▼                          ▼
┌────────────────────────────────────────┐
│        GCS: mrhealth-datalake-485810   │
│  raw/reference_data/   raw/csv_sales/  │
└────────────────────────────────────────┘
                 │
                 │ Eventarc trigger
                 ▼
         ┌──────────────┐
         │ csv-processor│
         │ Cloud Func   │
         └──────────────┘
                 │
                 ▼
┌────────────────────────────────────────┐
│     BigQuery: mrhealth_bronze          │
│  orders, order_items, products, etc    │
└────────────────────────────────────────┘
                 │
                 │ Airflow DAG (02:00 BRT)
                 ▼
┌────────────────────────────────────────┐
│     BigQuery: mrhealth_silver          │
│  Dados limpos e dedupados              │
└────────────────────────────────────────┘
                 │
                 │ Airflow DAG (continuacao)
                 ▼
┌────────────────────────────────────────┐
│     BigQuery: mrhealth_gold            │
│  Star Schema + Agregacoes              │
│  dim_*, fact_*, agg_*                  │
└────────────────────────────────────────┘
                 │
                 ▼
         ┌──────────────┐
         │   Superset   │
         │  Dashboards  │
         └──────────────┘
```

---

**Documento atualizado em 2026-02-03 06:21 BRT**

> **Changelog:** Airflow e Superset migrados para Kubernetes (namespace mrhealth-db)
