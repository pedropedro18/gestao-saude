"""Importação, validação e identificação de duplicados -> SQLite."""
import sqlite3
from pathlib import Path
import pandas as pd

DB = "seguro.db"

def ligar():
    return sqlite3.connect(DB)

def validar(df, chave, obrigatorios):
    duplicados = df[df.duplicated(chave, keep="first")]
    df = df.drop_duplicates(chave, keep="first")
    invalidos = df[df[obrigatorios].isna().any(axis=1)]
    df = df.dropna(subset=obrigatorios)
    return df, duplicados, invalidos

def importar(pasta="dados"):
    pasta = Path(pasta)
    relatorio = {}

    ap = pd.read_csv(pasta / "apolices.csv", parse_dates=["inicio", "fim"])
    ap, dup, inv = validar(ap, "apolice_id", ["apolice_id", "empresa", "inicio", "fim", "premio_mensal"])
    ap = ap[ap["premio_mensal"] > 0]
    relatorio["apolices"] = (len(ap), len(dup), len(inv))

    be = pd.read_csv(pasta / "beneficiarios.csv")
    be, dup, inv = validar(be, "beneficiario_id", ["beneficiario_id", "nome", "apolice_id"])
    be = be[be["apolice_id"].isin(ap["apolice_id"])]
    relatorio["beneficiarios"] = (len(be), len(dup), len(inv))

    si = pd.read_csv(pasta / "sinistros.csv", parse_dates=["data"])
    si, dup, inv = validar(si, "sinistro_id", ["sinistro_id", "beneficiario_id", "apolice_id", "data", "valor"])
    antes = len(si)
    si = si[(si["valor"] > 0) & si["beneficiario_id"].isin(be["beneficiario_id"])]
    relatorio["sinistros"] = (len(si), len(dup), len(inv) + antes - len(si))

    with ligar() as con:
        ap.to_sql("apolices", con, if_exists="replace", index=False)
        be.to_sql("beneficiarios", con, if_exists="replace", index=False)
        si.to_sql("sinistros", con, if_exists="replace", index=False)

    for tabela, (ok, d, i) in relatorio.items():
        print(f"{tabela}: {ok} válidos | {d} duplicados | {i} inválidos")
    return relatorio

if __name__ == "__main__":
    importar()