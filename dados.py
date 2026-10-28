"""Gera dados FICTÍCIOS (com alguns erros e duplicados de propósito)."""
import random
from pathlib import Path
from datetime import date, timedelta
import pandas as pd

random.seed(42)
PASTA = Path("dados"); PASTA.mkdir(exist_ok=True)

empresas = ["Alfa Lda", "Beta SA", "Gama Lda", "Delta SA", "Epsilon Lda"]
prestadores = ["Clínica Sagrada Esperança", "Hospital Girassol", "Clínica Multiperfil",
               "Farmácia Central", "Laboratório Lab+"]

apolices = [{"apolice_id": f"AP{i:03d}", "empresa": e, "inicio": "2026-01-01",
             "fim": "2026-12-31", "premio_mensal": random.choice([1500000, 2000000, 2500000, 3000000])}
            for i, e in enumerate(empresas, 1)]

benef = []
for i in range(1, 61):
    ap = random.choice(apolices)["apolice_id"]
    nasc = date(1960, 1, 1) + timedelta(days=random.randint(0, 20000))
    benef.append({"beneficiario_id": f"B{i:04d}", "nome": f"Beneficiário {i}",
                  "apolice_id": ap, "data_nascimento": nasc.isoformat()})
benef.append(dict(benef[0]))                       # duplicado
benef.append({"beneficiario_id": "B9999", "nome": None, "apolice_id": "AP001",
              "data_nascimento": "1990-01-01"})    # inválido (sem nome)

sin = []
for i in range(1, 401):
    b = random.choice(benef[:60])
    d = date(2026, 1, 1) + timedelta(days=random.randint(0, 300))
    valor = round(random.lognormvariate(10.5, 0.6), 2)
    if random.random() < 0.02:
        valor *= 15                                # valores atípicos (suspeitos)
    sin.append({"sinistro_id": f"S{i:05d}", "beneficiario_id": b["beneficiario_id"],
                "apolice_id": b["apolice_id"], "prestador": random.choice(prestadores),
                "data": d.isoformat(), "valor": round(valor, 2)})
sin.append(dict(sin[0]))                           # duplicado
sin.append({**sin[1], "sinistro_id": "S99999", "beneficiario_id": "B0000"})  # beneficiário inexistente

pd.DataFrame(apolices).to_csv(PASTA / "apolices.csv", index=False)
pd.DataFrame(benef).to_csv(PASTA / "beneficiarios.csv", index=False)
pd.DataFrame(sin).to_csv(PASTA / "sinistros.csv", index=False)
print("Dados fictícios criados em ./dados")