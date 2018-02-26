cd /home/pixiv_top10
if $1
    DATE = $1
else
    DATE=$(date -d last-day +%Y%m%d)
fi
python3 pixivWithDate.py $DATE
qshell quaload 10 /root/qshell.conf