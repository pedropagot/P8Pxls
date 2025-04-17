
import streamlit as st
import pandas as pd
from io import BytesIO

# Função para formatar o DataFrame
def formatar_planilha(df):
    for col in ['CNPJ ou CPF', 'CNPJ ou CPF_2']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)

    for col in ['Data', 'Data do TVI']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d/%m/%Y')

    if 'Aliq Interna' in df.columns:
        df['Aliq Interna'] = pd.to_numeric(df['Aliq Interna'], errors='coerce').map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")

    colunas_financeiras = [
        'Valor do Produto', 'Base de Cálculo ICMS', 'Valor do ICMS',
        'BC + 50%', 'Débito ICMS', 'Base de Cálculo do ICMS ST',
        'Valor do ICMS ST', 'Valor da NFe', 'Valor Débito TVI'
    ]
    for col in colunas_financeiras:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').map(lambda x: f"{x:,.2f}".replace('.', '#').replace(',', '.').replace('#', ','))

    return df

st.title("Conversor P8Pxls 📊")
st.write("Envie um arquivo `.xls` ou `.xlsx` e receba de volta a versão formatada conforme o padrão P8Pxls_formatado_financeiro.xlsx")

arquivo = st.file_uploader("Selecione o arquivo Excel", type=["xls", "xlsx"])

if arquivo:
    try:
        # Detecta extensão para usar o engine correto
        ext = arquivo.name.split('.')[-1].lower()
        if ext == 'xls':
            df = pd.read_excel(arquivo, engine='xlrd')
        else:
            df = pd.read_excel(arquivo, engine='openpyxl')

        df_formatado = formatar_planilha(df)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_formatado.to_excel(writer, index=False, sheet_name='Planilha Formatada')

        st.success("Arquivo formatado com sucesso!")
        st.download_button(
            label="📥 Baixar arquivo formatado",
            data=output.getvalue(),
            file_name="P8Pxls_formatado_financeiro.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
