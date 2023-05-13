# Script to manage bot process
BOT_DIR="/root/WarehouseBot"
BOT_CMD="(cd $BOT_DIR && source /root/.venv/bin/activate && python3.10 -m app)"

BOT_PID_FILE="/root/WarehouseBot/bot.pid"
BOT_LOG_FILE="/root/WarehouseBot/bot.log"

case "$1" in
   start)
       echo "Starting bot process..."
       nohup bash -c "$BOT_CMD" >> $BOT_LOG_FILE 2>&1 &
       echo $! > $BOT_PID_FILE
       ;;
   stop)
       if [ -f $BOT_PID_FILE ]; then
           echo "Stopping bot processes..."
           pkill -f "python3.10 -m app"
           rm $BOT_PID_FILE
       else
           echo "Bot process not running!"
       fi
       ;;
   stop-all)
       echo "Stopping all related processes..."
       pkill -f "python3.10 -m app"
       ;;
   restart)
       $0 stop
       sleep 2
       $0 start
       ;;
   status)
       if [ -f $BOT_PID_FILE ]; then
           echo "Bot.sh main process is running (PID $(cat $BOT_PID_FILE))."
       else
           echo "Bot.sh main process is not running."
       fi
       echo "Related processes:"
       pgrep -f "python3.10 -m app"
       ;;
   *)
       echo "Usage: $0 {start|stop|restart|status}"
       exit 1
       ;;
esac

exit 0