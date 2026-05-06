import gspread
import csv
import sys

# ⭐️ เพิ่ม sheet_name เข้ามารับค่า
def upload_to_sheets(csv_file_path, sheet_name):
    gc = gspread.service_account(filename='credentials.json')
    
    # ⭐️ เอา URL ไฟล์ใหม่ มาใส่ตรงนี้!
    SHEET_URL = ''
    sh = gc.open_by_url(SHEET_URL)
    
    # ⭐️ สั่งให้มันเปิดชีตตามชื่อที่เราส่งมา
    worksheet = sh.worksheet(sheet_name)

    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)

    if len(data) > 0:
        cols_to_remove = [i for i, col in enumerate(data[0]) if col.strip().lower() == 'p']
        for row in data:
            for i in sorted(cols_to_remove, reverse=True):
                if i < len(row):
                    del row[i]

        if 'Global' in data[0]:
            global_idx = data[0].index('Global')
            for row in data:
                if len(row) > global_idx:
                    global_val = row.pop(global_idx) 
                    if global_val.strip() == "":
                        global_val = "0.0"
                    row.insert(2, global_val)

    if len(data) > 1:
        header = data[0]
        
        if "Max Possible Score" in str(data[1]):
            max_row = data[1]
            student_data = data[2:]
        else:
            max_row = []
            student_data = data[1:]

        student_data.sort(key=lambda x: x[0])

        for row in student_data:
            for i in range(len(row)):
                if row[i].strip() == "":
                    row[i] = "0.0"

        new_header = ['#'] + header
        new_max_row = [''] + max_row if max_row else []
        
        new_student_data = []
        for index, row in enumerate(student_data):
            new_student_data.append([str(index + 1)] + row)

        if new_max_row:
            sorted_data = [new_header, new_max_row] + new_student_data
        else:
            sorted_data = [new_header] + new_student_data
    else:
        sorted_data = data 

    worksheet.clear()
    worksheet.update(sorted_data)
    print(f"อัปโหลดคะแนนลงชีต '{sheet_name}' เรียบร้อย!")

if __name__ == '__main__':
    # ⭐️ เช็คว่าต้องใส่ parameter 2 ตัว (ไฟล์ csv กับ ชื่อชีต)
    if len(sys.argv) < 3:
        print("วิธีใช้: python3 upload_sheets.py <path_ของไฟล์_csv> <ชื่อชีตที่ต้องการอัปโหลด>")
        sys.exit(1)
        
    csv_path = sys.argv[1]
    sheet_name = sys.argv[2]
    upload_to_sheets(csv_path, sheet_name)