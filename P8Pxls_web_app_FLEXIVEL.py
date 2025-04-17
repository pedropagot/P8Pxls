
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="P8Pxls Web", layout="centered")

st.title("📊 P8Pxls Web - Conversor de CSV para XLS com formatação")
st.markdown("Envie um arquivo `.csv`, clique em **Processar** e baixe o Excel formatado automaticamente.")

uploaded_file = st.file_uploader("Escolha o arquivo CSV", type=["csv"])

if uploaded_file:
    try:
        # Lê o CSV com separador brasileiro
        df = pd.read_csv(uploaded_file, encoding="utf-8", sep=";", decimal=",")

        # Detecta a última coluna que contém "data" no nome (independente de maiúscula/minúscula)
        data_cols = [col for col in df.columns if "data" in col.lower()]
        if not data_cols:
            raise Exception("Nenhuma coluna com a palavra 'data' foi encontrada no CSV.")
        df = df.rename(columns={data_cols[-1]: "Data do TVI"})

        # Conversões
        df["Data do TVI"] = pd.to_datetime(df["Data do TVI"], errors="coerce")
        df["Valor do Produto"] = pd.to_numeric(df["Valor do Produto"], errors="coerce")
        df["Valor do ICMS"] = pd.to_numeric(df["Valor do ICMS"], errors="coerce")
        df["Valor Débito TVI"] = pd.to_numeric(df["Valor Débito TVI"], errors="coerce")

        df = df[df["Valor Débito TVI"].fillna(0) != 0]
        df = df.sort_values(by="Número do TVI")
        df["BC + 50%"] = df["Valor do Produto"] * 1.5

        df["Aliq Interna"] = 0.0
        df.loc[df["Data do TVI"] < "2023-03-31", "Aliq Interna"] = 0.18
        df.loc[(df["Data do TVI"] > "2023-03-31") & (df["Data do TVI"] < "2024-02-19"), "Aliq Interna"] = 0.20
        df.loc[(df["Data do TVI"] > "2024-02-18") & (df["Data do TVI"] < "2025-03-31"), "Aliq Interna"] = 0.22
        df.loc[df["Data do TVI"] > "2025-03-31", "Aliq Interna"] = 0.23

        df["Débito ICMS"] = (df["BC + 50%"] * df["Aliq Interna"]) - df["Valor do ICMS"]

        total_produto = df["Valor do Produto"].sum()
        total_icms = df["Valor do ICMS"].sum()
        total_debito = df["Débito ICMS"].sum()
        total_bc_50 = df["BC + 50%"].sum()
        multa = total_debito / 2
        total_com_multa = total_debito + multa

        df.loc["TOTAL"] = [""] * len(df.columns)
        df.at["TOTAL", "Valor do Produto"] = total_produto
        df.at["TOTAL", "Valor do ICMS"] = total_icms
        df.at["TOTAL", "Débito ICMS"] = total_debito
        df.at["TOTAL", "BC + 50%"] = total_bc_50

        df.loc["MULTA"] = [""] * len(df.columns)
        df.at["MULTA", "Débito ICMS"] = multa

        df.loc["TOTAL COM MULTA"] = [""] * len(df.columns)
        df.at["TOTAL COM MULTA", "Débito ICMS"] = total_com_multa

        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        st.success("✅ Arquivo processado com sucesso!")
        st.download_button(
            label="📥 Baixar Excel formatado",
            data=output,
            file_name="relatorio_formatado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
