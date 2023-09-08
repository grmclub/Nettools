IDENTITYFILE=""
FTP_USER=""
SERVER=""
FTP_DIR=""
DIR_LIST=""
LOGFILE=""
READ_FILE=""
OUTFILE=""

sftp -o Port=22 -o ${IDENTITYFILE} ${FTP_USER}@${SERVER} << EOF > ${DIR_LIST}
	cd $FTP_DIR
	dir
	exit
EOF

	RET_CODE=$?
	if [ $RET_CODE -ne 0 ]; then
		echo -e "Failed to get the ftp dir list ret_code :$RET_CODE"
		exit 5
	fi

	sftp -o Port=22 -o ${IDENTITYFILE} ${FTP_USER}@${SERVER} << EOF > ${LOGFILE}
	cd $FTP_DIR
	get $READ_FILE $OUTFILE
	exit
EOF

	RET_CODE=$?
	if [ $RET_CODE -ne 0 ]; then
		echo -e "Failed to FTP $READ_FILE from $SERVER ret_code :$RET_CODE"
		exit 5
	fi
