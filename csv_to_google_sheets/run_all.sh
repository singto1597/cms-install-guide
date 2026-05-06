#!/bin/bash

cd /home/singto1597/Documents/homelab/cms/cms-install-guide/csv_to_google_sheets

rm -rf ./downloads/ranking.csv


echo "กำลังดึงข้อมูล Contest 3..."
./venv/bin/python3 fetch_csv_login.py "" "" "" "1" "./downloads" && \
./venv/bin/python3 upload_sheets.py "./downloads/ranking.csv" "program"


echo "🎉 อัปเดตครบทุกวิชาแล้ว!"