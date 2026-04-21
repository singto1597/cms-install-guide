#!/bin/bash

BASE_DIR="$HOME/parse_subs"
SRC_DIR="$HOME/submissions/204xxx/AllSec"
BY_TASK_DIR="$HOME/submissions/204xxx/ByTask"
REPORT_DIR="$BASE_DIR/web_reports"
PORT=8000

echo "[1/4] ดึงข้อมูลการส่งล่าสุดจาก CMS..."
cd "$BASE_DIR" || exit
./update_submissions.sh

echo "[2/4] จัดระเบียบไฟล์แยกตามโจทย์"
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

echo "[3/4] สแกนลอกโค้ดและสร้างหน้าเว็บ Dashboard..."
rm -rf "$REPORT_DIR"
mkdir -p "$REPORT_DIR"

cat <<EOF > "$REPORT_DIR/index.html"
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMTE Grader - Plagiarism Report</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 40px 20px; }
        .container { max-width: 900px; margin: auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); }
        h1 { color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 15px; margin-top: 0; text-align: center; text-transform: uppercase; letter-spacing: 1px; }
        .update-time { text-align: center; color: #7f8c8d; margin-bottom: 30px; font-weight: bold; }
        .task-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
        .task-card { background: #ffffff; border: 1px solid #e1e8ed; border-radius: 8px; padding: 25px 20px; text-align: center; transition: all 0.3s ease; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
        .task-card:hover { transform: translateY(-5px); box-shadow: 0 12px 20px rgba(0,0,0,0.1); border-color: #e74c3c; }
        .task-title { font-size: 1.1em; font-weight: bold; margin-bottom: 20px; color: #34495e; word-break: break-all; }
        .btn { text-decoration: none; background-color: #3498db; color: white; padding: 10px 20px; border-radius: 20px; font-size: 0.9em; font-weight: bold; transition: background 0.3s; display: inline-block; }
        .btn:hover { background-color: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ระบบตรวจสอบการลอกโค้ด (Copydetect)</h1>
        <div class="update-time">อัปเดตข้อมูลล่าสุด: $(date "+%d/%m/%Y เวลา %H:%M:%S")</div>
        <div class="task-grid">
EOF

for task_path in "$BY_TASK_DIR"/*; do
    if [ -d "$task_path" ]; then
        task_name=$(basename "$task_path")
        echo "   กำลังสแกนข้อ: $task_name..."

        copydetect -t "$task_path" -e cpp -d 0.5 -O "$REPORT_DIR/$task_name" --disable-autoopen > /dev/null 2>&1

        cat <<EOF >> "$REPORT_DIR/index.html"
            <div class="task-card">
                <div class="task-title">โจทย์: $task_name</div>
                <a href="$task_name.html" class="btn">🔍 ดูรายงาน</a>
            </div>
EOF
    fi
done

cat <<EOF >> "$REPORT_DIR/index.html"
        </div>
    </div>
</body>
</html>
EOF

echo "⚡ [4/4] จัดการ Web Server..."
if ! lsof -i:$PORT -t >/dev/null 2>&1; then
    echo "   กำลังเปิด Web Server $PORT..."
    nohup python3 -m http.server $PORT --directory "$REPORT_DIR" > "$BASE_DIR/server.log" 2>&1 &
    echo "   Web Server เริ่มทำงานแล้ว"
else
    echo "   Web Server ทำงานอยู่ที่พอร์ต $PORT อยู่แล้ว"
fi


echo "Success"
echo "สามารถเข้าได้ที่ IP_Server:$PORT"