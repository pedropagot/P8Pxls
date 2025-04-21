
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import re

# Configuração da página
st.set_page_config(
    page_title="SEFAZ-MA - Fiscalização de Mercadorias",
    page_icon="🛃",
    layout="centered"
)

# URLs das imagens hospedadas no GitHub
URL_BRASAO = "https://raw.githubusercontent.com/pedropagot/P8Pxls/main/brasao.png"
URL_BANDEIRA = "https://raw.githubusercontent.com/pedropagot/P8Pxls/main/bandeira.png"

# Cabeçalho institucional
st.markdown(f"""
    <div style='text-align: center; margin-bottom: 15px;'>
        <img src="{URL_BRASAO}" width="120" style='margin-bottom: 0;'>
        <h2 style='margin-top: 0;'>SECRETARIA DE ESTADO DA FAZENDA - MA</h2>
        <h3 style='color: #004080;'>FISCALIZAÇÃO DE MERCADORIAS EM TRÂNSITO</h3>
    </div>
    <hr style='border: 1px solid #004080;'>
""", unsafe_allow_html=True)

# Upload
st.markdown("### 📤 Envie o arquivo Excel para processamento")
arquivo = st.file_uploader("Selecione um arquivo .xls ou .xlsx", type=["xls", "xlsx"])

def formatar_planilha(df):
    if 'Data_5' in df.columns:
        df.rename(columns={'Data_5': 'Data do TVI'}, inplace=True)

    df['Data do TVI'] = pd.to_datetime(df['Data do TVI'], errors='coerce')
    df['Valor do Produto'] = pd.to_numeric(df['Valor do Produto'], errors='coerce').fillna(0)
    df['BC + 50%'] = df['Valor do Produto'] * 1.5

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

    df['Aliq Interna'] = df['Data do TVI'].map(calcular_aliquota)
    df['Valor do ICMS'] = pd.to_numeric(df['Valor do ICMS'], errors='coerce').fillna(0)
    df['ICMS Débito'] = df['BC + 50%'] * df['Aliq Interna'] - df['Valor do ICMS']

    soma_icms_debito = df['ICMS Débito'].sum()
    multa = soma_icms_debito / 2
    total_com_multa = soma_icms_debito + multa

    resumo = pd.DataFrame({
        'Descrição': [
            '',
            f'Quadro Resumo - {df["Razão_4"].dropna().unique()[0]}',
            '',
            'Valor total dos produtos',
            'BC Aplicada - Base de Cálculo + 50%',
            'ICMS Débito = Alíquota x BC',
            'Crédito de ICMS destacado em NF-e',
            'Valor ICMS a recolher',
            'Multa de 50%',
            'Total Devido (ICMS a recolher + Multa de 50%)'
        ],
        'Valor': [
            '', '',
            '',
            df['Valor do Produto'].sum(),
            df['BC + 50%'].sum(),
            soma_icms_debito + df['Valor do ICMS'].sum(),
            df['Valor do ICMS'].sum(),
            soma_icms_debito,
            multa,
            total_com_multa
        ]
    })

    return df, resumo

if arquivo:
    try:
        extensao = arquivo.name.split('.')[-1].lower()
        if extensao == 'xls':
            df = pd.read_excel(arquivo, engine='xlrd')
        else:
            df = pd.read_excel(arquivo, engine='openpyxl')

        df_formatado, resumo = formatar_planilha(df)

        output_bytes = BytesIO()
        with pd.ExcelWriter(output_bytes, engine='xlsxwriter') as writer:
            workbook = writer.book

            # Sheet: Planilha Formatada
            df_formatado.to_excel(writer, sheet_name='Planilha Formatada', index=False)
            ws1 = writer.sheets['Planilha Formatada']
            money_fmt = workbook.add_format({'num_format': 'R$ #,##0.00', 'align': 'right'})
            perc_fmt = workbook.add_format({'num_format': '0%', 'align': 'center'})
            header_fmt = workbook.add_format({'bold': True, 'bg_color': '#F2F2F2'})

            for col_num, col in enumerate(df_formatado.columns):
                ws1.write(0, col_num, col, header_fmt)
                if col in ['Valor do Produto', 'Base de Cálculo ICMS', 'Valor do ICMS', 'Valor da NFe', 'ICMS Débito']:
                    ws1.set_column(col_num, col_num, 18, money_fmt)
                elif col in ['BC + 50%', 'Aliq Interna']:
                    ws1.set_column(col_num, col_num, 12, perc_fmt)
                else:
                    ws1.set_column(col_num, col_num, 15)

            # Sheet: Quadro Resumo
            resumo.to_excel(writer, sheet_name='Quadro Resumo', index=False, startrow=3)
            ws2 = writer.sheets['Quadro Resumo']
            ws2.merge_range('A1:B1', resumo.iloc[1, 0], workbook.add_format({'bold': True, 'align': 'center', 'font_size': 14}))
            resumo_header = workbook.add_format({'bold': True, 'bg_color': '#D9D9D9'})
            ws2.write('A4', 'Descrição', resumo_header)
            ws2.write('B4', 'Valor', resumo_header)
            ws2.set_column('A:A', 50)
            ws2.set_column('B:B', 25, money_fmt)
            azul_total = workbook.add_format({'bold': True, 'bg_color': '#B7D4F0', 'num_format': 'R$ #,##0.00'})
            ws2.write('B10', resumo.iloc[-1, 1], azul_total)

        st.success("✅ Processamento concluído. Baixe os arquivos abaixo:")
        st.download_button(
            label="📥 Baixar planilha formatada",
            data=output_bytes.getvalue(),
            file_name="P8Pxls_formatado_financeiro.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Erro: {e}")

# Rodapé
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; font-size: small; color: grey;'>Governo do Estado do Maranhão - SEFAZ/MA | © 2025</div>", unsafe_allow_html=True)
