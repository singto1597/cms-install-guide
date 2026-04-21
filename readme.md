# ไกด์การติดตั้งระบบ Contest Management System (CMS) เกรดเดอร์

## System Requests
เพื่อให้การติดตั้งและรัน CMS แนะนำให้เตรียมเครื่องเซิร์ฟเวอร์ขั้นต่ำตามสเปคนี้:

### 🖥️ Environment (สภาพแวดล้อม)
* **OS:** **Ubuntu Server 24.04 LTS** (แนะนำเวอร์ชั่นนี้เพราะมี Python 3.12 เป็นค่าเริ่มต้น ติดตั้งแบบ Live Server ไม่ต้องลง GUI)
* **Platform:** เครื่อง Bare Metal หรือ **Virtual Machine (VM)** ก็ได้ เช่น Proxmox, VMware, VirtualBox 
*(หมายเหตุ: ไม่แนะนำให้ใช้ LXC Container เพราะอาจจะมีปัญหาเรื่อง Permission ของ `cgroup` ที่ต้องใช้ทำ Sandbox ตรวจโค้ด แนะนำให้สร้าง VM ใหม่ จะเป็นทางที่ดีที่สุด)*
* **User:** บัญชีใช้งานธรรมดาที่มีสิทธิ์ `sudo`

### ⚙️ Hardware Specs (สเปคขั้นต่ำที่แนะนำ)
* **CPU:** 2 Cores ขึ้นไป *(แนะนำ 4-8 Cores: เพราะระบบจะสร้าง Worker ตรวจโค้ดตามจำนวน Core CPU ยิ่งเยอะยิ่งตรวจข้อสอบพร้อมกันได้ไว)*
* **RAM:** 4 GB ขั้นต่ำ *(แนะนำ 8 GB ขึ้นไป เพื่อรองรับการทำงานของ Database, Web Server และเผื่อให้ Sandbox คอมไพล์โค้ดแบบไม่ค้าง)*
* **Storage:** 30 GB ขึ้นไป *(แนะนำ SSD เผื่อพื้นที่ให้ OS, ฐานข้อมูล PostgreSQL และไฟล์ซอร์สโค้ดของคนส่ง)*

### 🌐 Network & Access
* อินเทอร์เน็ตที่เสถียร 
* หากตั้งใจจะเปิดให้คนภายนอกเข้าใช้งาน ต้องสามารถเข้าถึง / Forward Port `8888` (หน้าผู้เข้าแข่งขัน), `8889` (หน้าแอดมิน) และ `8890` (หน้าคะแนน) ได้

## แผนการติดตั้ง CMS 

### Step 1: ลง Dependencies
```bash
sudo apt-get update
sudo apt-get install build-essential openjdk-11-jdk-headless fp-compiler \
    postgresql postgresql-client python3.12 cppreference-doc-en-html \
    cgroup-lite libcap-dev zip python3.12-dev libpq-dev libcups2-dev \
    libyaml-dev libffi-dev python3-pip python3.12-venv nginx-full
```

### Step 2: เตรียมระบบ
1. โคลนโฟลเดอร์มาก่อน: `git clone --recursive https://github.com/cms-dev/cms.git`
3. เข้าไปในโฟลเดอร์: `cd cms`
2. ย้อน commit
```bash
git checkout v1.5.1
git submodule update --init
```
4. รันสคริปต์: `sudo python3 prerequisites.py install`
*(สคริปต์นี้จะจัดการสร้างกลุ่ม `cmsuser`, คอมไพล์ sandbox และจัดการเรื่องภาษาให้ แค่ตอบ Y ตอนมันถาม)*
5. **แอดตัวเองเข้ากลุ่ม:** พิมพ์คำสั่ง `sudo usermod -a -G cmsuser $(whoami)` เพื่อแอดตัวเองเข้ากลุ่ม แล้ว Logout / Login VM ใหม่ 1 รอบ

### Step 3: ติดตั้ง CMS
1. สร้าง venv: `python3 -m venv ~/cms_venv`
2. เปิดใช้งาน venv: `source ~/cms_venv/bin/activate` *(จะมี `(cms_venv)` โผล่มาหน้า terminal)*
3. ติดตั้ง Dependencies ใน venv: `pip install -r requirements.txt`
4. ติดตั้งตัว CMS: `pip install .`

### Step 4: Database
1. เข้าไปสร้าง DB: `sudo -u postgres psql`
2. พิมพ์คำสั่ง SQL ทีละบรรทัด:
```sql
CREATE ROLE cmsuser WITH LOGIN PASSWORD 'ตั้งรหัสผ่านตรงนี้';
CREATE DATABASE cmsdb OWNER cmsuser;
ALTER SCHEMA public OWNER TO cmsuser;
GRANT SELECT ON pg_largeobject TO cmsuser;
\q
```
3. ไปแก้ไฟล์ `cms.conf` (หรือ `cms.toml` ในเวอร์ชั่นใหม่) ให้ชี้ url มาที่ DB ตัวนี้ Path จะอยู่ที่ `/usr/local/etc/cms.conf` แล้วรัน `cmsInitDB` (ต้องทำตอน activate venv อยู่)
**จุดที่แก้**
```conf
"database": "postgresql+psycopg2://cmsuser:your_password_here@localhost:5432/cmsdb",
```

**ถ้าติดปัญหา cmsInitDB**
ถอยกลับ version setuptools
```bash
pip uninstall setuptools -y
pip install "setuptools<70"
cmsInitDB
```

