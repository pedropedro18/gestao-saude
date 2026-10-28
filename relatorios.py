"""Exportação para Excel e PDF."""
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import analise, fraude

def folhas():
    return {"Apolices": analise.resumo_apolices(),
            "Prestadores": analise.custos_por_prestador(),
            "Mensal": analise.sinistralidade_mensal(),
            "Suspeitos": fraude.detectar().assign(data=lambda d: d["data"].dt.date)}

def exportar_excel(caminho="relatorio.xlsx"):
    with pd.ExcelWriter(caminho, engine="openpyxl") as w:
        for nome, df in folhas().items():
            df.to_excel(w, sheet_name=nome, index=False)
    return caminho

def exportar_pdf(caminho="relatorio.pdf"):
    est = getSampleStyleSheet()
    doc = SimpleDocTemplate(caminho, pagesize=landscape(A4))
    el = [Paragraph("Relatório - Seguro de Saúde", est["Title"])]
    for nome, df in list(folhas().items())[:3]:
        el += [Spacer(1, 12), Paragraph(nome, est["Heading2"])]
        t = Table([list(df.columns)] + df.astype(str).values.tolist(), repeatRows=1)
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
                               ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                               ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                               ("FONTSIZE", (0, 0), (-1, -1), 8)]))
        el.append(t)
    doc.build(el)
    return caminho

if __name__ == "_main_":
    print(exportar_excel(), exportar_pdf())