# Plano Estrategico de Modernizacao -- Case Fictício - Teste
## Projeto de Data Warehouse e Data Lake na Google Cloud Platform

**Documento:** Plano Estrategico de Implementacao
**Empresa:** Case Fictício - Teste -- Rede Slow-Food (50 unidades, regiao Sul do Brasil)
**Projeto:** Modernizacao do Ecossistema de Dados
**Elaborado para:** Arthur Graf -- Processo Seletivo
**Data:** Janeiro de 2026

---

## Sumario Executivo

A Case Fictício - Teste, rede de Slow-Food com 50 unidades, enfrenta um gargalo critico: a consolidacao manual de dados de vendas diarias consome recursos humanos, introduz erros, e impede a tomada de decisao agil que o fundador Joao Silva precisa para escalar a operacao para novos estados.

Este plano propoe a construcao de uma plataforma de dados moderna na Google Cloud Platform, utilizando GCS como data lake, BigQuery como data warehouse analitico, Dataform para orquestracao de transformacoes, Dataproc com Spark/PySpark para processamento distribuido, e Python para automacao e integracao. A arquitetura segue o padrao medallion (Raw/Bronze/Silver/Gold) e incorpora praticas de CI/CD, modelagem dimensional, e processamento batch event-driven.

O resultado: dados consolidados automaticamente em minutos apos o recebimento, eliminando o trabalho manual da equipe de Ricardo Martins e habilitando alertas e recomendacoes automaticas para gestao de estoques e expansao geografica.

---

## PARTE 1: MAPEAMENTO DO PROCESSO ATUAL (AS-IS)

### 1.1 Fluxo de Dados Atual

```
                    PROCESSO ATUAL -- FLUXO DE DADOS Case Fictício - Teste
                    =============================================

  [50 Unidades]              [Equipe Operacoes]           [Gestao]
       |                           |                         |
       |  Meia-noite (D-1)        |                         |
       |  Envio de CSV            |                         |
       v                           |                         |
  +-----------+                    |                         |
  | PEDIDO.CSV|----+               |                         |
  +-----------+    |               |                         |
  +---------------+|   Manual      |                         |
  |ITEM_PEDIDO.CSV|+-------------->|                         |
  +---------------+    Download    |                         |
                       & abertura  |                         |
                                   v                         |
                          +------------------+               |
                          | Consolidacao     |               |
                          | Manual em        |               |
                          | Planilhas Excel  |               |
                          +------------------+               |
                                   |                         |
                                   | Horas/Dias              |
                                   v                         |
                          +------------------+               |
                          | Analise Visual   |               |
                          | dos Dados        |-------------->|
                          +------------------+   Relatorios  |
                                                 pontuais    v
                                                    +------------------+
                                                    | Decisao baseada  |
                                                    | em dados          |
                                                    | defasados e       |
                                                    | potencialmente    |
                                                    | incorretos        |
                                                    +------------------+
```

### 1.2 Detalhamento do Processo Atual

| Etapa | Descricao | Responsavel | Frequencia |
|-------|-----------|-------------|------------|
| 1. Geracao dos CSVs | Cada unidade gera PEDIDO.CSV e ITEM_PEDIDO.CSV com fechamento D-1 | Sistemas locais das unidades | Diaria, meia-noite |
| 2. Envio dos arquivos | 50 unidades enviam 2 arquivos cada = 100 arquivos/dia | Sistemas locais | Diaria |
| 3. Recebimento | Equipe de operacoes recebe os 100 CSVs | Equipe Ricardo Martins | Diaria, manha seguinte |
| 4. Validacao visual | Conferencia manual de completude e formato | Analistas de operacoes | Diaria |
| 5. Consolidacao | Copiar e colar dados em planilhas-mestre | Analistas de operacoes | Diaria, consumindo horas |
| 6. Cruzamento | Uniao manual com dados de Produto, Unidade, Estado | Analistas de operacoes | Conforme necessidade |
| 7. Analise | Criacao de graficos e tabelas em Excel | Analistas de operacoes | Semanal/Mensal |
| 8. Relatorio | Compilacao de insights para gestao | Coordenacao | Semanal/Mensal |

### 1.3 Pontos Problematicos e Gargalos

```
MAPA DE DOR -- PONTOS CRITICOS DO PROCESSO ATUAL
=================================================

 GRAVIDADE: [!!!] Critico  [!!] Alto  [!] Medio

 [!!!] CONSOLIDACAO MANUAL
      - 100 arquivos CSV por dia processados manualmente
      - Consome 4-6 horas/dia de trabalho humano qualificado
      - Escala linearmente: cada nova unidade = +2 CSVs/dia
      - Expansao para novos estados torna processo inviavel

 [!!!] PROPENSO A ERROS
      - Copy-paste entre planilhas introduz erros silenciosos
      - Sem validacao automatica de schema, tipos ou completude
      - Sem deteccao de duplicatas ou registros ausentes
      - Erros so descobertos dias/semanas depois (se descobertos)

 [!!] LATENCIA NA TOMADA DE DECISAO
      - Dados disponíveis somente apos consolidacao manual (D+1 a D+3)
      - Impossibilita reacao rapida a problemas de estoque
      - Oportunidades de negocio perdidas por falta de visibilidade

 [!!] SILOS DE DADOS
      - Dados de vendas (CSV) desconectados de dados cadastrais (PostgreSQL)
      - Tabelas PRODUTO, UNIDADE, ESTADO, PAIS isoladas no banco da matriz
      - Sem visao integrada produto + geografia + vendas

 [!!] AUSENCIA DE HISTORICO CONFIAVEL
      - Planilhas Excel sem versionamento ou auditoria
      - Sem capacidade de rastrear mudancas ou correcoes
      - Impossivel reconstruir estado dos dados em data passada

 [!] FALTA DE INTELIGENCIA AUTOMATIZADA
      - Sem alertas automaticos (ex: queda abrupta de vendas em unidade)
      - Sem recomendacoes para gestao de estoque
      - Sem modelos preditivos para suportar expansao

 [!] ESCALABILIDADE ZERO
      - Processo nao escala para 100, 200+ unidades
      - Cada novo estado adicionado multiplica complexidade
      - Infraestrutura local limitada em capacidade
```

### 1.4 Analise Quantitativa do Impacto

| Metrica | Valor Atual | Impacto |
|---------|-------------|---------|
| Arquivos CSV / dia | 100 (50 unidades x 2 arquivos) | Processamento manual inviavel em escala |
| Tempo de consolidacao | 4-6 horas / dia | ~1.250 horas / ano de trabalho humano |
| Latencia de dados | D+1 a D+3 | Decisoes baseadas em dados defasados |
| Taxa de erro estimada | 2-5% por arquivo | ~2-5 registros incorretos por arquivo processado |
| Fontes de dados integradas | 0 (silos separados) | Nenhuma visao unificada |
| Alertas automaticos | 0 | Zero deteccao proativa de anomalias |

---

## PARTE 2: MAPEAMENTO DO PROCESSO FUTURO (TO-BE)

### 2.1 Visao do Estado Futuro

```
              PROCESSO FUTURO -- PLATAFORMA DE DADOS Case Fictício - Teste
              ===================================================

  [50 Unidades]         [GCP Cloud]                       [Usuarios]
       |                     |                                 |
       | Meia-noite          |                                 |
       | Upload auto         |                                 |
       v                     |                                 |
  +-----------+    Event     |                                 |
  | PEDIDO.CSV|--->Trigger   |                                 |
  +-----------+    |         |                                 |
  +---------------+|         |                                 |
  |ITEM_PEDIDO.CSV|+         |                                 |
  +---------------+ |        |                                 |
                     v        |                                 |
              +------------+  |                                 |
              | GCS Bucket |  |    +------------------+        |
              | (Raw Layer)|--+--->| Dataproc         |        |
              +------------+  |   | Serverless       |        |
                              |    | (PySpark)        |        |
  [PostgreSQL]                |    | Validacao +      |        |
  | PRODUTO  |   Datastream   |    | Limpeza +        |        |
  | UNIDADE  |----(CDC)-------+--->| Transformacao    |        |
  | ESTADO   |                |    +------------------+        |
  | PAIS     |                |           |                    |
                              |           v                    |
                              |    +------------------+        |
                              |    | GCS (Bronze/     |        |
                              |    |  Silver Layers)  |        |
                              |    +------------------+        |
                              |           |                    |
                              |           v                    |
                              |    +------------------+        |
                              |    | BigQuery         |        |
                              |    | (Silver/Gold)    |        |
                              |    +------------------+        |
                              |           |                    |
                              |           v                    |
                              |    +------------------+        |
                              |    | Dataform         |------->|
                              |    | (Orquestracao    | Dashboards
                              |    |  SQL + Gold      | Alertas
                              |    |  Layer Models)   | Relatorios
                              |    +------------------+   Auto
                              |           |                    |
                              |           v                    |
                              |    +------------------+        |
                              |    | Looker Studio    |------->|
                              |    | (Visualizacao)   |  Decisao
                              |    +------------------+  baseada
                              |           |            em dados
                              |           v            atualizados
                              |    +------------------+        |
                              |    | Alertas &        |------->|
                              |    | Recomendacoes    |  Acoes
                              |    | Automaticas      |  proativas
                              |    +------------------+        |
```

### 2.2 Como os Problemas Atuais Sao Resolvidos

