cd /home/pixiv_top10
if [ "$1" ]
then
    DATE="$1"
else
    DATE=$(date -d last-day +%Y%m%d)
fi
python3 pixivWithDate.py $DATE
qshell qupload 10 /root/qshell.conf