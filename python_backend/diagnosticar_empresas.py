# Funções para classificação de risco
import pandas as pd
import numpy as np
from scipy.stats import skew
from sklearn.linear_model import LinearRegression
import requests

# Dicionário para títulos
titulos_graficos = {
    'Ano': 'Evolução Anual',
    'Empresa': 'Distribuição por Empresa',
    'Categoria': 'Distribuição por Setor Econômico',
    'EBITDA': 'EBITDA (milhões de USD)',
    'Fluxo_Caixa_Operacional': 'Fluxo de Caixa Operacional (milhões de USD)',
    'Liquidez_Corrente': 'Liquidez Corrente',
    'Margem_Liquida': 'Margem de Lucro Líquida (%)'
}

unidades_dict = {
    'Liquidez_Corrente': '',
    'Margem_Liquida': '%',
    'Fluxo_Caixa_Operacional': 'milhões de USD',
    'EBITDA': 'milhões de USD'
}


def obter_base_de_dados():
    url = "https://raw.githubusercontent.com/monicaneli/Analise_de_Indicadores_Financeiros_Automatizada/refs/heads/main/data/some_financial_statements_companies_2009_2023.csv"

    df = pd.read_csv(url)

    # Normaliza nome das colunas
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )

    return df

def gerar_frase_tendencia(resultado):
    """
    Gera frase descritiva automática com base no resultado da função analisar_tendencia_setor().
    """

    if "erro" in resultado:
        return f"Não foi possível analisar a tendência: {resultado['erro']}"

    empresa = resultado["empresa"]
    setor = resultado["setor"]
    metrica = resultado["metrica"]
    yoy = resultado["yoy_percent"]
    cagr = resultado["cagr_percent"]
    slope = resultado["tendencia_slope"]
    interpretacao = resultado["interpretacao"]
    anos = resultado["anos_analisados"]

    # Nome amigável da métrica
    nome_met = titulos_graficos[metrica]
    unidade = unidades_dict[metrica]
    
    # Parte 1 — introdução
    intro = (f"Na empresa {empresa}, representando o setor de {setor.upper()}, "
                 f"a {nome_met.upper()} apresentou ")

    # Parte 2 — tendência (slope)
    slope_fmt = round(slope, 2)
    
    if slope > 0:
        tendencia_txt = f"tendência de alta (regressão linear = {slope_fmt} {unidade}/ano)"
    elif slope < 0:
        tendencia_txt = f"tendência de queda (regressão linear = {slope_fmt} {unidade}/ano)"
    else:
        tendencia_txt = f"tendência estável (regressão linear = {slope_fmt} {unidade}/ano)"


    # Parte 3 — intensidade via CAGR
    if pd.isna(cagr):
        intensidade = "em ritmo variável"
        cagr_txt = "NA (não aplicável devido a valores negativos ou zero)"
    else:
        if abs(cagr) >= 10:
            intensidade = "de forma acentuada"
        elif abs(cagr) >= 3:
            intensidade = "de forma moderada"
        else:
            intensidade = "de forma leve"
        cagr_txt = f"{cagr:.2f}%"

    # Parte 4 — frase final
    frase = (
        f"{intro}{tendencia_txt} {intensidade} nos últimos {len(anos)} anos "
        f"({anos[0]}–{anos[-1]}). "
        f"O CAGR do período foi de {cagr_txt}, "
        f"e a variação total (YoY acumulado) foi de {yoy:.2f}%."
    )

    return frase



# Para uso com qualquer métrica (Lucro Líquido, Receita, EBITDA…).
def analisar_tendencia_empresa(df, empresa, setor, coluna, anos=3):
    """
    Calcula tendência da métrica para os últimos N anos.
    Métodos: YoY, CAGR e Regressão Linear.
    """
    df_emp = df[df['Empresa'] == empresa].sort_values('Ano')

    # últimos N anos disponíveis
    df_last = df_emp.tail(anos)

    if len(df_last) < 2:
        return "Histórico insuficiente para análise."

    valores = df_last[coluna].values
    anos_vals = df_last['Ano'].values

    # YoY: variação entre primeiros e últimos
    yoy = (valores[-1] - valores[0]) / valores[0]

    # CAGR: Média anual ao longo de vários anos  
    if (valores > 0).all():
        n = len(df_last) - 1
        cagr = (valores[-1] / valores[0]) ** (1/n) - 1
    else:
        cagr = pd.NA #CAGR não aplicável devido a valores negativos ou zero

    # Regressão linear (tendência estatística) / Séries voláteis — identifica tendência real
    X = anos_vals.reshape(-1, 1)
    y = valores
    model = LinearRegression().fit(X, y)
    slope = model.coef_[0]  # inclinação

    return {
        "empresa": empresa,
        "setor": setor,
        "metrica": coluna,
        "anos_analisados": anos_vals.tolist(),
        "valores": valores.tolist(),
        "yoy_percent": yoy * 100,
        "cagr_percent": float(cagr * 100) if cagr is not pd.NA else None,
        "tendencia_slope": slope,
        "interpretacao": (
            "Queda" if slope < 0 else "Alta"
        )
    }