| Problema Atual | Solucao Proposta | Tecnologia | Resultado |
|----------------|-----------------|------------|-----------|
| Consolidacao manual de 100 CSVs/dia | Ingestao automatica event-driven: upload no GCS dispara pipeline | Cloud Functions + Dataproc Serverless (PySpark) | Consolidacao em minutos, sem intervencao humana |
| Erros de copy-paste (2-5%) | Validacao automatica com PySpark: schema enforcement, null checks, dedup | Dataproc + PySpark + Great Expectations | Taxa de erro proxima a zero com quarentena de registros invalidos |
| Latencia D+1 a D+3 | Pipeline batch event-driven: dados disponiveis em 15-30 min apos upload | GCS Events + Cloud Functions + Dataproc + Dataform | Dados consolidados disponiveis antes do inicio do expediente |
| Silos de dados (CSV vs PostgreSQL) | Ingestao unificada com CDC do PostgreSQL e CSVs convergindo no mesmo data lake | Datastream (CDC) + GCS (Data Lake) + BigQuery | Visao integrada vendas + produtos + geografia |
| Sem historico confiavel | Data lake imutavel com camadas versionadas e BigQuery com particoes temporais | GCS (camadas Raw/Bronze) + BigQuery (particionamento) | Historico completo, auditavel, reconstruivel |
| Sem inteligencia automatizada | Modelos Gold em BigQuery com KPIs, alertas e dashboards automaticos | Dataform (Gold models) + Looker Studio + Cloud Monitoring | Alertas proativos e dashboards auto-atualizados |
| Escalabilidade zero | Infraestrutura serverless que escala elasticamente | GCS + Dataproc Serverless + BigQuery | Suporta 50, 500, 5000 unidades sem mudanca de arquitetura |

### 2.3 Detalhamento do Processo Futuro

| Etapa | Descricao | Tecnologia | SLA |
|-------|-----------|------------|-----|
| 1. Upload automatico | Unidades enviam CSVs para bucket GCS dedicado via script Python automatizado | GCS + Python client | Meia-noite (D-1) |
| 2. Deteccao de evento | Upload no GCS dispara notificacao via Eventarc/Pub/Sub | Cloud Functions (2nd gen) + Eventarc | < 1 min apos upload |
| 3. Orquestracao | Cloud Workflows coordena os passos do pipeline | Cloud Workflows | < 1 min |
| 4. Processamento Spark | PySpark valida, limpa e transforma os CSVs | Dataproc Serverless | 5-15 min |
| 5. Carga Bronze/Silver | Dados processados salvos no GCS (Parquet) e BigQuery | Spark BigQuery Connector | 2-5 min |
| 6. CDC PostgreSQL | Tabelas de referencia replicadas continuamente | Datastream | Near real-time |
| 7. Transformacao Gold | Dataform executa modelos SQL no BigQuery | Dataform (scheduled) | 5-10 min |
| 8. Disponibilizacao | Dados prontos em dashboards e alertas | Looker Studio + BigQuery | Automatico |

**Latencia total do pipeline: 15-30 minutos (vs. 4-6 horas + erros do processo manual)**

---

## PARTE 3: DIAGRAMA DE ARQUITETURA (GCP)

### 3.1 Arquitetura Completa

```
=====================================================================================
               ARQUITETURA DE DADOS Case Fictício - Teste -- GOOGLE CLOUD PLATFORM
=====================================================================================

FONTES DE DADOS                    INGESTAO                         DATA LAKE (GCS)
==================          ======================          =========================

+----------------+          +---------------------+          +----------------------+
| 50 Unidades    |  CSV     | GCS Bucket          |          | gs://case_ficticio-       |
| (Sistemas      |--------->| Landing Zone        |          |   datalake/          |
|  Locais)       | Upload   | gs://case_ficticio-      |          |                      |
|                | Python   |   landing/           |          | /raw/                |
| PEDIDO.CSV     | Script   |   {unidade}/{data}/ |          |   /csv_vendas/       |
| ITEM_PEDIDO.CSV|          +---------------------+          |     /{data}/         |
+----------------+               |                           |       /{unidade}/    |
                                 | Eventarc                  |         pedido.csv   |
                                 | (GCS Object              |         item.csv     |
                                 |  Finalize)               |                      |
                                 v                           |   /pg_cdc/           |
+----------------+          +---------------------+          |     /produto/        |
| PostgreSQL     | CDC      | Cloud Functions     |          |     /unidade/        |
| (Matriz)       |--------->| (2nd gen)           |          |     /estado/         |
|                |          | Trigger             |          |     /pais/           |
| PRODUTO        | Data-    | Orchestration       |          +----------------------+
| UNIDADE        | stream   +---------------------+               |
| ESTADO         |               |                                |
| PAIS           |               v                                |
+----------------+          +---------------------+               v
                            | Cloud Workflows     |     +----------------------+
                            | (Orchestracao)      |     | BRONZE LAYER         |
                            |                     |     | gs://case_ficticio-       |
                            | Step 1: Validate    |     |   datalake/bronze/   |
                            | Step 2: Process     |     |                      |
                            | Step 3: Load        |     | Formato: Parquet     |
                            | Step 4: Transform   |     | Schema enforced      |
                            | Step 5: Notify      |     | Deduplicado          |
                            +---------------------+     | Tipado               |
                                 |                      +----------------------+
                                 v                                |
PROCESSAMENTO                                                     v
==============                                          +----------------------+
                                                        | SILVER LAYER         |
+---------------------+                                 | BigQuery Dataset:    |
| Dataproc Serverless |                                 |   case_ficticio_silver    |
| (PySpark Jobs)      |                                 |                      |
|                     |                                 | Tabelas:             |
| Job 1: CSV Ingestion|    Spark BigQuery               | - pedidos            |
|   - Schema validate |    Connector                    | - itens_pedido       |
|   - Type casting    |---(direct write)--------------->| - produtos           |
|   - Null handling   |                                 | - unidades           |
|   - Deduplication   |                                 | - estados            |
|   - Partitioning    |                                 | - paises             |
|                     |                                 |                      |
| Job 2: PG Ingestion |                                 | Particionado por:    |
|   - CDC merge       |                                 |   data_pedido        |
|   - SCD Type 2      |                                 | Clusterizado por:    |
|   - Enrichment      |                                 |   id_unidade,        |
+---------------------+                                 |   tipo_pedido        |
                                                        +----------------------+
                                                                  |
TRANSFORMACAO                                                     v
==============                                          +----------------------+
                                                        | GOLD LAYER           |
+---------------------+                                 | BigQuery Dataset:    |
| Dataform            |                                 |   case_ficticio_gold      |
| (SQL Workflows)     |                                 |                      |
|                     |    SQLX Models                  | Modelos Dimensionais:|
| /definitions/       |-------------------------------->| - dim_produto        |
|   /staging/         |                                 | - dim_unidade        |
|     stg_pedidos     |                                 | - dim_geografia      |
|     stg_itens       |                                 | - dim_tempo          |
|   /intermediate/    |                                 | - fato_vendas        |
|     int_vendas_     |                                 | - fato_itens_venda   |
|       enriched      |                                 |                      |
|   /gold/            |                                 | Aggregated:          |
|     dim_produto     |                                 | - vendas_diarias_    |
|     dim_unidade     |                                 |     unidade          |
|     dim_geografia   |                                 | - vendas_produto_    |
|     dim_tempo       |                                 |     periodo          |
|     fato_vendas     |                                 | - kpi_operacional    |
|     fato_itens_venda|                                 | - alerta_anomalia    |
|     kpi_operacional |                                 +----------------------+
|     alerta_anomalia |                                           |
+---------------------+                                           v
                                                        +----------------------+
CONSUMO                                                 | Looker Studio        |
=======                                                 | (Dashboards)         |
                                                        |                      |
+---------------------+                                 | - Painel Executivo   |
| Usuarios Finais     |<-------------------------------| - Vendas por Unidade |
|                     |                                 | - Ranking Produtos   |
| Joao Silva (CEO)    |    +---------------------+     | - Mapa Geografico    |
|   - Dashboard exec. |<---| Cloud Monitoring    |     | - Gestao de Estoque  |
|                     |    | + Alertas           |     +----------------------+
| Ricardo Martins     |    | (Email/Slack)       |
|   - KPIs operacao   |    +---------------------+
|                     |
| Wilson Luiz (TI)    |    +---------------------+
|   - Monitoramento   |<---| Cloud Logging +     |
|   - Pipeline health |    | Error Reporting     |
+---------------------+    +---------------------+


=====================================================================================
                         INFRAESTRUTURA DE SUPORTE
=====================================================================================

+---------------------+    +---------------------+    +---------------------+
| Cloud Build         |    | Artifact Registry   |    | Secret Manager      |
| (CI/CD Pipeline)    |    | (Container Images)  |    | (Credenciais PG,    |
|                     |    |                     |    |  API Keys)          |
| - Build PySpark     |    | - PySpark job       |    |                     |
|   images            |    |   containers        |    | - pg_connection     |
| - Deploy Dataform   |    | - Python utils      |    | - service_accounts  |
| - Run tests         |    |                     |    |                     |
| - Promote envs      |    |                     |    |                     |
+---------------------+    +---------------------+    +---------------------+

+---------------------+    +---------------------+    +---------------------+
| Terraform           |    | GitHub Repository   |    | IAM & VPC           |
| (IaC)               |    | (Codigo Fonte)      |    | (Seguranca)         |
|                     |    |                     |    |                     |
| - Infra GCP         |    | - PySpark jobs      |    | - Service accounts  |
| - Buckets           |    | - Dataform SQLX     |    | - Least privilege   |
| - BigQuery datasets |    | - Cloud Functions   |    | - VPC peering       |
| - Dataproc configs  |    | - Terraform         |    | - Firewall rules    |
| - IAM policies      |    | - CI/CD configs     |    |                     |
+---------------------+    +---------------------+    +---------------------+
```

### 3.2 Componentes da Arquitetura -- Detalhamento

#### 3.2.1 Camada de Ingestao

**Google Cloud Storage (GCS) -- Landing Zone**
- **Bucket:** `gs://case_ficticio-landing/`
- **Estrutura:** `/{id_unidade}/{YYYY-MM-DD}/pedido.csv` e `item_pedido.csv`
- **Proposito:** Ponto de entrada para CSVs das unidades. Imutavel -- arquivos nunca sao deletados, apenas movidos apos processamento.
- **Lifecycle Policy:** Arquivos movidos para Nearline apos 30 dias, Coldline apos 90 dias.
- **Upload:** Script Python distribuido para as unidades, executado via cron/agendador local a meia-noite.

