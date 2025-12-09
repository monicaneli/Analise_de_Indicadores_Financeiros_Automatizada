# MVP - Análise de Indicadores Financeiros Automatizada

**MVP - Análise de Crédito Inteligente para Duplicata Escritural**

![Status](https://img.shields.io/badge/Status-MVP%20Concluído-success)
![Python](https://img.shields.io/badge/Backend-FastAPI-blue)
![IA](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-orange)
![Automation](https://img.shields.io/badge/Workflow-n8n-ff69b4)

## 📄 Introdução e Contexto

O mercado de crédito brasileiro passa por uma transformação estrutural com a consolidação das **Duplicatas Escriturais** entre 2025 e 2026. Esse novo ambiente regulatório fortalece a segurança jurídica e a transparência, permitindo que recebíveis sejam registrados, validados e negociados com maior agilidade e rastreabilidade.

Com essa evolução, operações lastreadas em recebíveis — como antecipação de duplicatas e linhas de capital de giro — passam a exigir avaliações cada vez mais precisas sobre a saúde financeira do cedente. Empresas com fragilidades estruturais de liquidez, geração de caixa ou solvência ampliam significativamente o risco operacional e a probabilidade de inadimplência comercial, afetando diretamente a performance da duplicata cedida.

Nesse contexto, este projeto propõe um **MVP (Produto Mínimo Viável)** de um sistema automatizado de análise financeira, combinando:

*   **Engenharia de Dados:** Estatísticas descritivas, regras determinísticas e comparação setorial (Benchmarking).
*   **Inteligência Artificial Generativa:** Interpretação narrativa, recomendações estratégicas e contextualização de risco.

O objetivo é traduzir indicadores financeiros complexos em *insights* acionáveis, suportando decisões relacionadas à concessão de crédito. O sistema integra histórico temporal, benchmarking setorial e métricas-chave de desempenho operacional.

---

## 🎯 Objetivo do Projeto

Em operações com duplicata escritural, a análise de risco concentra-se na capacidade financeira do sacado/cedente, especialmente sua liquidez, geração de caixa e estabilidade operacional.

Este MVP busca validar a hipótese de que é possível produzir análises de crédito com **profundidade equivalente à de um especialista humano**, mas com **escala e velocidade de processamento** compatíveis com o ambiente digital.

O pipeline foi projetado para:
1.  **Extração e Processamento:** Obtenção de base de dados com os indicadores históricos (Liquidez Corrente, FCO, EBITDA, Margens).
2.  **Aplicação de Regras:** Utilizar estatística (Medianas, Quartis, IQR) para identificar desvios de performance.
3.  **Diagnóstico:** Gerar classificações objetivas (ex: Risco de Liquidez, Deterioração Operacional).
4.  **Relatório Inteligente:** Produzir um parecer narrativo via LLM (Large Language Model) que vai além do "Aprovado/Reprovado", oferecendo sugestões de mitigação de risco (ex: travas, coobrigação).

---

## 🛠️ Arquitetura e Tecnologias

O projeto opera em um fluxo automatizado e modular:

*   **Linguagem & Análise:** Python (Pandas, NumPy).
*   **Backend:** FastAPI (Hospedado no Render).
*   **Orquestração:** n8n (Workflow Automation).
*   **Inteligência Artificial:** Google Gemini 2.0 Flash Lite (via Google AI Studio).
*   **Frontend (Teste):** n8n Form Trigger.

---

## 🚀 Etapas de Desenvolvimento

O projeto foi construído seguindo um rigoroso processo de validação de dados:

### 1. Análise Exploratória dos Dados (EDA)
Investigação do comportamento histórico de 12 empresas em 8 setores. Definição de estatísticas descritivas e detecção de *outliers* relevantes para o risco de crédito.
- *Ferramenta:* Jupyter Notebook (disponível aqui e no [Kaggle](https://www.kaggle.com/code/monicaneli/ead-para-an-lise-de-cr-dito)).

### 2. Validação das Regras de Negócio
Aplicação piloto das regras em empresas selecionadas para verificar a aderência dos critérios de risco (ex: Liquidez < Mediana do Setor = Alerta).
- *Ferramenta:* Jupyter Notebook.

### 3. Desenvolvimento do Backend (API)
Implementação de uma API robusta em **Python (FastAPI)**. Esta API recebe a solicitação, acessa a base de dados, calcula todas as estatísticas (empresariais e setoriais) e retorna um JSON estruturado com o "Dossiê Financeiro" da empresa.

### 4. Pipeline de Automação (n8n)
Criação do fluxo ponta a ponta:
1.  **Entrada:** Formulário web para seleção da empresa.
2.  **Processamento:** Chamada à API Python para cálculos.
3.  **Inteligência:** Envio dos dados calculados para o modelo **Gemini 2.0 Flash**.
4.  **Saída:** Geração de relatório HTML, commit automático no GitHub e entrega do link de visualização.

---

## 🧪 Como Testar (Live Demo)

O sistema está disponível para testes públicos. O fluxo simula a chegada de uma nova solicitação de análise de crédito.

1.  Acesse o formulário de teste: **[LINK PARA O FORMULÁRIO AQUI](https://monicaneli.app.n8n.cloud/form/ed8f7bd5-bae0-4ed7-9e0c-66611ac4f51e)**
2.  Selecione uma empresa da lista.
3.  Aguarde o processamento (o sistema consultará o histórico, aplicará as regras e gerará o texto via IA).
4.  Visualize o Relatório Executivo final gerado.


<div align="center">
	<img src="https://github.com/monicaneli/Analise_de_Indicadores_Financeiros_Automatizada/blob/87fa79d243f52eb5e8dc5bac4439bb33d4cb5a06/images/formulario_n8n.JPG" alt="Demo" width="18%" style="display:inline-block;"/>
  	<img src="https://github.com/monicaneli/Analise_de_Indicadores_Financeiros_Automatizada/blob/87fa79d243f52eb5e8dc5bac4439bb33d4cb5a06/images/N8N%20Workflow.JPG" alt="Workflow no N8N" width="80%" style="display:inline-block; margin-right:10px;"/>
</div>

<p align="center"><i>Workflow no N8N encapsulando os processos da demo</i></p>

---

## 📊 Indicadores Analisados

O sistema avalia quatro pilares fundamentais para a segurança da Duplicata Escritural:

| Pilar | Métricas | O que buscamos? |
| :--- | :--- | :--- |
| **Liquidez** | Liquidez Corrente | Capacidade de honrar dívidas de curto prazo. |
| **Geração de Caixa** | Fluxo de Caixa Operacional (CFO) | A operação para de pé sozinha ou queima caixa? |
| **Rentabilidade** | Margem Líquida, EBITDA | Eficiência operacional e "colchão" para crises. |
| **Comparativo** | Mediana Setorial, Quartis | A empresa performa acima ou abaixo de seus pares? |

---
<img src="https://github.com/monicaneli/Analise_de_Indicadores_Financeiros_Automatizada/blob/87fa79d243f52eb5e8dc5bac4439bb33d4cb5a06/images/Empesa_AAPL_Setor_Tecnologia_da_Informacao.png" alt="Análise Empresa AAPL" width="100%" style="display:block;"/>


## ⚠️ Disclaimer

*Este é um projeto educacional e de demonstração técnica (MVP). As análises geradas pela IA são baseadas em dados históricos limitados e regras pré-definidas, não devendo ser utilizadas como única fonte para decisões reais de investimento ou concessão de crédito sem a devida diligência humana.*