def calcular_stats(df, metrica="Liquidez_Corrente"):
    x = df[metrica]
    empresa = df["Empresa"].iloc[0]
    setor = df["Categoria"].iloc[0]

    tendencias = analisar_tendencia_empresa(df, empresa=empresa, setor=setor, coluna=metrica, anos=3)
    resumo_tendencia = gerar_frase_tendencia(tendencias)
    
    return pd.Series({
        "Min": min(x),
        "Max": max(x),
        "Mean": np.mean(x),
        "Median": np.median(x),
        "Std": np.std(x),
        "Q1": np.quantile(x, 0.25),
        "Q3": np.quantile(x, 0.75),
        "IQR": np.quantile(x, 0.75) - np.quantile(x, 0.25),
        "Skewness": skew(x),
        "YoY Acumulado % (3 últimos anos)": tendencias["yoy_percent"],
        "CAGR % (3 últimos anos)": tendencias["cagr_percent"],
        "Slope (Regressão Linear, 3 últimos anos)": tendencias["tendencia_slope"],
        "Interpretação Tendência (3 últimos anos)": tendencias["interpretacao"],
        "Tendência": resumo_tendencia
    })

def classificar_liquidez_corrente(historico_empresa_df, nome_coluna="Liquidez_Corrente"):
    """
    Classifica a Liquidez Corrente baseada na Solvência (Piso > 1) e Gordura (Mediana > 2).
    Trata exceção para Bancos.
    """
    # 1. Calcular estatísticas base
    stats = calcular_stats(historico_empresa_df, metrica=nome_coluna)
    stats["Indicador"] = "Liquidez Corrente"
    
    # 2. Extrair variáveis para legibilidade
    mediana = stats['Median']
    q1 = stats['Q1'] # Piso Histórico (Recorrente)
    q3 = stats['Q3'] # Teto Histórico
    
    # Tenta identificar o setor para a regra de exceção
    # (Assumindo que a coluna 'Categoria' existe no DF)
    setor = historico_empresa_df['Categoria'].iloc[0] if 'Categoria' in historico_empresa_df.columns else ""

    # ÁRVORE DE DECISÃO (LIQUIDEZ)

    # Exceção: Setor Bancário
    # Bancos operam com liquidez ~1.0 por regulação (Casamento de ativos/passivos)
    if setor in ['Bancos', 'Banking', 'Bank']:
        stats["Classificacao"] = "Neutro (Setor Bancário)"
        stats["Justificativa"] = "Indicador menos relevante para Bancos devido à estrutura de balanço regulatória (Liquidez tende a 1.0)."
        return stats

    # Risco Elevado (Insolvência Estrutural)
    # Se nem no melhor cenário (Q3) ela paga as contas, ou se a média é insolvente.
    if q3 < 1.0 or mediana < 0.95:
        stats["Classificacao"] = "Risco Elevado"
        stats["Justificativa"] = "Incapacidade estrutural de cobrir passivos de curto prazo (Insolvência recorrente)."

    # Forte (Cash Rich / Gordura)
    # Mediana alta (>2) E Piso seguro (>1). Aqui a volatilidade é irrelevante.
    elif mediana >= 2.0 and q1 >= 1.0:
        stats["Classificacao"] = "Forte"
        stats["Justificativa"] = "Ampla folga financeira ('Colchão de Liquidez'). Alta resiliência a crises."

    # Risco Moderado (No Limite)
    # Mediana apertada (<1.2) OU já teve ano com liquidez < 1 (Q1 < 1)
    elif mediana < 1.20 or q1 < 1.0:
        stats["Classificacao"] = "Risco Moderado"
        stats["Justificativa"] = "Margem de segurança estreita (< 1.20) ou histórico de quebra de caixa (Q1 < 1.0)."

    # Adequado (Eficiência)
    # Sobrou: 1.2 <= Mediana < 2.0 E Q1 >= 1.0
    else:
        stats["Classificacao"] = "Adequado"
        stats["Justificativa"] = "Gestão financeira equilibrada e eficiente. Honra obrigações sem excessos."

    return stats