**Datastream (CDC do PostgreSQL)**
- **Tipo:** Change Data Capture continuo
- **Fonte:** PostgreSQL da matriz (tabelas PRODUTO, UNIDADE, ESTADO, PAIS)
- **Destino:** GCS (`gs://case_ficticio-datalake/raw/pg_cdc/`) e BigQuery (dataset `case_ficticio_raw_pg`)
- **Modo:** Merge (manter tabelas em sincronia para dados de referencia)
- **Staleness:** 1 hora (tabelas de referencia mudam com pouca frequencia)
- **Justificativa:** Datastream e serverless, nao requer gerenciamento de infraestrutura, e garante que as tabelas de referencia no BigQuery estejam sempre atualizadas. Para tabelas de referencia com baixa frequencia de mudanca, o modo Merge e a opcao ideal.

#### 3.2.2 Camada de Processamento

**Dataproc Serverless (PySpark)**
- **Modelo:** Serverless (sem provisionamento de cluster)
- **Jobs PySpark:**
  - `csv_ingestion_job.py` -- Processa CSVs do landing zone
  - `data_quality_job.py` -- Validacao e qualidade de dados
  - `bronze_writer_job.py` -- Escrita na camada Bronze (Parquet no GCS)
  - `silver_loader_job.py` -- Carga na camada Silver (BigQuery)
- **Justificativa:** Dataproc Serverless elimina a necessidade de gerenciar clusters. Paga-se apenas pelo tempo de execucao. Para um batch diario de 100 CSVs de tamanho moderado, o Serverless e mais econoico que manter um cluster dedicado. O Spark permite processamento paralelo e distribuido, essencial para escalabilidade futura (centenas de unidades).

**Cloud Functions (2nd gen) + Eventarc**
- **Trigger:** `google.cloud.storage.object.v1.finalized` no bucket landing
- **Funcao:** Inicia Cloud Workflow que coordena o pipeline
- **Runtime:** Python 3.11+
- **Timeout:** 60 segundos (apenas dispara o workflow)

**Cloud Workflows**
- **Proposito:** Orquestrar os passos do pipeline em sequencia com controle de erro e retry
- **Passos:**
  1. Validar metadados do arquivo recebido
  2. Submeter job PySpark no Dataproc Serverless
  3. Aguardar conclusao do job
  4. Disparar execucao do Dataform (via API REST)
  5. Enviar notificacao de sucesso/falha

#### 3.2.3 Camada de Transformacao

**Dataform (BigQuery SQL Workflows)**
- **Repositorio:** Vinculado ao GitHub (`case_ficticio-dataform`)
- **Linguagem:** SQLX (SQL + Jinja-like templating)
- **Estrutura de modelos:**
  - `/definitions/staging/` -- Modelos de staging (limpeza e tipagem)
  - `/definitions/intermediate/` -- Enriquecimento e joins
  - `/definitions/gold/` -- Modelos dimensionais e fatos
  - `/definitions/metrics/` -- KPIs agregados e alertas
- **Scheduled Execution:** Diario, apos conclusao do pipeline PySpark (trigger via API)
- **Ambiente:** dev (branch develop) / prod (branch main)
- **Justificativa:** Dataform e nativo do GCP e integrado ao BigQuery. Permite versionamento Git, testes de dados (assertions), documentacao inline, e gerenciamento de dependencias entre modelos. A escolha do Dataform sobre o dbt se justifica pela integracao nativa, custo zero de licenciamento, e menor overhead operacional.

#### 3.2.4 Camada de Armazenamento e Analise

**BigQuery**
- **Datasets:**
  - `case_ficticio_raw_pg` -- Dados brutos do PostgreSQL (Datastream)
  - `case_ficticio_silver` -- Dados limpos e normalizados
  - `case_ficticio_gold` -- Modelos dimensionais e fatos
  - `case_ficticio_metrics` -- KPIs agregados e alertas
- **Particionamento:** Por `data_pedido` (tabelas de fato)
- **Clusterizacao:** Por `id_unidade`, `tipo_pedido` (queries frequentes)
- **Reservations:** On-demand para inicio, migrar para Editions conforme volume cresce
- **Justificativa:** BigQuery e o servico analitico mais maduro do GCP. Separacao em datasets reflete as camadas da arquitetura e permite controle granular de acesso (IAM por dataset). Particionamento e clusterizacao otimizam custo e performance para os padroes de query da Case Fictício - Teste (sempre filtram por data e unidade).

#### 3.2.5 Camada de Consumo

**Looker Studio**
- **Dashboards planejados:**
  - Painel Executivo (CEO -- Joao Silva)
  - Operacoes Diarias (COO -- Ricardo Martins)
  - Monitoramento de Pipeline (TI -- Wilson Luiz)
- **Conexao:** Direta ao BigQuery (dataset gold)
- **Refresh:** Automatico (BigQuery BI Engine para cache)

### 3.3 Decisoes de Arquitetura e Trade-offs

| Decisao | Escolha | Alternativa Rejeitada | Justificativa |
|---------|---------|----------------------|---------------|
| Runtime Spark | Dataproc Serverless | Dataproc Managed Cluster | Volume diario nao justifica cluster 24/7. Serverless reduz custo em ~70% para batch esporadico |
| CDC PostgreSQL | Datastream | PySpark JDBC + schedule | Datastream e serverless, near-real-time, e nao impacta performance do PostgreSQL. JDBC requer cluster ativo e locks de leitura |
| Transformacao | Dataform | dbt Cloud | Dataform e nativo GCP (custo zero), Git-integrated, e com suporte direto Google. dbt teria custo adicional de licenciamento |
| Orquestracao | Cloud Workflows + Functions | Cloud Composer (Airflow) | Para um pipeline com 4-5 passos, Cloud Composer e over-engineering. Workflows e serverless e custa centavos. Migrar para Composer se complexidade crescer |
| Formato Data Lake | Parquet (GCS) | Delta Lake / Iceberg | Parquet e nativamente suportado por Spark e BigQuery. Delta/Iceberg adicionam complexidade sem beneficio claro para o volume atual |
| Modelagem Gold | Star Schema (Kimball) | Data Vault 2.0 | Star Schema e mais simples, performatico em BigQuery, e adequado para o dominio (vendas retail). Data Vault seria overengineering |

---

## PARTE 4: ESTRATEGIA DE DATA LAKE -- ARQUITETURA MEDALLION

### 4.1 Visao Geral das Camadas

```
ARQUITETURA MEDALLION -- Case Fictício - Teste DATA LAKE
==============================================

 +----------+     +-----------+     +-----------+     +----------+
 |   RAW    |---->|  BRONZE   |---->|  SILVER   |---->|   GOLD   |
 | (Landing)|     | (Cleaned) |     | (Enriched)|     | (Business|
 |          |     |           |     |           |     |  Ready)  |
 +----------+     +-----------+     +-----------+     +----------+
   GCS             GCS (Parquet)     BigQuery          BigQuery
   CSV/JSON        + BigQuery        Dataset           Dataset

  Imutavel         Schema            Normalizado       Dimensional
  Original         Enforced          Enriquecido       Star Schema
  Append-only      Deduplicated      Joins             KPIs
                   Type-cast         Business Rules    Alertas
```

### 4.2 Camada RAW (Landing Zone)

**Armazenamento:** Google Cloud Storage
**Bucket:** `gs://case_ficticio-landing/`
**Formato:** CSV original (sem transformacao)
**Retencao:** Permanente (lifecycle para Coldline apos 90 dias)

```
gs://case_ficticio-landing/
|
+-- csv_vendas/
|   +-- 2026/
|       +-- 01/
|           +-- 29/
|               +-- unidade_001/
|               |   +-- pedido.csv
|               |   +-- item_pedido.csv
|               |   +-- _metadata.json        (timestamp upload, checksum)
|               +-- unidade_002/
|               |   +-- pedido.csv
|               |   +-- item_pedido.csv
|               |   +-- _metadata.json
|               +-- ...
|               +-- unidade_050/
|                   +-- pedido.csv
|                   +-- item_pedido.csv
|                   +-- _metadata.json
|
+-- pg_cdc/                                   (Datastream output)
|   +-- produto/
|   |   +-- 2026/01/29/
|   |       +-- *.avro                         (Datastream format)
|   +-- unidade/
|   +-- estado/
|   +-- pais/
|
+-- _quarantine/                               (Arquivos com erros)
    +-- 2026/01/29/
        +-- unidade_003/
            +-- pedido.csv                     (arquivo invalido)
            +-- _error_report.json             (detalhes do erro)
```

**Principios da Camada Raw:**
- **Imutabilidade:** Arquivos originais nunca sao alterados ou deletados
- **Rastreabilidade:** `_metadata.json` com timestamp de upload, checksum MD5, tamanho do arquivo
- **Quarentena:** Arquivos que falham na validacao sao movidos para `_quarantine/` com relatorio de erro
- **Particionamento temporal:** Estrutura `ano/mes/dia` facilita processamento incremental

### 4.3 Camada BRONZE (Cleaned & Standardized)

**Armazenamento:** GCS (Parquet) + BigQuery (espelho)
**Bucket GCS:** `gs://case_ficticio-datalake/bronze/`
**BigQuery Dataset:** `case_ficticio_bronze`
**Formato:** Apache Parquet (compressao Snappy)
**Processamento:** Dataproc Serverless (PySpark)

```
gs://case_ficticio-datalake/bronze/
|
+-- pedidos/
|   +-- data_ingestao=2026-01-29/              (particionado por data)
|       +-- part-00000-xxxx.snappy.parquet
|       +-- part-00001-xxxx.snappy.parquet
|       +-- _SUCCESS
|
+-- itens_pedido/
|   +-- data_ingestao=2026-01-29/
|       +-- part-00000-xxxx.snappy.parquet
|       +-- _SUCCESS
|
+-- produtos/                                   (fonte: PostgreSQL CDC)
|   +-- snapshot_date=2026-01-29/
|       +-- part-00000-xxxx.snappy.parquet
|
+-- unidades/
+-- estados/
+-- paises/
```

**Transformacoes PySpark na camada Bronze:**

