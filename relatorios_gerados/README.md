# Relatórios de Análise de Crédito (Duplicata Escritural)

Este diretório contém os relatórios executivos gerados automaticamente pelo pipeline de Inteligência Artificial. O foco da análise é a avaliação de risco para operações de antecipação de recebíveis (Duplicata Escritural).

## ⚙️ Parâmetros de Configuração da IA

Para garantir consistência, objetividade e baixo risco de alucinação, foram utilizados os seguintes parâmetros no modelo generativo:

| Parâmetro | Valor Configurado |
| :--- | :--- |
| **Modelo** | `models/gemini-2.0-flash-lite` |
| **Temperatura** | `0.3` (Baixa aleatoriedade, foco em dados) |
| **Max Tokens** | `1000` |
| **Formato de Saída** | HTML Puro (sem CSS/Markdown) |

---

## 🧠 Engenharia de Prompt

A estrutura de comunicação com o modelo foi dividida em **Persona (System)** e **Tarefa (User)** conforme abaixo:

### 1. Mensagem de Sistema (Persona)
> "Você é um analista de crédito sênior, especializado em avaliações de risco para operações de Duplicata Escritural (antecipação de recebíveis)."

### 2. Prompt do Usuário (Tarefa e Regras)

**Instrução Principal:**
"Sua tarefa é analisar os dados JSON fornecidos e gerar um relatório executivo para apoiar a decisão de crédito."

**Regras de Formatação Rígidas:**
1.  **SAÍDA:** Apenas código HTML limpo.
2.  NÃO use crases (\`\`\`html) ou blocos de código markdown. Retorne o HTML puro.
3.  NÃO use CSS ou tags `<style>`.
4.  Tags permitidas: `<h1>`, `<h2>`, `<h3>`, `<p>`, `<ul>`, `<li>`, `<strong>`, `<em>`.
5.  NÃO invente valores. Use estritamente os números e estatísticas fornecidos no JSON. Se um dado faltar, diga "Não disponível".
6.  **Unidades:** Liquidez Corrente (sem unidade), Margem Líquida (%), Fluxo de Caixa Operacional (milhões de USD) e EBITDA (milhões de USD).

**Template de Estrutura do Relatório:**

```html
<h1>Análise de Crédito: [Nome da Empresa]</h1>
<p><em>Setor: [Nome do Setor] | Análise baseada em [N] anos de histórico.</em></p>

<h2>1. Resumo Executivo</h2>
<p>[Breve parágrafo sintetizando se a empresa está apta ou não para operar duplicatas, destacando o nível de risco (Baixo, Médio, Alto).]</p>

<h2>2. Liquidez e Solvência (Capacidade de Pagamento)</h2>
<ul>
    <li><strong>Liquidez Corrente Atual:</strong> [Valor] (Média Histórica: [Valor])</li>
    <li><strong>Análise:</strong> [Compare a liquidez atual com a média histórica e, se disponível no JSON, com a Mediana/Quartis do setor. A empresa tem folga para pagar curto prazo?]</li>
</ul>

<h2>3. Geração de Caixa (Operação)</h2>
<p>[Analise o Fluxo de Caixa Operacional (CFO). É positivo ou negativo? A tendência é de queima ou geração de caixa? Isso é crucial para saber se a duplicata tem lastro real.]</p>

<h2>4. Performance Relativa e Setorial</h2>
<p>[Se houver dados de "mediana_setor" ou "quartis" no JSON, compare a empresa com o setor. Ela é um "Outperformer" ou "Underperformer"? Se não houver dados do setor, analise apenas a volatilidade histórica da própria empresa.]</p>

<h2>5. Riscos e Recomendações (Duplicata Escritural)</h2>
<ul>
    <li><strong>Riscos Identificados:</strong> [Liste riscos pontuais ex: Queda de liquidez, Margem decrescente, Caixa negativo].</li>
    <li><strong>Parecer Final:</strong> [Recomendação clara: Aprovado / Aprovado com Travas / Reprovado].</li>
    <li><strong>Sugestão Operacional:</strong> [Ex: "Solicitar coobrigação", "Trava de domicílio bancário", "Operar apenas com sacados listados"].</li>
</ul>

<!-- DADOS DE ENTRADA -->
Analise os dados abaixo:
[JSON DINÂMICO INSERIDO AQUI]