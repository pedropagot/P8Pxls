
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="SEFAZ-MA - Fiscalização de Mercadorias",
    page_icon="🛃",
    layout="centered"
)

# URLs das imagens hospedadas no GitHub
URL_BRASAO = "https://raw.githubusercontent.com/pedropagot/P8Pxls/main/brasao.png"
URL_BANDEIRA = "https://raw.githubusercontent.com/pedropagot/P8Pxls/main/bandeira.png"

# Estilo customizado
st.markdown(f'''
    <div style="text-align: center; margin-bottom: 15px;">
        <img src="{URL_BRASAO}" width="120" style="margin-bottom: 0;">
        <h2 style="margin-top: 0;">SECRETARIA DE ESTADO DA FAZENDA - MA</h2>
        <h3 style="color: #004080;">FISCALIZAÇÃO DE MERCADORIAS EM TRÂNSITO</h3>
    </div>
    <hr style="border: 1px solid #004080;">
''', unsafe_allow_html=True)

# Upload de arquivo
st.markdown("### 📤 Envie o arquivo Excel para processamento")
arquivo = st.file_uploader("Selecione um arquivo .xls ou .xlsx", type=["xls", "xlsx"])

if arquivo:
    st.success("✅ Arquivo recebido com sucesso. Processamento em andamento...")

    # Aqui entraria o processamento real
    st.download_button("📥 Baixar planilha formatada", data=b"", file_name="P8Pxls_formatado_financeiro.xlsx")
    st.download_button("📥 Baixar GFIS + Nome da Empresa", data=b"", file_name="GFIS_EMPRESA.xls")

# Rodapé
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; font-size: small; color: grey;'>"
    "Governo do Estado do Maranhão - SEFAZ/MA | © 2025</div>",
    unsafe_allow_html=True
)