```python
# Exemplo conceitual: csv_to_bronze_job.py
# Executado no Dataproc Serverless

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType,
    DecimalType, DateType, TimestampType
)

# Schema enforcement para PEDIDO.CSV
PEDIDO_SCHEMA = StructType([
    StructField("Id_Unidade", IntegerType(), nullable=False),
    StructField("Id_Pedido", StringType(), nullable=False),
    StructField("Tipo_Pedido", StringType(), nullable=False),
    StructField("Data_Pedido", DateType(), nullable=False),
    StructField("Vlr_Pedido", DecimalType(10, 2), nullable=False),
    StructField("Endereco_Entrega", StringType(), nullable=True),
    StructField("Taxa_Entrega", DecimalType(10, 2), nullable=True),
    StructField("Status", StringType(), nullable=False),
])

def process_csv_to_bronze(spark, input_path, output_path, processing_date):
    """
    Processa CSVs do landing zone para a camada Bronze.
    - Aplica schema enforcement
    - Remove duplicatas
    - Padroniza encoding e formatos
    - Adiciona metadados de ingestao
    """
    # Leitura com schema enforcement
    df_raw = (
        spark.read
        .option("header", "true")
        .option("delimiter", ";")
        .option("encoding", "UTF-8")
        .option("mode", "PERMISSIVE")
        .option("columnNameOfCorruptRecord", "_corrupted")
        .schema(PEDIDO_SCHEMA)
        .csv(input_path)
    )

    # Separar registros validos e corrompidos
    df_valid = df_raw.filter(F.col("_corrupted").isNull()).drop("_corrupted")
    df_invalid = df_raw.filter(F.col("_corrupted").isNotNull())

    # Quarentena para registros invalidos
    if df_invalid.count() > 0:
        df_invalid.write.mode("append").json(
            f"gs://case_ficticio-landing/_quarantine/{processing_date}/"
        )

    # Padronizacao
    df_bronze = (
        df_valid
        .withColumn("tipo_pedido",
            F.when(F.upper(F.col("Tipo_Pedido")).contains("ONLINE"), "ONLINE")
             .when(F.upper(F.col("Tipo_Pedido")).contains("FISICA"), "FISICA")
             .otherwise("DESCONHECIDO")
        )
        .withColumn("status",
            F.upper(F.trim(F.col("Status")))
        )
        # Deduplicacao por Id_Pedido (mantendo registro mais recente)
        .dropDuplicates(["Id_Pedido"])
        # Metadados de ingestao
        .withColumn("_data_ingestao", F.lit(processing_date))
        .withColumn("_timestamp_processamento", F.current_timestamp())
        .withColumn("_fonte", F.lit("csv_vendas"))
    )

    # Escrita em Parquet particionado
    (
        df_bronze.write
        .mode("append")
        .partitionBy("_data_ingestao")
        .parquet(output_path)
    )

    return df_bronze.count(), df_invalid.count()
```

**Regras da Camada Bronze:**
- Schema enforcement rigido (rejeitar registros que nao conformam)
- Casting de tipos (string -> date, string -> decimal)
- Deduplicacao por chave primaria
- Padronizacao de encoding (UTF-8) e formatos (datas ISO 8601)
- Adicao de metadados de linhagem (`_data_ingestao`, `_timestamp_processamento`, `_fonte`)
- Registros invalidos enviados para quarentena com relatorio de erro

### 4.4 Camada SILVER (Enriched & Normalized)

**Armazenamento:** BigQuery
**Dataset:** `case_ficticio_silver`
**Processamento:** Dataproc (carga inicial) + Dataform (incrementais)

```
BigQuery: case_ficticio_silver
|
+-- pedidos                    (particionado por data_pedido, clusterizado por id_unidade)
|   Campos: id_pedido, id_unidade, tipo_pedido, data_pedido,
|           vlr_pedido, endereco_entrega, taxa_entrega, status,
|           _data_ingestao, _timestamp_processamento
|
+-- itens_pedido               (particionado por _data_ingestao, clusterizado por id_pedido)
|   Campos: id_pedido, id_item_pedido, id_produto, qtd,
|           vlr_item, vlr_total_item, observacao,
|           _data_ingestao, _timestamp_processamento
|
+-- produtos                   (tabela regular, SCD Type 2)
|   Campos: id_produto, nome_produto, _valido_de, _valido_ate, _corrente
|
+-- unidades                   (tabela regular, SCD Type 2)
|   Campos: id_unidade, nome_unidade, id_estado, _valido_de, _valido_ate, _corrente
|
+-- estados                    (tabela regular)
|   Campos: id_estado, id_pais, nome_estado
|
+-- paises                     (tabela regular)
|   Campos: id_pais, nome_pais
```

**Transformacoes na camada Silver:**
- Join de itens_pedido com pedidos para validacao de integridade referencial
- Calculo de `vlr_total_item` = `qtd` * `vlr_item`
- Aplicacao de business rules (ex: status validos, faixas de valor)
- SCD Type 2 para tabelas de referencia (rastrear mudancas historicas de produtos/unidades)
- Testes de integridade (assertions no Dataform)

### 4.5 Camada GOLD (Business-Ready / Dimensional Model)

**Armazenamento:** BigQuery
**Dataset:** `case_ficticio_gold`
**Processamento:** Dataform (SQLX models)

#### 4.5.1 Modelo Dimensional (Star Schema)

```
                    STAR SCHEMA -- Case Fictício - Teste
                    =========================

                        +----------------+
                        | dim_tempo      |
                        |----------------|
                        | sk_tempo (PK)  |
                        | data           |
                        | dia            |
                        | dia_semana     |
                        | nome_dia_semana|
                        | semana_ano     |
                        | mes            |
                        | nome_mes       |
                        | trimestre      |
                        | ano            |
                        | eh_fim_semana  |
                        | eh_feriado     |
                        +-------+--------+
                                |
+----------------+     +--------+--------+     +----------------+
| dim_produto    |     | fato_vendas     |     | dim_unidade    |
|----------------|     |-----------------|     |----------------|
| sk_produto (PK)|<----| sk_produto (FK) |     | sk_unidade (PK)|
| id_produto     |     | sk_unidade (FK) |--->| id_unidade     |
| nome_produto   |     | sk_tempo (FK)   |     | nome_unidade   |
| _valido_de     |     | sk_geografia(FK)|     | id_estado      |
| _valido_ate    |     |                 |     | nome_estado    |
| _corrente      |     | id_pedido       |     | id_pais        |
+----------------+     | tipo_pedido     |     | nome_pais      |
                       | vlr_pedido      |     | regiao         |
+----------------+     | taxa_entrega    |     | _valido_de     |
| dim_geografia  |     | vlr_itens_total |     | _valido_ate    |
|----------------|     | qtd_itens       |     | _corrente      |
| sk_geo (PK)    |<----| status          |     +----------------+
| id_estado      |     | margem_entrega  |
| nome_estado    |     | _data_ingestao  |
| id_pais        |     +-----------------+
| nome_pais      |              |
| regiao_brasil  |     +--------+--------+
+----------------+     | fato_itens_venda|
                       |-----------------|
                       | sk_produto (FK) |
                       | sk_tempo (FK)   |
                       | id_pedido (FK)  |
                       | id_item_pedido  |
                       | qtd             |
                       | vlr_unitario    |
                       | vlr_total       |
                       | _data_ingestao  |
                       +-----------------+
```

#### 4.5.2 Modelos Dataform (SQLX) -- Exemplos

**Arquivo: `/definitions/gold/dim_tempo.sqlx`**
```sql
config {
  type: "table",
  schema: "case_ficticio_gold",
  description: "Dimensao tempo com granularidade diaria",
  tags: ["gold", "dimensao"],
  assertions: {
    uniqueKey: ["sk_tempo"],
    nonNull: ["sk_tempo", "data", "ano", "mes", "dia"]
  }
}

WITH date_spine AS (
  SELECT date
  FROM UNNEST(
    GENERATE_DATE_ARRAY('2020-01-01', CURRENT_DATE(), INTERVAL 1 DAY)
  ) AS date
)

SELECT
  FORMAT_DATE('%Y%m%d', date) AS sk_tempo,
  date AS data,
  EXTRACT(DAY FROM date) AS dia,
  EXTRACT(DAYOFWEEK FROM date) AS dia_semana,
  FORMAT_DATE('%A', date) AS nome_dia_semana,
  EXTRACT(ISOWEEK FROM date) AS semana_ano,
  EXTRACT(MONTH FROM date) AS mes,
  FORMAT_DATE('%B', date) AS nome_mes,
  EXTRACT(QUARTER FROM date) AS trimestre,
  EXTRACT(YEAR FROM date) AS ano,
  CASE WHEN EXTRACT(DAYOFWEEK FROM date) IN (1, 7) THEN TRUE ELSE FALSE END AS eh_fim_semana,
  FALSE AS eh_feriado  -- Expandir com tabela de feriados nacionais/regionais
FROM date_spine
```

**Arquivo: `/definitions/gold/fato_vendas.sqlx`**
```sql
config {
  type: "incremental",
  schema: "case_ficticio_gold",
  description: "Fato de vendas - granularidade por pedido",
  tags: ["gold", "fato"],
  bigquery: {
    partitionBy: "data_pedido",
    clusterBy: ["id_unidade", "tipo_pedido"]
  },
  assertions: {
    uniqueKey: ["id_pedido"],
    nonNull: ["id_pedido", "sk_tempo", "sk_unidade", "vlr_pedido"]
  }
}

SELECT
  p.id_pedido,
  FORMAT_DATE('%Y%m%d', p.data_pedido) AS sk_tempo,
  CAST(p.id_unidade AS STRING) AS sk_unidade,
  COALESCE(
    (SELECT sk_produto FROM ${ref("dim_produto")} dp
     WHERE dp.id_produto = ip_agg.produto_principal AND dp._corrente = TRUE),
    'DESCONHECIDO'
  ) AS sk_produto_principal,
  CAST(p.id_unidade AS STRING) AS sk_geografia,
  p.tipo_pedido,
  p.data_pedido,
  p.vlr_pedido,
  COALESCE(p.taxa_entrega, 0) AS taxa_entrega,
  ip_agg.vlr_itens_total,
  ip_agg.qtd_itens,
  p.status,
  CASE
    WHEN p.tipo_pedido = 'ONLINE' AND p.taxa_entrega > 0
    THEN p.taxa_entrega / NULLIF(p.vlr_pedido, 0)
    ELSE 0
  END AS pct_taxa_sobre_pedido,
  p._data_ingestao
FROM ${ref("pedidos")} p
LEFT JOIN (
  SELECT
    id_pedido,
    SUM(vlr_item * qtd) AS vlr_itens_total,
    SUM(qtd) AS qtd_itens,
    -- Produto principal = item de maior valor
    ARRAY_AGG(id_produto ORDER BY vlr_item * qtd DESC LIMIT 1)[OFFSET(0)] AS produto_principal
  FROM ${ref("itens_pedido")}
  GROUP BY id_pedido
) ip_agg ON p.id_pedido = ip_agg.id_pedido

${when(incremental(),
  `WHERE p._data_ingestao > (SELECT MAX(_data_ingestao) FROM ${self()})`
)}
```

