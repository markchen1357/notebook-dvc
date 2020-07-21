import extract

stage_count, stages, imports= extract.extract_cells('housing.ipynb')
if stage_count != len(stages):
    print('error')
print(stages)
print(imports)

