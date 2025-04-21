
import streamlit as st
import pandas as pd
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Conversão de TVI em Auto de Infração - SEFAZ",
    page_icon="🧾",
    layout="centered"
)

# Imagem do brasão (via GitHub do usuário)
URL_BRASAO = "https://raw.githubusercontent.com/pedropagot/P8Pxls/main/brasao.png"

# Topo institucional com ajustes refinados
st.markdown(f'''
    <div style="text-align:center; margin-bottom: 10px;">
        <img src="{URL_BRASAO}" style="height:120px;" />
        <h2 style="margin:5px 0 0 0; color:black;">SECRETARIA DE ESTADO DA FAZENDA</h2>
        <h3 style="color:#004080; font-weight:normal; margin:0;">
            FISCALIZAÇÃO DE MERCADORIAS EM TRÂNSITO
        </h3>
    </div>
''', unsafe_allow_html=True)

# Título principal centralizado e com tamanho reduzido
st.markdown(
    "<h4 style='text-align:center; margin-top:30px;'>Conversão de TVI em Auto de Infração</h4>",
    unsafe_allow_html=True
)

# Subtítulo com letra menor
st.markdown(
    "<p style='text-align:center; font-size:14px;'>Envie seu arquivo .xls ou .xlsx e baixe os arquivos gerados</p>",
    unsafe_allow_html=True
)

# Upload
arquivo = st.file_uploader("Selecione o arquivo Excel", type=["xls", "xlsx"], label_visibility="collapsed")

if arquivo:
    try:
        extensao = arquivo.name.split('.')[-1].lower()
        if extensao == 'xls':
            df = pd.read_excel(arquivo, engine='xlrd')
        else:
            df = pd.read_excel(arquivo, engine='openpyxl')

        df_formatado, resumo, gfis, nome_arquivo_gfis = formatar_planilha(df)

        output_principal = BytesIO()
        with pd.ExcelWriter(output_principal, engine='xlsxwriter') as writer:
            df_formatado.to_excel(writer, index=False, sheet_name='Planilha Formatada')
            resumo.to_excel(writer, index=False, sheet_name='Quadro Resumo')

        output_gfis = BytesIO()
        with pd.ExcelWriter(output_gfis, engine='xlsxwriter') as writer:
            gfis.to_excel(writer, index=False, sheet_name='GFIS + Razão_4')

        st.success("✅ Arquivos gerados com sucesso!")

        st.download_button(
            label="📥 Baixar Planilha Formatada + Quadro Resumo",
            data=output_principal.getvalue(),
            file_name="P8Pxls_formatado_financeiro.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.download_button(
            label=f"📥 Baixar {nome_arquivo_gfis}",
            data=output_gfis.getvalue(),
            file_name=nome_arquivo_gfis,
            mime="application/vnd.ms-excel"
        )

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")



        # Gerar Quadro Resumo com título omitido e cabeçalho em A3/B3
        resumo_df = pd.DataFrame({
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
                total_produtos,
                total_bc_mais_50,
                total_icms_debito + total_valor_icms,
                total_valor_icms,
                total_icms_debito,
                multa,
                total_com_multa
            ]
        })

        resumo_df.to_excel(writer, sheet_name='Quadro Resumo', startrow=3, index=False, header=False)
        ws2 = writer.sheets['Quadro Resumo']

        # Estilos
        header_fmt = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D9D9D9',
            'border': 1
        })
        valor_fmt = workbook.add_format({'num_format': 'R$ #,##0.00'})

        # Cabeçalho manual na linha 3
        ws2.write('A3', 'Descrição', header_fmt)
        ws2.write('B3', 'Valor', header_fmt)
        ws2.set_column('A:A', 55)
        ws2.set_column('B:B', 25, valor_fmt)


# Rodapé
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; font-size: small; color: grey;'>"
    "Governo do Estado do Maranhão - SEFAZ/MA | © 2025</div>",
    unsafe_allow_html=True
)