**Arquivo: `/definitions/metrics/kpi_operacional.sqlx`**
```sql
config {
  type: "table",
  schema: "case_ficticio_gold",
  description: "KPIs operacionais agregados por unidade e dia",
  tags: ["gold", "kpi"],
  bigquery: {
    partitionBy: "data_referencia",
    clusterBy: ["id_unidade"]
  }
}

SELECT
  fv.data_pedido AS data_referencia,
  fv.sk_unidade AS id_unidade,
  du.nome_unidade,
  du.nome_estado,

  -- Volume
  COUNT(DISTINCT fv.id_pedido) AS total_pedidos,
  COUNT(DISTINCT CASE WHEN fv.status = 'FINALIZADO' THEN fv.id_pedido END) AS pedidos_finalizados,
  COUNT(DISTINCT CASE WHEN fv.status = 'CANCELADO' THEN fv.id_pedido END) AS pedidos_cancelados,
  COUNT(DISTINCT CASE WHEN fv.status = 'PENDENTE' THEN fv.id_pedido END) AS pedidos_pendentes,

  -- Receita
  SUM(CASE WHEN fv.status = 'FINALIZADO' THEN fv.vlr_pedido ELSE 0 END) AS receita_bruta,
  SUM(CASE WHEN fv.status = 'FINALIZADO' THEN fv.taxa_entrega ELSE 0 END) AS receita_taxa_entrega,
  AVG(CASE WHEN fv.status = 'FINALIZADO' THEN fv.vlr_pedido END) AS ticket_medio,

  -- Canal
  COUNT(DISTINCT CASE WHEN fv.tipo_pedido = 'ONLINE' AND fv.status = 'FINALIZADO' THEN fv.id_pedido END) AS pedidos_online,
  COUNT(DISTINCT CASE WHEN fv.tipo_pedido = 'FISICA' AND fv.status = 'FINALIZADO' THEN fv.id_pedido END) AS pedidos_loja,
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN fv.tipo_pedido = 'ONLINE' AND fv.status = 'FINALIZADO' THEN fv.id_pedido END),
    COUNT(DISTINCT CASE WHEN fv.status = 'FINALIZADO' THEN fv.id_pedido END)
  ) AS pct_vendas_online,

  -- Operacional
  SAFE_DIVIDE(
    COUNT(DISTINCT CASE WHEN fv.status = 'CANCELADO' THEN fv.id_pedido END),
    COUNT(DISTINCT fv.id_pedido)
  ) AS taxa_cancelamento,

  SUM(fv.qtd_itens) AS total_itens_vendidos

FROM ${ref("fato_vendas")} fv
LEFT JOIN ${ref("dim_unidade")} du ON fv.sk_unidade = du.sk_unidade AND du._corrente = TRUE
GROUP BY 1, 2, 3, 4
```

**Arquivo: `/definitions/metrics/alerta_anomalia.sqlx`**
```sql
config {
  type: "table",
  schema: "case_ficticio_gold",
  description: "Deteccao de anomalias para alertas automaticos",
  tags: ["gold", "alerta"]
}

WITH metricas_recentes AS (
  SELECT
    id_unidade,
    nome_unidade,
    data_referencia,
    total_pedidos,
    receita_bruta,
    taxa_cancelamento,
    ticket_medio,
    -- Media movel 7 dias
    AVG(total_pedidos) OVER (
      PARTITION BY id_unidade ORDER BY data_referencia
      ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
    ) AS media_pedidos_7d,
    AVG(receita_bruta) OVER (
      PARTITION BY id_unidade ORDER BY data_referencia
      ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
    ) AS media_receita_7d,
    AVG(taxa_cancelamento) OVER (
      PARTITION BY id_unidade ORDER BY data_referencia
      ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
    ) AS media_cancelamento_7d
  FROM ${ref("kpi_operacional")}
)

SELECT
  data_referencia,
  id_unidade,
  nome_unidade,
  CASE
    WHEN total_pedidos < media_pedidos_7d * 0.5
    THEN 'CRITICO: Queda de >50% no volume de pedidos'
    WHEN receita_bruta < media_receita_7d * 0.6
    THEN 'ALTO: Queda de >40% na receita'
    WHEN taxa_cancelamento > media_cancelamento_7d * 2
    THEN 'ALTO: Taxa de cancelamento dobrou'
    WHEN taxa_cancelamento > 0.15
    THEN 'MEDIO: Taxa de cancelamento acima de 15%'
    WHEN total_pedidos = 0
    THEN 'CRITICO: Unidade sem pedidos (possivel falha no envio)'
  END AS tipo_alerta,
  CASE
    WHEN total_pedidos < media_pedidos_7d * 0.5 THEN 'CRITICO'
    WHEN receita_bruta < media_receita_7d * 0.6 THEN 'ALTO'
    WHEN taxa_cancelamento > media_cancelamento_7d * 2 THEN 'ALTO'
    WHEN taxa_cancelamento > 0.15 THEN 'MEDIO'
    WHEN total_pedidos = 0 THEN 'CRITICO'
  END AS severidade,
  total_pedidos,
  media_pedidos_7d,
  receita_bruta,
  media_receita_7d,
  taxa_cancelamento,
  media_cancelamento_7d,
  CURRENT_TIMESTAMP() AS gerado_em
FROM metricas_recentes
WHERE
  total_pedidos < media_pedidos_7d * 0.5
  OR receita_bruta < media_receita_7d * 0.6
  OR taxa_cancelamento > media_cancelamento_7d * 2
  OR taxa_cancelamento > 0.15
  OR total_pedidos = 0
```

### 4.6 Resumo da Estrategia Medallion

| Camada | Armazenamento | Formato | Processamento | Retencao | Acesso |
|--------|--------------|---------|---------------|----------|--------|
| **Raw** | GCS (`case_ficticio-landing`) | CSV original | Nenhum (copia fiel) | Permanente (lifecycle Coldline 90d) | Engenharia de dados |
| **Bronze** | GCS (`case_ficticio-datalake/bronze`) + BigQuery (`case_ficticio_bronze`) | Parquet (Snappy) | PySpark: schema enforcement, dedup, type cast | 2 anos (GCS), 1 ano (BQ) | Engenharia de dados |
| **Silver** | BigQuery (`case_ficticio_silver`) | BigQuery native | PySpark + Dataform: normalizado, enriquecido, SCD | 3 anos | Analistas + Engenharia |
| **Gold** | BigQuery (`case_ficticio_gold`) | BigQuery native | Dataform: modelagem dimensional, KPIs | 5 anos | Todos (dashboards, alertas) |

---

## PARTE 5: CI/CD E DEVOPS PARA DATA ENGINEERING

### 5.1 Estrategia de CI/CD

```
CI/CD PIPELINE -- Case Fictício - Teste DATA PLATFORM
============================================

 [Developer]     [GitHub]          [Cloud Build]        [GCP Environments]
      |              |                   |                      |
      |  git push    |                   |                      |
      +------------->|                   |                      |
      |              |   Trigger         |                      |
      |              +------------------>|                      |
      |              |                   |                      |
      |              |            +------+------+               |
      |              |            |  CI Stage   |               |
      |              |            |             |               |
      |              |            | 1. Lint SQL |               |
      |              |            |    (SQLX)   |               |
      |              |            | 2. Lint     |               |
      |              |            |    Python   |               |
      |              |            | 3. Unit     |               |
      |              |            |    Tests    |               |
      |              |            | 4. Dataform |               |
      |              |            |    Compile  |               |
      |              |            | 5. Dry-run  |               |
      |              |            |    PySpark  |               |
      |              |            +------+------+               |
      |              |                   |                      |
      |              |            +------+------+               |
      |              |            | CD Stage    |               |
      |              |            | (on merge   |               |
      |              |            |  to main)   |               |
      |              |            |             |        +------+------+
      |              |            | 1. Deploy   |------->| DEV         |
      |              |            |    Terraform|        | project-dev |
      |              |            | 2. Deploy   |        +-------------+
      |              |            |    Dataform |               |
      |              |            | 3. Deploy   |        +------+------+
      |              |            |    PySpark  |------->| STAGING     |
      |              |            |    jobs     |        | project-stg |
      |              |            | 4. Run      |        +-------------+
      |              |            |    integ    |               |
      |              |            |    tests    |        +------+------+
      |              |            | 5. Promote  |------->| PRODUCTION  |
      |              |            |    to prod  |        | project-prd |
      |              |            +-------------+        +-------------+
```

### 5.2 Estrutura do Repositorio GitHub

