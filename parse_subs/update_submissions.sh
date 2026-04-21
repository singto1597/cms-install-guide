#!/usr/bin/env bash
# @Author: kitt k
# @Date:   2021-08-26
# @Last Modified by:   kitt k
# @Last Modified time: 2025-06-15 05:41:16

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

CLASS="${1:-204xxx}"
EXT="${2:-unk}"
RAW_DIR="${RAW_DIR:-/var/local/lib/cms/submissions/}"

# CLASS="CMUTOI"
# RAW_DIR="/var/local/lib/cms/submissions_ALL/"

# CONTEST_ID="0"

FETCH_HIST=true
DEBUG=false
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"/

RUNNER=""
if ! python3 -c "import psycopg2" &> /dev/null; then
    RUNNER="uv run"
fi

echo RAW_DIR $RAW_DIR

DST_DIR="/home/$(whoami)/submissions/$CLASS/AllSec/"
TMP_DIR="/tmp/submissions_parsed/"


FILE_LIST="$DST_DIR""$CLASS"_file_list.txt
OLD_FILE_LIST=$FILE_LIST".old"
CHG_FILE="$DST_DIR""$CLASS"_file_change.txt
CONTEST_TASK_MAP_FILE="$DST_DIR""$CLASS"_contest_task_map.txt

$RUNNER "$SCRIPTPATH""contest_name_id.py" > "$CONTEST_TASK_MAP_FILE"

# REMOVE_COMMENTS=true

rm -rq "$TMP_DIR" 2> /dev/null
mkdir -p "$TMP_DIR"


if [ ! -d "$DST_DIR" ]; then

    mkdir -p "$DST_DIR"
    chmod +rwx "$DST_DIR"
fi


rsync -t -q -av -f"+ */" -f"- *" "$RAW_DIR" "$DST_DIR"
find "$DST_DIR"

touch "$OLD_FILE_LIST"
find "$RAW_DIR" -type f | sort > "$FILE_LIST"

/usr/bin/diff "$FILE_LIST" "$OLD_FILE_LIST" | grep '<' | awk -F'< ' '{print $2}' | sort > "$CHG_FILE"


if [[ $(/usr/bin/wc -l < "$CHG_FILE") -eq 0 ]];
then
    echo "nothing changed"
    # "$pythonCommand" "$pythonScript" "$outFile"
    exit 0
fi

while read line;
do
    echo "$line"
    user_id="$(basename "$(dirname "$line")")"
    echo "user_id" "$user_id"
    time_string=$(date +%s)
    echo "time_string" "$time_string"
    raw_out=$($RUNNER "$SCRIPTPATH""decode.py" "$line" "$user_id" "$time_string" "$EXT")
    echo "$raw_out"
    stringarray=($raw_out)

    task_id="${stringarray[0]}"
    EXT="${stringarray[1]}"

    # file_path_src="$(dirname "$line")"
    file_path_dst="$DST_DIR""$user_id"/

    base_filename="$task_id"_"$user_id"

    if [ "$DEBUG" = true ] ; then
        echo "$user_id"
        echo "$task_id"
        echo "$base_filename"
    fi

    new_filename="$base_filename".$EXT
    new_filename_BAK="$base_filename".HIS.$EXT
    # #list the file today w/ time stamp

    mv "$base_filename"_"$time_string".RAW "$TMP_DIR""$new_filename"
    # ls -al "$TMP_DIR""$new_filename"


    touch -r "$line" "$TMP_DIR""$new_filename"

    cp -p "$TMP_DIR""$new_filename" "$file_path_dst"

    if [ "$DEBUG" = true ] ; then
        echo "$file_path_dst""$new_filename"
    fi
    if [ "$FETCH_HIST" = true ] ; then
        hist_file="$file_path_dst""$new_filename_BAK"
        cp -p "$TMP_DIR""$new_filename" "$hist_file"
        mv --backup=t "$TMP_DIR""$new_filename"  "$hist_file"
        rm "$hist_file"
    else
        rm "$TMP_DIR""$new_filename"
    fi


    # exit

done < "$CHG_FILE"

rm -r $TMP_DIR
rsync -t -q -av -f"+ */" -f"- *" "$RAW_DIR" "$DST_DIR"
mv "$FILE_LIST" "$OLD_FILE_LIST"
