from docxtpl import DocxTemplate
import pandas as pd
import os

def generate_letters_from_excel(excel_path: str, template_path: str, output_dir: str):
    df = pd.read_excel(excel_path, dtype=str)
    df.rename(columns=lambda x: x.replace(" ", "_"), inplace=True)
    os.makedirs(output_dir, exist_ok=True)

    for index, row in df.iterrows():
        doc = DocxTemplate(template_path)
        context = row.to_dict()  # Isi variabel Word dengan data per baris

        doc.render(context)

        filename = f"Surat_{row.get('Nama_Nasabah', 'User')}_{index+1}.docx"
        output_path = os.path.join(output_dir, filename)
        doc.save(output_path)

    return f"{len(df)} surat berhasil dibuat di folder: {output_dir}"