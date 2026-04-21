
Replace the files at
(Make backups first if unsure)

[UPDATE 2025-04-15] joinedload submissions to avoid lazy loading on every score calc in main.py
[UPDATE 2025-04-18] fix css display of 100/100 score becoming yellow b/c of floating point scores not rounded properly

<ROOT_CMS_DIR>/cms/server/contest/handlers/main.py
<ROOT_CMS_DIR>/cms/server/contest/templates/overview.html
<ROOT_CMS_DIR>/cms/server/contest/static/cws_style.css

(use the unmodified <ROOT_CMS_DIR>/cms/server/contest/handlers/contest.py)

Might need to ctrl-f5 or shift-f5 to force reload the css on browsers.

#Patched by kk@CSCMU
