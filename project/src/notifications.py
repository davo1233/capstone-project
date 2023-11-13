from src.auth import check_token
from src.data import NotificationIn
from src.database import Session,lookup_username_db,get_notifications_db,add_notifications_db
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()

def get_notifs(token:str, db:Session):
    username = check_token(token)
    u_id = lookup_username_db(db, username)
    return get_notifications_db(db,u_id)

def add_notifications(db, notificationData:NotificationIn):
    return add_notifications_db(db, notificationData)

def create_notification_reminder(db, due_date, reminder_time, project_id,taskInfo,message):
    reminder_datetime = due_date - reminder_time
    scheduler.add_job(send_reminder, 'date', run_date=reminder_datetime, args=[db,taskInfo.assignee,message], id = project_id)

def remove_notification_reminder(task_notif_id):
    scheduler.remove_job(task_notif_id)

def send_reminder(db, user_id, message):
    notifData = {
        'user_id': user_id,
        'message': message,
    }
    add_notifications(db, notifData)