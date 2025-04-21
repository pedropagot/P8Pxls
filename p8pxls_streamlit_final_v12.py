
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

def formatar_planilha(df):
    if 'Data_5' in df.columns:
        df.rename(columns={'Data_5': 'Data do TVI'}, inplace=True)

    for col in ['CNPJ ou CPF', 'CNPJ ou CPF_2']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.extract(r'(\d+)')[0].fillna('').str.zfill(11)

    for col in ['Data', 'Data do TVI']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[col] = df[col].dt.strftime('%d/%m/%Y')

    df['Data do TVI_dt'] = pd.to_datetime(df['Data do TVI'], format='%d/%m/%Y', errors='coerce')

    if 'Valor do Produto' in df.columns:
        df['BC + 50%'] = pd.to_numeric(df['Valor do Produto'], errors='coerce').fillna(0) * 1.5

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

    df['Valor do ICMS'] = pd.to_numeric(df['Valor do ICMS'], errors='coerce').fillna(0)
    df['ICMS Débito'] = df['BC + 50%'] * df['Aliq Interna'] - df['Valor do ICMS']
    df['Aliq Interna'] = df['Aliq Interna'].map(lambda x: f"{x*100:.0f}%" if pd.notnull(x) else "")
    df.drop(columns=['Data do TVI_dt'], inplace=True)

    for coluna_remover in ['Base de Cálculo do ICMS ST', 'Valor do ICMS ST']:
        if coluna_remover in df.columns:
            df.drop(columns=[coluna_remover], inplace=True)

    colunas_financeiras = [
        'Valor do Produto', 'Base de Cálculo ICMS', 'Valor do ICMS',
        'BC + 50%', 'Débito ICMS', 'ICMS Débito'
    ]
    colunas_presentes = [col for col in colunas_financeiras if col in df.columns]
    for col in colunas_presentes:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    if 'Valor Débito TVI' in df.columns:
        df['Valor Débito TVI'] = pd.to_numeric(df['Valor Débito TVI'], errors='coerce').fillna(0)
        df = df[df['Valor Débito TVI'] != 0]

    soma = df[colunas_presentes].sum(numeric_only=True)

    # VALORES ANTES DE ADICIONAR A MULTA
    icms_debito_sem_multa = soma.get('ICMS Débito', 0)
    multa = icms_debito_sem_multa / 2
    total_com_multa = icms_debito_sem_multa + multa

    linha_soma = {col: soma[col] if col in soma else '' for col in df.columns}
    linha_multa = {col: multa if col == 'ICMS Débito' else '' for col in df.columns}
    linha_total_multa = {col: total_com_multa if col == 'ICMS Débito' else '' for col in df.columns}
    df = pd.concat([df, pd.DataFrame([linha_soma, linha_multa, linha_total_multa])], ignore_index=True)

    colunas_novas = ['BC + 50%', 'Aliq Interna', 'ICMS Débito']
    for col in colunas_novas:
        if col not in df.columns:
            colunas_novas.remove(col)

    if 'Valor da NFe' in df.columns:
        cols = list(df.columns)
        idx = cols.index('Valor da NFe') + 1
        for col in reversed(colunas_novas):
            cols.insert(idx, cols.pop(cols.index(col)))
        df = df[cols]

    resumo = pd.DataFrame({
        'Descrição': [
            'Valor total dos produtos',
            'BC Aplicada - Base de Cálculo + 50%',
            'ICMS Débito = Alíquota x BC',
            'Crédito de ICMS destacado em NF-e',
            'Valor ICMS a recolher',
            'Multa de 50%',
            'Total Devido (ICMS a recolher + Multa de 50%)'
        ],
        'Valor': [
            soma.get('Valor do Produto', 0),
            soma.get('BC + 50%', 0),
            icms_debito_sem_multa + soma.get('Valor do ICMS', 0),
            soma.get('Valor do ICMS', 0),
            icms_debito_sem_multa,
            multa,
            total_com_multa
        ]
    })

    return df, resumo

# Streamlit App
st.title("Conversor P8Pxls 📊")
st.write("Envie seu arquivo Excel `.xls` ou `.xlsx` e baixe a versão final com Quadro Resumo")

arquivo = st.file_uploader("Selecione o arquivo Excel", type=["xls", "xlsx"])

if arquivo:
    try:
        extensao = arquivo.name.split('.')[-1].lower()
        if extensao == 'xls':
            df = pd.read_excel(arquivo, engine='xlrd')
        else:
            df = pd.read_excel(arquivo, engine='openpyxl')

        df_formatado, resumo = formatar_planilha(df)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_formatado.to_excel(writer, index=False, sheet_name='Planilha Formatada')
            resumo.to_excel(writer, index=False, sheet_name='Quadro Resumo')

        st.success("✅ Arquivo formatado com sucesso!")
        st.download_button(
            label="📥 Baixar arquivo com Quadro Resumo",
            data=output.getvalue(),
            file_name="P8Pxls_formatado_financeiro.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
