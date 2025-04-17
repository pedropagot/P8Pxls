
import streamlit as st
import pandas as pd
from io import BytesIO

# Função para formatar os dados conforme padrão desejado
def formatar_planilha(df):
    # Renomear coluna Data_5 para Data do TVI, se existir
    if 'Data_5' in df.columns:
        df.rename(columns={'Data_5': 'Data do TVI'}, inplace=True)

    # CNPJ ou CPF e CNPJ ou CPF_2 como texto numérico sem decimais
    for col in ['CNPJ ou CPF', 'CNPJ ou CPF_2']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.extract(r'(\d+)')[0].fillna('').str.zfill(11)

    # Datas no formato dd/mm/aaaa
    for col in ['Data', 'Data do TVI']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%d/%m/%Y')

    # Aliq Interna como percentual
    if 'Aliq Interna' in df.columns:
        df['Aliq Interna'] = pd.to_numeric(df['Aliq Interna'], errors='coerce')                                .map(lambda x: f"{x:.2f}%" if pd.notnull(x) else "")

    # Colunas financeiras
    colunas_financeiras = [
        'Valor do Produto', 'Base de Cálculo ICMS', 'Valor do ICMS',
        'BC + 50%', 'Débito ICMS', 'Valor da NFe'
    ]

    # Remover colunas indesejadas se existirem
    for coluna_remover in ['Base de Cálculo do ICMS ST', 'Valor do ICMS ST']:
        if coluna_remover in df.columns:
            df.drop(columns=[coluna_remover], inplace=True)

    colunas_presentes = [col for col in colunas_financeiras if col in df.columns]

    for col in colunas_presentes:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Excluir linhas com Valor Débito TVI igual a 0
    if 'Valor Débito TVI' in df.columns:
        df['Valor Débito TVI'] = pd.to_numeric(df['Valor Débito TVI'], errors='coerce').fillna(0)
        df = df[df['Valor Débito TVI'] != 0]

    # Adicionar linha de somatório (exceto para Valor Débito TVI)
    soma = df[colunas_presentes].sum(numeric_only=True)
    linha_total = {col: soma[col] if col in soma else '' for col in df.columns}
    df = pd.concat([df, pd.DataFrame([linha_total])], ignore_index=True)

    return df

# Streamlit App
st.title("Conversor P8Pxls 📊")
st.write("Envie seu arquivo Excel `.xls` ou `.xlsx` e baixe a versão final no padrão P8Pxls_formatado_financeiro.xlsx")

arquivo = st.file_uploader("Selecione o arquivo Excel", type=["xls", "xlsx"])

if arquivo:
    try:
        extensao = arquivo.name.split('.')[-1].lower()
        if extensao == 'xls':
            df = pd.read_excel(arquivo, engine='xlrd')
        else:
            df = pd.read_excel(arquivo, engine='openpyxl')

        df_formatado = formatar_planilha(df)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_formatado.to_excel(writer, index=False, sheet_name='Planilha Formatada')

        st.success("✅ Arquivo formatado com sucesso!")
        st.download_button(
            label="📥 Baixar arquivo formatado",
            data=output.getvalue(),
            file_name="P8Pxls_formatado_financeiro.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
