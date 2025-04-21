
# Geração do Quadro Resumo com layout institucional padronizado
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

# Salvar quadro resumo com layout perfeito
with pd.ExcelWriter(output_quadro_resumo, engine='xlsxwriter') as writer:
    resumo_df.to_excel(writer, sheet_name='Quadro Resumo', startrow=2, index=False, header=False)
    sheet = writer.sheets['Quadro Resumo']
    workbook = writer.book

    # Estilos
    titulo_fmt = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#B7D4F0',
        'font_size': 12
    })
    header_fmt = workbook.add_format({
        'bold': True,
        'bg_color': '#D9D9D9',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    valor_fmt = workbook.add_format({'num_format': 'R$ #,##0.00'})

    # Título mesclado
    sheet.merge_range('A1:B1', f"Quadro Resumo - {razao_social}", titulo_fmt)
    sheet.write('A2', 'Descrição', header_fmt)
    sheet.write('B2', 'Valor', header_fmt)
    sheet.set_column('A:A', 55)
    sheet.set_column('B:B', 25, valor_fmt)
