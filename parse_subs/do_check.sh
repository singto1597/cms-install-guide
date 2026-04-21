#!/bin/bash

SRC_DIR="$HOME/submissions/204xxx/AllSec"
BY_TASK_DIR="$HOME/submissions/204xxx/ByTask"
REPORT_DIR="$HOME/parse_subs/web_reports"

echo "[1/3] แยกตามโจทย์..."
rm -rf "$BY_TASK_DIR"
mkdir -p "$BY_TASK_DIR"

find "$SRC_DIR" -type f -name "*.cpp" ! -name "*.HIS.*" | while read filepath; do
    filename=$(basename "$filepath")
    user_dir=$(basename $(dirname "$filepath"))
    
    name_no_ext="${filename%.cpp}"
    task_id="${name_no_ext%_$user_dir}"
    
    mkdir -p "$BY_TASK_DIR/$task_id"
    cp "$filepath" "$BY_TASK_DIR/$task_id/${user_dir}.cpp"
done

echo "[2/3] กำลังสร้างหน้าเว็บ Dashboard..."
rm -rf "$REPORT_DIR"
mkdir -p "$REPORT_DIR"

cat <<EOF > "$REPORT_DIR/index.html"
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SMTE Grader - Plagiarism Report</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f4f4f9; }
        .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 15px 0; font-size: 18px; }
        a { text-decoration: none; color: #007bff; font-weight: bold; padding: 10px 15px; border: 1px solid #007bff; border-radius: 5px; display: inline-block; transition: 0.3s; }
        a:hover { background-color: #007bff; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 ระบบตรวจจับการคัดลอกโค้ด (แยกตามข้อ)</h1>
        <ul>
EOF

echo "[3/3] กำลังสแกนหาคนลอกข้อสอบ..."

for task_path in "$BY_TASK_DIR"/*; do
    if [ -d "$task_path" ]; then
        task_name=$(basename "$task_path")
        echo "   -> สแกนข้อ: $task_name"
        
        copydetect -t "$task_path" -e cpp -d 0.5 -O "$REPORT_DIR/$task_name" --disable-autoopen > /dev/null 2>&1
        
        echo "            <li><a href='$task_name.html'>🔍 ดูรายงานข้อ: $task_name</a></li>" >> "$REPORT_DIR/index.html"
    fi
done

echo "        </ul></div></body></html>" >> "$REPORT_DIR/index.html"

echo "Success! "