```
case_ficticio-data-platform/
|
+-- terraform/                          # Infraestrutura como Codigo
|   +-- modules/
|   |   +-- gcs/                        # Buckets GCS
|   |   +-- bigquery/                   # Datasets e tabelas
|   |   +-- dataproc/                   # Config Dataproc Serverless
|   |   +-- dataform/                   # Repositorio Dataform
|   |   +-- datastream/                 # CDC PostgreSQL
|   |   +-- iam/                        # Service accounts e roles
|   |   +-- networking/                 # VPC, firewall
|   +-- environments/
|   |   +-- dev/
|   |   |   +-- main.tf
|   |   |   +-- variables.tf
|   |   |   +-- terraform.tfvars
|   |   +-- staging/
|   |   +-- production/
|   +-- backend.tf
|
+-- pyspark/                            # Jobs PySpark
|   +-- jobs/
|   |   +-- csv_ingestion_job.py        # Ingestao CSV -> Bronze
|   |   +-- data_quality_job.py         # Validacao de qualidade
|   |   +-- silver_loader_job.py        # Bronze -> Silver (BigQuery)
|   +-- utils/
|   |   +-- schema_registry.py          # Schemas centralizados
|   |   +-- quality_checks.py           # Regras de qualidade
|   |   +-- gcs_utils.py               # Helpers GCS
|   +-- tests/
|   |   +-- test_csv_ingestion.py
|   |   +-- test_data_quality.py
|   |   +-- test_silver_loader.py
|   +-- requirements.txt
|   +-- Dockerfile                      # Para Dataproc custom container
|
+-- dataform/                           # Transformacoes SQL
|   +-- definitions/
|   |   +-- staging/
|   |   |   +-- stg_pedidos.sqlx
|   |   |   +-- stg_itens_pedido.sqlx
|   |   |   +-- stg_produtos.sqlx
|   |   |   +-- stg_unidades.sqlx
|   |   +-- intermediate/
|   |   |   +-- int_vendas_enriched.sqlx
|   |   |   +-- int_produto_unidade.sqlx
|   |   +-- gold/
|   |   |   +-- dim_tempo.sqlx
|   |   |   +-- dim_produto.sqlx
|   |   |   +-- dim_unidade.sqlx
|   |   |   +-- dim_geografia.sqlx
|   |   |   +-- fato_vendas.sqlx
|   |   |   +-- fato_itens_venda.sqlx
|   |   +-- metrics/
|   |       +-- kpi_operacional.sqlx
|   |       +-- alerta_anomalia.sqlx
|   |       +-- vendas_diarias_unidade.sqlx
|   +-- includes/
|   |   +-- constants.js                # Variaveis compartilhadas
|   |   +-- helpers.js                  # Funcoes helper
|   +-- dataform.json
|   +-- package.json
|
+-- cloud_functions/                    # Triggers e automacao
|   +-- gcs_event_trigger/
|   |   +-- main.py
|   |   +-- requirements.txt
|   +-- alert_notifier/
|       +-- main.py
|       +-- requirements.txt
|
+-- cloud_workflows/                    # Orquestracao
|   +-- daily_pipeline.yaml
|   +-- backfill_pipeline.yaml
|
+-- scripts/                            # Utilidades
|   +-- upload_csv.py                   # Script para unidades
|   +-- backfill_historical.py          # Carga historica
|   +-- setup_datastream.sh             # Config CDC
|
+-- tests/                              # Testes de integracao
|   +-- integration/
|   |   +-- test_pipeline_e2e.py
|   +-- data_quality/
|       +-- test_silver_assertions.py
|
+-- cloudbuild.yaml                     # CI/CD Pipeline definition
+-- cloudbuild-deploy.yaml              # CD Pipeline
+-- .gitignore
+-- README.md
```

### 5.3 Cloud Build Pipeline (cloudbuild.yaml)

```yaml
# cloudbuild.yaml -- CI Pipeline
steps:
  # Step 1: Lint Python
  - name: 'python:3.11-slim'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install flake8 black mypy
        cd pyspark
        flake8 jobs/ utils/ --max-line-length=120
        black --check jobs/ utils/
    id: 'lint-python'

  # Step 2: Unit Tests PySpark
  - name: 'python:3.11-slim'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r pyspark/requirements.txt
        pip install pytest pytest-cov
        cd pyspark
        python -m pytest tests/ -v --cov=jobs --cov=utils --cov-report=term-missing
    id: 'unit-tests-pyspark'
    waitFor: ['lint-python']

  # Step 3: Compile Dataform
  - name: 'node:18-slim'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        cd dataform
        npm install
        npx dataform compile --json
    id: 'compile-dataform'

  # Step 4: Validate Terraform
  - name: 'hashicorp/terraform:1.7'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        cd terraform/environments/dev
        terraform init -backend=false
        terraform validate
        terraform fmt -check -recursive
    id: 'validate-terraform'

  # Step 5: Build PySpark container
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/case_ficticio-repo/pyspark-jobs:$SHORT_SHA'
      - './pyspark'
    id: 'build-pyspark-image'
    waitFor: ['unit-tests-pyspark']

  # Step 6: Push container to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/case_ficticio-repo/pyspark-jobs:$SHORT_SHA'
    id: 'push-pyspark-image'
    waitFor: ['build-pyspark-image']

options:
  logging: CLOUD_LOGGING_ONLY

substitutions:
  _REGION: 'southamerica-east1'
```

---

## PARTE 6: PRODUCT BACKLOG -- PLANO DE IMPLEMENTACAO

### 6.1 Visao Geral das Fases

```
ROADMAP DE IMPLEMENTACAO
========================

    Fase 1          Fase 2            Fase 3           Fase 4          Fase 5
  Fundacao        Ingestao          Transformacao    Consumo &        Escala &
  & Infra         & Bronze          & Gold           Inteligencia     Otimizacao
  |---------|-----------|-------------|-------------|-------------|
  Sem 1-2       Sem 3-4           Sem 5-6          Sem 7-8         Sem 9-10

  - GCP Setup    - PySpark jobs    - Dataform        - Dashboards   - Performance
  - Terraform    - GCS triggers    - Star Schema     - Alertas      - Backfill hist
  - Buckets      - CSV pipeline    - KPIs            - Notificacoes - Doc & treino
  - BigQuery     - CDC Postgres    - Assertions      - Self-service - Expansao
  - CI/CD base   - Bronze layer    - Silver/Gold     - Monitoring   - Otimizacao

  MVP: Fase 1-3 (6 semanas)
  Completo: Fase 1-5 (10 semanas)
```

### 6.2 Product Backlog Detalhado

---

#### FASE 1: FUNDACAO E INFRAESTRUTURA (Semanas 1-2)

| ID | Tarefa | Descricao | Prioridade | Estimativa | Dependencias |
|----|--------|-----------|------------|------------|--------------|
| F1.1 | Criacao do projeto GCP | Criar projeto GCP, habilitar APIs (BigQuery, Dataproc, Dataform, Cloud Functions, Cloud Build, Datastream, Cloud Workflows, Secret Manager, Artifact Registry), definir billing alerts | CRITICA | 0.5 dia | Nenhuma |
| F1.2 | Configuracao IAM e Service Accounts | Criar service accounts dedicadas: `sa-dataproc-runner`, `sa-dataform-executor`, `sa-cloud-function`, `sa-datastream`. Aplicar principio least-privilege. Configurar Workload Identity Federation | CRITICA | 1 dia | F1.1 |
| F1.3 | Configuracao de rede (VPC) | Criar VPC com subnet na regiao `southamerica-east1`. Configurar Private Google Access para acesso a servicos GCP sem IP publico. Regras de firewall para Dataproc Serverless | CRITICA | 0.5 dia | F1.1 |
| F1.4 | Setup Terraform (IaC) | Estruturar modulos Terraform para GCS, BigQuery, Dataproc, IAM. Configurar backend remoto (GCS bucket para state). Criar ambientes dev/staging/prod | ALTA | 2 dias | F1.1, F1.2 |
| F1.5 | Provisionar buckets GCS | Criar buckets: `case_ficticio-landing` (landing zone), `case_ficticio-datalake` (bronze/silver layers), `case_ficticio-temp` (Spark temp), `case_ficticio-artifacts` (jars, scripts). Configurar lifecycle policies e versionamento | CRITICA | 0.5 dia | F1.4 |
| F1.6 | Provisionar datasets BigQuery | Criar datasets: `case_ficticio_raw_pg`, `case_ficticio_bronze`, `case_ficticio_silver`, `case_ficticio_gold`, `case_ficticio_metrics`. Configurar regiao, default expiration, labels | CRITICA | 0.5 dia | F1.4 |
| F1.7 | Setup repositorio GitHub | Criar repositorio `case_ficticio-data-platform`. Configurar branch protection (main, develop). Definir PR templates, CODEOWNERS. Inicializar estrutura de pastas | ALTA | 0.5 dia | Nenhuma |
| F1.8 | Setup CI/CD (Cloud Build) | Configurar Cloud Build triggers: PR para CI (lint, test, compile), merge para CD (deploy). Integrar com GitHub. Criar `cloudbuild.yaml` com steps de validacao | ALTA | 1.5 dias | F1.7, F1.1 |
| F1.9 | Setup Artifact Registry | Criar repositorio Docker em `southamerica-east1` para imagens de containers PySpark customizados | MEDIA | 0.5 dia | F1.1 |
| F1.10 | Documentacao de arquitetura | Criar ADR (Architecture Decision Records) para decisoes chave: escolha de Dataproc Serverless vs Managed, Dataform vs dbt, Cloud Workflows vs Composer, Star Schema vs Data Vault | MEDIA | 1 dia | F1.1 a F1.9 |

**Entregaveis Fase 1:**
- Projeto GCP configurado com todas as APIs habilitadas
- Infraestrutura provisionada via Terraform (buckets, datasets, IAM, rede)
- Pipeline CI/CD funcional (push to GitHub -> lint + test + compile)
- Repositorio GitHub estruturado com padrao do projeto

---

#### FASE 2: INGESTAO E CAMADA BRONZE (Semanas 3-4)

