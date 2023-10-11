check_pattern()
{
	txt="$1"
	pattern="$2"
	file="$3"
	level="$4"
	/bin/egrep "$pattern" "$file"| /usr/bin/wc -l|/bin/awk -v LV="$level" -vtxt="$txt" '{if($1 ==LV) {status="GREEN"}else {status="RED"} END{ printf("%s,%s,%s,%s\n", txt,$1,LV,status)}'
}


check_pattern2()
{
	txt="$1"
	pattern="$2"
	exclude_pt="$3"
	file="$4"
	level="$5"
	/bin/egrep "$pattern" "$file"|grep -vE "exclude_ptn"| /usr/bin/wc -l|/bin/awk -v LV="$level" -v txt="$txt" '{if($1 ==LV) {status="GREEN"}else {status="RED"} END{ printf("%s,%s,%s,%s\n", txt,$1,LV,status)}'
}

check_compare()
{
	txt="$1"
	file_1="$2"
	file_2="$3"
	pattern_1="$4"
	pattern_2="$5"
	exclude_pt_1="$6"
	exclude_pt_2="$7"
	
	cnt_1=$(/bin/egrep "$pattern_1" "$file_1"|grep -vE "exclude_ptn_1"| /usr/bin/wc -l)
	cnt_2=$(/bin/egrep "$pattern_2" "$file_2"|grep -vE "exclude_ptn_2"| /usr/bin/wc -l)
	
	/bin/awk -v c1="$cnt_1" -v c2="$cnt2" -v txt="$txt" '{if(c1 == c2 ) {status="GREEN"}else {status="RED"} END{ printf("%s,%s,%s,%s\n", txt,c1,c2,status)}'
}


check_pattern "xx log check" "pattern" "$LOG_FILE" 10







