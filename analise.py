"""Cálculo de prémios, despesas, sinistralidade e custos."""
import pandas as pd
from db import ligar

def carregar(tabela):
    with ligar() as con:
        df = pd.read_sql(f"SELECT * FROM {tabela}", con)
    for c in ("inicio", "fim", "data"):
        if c in df.columns:
            df[c] = pd.to_datetime(df[c])
    return df

def resumo_apolices():
    ap, si = carregar("apolices"), carregar("sinistros")
    ap["meses"] = ((ap["fim"].dt.year - ap["inicio"].dt.year) * 12
                   + ap["fim"].dt.month - ap["inicio"].dt.month + 1)
    ap["premios"] = ap["premio_mensal"] * ap["meses"]
    desp = si.groupby("apolice_id")["valor"].agg(despesas="sum", n_sinistros="count").reset_index()
    r = ap.merge(desp, on="apolice_id", how="left").fillna({"despesas": 0, "n_sinistros": 0})
    r["sinistralidade_%"] = (r["despesas"] / r["premios"] * 100).round(2)
    return r[["apolice_id", "empresa", "premios", "despesas", "n_sinistros", "sinistralidade_%"]]

def custos_por_prestador():
    si = carregar("sinistros")
    return (si.groupby("prestador")["valor"].agg(total="sum", n="count", media="mean")
              .round(2).sort_values("total", ascending=False).reset_index())

def custos_por_apolice_prestador():
    si = carregar("sinistros")
    return si.pivot_table(index="apolice_id", columns="prestador", values="valor",
                          aggfunc="sum", fill_value=0).round(2).reset_index()

def sinistralidade_mensal():
    ap, si = carregar("apolices"), carregar("sinistros")
    si["mes"] = si["data"].dt.to_period("M")
    linhas = []
    for mes, g in si.groupby("mes"):
        ini, fim = mes.start_time, mes.end_time
        activas = ap[(ap["inicio"] <= fim) & (ap["fim"] >= ini)]
        premios = activas["premio_mensal"].sum()
        desp = g["valor"].sum()
        linhas.append({"mes": str(mes), "premios": premios, "despesas": round(desp, 2),
                       "sinistros": len(g),
                       "sinistralidade_%": round(desp / premios * 100, 2) if premios else 0})
    return pd.DataFrame(linhas)

if __name__ == "__main__":
    print(resumo_apolices()); print(custos_por_prestador()); print(sinistralidade_mensal())