| ID | Tarefa | Descricao | Prioridade | Estimativa | Dependencias |
|----|--------|-----------|------------|------------|--------------|
| F2.1 | Script Python de upload (unidades) | Desenvolver script Python que cada unidade executara para enviar CSVs para GCS. Inclui: autenticacao via service account, validacao local basica, upload com retry, geracao de `_metadata.json` com checksum MD5 | CRITICA | 1.5 dias | F1.5 |
| F2.2 | PySpark: Schema Registry | Criar modulo `schema_registry.py` com schemas StructType para PEDIDO.CSV e ITEM_PEDIDO.CSV. Centralizar regras de tipagem, nullable, e valores default | CRITICA | 0.5 dia | F1.7 |
| F2.3 | PySpark: Job de ingestao CSV | Desenvolver `csv_ingestion_job.py`: ler CSVs do landing zone, aplicar schema enforcement, type casting, deduplicacao, padronizacao de encoding. Escrever em Parquet (GCS bronze) e BigQuery (bronze dataset) via Spark BigQuery Connector (metodo direct) | CRITICA | 3 dias | F2.2, F1.5, F1.6 |
| F2.4 | PySpark: Validacao de qualidade | Desenvolver `data_quality_job.py`: checks de completude (% nulls), unicidade (chaves primarias), validade (ranges de valores, datas futuras), integridade referencial (id_pedido entre pedido e item). Gerar relatorio de qualidade | ALTA | 2 dias | F2.3 |
| F2.5 | Mecanismo de quarentena | Implementar logica para mover arquivos/registros que falham na validacao para `_quarantine/` com relatorio JSON detalhando os erros. Cloud Function para notificar equipe via email | ALTA | 1 dia | F2.4 |
| F2.6 | Cloud Function: Event trigger | Desenvolver Cloud Function (2nd gen) que detecta upload no bucket landing (`google.cloud.storage.object.v1.finalized`) e inicia o Cloud Workflow. Filtrar por padrao de nome de arquivo para evitar triggers em metadata files | CRITICA | 1 dia | F1.5, F2.3 |
| F2.7 | Cloud Workflows: Pipeline diario | Criar workflow YAML que orquestra: (1) validar arquivo, (2) submeter job PySpark no Dataproc Serverless, (3) aguardar conclusao, (4) registrar metricas, (5) notificar sucesso/falha. Incluir retry policy e error handling | CRITICA | 1.5 dias | F2.6, F2.3 |
| F2.8 | Datastream: CDC PostgreSQL | Configurar Datastream para replicar tabelas PRODUTO, UNIDADE, ESTADO, PAIS do PostgreSQL para GCS (raw) e BigQuery (raw_pg). Modo Merge, staleness 1 hora. Configurar replication slot e publication no PostgreSQL | ALTA | 2 dias | F1.1, F1.5, F1.6 |
| F2.9 | Testes unitarios PySpark | Escrever testes unitarios para jobs PySpark usando pytest + pyspark.testing. Cobrir cenarios: CSV valido, CSV com erros, CSV vazio, duplicatas, tipos incorretos. Minimo 80% coverage | ALTA | 2 dias | F2.3, F2.4 |
| F2.10 | Batch processing de coleta | Implementar logica de espera inteligente: aguardar recebimento de todos os 50 CSVs (ou timeout de 2 horas) antes de iniciar processamento batch. Evitar 50 jobs Spark separados -- consolidar em unico job com wildcard path | ALTA | 1 dia | F2.6, F2.7 |

**Entregaveis Fase 2:**
- Pipeline de ingestao funcional: CSV upload -> GCS -> PySpark -> Bronze (Parquet + BigQuery)
- CDC do PostgreSQL operacional via Datastream
- Event-driven trigger com Cloud Functions + Cloud Workflows
- Testes unitarios com cobertura >= 80%
- Mecanismo de quarentena e notificacao de erros

---

#### FASE 3: TRANSFORMACAO E CAMADA GOLD (Semanas 5-6)

| ID | Tarefa | Descricao | Prioridade | Estimativa | Dependencias |
|----|--------|-----------|------------|------------|--------------|
| F3.1 | Setup Dataform workspace | Criar repositorio Dataform no GCP vinculado ao GitHub. Configurar `dataform.json` com default schema, assertion schema, variaveis de ambiente. Configurar custom service account (strict act-as mode) | CRITICA | 0.5 dia | F1.6, F1.8 |
| F3.2 | Modelos staging (Dataform) | Criar modelos SQLX de staging: `stg_pedidos`, `stg_itens_pedido`, `stg_produtos`, `stg_unidades`, `stg_estados`, `stg_paises`. Aplicar renomeacao padronizada, casting final, filtros de qualidade | CRITICA | 1.5 dias | F3.1, F2.3, F2.8 |
| F3.3 | Modelos intermediate (Dataform) | Criar modelos de enriquecimento: `int_vendas_enriched` (join pedidos + itens + produto + unidade + geografia), `int_produto_unidade` (cross-reference). Materializar como views para Silver | ALTA | 1 dia | F3.2 |
| F3.4 | Dimensoes Gold (Dataform) | Criar dimensoes do Star Schema: `dim_tempo` (date spine), `dim_produto` (SCD Type 2), `dim_unidade` (SCD Type 2), `dim_geografia` (hierarquia estado-pais). Incluir surrogate keys | CRITICA | 2 dias | F3.3 |
| F3.5 | Fatos Gold (Dataform) | Criar tabelas de fato: `fato_vendas` (granularidade pedido, incremental), `fato_itens_venda` (granularidade item). Configurar particionamento por `data_pedido`, clusterizacao por `id_unidade`, `tipo_pedido` | CRITICA | 2 dias | F3.4 |
| F3.6 | Modelos de KPI (Dataform) | Criar tabelas agregadas: `kpi_operacional` (metricas por unidade/dia), `vendas_diarias_unidade`, `vendas_produto_periodo`, `ranking_produtos`. Estes serao a base dos dashboards | ALTA | 1.5 dias | F3.5 |
| F3.7 | Modelo de alertas (Dataform) | Criar `alerta_anomalia`: deteccao de queda de vendas, pico de cancelamentos, unidades sem dados. Baseado em media movel 7 dias com thresholds configuraveis | ALTA | 1 dia | F3.6 |
| F3.8 | Assertions e testes (Dataform) | Configurar assertions em todos os modelos: uniqueKey, nonNull, referential integrity, row count checks. Assertions de negocio: vlr_pedido > 0, datas nao futuras, status validos | CRITICA | 1 dia | F3.2 a F3.7 |
| F3.9 | Dataform scheduled execution | Configurar execucao automatica do Dataform: trigger via API REST apos conclusao do pipeline PySpark (chamado pelo Cloud Workflow). Configurar tags para execucao seletiva (staging -> gold) | ALTA | 0.5 dia | F3.1, F2.7 |
| F3.10 | Teste end-to-end do pipeline | Executar pipeline completo com dados de teste: upload CSV -> GCS -> PySpark (Bronze) -> BigQuery (Silver) -> Dataform (Gold). Validar dados em cada camada. Medir latencia total | CRITICA | 1 dia | Todos anteriores |

**Entregaveis Fase 3:**
- Dataform operacional com modelos staging -> intermediate -> gold
- Star Schema completo em BigQuery (dimensoes + fatos)
- KPIs e alertas automaticos calculados diariamente
- Assertions validando qualidade em cada camada
- Pipeline end-to-end funcional e testado (MVP alcancado)

---

#### FASE 4: CONSUMO E INTELIGENCIA (Semanas 7-8)

| ID | Tarefa | Descricao | Prioridade | Estimativa | Dependencias |
|----|--------|-----------|------------|------------|--------------|
| F4.1 | Dashboard executivo (Looker Studio) | Criar dashboard para Joao Silva: receita total, tendencia de crescimento, comparativo de unidades, performance por canal (online vs fisico), mapa geografico de vendas | ALTA | 2 dias | F3.5, F3.6 |
| F4.2 | Dashboard operacional (Looker Studio) | Criar dashboard para Ricardo Martins: KPIs diarios por unidade, taxa de cancelamento, ticket medio, ranking de produtos, alertas de anomalia | ALTA | 2 dias | F3.6, F3.7 |
| F4.3 | Dashboard de monitoramento (Looker Studio) | Criar dashboard para Wilson Luiz: status do pipeline, latencia de ingestao, volume de dados processados, erros e quarentena, health checks | MEDIA | 1 dia | F2.7, F3.10 |
| F4.4 | Sistema de alertas automaticos | Implementar Cloud Function que consulta `alerta_anomalia` e envia notificacoes via email (SendGrid) e/ou Slack webhook. Schedule via Cloud Scheduler | ALTA | 1.5 dias | F3.7 |
| F4.5 | Monitoramento de pipeline | Configurar Cloud Monitoring com alertas para: falha de job PySpark, Dataform execution failure, ausencia de arquivos de unidades, latencia acima do SLA. Integrar com Cloud Logging | ALTA | 1.5 dias | F2.7, F3.9 |
| F4.6 | BigQuery BI Engine | Habilitar BI Engine no BigQuery para acelerar queries do Looker Studio na camada Gold. Configurar reservas de slots para horarios de pico de consumo | MEDIA | 0.5 dia | F3.5 |
| F4.7 | Controle de acesso por persona | Configurar IAM no BigQuery: Joao/Ricardo -> leitura em gold/metrics, Wilson -> leitura em todos os datasets + admin pipeline, Engenharia -> full access. Implementar column-level security se necessario | MEDIA | 1 dia | F1.2, F3.5 |
| F4.8 | Documentacao de dados (Data Catalog) | Configurar Google Data Catalog com metadados dos datasets: descricao de tabelas e colunas, owners, classificacao de sensibilidade, linhagem de dados. Integrar com tags do Dataform | MEDIA | 1 dia | F3.5 |

**Entregaveis Fase 4:**
- Dashboards operacionais para CEO, COO, e TI
- Alertas automaticos por email/Slack
- Monitoramento completo do pipeline com alertas de falha
- Controle de acesso granular por persona
- Catalogo de dados documentado

---

#### FASE 5: ESCALA E OTIMIZACAO (Semanas 9-10)

