
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# Função para formatar os dados conforme padrão desejado
def formatar_planilha(df):
    # Renomear coluna Data_5 para Data do TVI, se existir
    if 'Data_5' in df.columns:
        df.rename(columns={'Data_5': 'Data do TVI'}, inplace=True)

    # CNPJ ou CPF e CNPJ ou CPF_2 como texto numérico sem decimais
    for col in ['CNPJ ou CPF', 'CNPJ ou CPF_2']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.extract(r'(\d+)')[0].fillna('').str.zfill(11)

    # Datas no formato datetime e também formatadas
    for col in ['Data', 'Data do TVI']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[col] = df[col].dt.strftime('%d/%m/%Y')

    # Converter Data do TVI para datetime novamente para lógica de Aliq Interna
    df['Data do TVI_dt'] = pd.to_datetime(df['Data do TVI'], format='%d/%m/%Y', errors='coerce')

    # Criar coluna "BC + 50%" = Valor do Produto * 1.5
    if 'Valor do Produto' in df.columns:
        df['BC + 50%'] = pd.to_numeric(df['Valor do Produto'], errors='coerce').fillna(0) * 1.5

    # Criar coluna "Aliq Interna"
    def calcular_aliquota(data):
        if pd.isnull(data):
            return None
        elif data < datetime(2023, 3, 31):
            return 0.18
        elif data < datetime(2024, 2, 19):
            return 0.20
        elif data < datetime(2025, 3, 31):
            return 0.22
        else:
            return 0.23
    df['Aliq Interna'] = df['Data do TVI_dt'].map(calcular_aliquota)

    # Criar coluna "ICMS Débito" = (BC + 50%) * Aliq Interna - Valor do ICMS
    df['Valor do ICMS'] = pd.to_numeric(df['Valor do ICMS'], errors='coerce').fillna(0)
    df['ICMS Débito'] = df['BC + 50%'] * df['Aliq Interna'] - df['Valor do ICMS']

    # Converter Aliq Interna para string percentual
    df['Aliq Interna'] = df['Aliq Interna'].map(lambda x: f"{x*100:.0f}%" if pd.notnull(x) else "")

    # Remover coluna auxiliar
    df.drop(columns=['Data do TVI_dt'], inplace=True)

    # Excluir colunas indesejadas se existirem
    for coluna_remover in ['Base de Cálculo do ICMS ST', 'Valor do ICMS ST']:
        if coluna_remover in df.columns:
            df.drop(columns=[coluna_remover], inplace=True)

    # Converter valores financeiros para numérico
    colunas_financeiras = [
        'Valor do Produto', 'Base de Cálculo ICMS', 'Valor do ICMS',
        'BC + 50%', 'Débito ICMS', 'Valor da NFe', 'ICMS Débito'
    ]
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
