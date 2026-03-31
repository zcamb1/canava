#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script: Excel -> CSV
- Đọc toàn bộ nội dung từ file Excel (.xlsx)
- Export ra CSV với encoding chuẩn (utf-8-sig)
- Giữ nguyên dữ liệu (không bị mất số 0, format...)
"""

import pandas as pd
import os
import sys


def convert_excel_to_csv(input_file, output_file):
    try:
        print(f"📥 Đang đọc file Excel: {input_file}")

        # Đọc sheet đầu tiên, ép tất cả về string để giữ nguyên dữ liệu
        df = pd.read_excel(input_file, sheet_name=0, dtype=str)

        print(f"📊 Số dòng: {len(df)}, Số cột: {len(df.columns)}")

        print(f"💾 Đang ghi ra CSV: {output_file}")

        # Xuất CSV với encoding chuẩn
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print("✅ Export thành công!")

    except FileNotFoundError:
        print(f"❌ Không tìm thấy file: {input_file}")
    except Exception as e:
        print(f"❌ Lỗi xảy ra: {e}")


def main():
    # Nếu truyền tham số từ command line
    if len(sys.argv) >= 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        # Default file name
        input_file = "input.xlsx"
        output_file = "output.csv"

    # Kiểm tra file tồn tại
    if not os.path.exists(input_file):
        print(f"❌ File không tồn tại: {input_file}")
        return

    convert_excel_to_csv(input_file, output_file)


if __name__ == "__main__":
    main()
