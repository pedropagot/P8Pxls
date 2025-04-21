
import streamlit as st
import pandas as pd
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Conversor P8Pxls - SEFAZ-MA",
    page_icon="🧾",
    layout="centered"
)

# Imagens do brasão (via GitHub do usuário)
URL_BRASAO = "https://raw.githubusercontent.com/pedropagot/P8Pxls/main/brasao.png"

# Topo institucional moderno
st.markdown(f'''
    <div style="background-color:#002147;padding:25px 10px;border-radius:6px;text-align:center;">
        <img src="{URL_BRASAO}" style="height:80px;margin-bottom:10px;" />
        <h1 style="color:white;margin:0;font-size:36px;">SEFAZ</h1>
        <h2 style="color:white;margin:0;font-size:20px;">SECRETARIA DE ESTADO DA FAZENDA - MA</h2>
        <h3 style="color:#DCE6F5;font-weight:normal;font-size:18px;margin-top:10px;">
            FISCALIZAÇÃO DE MERCADORIAS EM TRÂNSITO
        </h3>
    </div>
''', unsafe_allow_html=True)

st.markdown("## Conversor P8Pxls 🧾📊")
st.markdown("### Envie seu arquivo `.xls` ou `.xlsx` e baixe os arquivos gerados")

# Upload
arquivo = st.file_uploader("Selecione o arquivo Excel", type=["xls", "xlsx"], label_visibility="collapsed")

# Simulação de geração e download (substituir pelo processamento real)
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
    "Governo do Estado do Maranhão - SEFAZ/MA | © 2025</div>",
    unsafe_allow_html=True
)