| ID | Tarefa | Descricao | Prioridade | Estimativa | Dependencias |
|----|--------|-----------|------------|------------|--------------|
| F5.1 | Backfill de dados historicos | Desenvolver script de backfill para carregar dados historicos (planilhas Excel existentes) nas camadas Bronze/Silver/Gold. PySpark job dedicado com tratamento de formatos legados | ALTA | 2 dias | F3.10 |
| F5.2 | Otimizacao de performance BigQuery | Analisar query patterns e otimizar: revisao de particionamento/clusterizacao, materialized views para queries frequentes, otimizacao de modelos Dataform (incremental vs full refresh) | MEDIA | 1.5 dias | F4.1, F4.2 |
| F5.3 | Otimizacao de custos | Revisar custos GCP: Dataproc Serverless (right-sizing de executors), BigQuery (flat-rate vs on-demand), GCS (lifecycle policies), Datastream (staleness optimization). Implementar billing alerts e budgets | MEDIA | 1 dia | Todos |
| F5.4 | Testes de carga e stress | Simular cenario de expansao: 100 unidades, 200 unidades. Medir impacto em latencia, custo, e performance do pipeline. Identificar gargalos e planejar scaling strategy | MEDIA | 1.5 dias | F3.10 |
| F5.5 | Runbook operacional | Documentar procedimentos operacionais: como investigar falhas, como executar backfill, como adicionar nova unidade, como alterar schema de CSV. Incluir troubleshooting guide | ALTA | 1.5 dias | Todos |
| F5.6 | Treinamento de equipe | Treinar equipe de Ricardo (operacoes) nos dashboards e alertas. Treinar Wilson (TI) no monitoramento e operacao do pipeline. Gravar videos de treinamento | ALTA | 2 dias | F4.1 a F4.5 |
| F5.7 | Preparacao para expansao geografica | Documentar processo para onboarding de novas unidades em novos estados: configuracao do script de upload, validacao de conectividade, testes de integracao. Criar checklist automatizado | MEDIA | 1 dia | F2.1 |
| F5.8 | Estrategia de DR e backup | Configurar cross-region replication para bucket landing. BigQuery dataset snapshots semanais. Documentar RTO/RPO targets e procedimentos de recuperacao | MEDIA | 1 dia | F1.5, F1.6 |

**Entregaveis Fase 5:**
- Dados historicos carregados e integrados
- Performance e custos otimizados
- Documentacao operacional completa (runbooks)
- Equipe treinada e autonoma
- Plataforma preparada para expansao geografica

---

### 6.3 Resumo do Backlog por Prioridade

| Prioridade | Quantidade | Exemplos |
|------------|-----------|----------|
| CRITICA | 16 tarefas | Setup GCP, PySpark ingestion, Dataform Gold, Pipeline E2E |
| ALTA | 18 tarefas | CI/CD, CDC PostgreSQL, Dashboards, Alertas, Treinamento |
| MEDIA | 12 tarefas | Artifact Registry, BI Engine, Data Catalog, DR |

### 6.4 Marcos (Milestones)

| Marco | Semana | Criterio de Sucesso |
|-------|--------|---------------------|
| **M1: Infra Ready** | Fim Sem 2 | Projeto GCP provisionado, CI/CD funcional, Terraform aplicado |
| **M2: Pipeline Operacional** | Fim Sem 4 | 1 CSV processado end-to-end: GCS -> PySpark -> Bronze -> BigQuery |
| **M3: MVP (Minimum Viable Platform)** | Fim Sem 6 | Pipeline completo com Dataform Gold, Star Schema populado, dados de 1 semana |
| **M4: Plataforma Completa** | Fim Sem 8 | Dashboards, alertas, monitoramento, controle de acesso |
| **M5: Production Ready** | Fim Sem 10 | Historico carregado, equipe treinada, documentacao completa, DR configurado |

---

## PARTE 7: AVALIACAO DE RISCOS

### 7.1 Matriz de Riscos

| Risco | Impacto | Probabilidade | Mitigacao |
|-------|---------|---------------|-----------|
| Conectividade das unidades com GCS (upload falha) | ALTO | MEDIO | Retry automatico no script Python com backoff exponencial. Fila local de arquivos pendentes. Alerta se unidade nao envia por 24h |
| Formato CSV inconsistente entre unidades | ALTO | ALTO | Schema enforcement rigido no PySpark. Quarentena com notificacao. Guia de formato para unidades. Validacao no script de upload |
| Performance do Dataproc Serverless com cold start | MEDIO | MEDIO | Aceitar 2-3 min de cold start para batch diario (aceitavel). Monitorar. Se critico, considerar Dataproc Managed com autoscaling |
| Custo GCP acima do orcamento | MEDIO | MEDIO | Billing alerts progressivos (50%, 75%, 90%). BigQuery on-demand com quotas. Lifecycle policies agressivas no GCS. Revisao mensal de custos |
| Mudanca de schema no PostgreSQL sem aviso | ALTO | BAIXO | Datastream detecta automaticamente. Alertas de schema drift. Versionamento SCD Type 2 no Silver. Comunicacao com equipe de TI |
| Falha no pipeline sem deteccao | ALTO | BAIXO | Cloud Monitoring com alertas de falha. Health check diario (verificar se Gold foi atualizado). Dashboard de monitoramento para Wilson |
| Resistencia a mudanca da equipe operacional | MEDIO | MEDIO | Treinamento hands-on. Demonstrar economia de tempo. Manter acesso a planilhas durante transicao. Feedback loop semanal |

### 7.2 Planos de Contingencia

| Trigger | Resposta |
|---------|----------|
| Se Dataproc Serverless tiver latencia inaceitavel (> 30 min) | Migrar para Dataproc Managed com cluster pre-aquecido em horario de ingestao |
| Se Datastream apresentar lag > 4 horas | Fallback para PySpark JDBC job agendado (batch diario) para tabelas de referencia |
| Se custo BigQuery exceder budget | Migrar de on-demand para Editions (flat-rate) com reservas. Revisar queries nao otimizadas |
| Se volume de dados crescer 10x com expansao | Implementar Delta Lake ou Apache Iceberg no GCS para ACID transactions e time travel. Considerar BigLake para unificar storage |

---

## PARTE 8: ESTIMATIVA DE CUSTOS MENSAIS (GCP)

### 8.1 Estimativa para 50 Unidades

| Servico | Uso Estimado | Custo Mensal (USD) |
|---------|-------------|-------------------|
| GCS (Storage) | ~50 GB total (landing + lake) | ~$1-2 |
| BigQuery (Storage) | ~20 GB (silver + gold) | ~$0.40 |
| BigQuery (Queries) | ~2 TB scanned/mes (on-demand) | ~$10 |
| Dataproc Serverless | ~1h processamento/dia x 30 dias | ~$30-50 |
| Dataform | Incluido (nativo BigQuery) | $0 |
| Cloud Functions | ~1500 invocacoes/mes | ~$0 (free tier) |
| Cloud Workflows | ~30 execucoes/mes | ~$0 (free tier) |
| Datastream | ~5 GB CDC/mes | ~$5-10 |
| Cloud Build | ~60 builds/mes | ~$0 (free tier 120 min) |
| Cloud Monitoring | Alertas basicos | ~$0 (free tier) |
| Looker Studio | Uso basico | $0 (free) |
| **TOTAL ESTIMADO** | | **~$50-75/mes** |

**Nota:** Estimativa conservadora para 50 unidades com ~100 CSVs/dia de tamanho moderado (~1-5 MB cada). Custo escala sub-linearmente com numero de unidades gracas a batch processing consolidado.

---

## PARTE 9: CONSIDERACOES FINAIS

### 9.1 Principios de Design Aplicados

1. **Event-driven over scheduled:** O pipeline reage ao upload de dados (evento) em vez de rodar em horario fixo. Isso garante que dados sao processados assim que disponiveis, sem desperdicio de recursos em execucoes vazias.

2. **Serverless-first:** Todos os componentes de processamento sao serverless (Dataproc Serverless, Cloud Functions, Cloud Workflows, Dataform, BigQuery). Zero gerenciamento de infraestrutura, pagamento por uso.

3. **Imutabilidade de dados:** A camada Raw preserva dados originais indefinidamente. Qualquer transformacao cria novos dados, nunca altera os originais. Permite reprocessamento completo se necessario.

4. **Separation of concerns:** Ingestao (PySpark) separada de transformacao (Dataform) separada de consumo (Looker Studio). Cada camada tem responsabilidade unica e pode evoluir independentemente.

5. **Infrastructure as Code:** Toda infraestrutura definida em Terraform, versionada em Git, aplicada via CI/CD. Ambientes dev/staging/prod identicos. Disaster recovery por re-apply.

6. **Data Quality as first-class citizen:** Validacao em multiplas camadas (PySpark na ingestao, assertions no Dataform, monitoramento no Gold). Quarentena para dados invalidos com notificacao automatica.

### 9.2 Escalabilidade para Expansao Nacional

A arquitetura proposta suporta a expansao da Case Fictício - Teste para novos estados sem mudancas estruturais:

- **Novas unidades:** Basta distribuir o script Python de upload e registrar no sistema. O pipeline processa qualquer numero de CSVs no mesmo batch.
- **Novos estados:** Tabelas de referencia (ESTADO, UNIDADE) sao atualizadas automaticamente via CDC do PostgreSQL. Dimensao geografia se atualiza no proximo refresh do Dataform.
- **Volume 10x:** Dataproc Serverless escala automaticamente. BigQuery e ilimitado em storage e processamento. GCS e infinito.
- **Novos dashboards:** A camada Gold e consumivel por qualquer ferramenta de BI. Novos modelos Dataform podem ser adicionados sem impactar os existentes.

### 9.3 Proximo Passo Imediato

Apos aprovacao deste plano, a recomendacao e iniciar pela **Fase 1 (Fundacao)** imediatamente, com foco em:

1. Criar o projeto GCP e habilitar APIs
2. Configurar o repositorio GitHub e CI/CD basico
3. Provisionar buckets GCS e datasets BigQuery via Terraform
4. Desenvolver o primeiro job PySpark (`csv_ingestion_job.py`) em paralelo

O MVP (pipeline funcional end-to-end) pode ser demonstrado em 6 semanas.

---

**Documento elaborado com base em analise tecnica do cenario Case Fictício - Teste e melhores praticas de engenharia de dados na Google Cloud Platform.**
