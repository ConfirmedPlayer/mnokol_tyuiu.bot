import os


token = os.getenv('MNOKOL_BOT_TOKEN')


api_link = 'https://temnomor.ru/api/groups?group={group}&sid={sid}&gr={gr}'


group_id = 212422399
admin_user_id = 641064938  # Admin commands will work only for ID provided


schedule_menu_url = 'http://mnokol.tyuiu.ru/rtsp/index2.php'


chrome_path = '/usr/bin/google-chrome'


db = 'MNOKOL_DB'
db_user = os.getenv('postgresql_user')
db_password = os.getenv('postgresql_password')
db_host = '127.0.0.1'


assert group_id > 0
