from datetime import datetime
import pandas as pd


def compare_excel_files(reference_path: str, target_path: str, save_result: bool = True) -> tuple[str, str]:
    """
    Membandingkan file Excel berdasarkan struktur file acuan (template).

    Args:
        reference_path (str): Path file acuan/template.
        target_path (str): Path file hasil scraping yang ingin dicek.
        save_result (bool): Jika True, hasil akan ditulis kembali ke file target.

    Returns:
        Tuple:
            - Path ke file hasil (biasanya target_path yang di-overwrite)
            - String ringkasan hasil (untuk ditampilkan ke GUI)
    """
    try:
        # Baca file template dan file hasil scraping
        template_df = pd.read_excel(reference_path, dtype=str)
        scraped_df = pd.read_excel(target_path, dtype=str)

        # Tentukan kolom yang akan dibandingkan (mengikuti template)
        compare_columns = list(template_df.columns)

        # Filter scraped agar hanya memiliki kolom-kolom yang ingin dibandingkan
        filtered_scraped_df = scraped_df[compare_columns]

        # Siapkan list untuk hasil per baris
        status_list = []
        status_msg_list = []
        start_time = datetime.now()

        for i in range(len(template_df)):
            if i >= len(filtered_scraped_df):
                status_list.append("MISMATCH")
                status_msg_list.append("Row missing in scraped file")
                continue

            diffs = []
            for col in compare_columns:
                val_ref = template_df.iloc[i][col]
                val_scraped = filtered_scraped_df.iloc[i][col]
                if pd.isna(val_ref) and pd.isna(val_scraped):
                    continue
                if val_ref != val_scraped:
                    # diffs.append(col)
                    diffs.append(f"{col}: expected '{val_ref}', found '{val_scraped}'")

            if diffs:
                status_list.append("MISMATCH")
                status_msg_list.append(", ".join(diffs))
            else:
                status_list.append("MATCH")
                status_msg_list.append("OK")

        # Tambahkan kolom hasil ke scraped_df
        scraped_df['STATUS'] = status_list
        scraped_df['STATUSMSG'] = status_msg_list
        scraped_df['STARTTIME'] = start_time
        scraped_df['ENDTIME'] = datetime.now()
        scraped_df['SCRAPINGSTATUS'] = "PROCESSED"

        # Simpan ke file (overwrite target)
        output_path = target_path
        if save_result:
            scraped_df.to_excel(output_path, index=False)

        # Buat log teks ringkasan
        log_lines = [
            f"Row {idx + 1}: {status} - {msg}"
            for idx, (status, msg) in enumerate(zip(status_list, status_msg_list))
        ]
        log_text = "\n".join(log_lines)

        return output_path, log_text

    except Exception as e:
        raise RuntimeError(f"Comparison failed: {str(e)}")
