from fastapi import FastAPI
from diagnosticar_empresas import gerar_diagnostico_completo

app = FastAPI(
    title="API de Diagnóstico Financeiro",
    description="API que calcula indicadores financeiros e tendências por empresa.",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"status": "online", "message": "API funcionando corretamente."}

@app.get("/diagnostico")
def diagnostico(empresa: str):
    """
    Retorna o diagnóstico completo de uma empresa,
    conforme sua função gerar_diagnostico_completo().
    """
    try:
        resultado = gerar_diagnostico_completo(empresa=empresa)
        return resultado

    except Exception as e:
        return {
            "erro": "Falha ao gerar diagnóstico.",
            "detalhes": str(e)
        }
# Para rodar a API, use o comando:
# uvicorn api:app --reload       