# FLUXO DE CAIXA OPERACIONAL (FCO) 
def classificar_fco(historico_empresa_df, nome_coluna="Fluxo_Caixa_Operacional"):
    """
    Classifica o FCO baseado na Sustentabilidade (Gera caixa?) e Tendência.
    """
    # Calcula estatísticas e tendências
    stats = calcular_stats(historico_empresa_df, metrica=nome_coluna)
    stats["Indicador"] = "Fluxo de Caixa Operacional"

    # Extração de variáveis para legibilidade
    mediana = stats['Median']
    q1 = stats['Q1']     # Piso Histórico
    q3 = stats['Q3']     # Teto Histórico
    cagr = stats['CAGR % (3 últimos anos)'] # Tendência recente
    slope = stats['Slope (Regressão Linear, 3 últimos anos)'] 

    # TENDÊNCIA
    # Se CAGR for NaN (devido a negativos), olhamos se a reta (slope) está caindo
    if pd.isna(cagr):
        tendencia_queda_forte = (slope < 0) # Simplificação: se reta cai, é ruim
        tendencia_positiva = (slope > 0)
    else:
        tendencia_queda_forte = (cagr < -10)
        tendencia_positiva = (cagr >= 0)

    # ÁRVORE DE DECISÃO (FCO)
    
    # Risco Elevado (Dependência Crônica)
    # Queima caixa na média OU mesmo no melhor momento (Q3) é negativo/zero
    if mediana < 0 or q3 <= 0:
        stats["Classificacao"] = "Risco Elevado"
        stats["Justificativa"] = "Geração de caixa estruturalmente negativa."

    # Forte (Cash Cow)
    # Gera caixa sempre (Q1 > 0) e tem tendência positiva/estável
    elif mediana > 0 and q1 > 0 and tendencia_positiva:
        stats["Classificacao"] = "Forte"
        stats["Justificativa"] = "Geração de caixa recorrente e sustentável."

    # Risco Moderado (Oscilação ou Deterioração)
    # Teve anos de queima (Q1 < 0) OU a tendência é de queda forte (< -10%)
    elif q1 < 0 or tendencia_queda_forte:
        stats["Classificacao"] = "Risco Moderado"
        stats["Justificativa"] = "Histórico de queima de caixa ou tendência de deterioração acentuada."

    # Adequado (Sustentabilidade Padrão)
    # Sobrou: Gera caixa na média, mas talvez com queda leve ou sem grande folga
    else:
        stats["Classificacao"] = "Adequado"
        stats["Justificativa"] = "Geração de caixa positiva, mas com estabilidade ou queda leve."

    return stats


# MARGEM LÍQUIDA 
def classificar_margem_liquida(historico_empresa_df, nome_coluna="Margem_Liquida"):
    """
    Classifica Margem Líquida baseado em Eficiência e Colchão de Lucratividade.
    """
    stats = calcular_stats(historico_empresa_df, metrica=nome_coluna)
    stats["Indicador"] = "Margem Líquida"

    mediana = stats['Median']
    q1 = stats['Q1'] # Piso Histórico
    q3 = stats['Q3'] # Teto Histórico
    std = stats['Std']
    
    # ÁRVORE DE DECISÃO (MARGEM)

    # Risco Elevado (Destruição de Valor)
    # Prejuízo na média OU Teto muito baixo (margem < 2% no melhor cenário)
    if mediana < 0 or q3 < 2.0:
        stats["Classificacao"] = "Risco Elevado"
        stats["Justificativa"] = "Operação não gera lucro consistente ou opera no prejuízo."

    # Forte (Alta Eficiência)
    # Mediana alta (>= 15%) E Piso seguro (> 5%)
    elif mediana >= 15.0 and q1 > 5.0:
        stats["Classificacao"] = "Forte"
        stats["Justificativa"] = "Alta eficiência e 'colchão' de rentabilidade."

    # Risco Moderado (Margem Apertada/Volátil)
    # Break-even apertado (< 5%) OU Prejuízo pontual (Q1 < 0) 
    # OU Alta volatilidade se a margem não for alta (Mediana < 8% e Std alto)
    elif (0 < mediana < 5.0) or (q1 < 0) or (mediana < 8.0 and std > 5.0):
        stats["Classificacao"] = "Risco Moderado"
        stats["Justificativa"] = "Margens estreitas, volatilidade alta ou prejuízos pontuais."

    # Adequado (Estável)
    # Mediana saudável (entre 5% e 15%) e sempre positiva
    else:
        stats["Classificacao"] = "Adequado"
        stats["Justificativa"] = "Rentabilidade estável dentro da média de mercado."

    return stats

