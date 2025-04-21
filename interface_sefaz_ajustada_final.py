
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

# Simulação de geração e download
if arquivo:
    st.success("✅ Arquivos gerados com sucesso!")

    buffer1 = BytesIO()
    pd.DataFrame({'Exemplo': [1, 2]}).to_excel(buffer1, index=False)
    st.download_button("📥 Baixar Planilha Formatada + Quadro Resumo", buffer1.getvalue(), file_name="Planilha_Formatada.xlsx")

    buffer2 = BytesIO()
    pd.DataFrame({'Inscrição': [123], 'CNPJ': ['00000000000100'], 'Data': ['01/01/2024'], 'ICMS Débito': [1234.56]}).to_excel(buffer2, index=False)
    st.download_button("📥 Baixar GFIS_LBM_COMERCIO_E_SERVICOS_LTDA.xls", buffer2.getvalue(), file_name="GFIS_LBM_COMERCIO_E_SERVICOS_LTDA.xls")

# Rodapé
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;font-size:small;color:grey;'>"
    "Governo do Estado do Maranhão - SEFAZ | © 2025</div>",
    unsafe_allow_html=True
)
