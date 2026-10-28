"""Dashboard: streamlit run dashboard.py"""
import streamlit as st
import analise, fraude, relatorios

st.set_page_config(page_title="Seguro de Saúde", layout="wide")
st.title("🏥 Análise e Gestão de Seguro de Saúde")

ap = analise.resumo_apolices()
prest = analise.custos_por_prestador()
mensal = analise.sinistralidade_mensal()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Prémios", f"{ap['premios'].sum():,.0f}")
c2.metric("Despesas", f"{ap['despesas'].sum():,.0f}")
c3.metric("Sinistralidade", f"{ap['despesas'].sum() / ap['premios'].sum() * 100:.1f}%")
c4.metric("Sinistros", int(ap["n_sinistros"].sum()))

e, d = st.columns(2)
e.subheader("Sinistralidade mensal (%)")
e.line_chart(mensal.set_index("mes")["sinistralidade_%"])
d.subheader("Custos por prestador")
d.bar_chart(prest.set_index("prestador")["total"])

st.subheader("Apólices")
st.dataframe(ap, use_container_width=True)
st.subheader("⚠️ Sinistros suspeitos")
st.dataframe(fraude.detectar(), use_container_width=True)

b1, b2 = st.columns(2)
if b1.button("Gerar Excel"):
    with open(relatorios.exportar_excel(), "rb") as f:
        b1.download_button("Descarregar Excel", f, "relatorio.xlsx")
if b2.button("Gerar PDF"):
    with open(relatorios.exportar_pdf(), "rb") as f:
        b2.download_button("Descarregar PDF", f, "relatorio.pdf")