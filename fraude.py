"""Deteção de padrões atípicos com Isolation Forest."""
import pandas as pd
from sklearn.ensemble import IsolationForest
from analise import carregar

def detectar(contaminacao=0.03):
    si = carregar("sinistros")
    si["freq_benef"] = si.groupby("beneficiario_id")["sinistro_id"].transform("count")
    si["rel_prestador"] = si["valor"] / si.groupby("prestador")["valor"].transform("mean")
    X = si[["valor", "freq_benef", "rel_prestador"]]
    modelo = IsolationForest(contamination=contaminacao, random_state=42).fit(X)
    si["score"] = modelo.decision_function(X)
    si["suspeito"] = modelo.predict(X) == -1
    return si[si["suspeito"]].sort_values("score")[
        ["sinistro_id", "beneficiario_id", "prestador", "data", "valor", "freq_benef", "score"]]

if __name__ == "_main_":
    print(detectar())