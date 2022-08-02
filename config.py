import os


token = os.getenv('MNOKOL_BOT_TOKEN')


api_link = 'https://temnomor.ru/api/groups?group={group}&sid={sid}&gr={gr}'


group_id = 212422399
admin_user_id = 641064938  # Admin commands will work only for ID provided


schedule_menu_url = 'http://mnokol.tyuiu.ru/rtsp/index2.php'


chrome_path = '/usr/bin/google-chrome'


db_credentials = {
    'host': '127.0.0.1',
    'database': 'mnokol_db',
    'user': os.getenv('postgresql_user'),
    'password': os.getenv('postgresql_password')
}


assert group_id > 0
