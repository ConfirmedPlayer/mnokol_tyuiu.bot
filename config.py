import os


token = os.getenv('MNOKOL_BOT_TOKEN')


api_link = 'https://temnomor.ru/api/groups?group={group}&sid={sid}&gr={gr}'


group_id = 212422399
admin_user_id = 641064938 # Admin commands will work only for ID provided
message_send_url = 'https://api.vk.com/method/messages.send?access_token={token}&v=5.130&peer_id={peer_id}&attachment={attachment}&random_id={random_id}'


schedule_menu_url = 'http://mnokol.tyuiu.ru/rtsp/index2.php'


chrome_path = '/usr/bin/google-chrome'


assert group_id > 0
