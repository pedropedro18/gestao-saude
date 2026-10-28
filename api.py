from fastapi import FastAPI, HTTPException
import analise
from db import ligar

app = FastAPI(title="API Seguro de Saúde")

def consulta(sql, params=()):
    with ligar() as con:
        con.row_factory = lambda c, r: {d[0]: r[i] for i, d in enumerate(c.description)}
        return con.execute(sql, params).fetchall()

@app.get("/beneficiarios")
def listar(apolice_id: str | None = None):
    if apolice_id:
        return consulta("SELECT * FROM beneficiarios WHERE apolice_id=?", (apolice_id,))
    return consulta("SELECT * FROM beneficiarios")

@app.get("/beneficiarios/{beneficiario_id}")
def beneficiario(beneficiario_id: str):
    b = consulta("SELECT * FROM beneficiarios WHERE beneficiario_id=?", (beneficiario_id,))
    if not b:
        raise HTTPException(404, "Beneficiário não encontrado")
    s = consulta("SELECT * FROM sinistros WHERE beneficiario_id=?", (beneficiario_id,))
    return {**b[0], "total_sinistros": len(s),
            "total_gasto": round(sum(x["valor"] for x in s), 2), "sinistros": s}

@app.get("/resumo")
def resumo():
    return analise.resumo_apolices().to_dict("records")

@app.get("/prestadores")
def prestadores():
    return analise.custos_por_prestador().to_dict("records")