### Step 5: Init System
1. สร้าง Admin: 
```bash
source ~/cms_venv/bin/activate
cmsAddAdmin <admin_username> -p <admin_password>
```
2. ทดสอบรัน
**จอที่ 1 เปิด Log Service รอรับข้อมูล:**
```bash
source ~/cms_venv/bin/activate
cmsLogService
```
**จอที่ 2 เปิด Resource Service เพื่อปลุกทุกระบบของ CMS:**
```bash
source ~/cms_venv/bin/activate
cmsResourceService -a ALL
```

**ลองเข้าหน้าเว็บ**
* หน้า Admin: `http://<IP_ของ_VM>:8889` (ลองล็อกอินด้วยรหัสที่สร้างไว้)

* หน้า Contest: `http://<IP_ของ_VM>:8888`

* หน้า Ranking: `http://<IP_ของ_VM>:8890`


## ทำรันออโต้ 

### 1. Log Service:
```bash
sudo nano /etc/systemd/system/cms-log.service
```
ใส่โค้ดนี้:
```ini
[Unit]
Description=CMS Log Service
Requires=postgresql.service
After=postgresql.service

[Service]
Type=simple
User=singto1597
ExecStart=/home/singto1597/cms_venv/bin/cmsLogService
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 2. Resource Service (ตัวจัดการ Worker):
```bash
sudo nano /etc/systemd/system/cms-resource.service
```
ใส่โค้ดนี้:
```ini
[Unit]
Description=CMS Resource Service
Requires=cms-log.service postgresql.service
After=cms-log.service postgresql.service

[Service]
Type=simple
User=singto1597
ExecStart=/home/singto1597/cms_venv/bin/cmsResourceService -a ALL
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 3. Ranking Service:
```bash
sudo nano /etc/systemd/system/cms-ranking.service
```
ใส่โค้ดนี้:
```ini
[Unit]
Description=CMS Ranking Service
Requires=cms-log.service postgresql.service
After=cms-log.service postgresql.service

[Service]
Type=simple
User=singto1597
ExecStart=/home/singto1597/cms_venv/bin/cmsRankingWebServer
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

พอสร้างเสร็จ 3 ไฟล์ รันคำสั่งนี้เพื่อเปิดใช้งานตอนเปิดเครื่อง:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cms-log cms-resource cms-ranking
sudo systemctl start cms-log cms-resource cms-ranking
```

---

## ติดตั้ง Score Overview

เนื่องจากอาจารย์มหาวิทยาลัยเชียงใหม่ มีการแก้ไขระบบหลังบ้าน (ดึงคะแนน) และแสดงผลที่ Overview จึงเอาไฟล์ของอาจารย์มาอัปเดตใส่ CMS ของเรา เพื่อให้การดูคะแนนง่ายขึ้น

### 1. นำไฟล์ของอาจารย์ไปวางทับใน Source Code
เข้าไปที่โฟลเดอร์ `~/cms` แล้วเอาไฟล์ของอาจารย์ `overview_score_patch_cms1.5_CSCMU` ไปวางทับตาม Path นี้:
* `~/cms/cms/server/contest/handlers/main.py`
* `~/cms/cms/server/contest/templates/overview.html`
* `~/cms/cms/server/contest/static/cws_style.css`

### 2. อัปเดตเข้าระบบ (Re-install)
เพื่อให้ระบบรู้จักโค้ดใหม่ที่เพิ่งเอาไปทับ ต้องรันคำสั่งติดตั้งซ้ำอีกรอบใน venv:
```bash
cd ~/cms
source ~/cms_venv/bin/activate
pip install .
```

### 3. รีสตาร์ท Service
```bash
sudo systemctl restart cms-resource
```
*(หมายเหตุ: หากหน้าเว็บสียังไม่เปลี่ยน ให้กด `Ctrl + F5`, `Shift + F5` หรือ `Ctrl + Shift + R` เพื่อเคลียร์แคชบนเบราว์เซอร์)*




## ติดตั้งระบบตรวจจับการคัดลอก (Copydetect Dashboard)

ระบบนี้จะใช้สคริปต์ดึงไฟล์ข้อสอบจาก CMS มาตรวจการลอกโค้ด และสร้างหน้าเว็บ Dashboard สรุปผลให้ที่พอร์ต 8000

### 1. เตรียมโฟลเดอร์และแพ็กเกจ
นำโฟลเดอร์ `parse_subs` มาวางไว้ที่ `~/parse_subs` 
```bash
rsync -avz /full_path/parse_subs user@ip_addr:/home/user/parse_subs/
```
จากนั้นติดตั้งเครื่องมือที่จำเป็น (ทำใน venv):
```bash
source ~/cms_venv/bin/activate
pip install copydetect psycopg2-binary
```

### 2. แก้ไขลิงค์ Database 
แก้ password ที่ใส่ไปก่อนหน้านั้นในไฟล์ cms.conf (ของ parse_subs ไม่ใช่ของ cms)
```conf
  "database": "postgresql://cmsuser:yourpassword@localhost:5432/cmsdb"
```

### 3. รันสคริปต์ตรวจจับลอกโค้ด
เมื่อต้องการตรวจ ให้รันสคริปต์ตัวหลัก (Master Script):
```bash
cd ~/parse_subs
./master_check.sh
```

### ที่มาของ Scripts
สคริปต์นี้เป็นของอาจารย์มหาวิทยาลัยเชียงใหม่ เช่นเคย ซึ่ง ผมได้นำมาเขียนสคริปต์เพิ่มเติมบางส่วน เพื่อให้การตรวจสอบสามารถแยกโจทย์ได้