# EBITDA 
def classificar_ebitda(historico_empresa_df, nome_coluna="EBITDA"):
    """
    Classifica EBITDA baseado em Potencial Operacional e Crescimento.
    """
    stats = calcular_stats(historico_empresa_df, metrica=nome_coluna)
    stats["Indicador"] = "EBITDA"

    mediana = stats['Median']
    q1 = stats['Q1']
    q3 = stats['Q3']
    cagr = stats['CAGR % (3 últimos anos)']
    slope = stats['Slope (Regressão Linear, 3 últimos anos)']

    # TENDÊNCIA
    if pd.isna(cagr):
        crescimento_forte = (slope > 0) # Assumimos qualquer crescimento se vier de negativo
        queda_acentuada = (slope < 0)
    else:
        crescimento_forte = (cagr > 5.0)
        queda_acentuada = (cagr < -10.0)
        
    # ÁRVORE DE DECISÃO (EBITDA) 

    # Risco Elevado (Prejuízo Operacional)
    # Operação principal dá prejuízo
    if mediana < 0 or q3 <= 0:
        stats["Classificacao"] = "Risco Elevado"
        stats["Justificativa"] = "Operação principal deficitária (EBITDA negativo)."

    # Forte (Expansão)
    # Mediana positiva, Piso positivo E Crescimento (> 5%)
    elif mediana > 0 and q1 > 0 and crescimento_forte:
        stats["Classificacao"] = "Forte"
        stats["Justificativa"] = "Operação rentável e em expansão (CAGR positivo)."

    # Risco Moderado (Deterioração)
    # Queda acentuada recente (< -10%) OU Prejuízo operacional pontual (Q1 < 0)
    elif cagr < -10.0 or q1 < 0:
        stats["Classificacao"] = "Risco Moderado"
        stats["Justificativa"] = "Deterioração operacional rápida ou EBITDA negativo pontual."

    # Adequado (Maturidade)
    # Positivo, estável ou queda leve
    else:
        stats["Classificacao"] = "Adequado"
        stats["Justificativa"] = "Geração operacional estável (Maturidade)."

    return stats

def calcular_stats_setor(df, setor, metrica="Liquidez_Corrente"):
    x = df[df["Categoria"] == setor][metrica].dropna()
    
    return {
        "Min": float(x.min()),
        "Max": float(x.max()),
        "Mean": float(x.mean()),
        "Median": float(x.median()),
        "Std": float(x.std()),
        "Q1": float(x.quantile(0.25)),
        "Q3": float(x.quantile(0.75)),
        "IQR": float(x.quantile(0.75) - x.quantile(0.25)),
        "Skewness": float(skew(x))
    }


def gerar_diagnostico_completo(empresa="AAPL"):

    df = obter_base_de_dados()
    df_empresa = df[df["Empresa"] == empresa]
    
    if df_empresa.empty:
        return {"erro": f"Empresa {empresa} não encontrada na base."}

    setor = df_empresa["Categoria"].iloc[0]

    # Quantidade de empresas no setor
    empresas_no_setor = df[df["Categoria"] == setor]["Empresa"].nunique()
    incluir_setor = empresas_no_setor > 1

    # Empresa
    res_liquidez = classificar_liquidez_corrente(df_empresa)
    res_fco = classificar_fco(df_empresa)
    res_margem = classificar_margem_liquida(df_empresa)
    res_ebitda = classificar_ebitda(df_empresa)

    # Setor (somente se houver mais de uma empresa)
    res_liquidez_setor = calcular_stats_setor(df, setor, "Liquidez_Corrente") if incluir_setor else None
    res_fco_setor = calcular_stats_setor(df, setor, "Fluxo_Caixa_Operacional") if incluir_setor else None
    res_margem_setor = calcular_stats_setor(df, setor, "Margem_Liquida") if incluir_setor else None
    res_ebitda_setor = calcular_stats_setor(df, setor, "EBITDA") if incluir_setor else None

    metricas = [
        ("Liquidez Corrente", res_liquidez, res_liquidez_setor),
        ("Fluxo_Caixa_Operacional", res_fco, res_fco_setor),
        ("Margem Líquida", res_margem, res_margem_setor),
        ("EBITDA", res_ebitda, res_ebitda_setor),
    ]

    # Monta o JSON final
    resultado_metricas = []
    for nome_indicador, emp, setor_stats in metricas:
        bloco = {
            "Indicador": nome_indicador,
            "Empresa": emp
        }
        if incluir_setor:
            bloco["Setor"] = setor_stats
        resultado_metricas.append(bloco)

    return {
        "empresa": empresa,
        "setor": setor,
        "metricas": resultado_metricas,
        "incluiu_setor": incluir_setor,
        "empresas_no_setor": empresas_no_setor
    }