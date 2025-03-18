# sentiment-bot
Linux based Discord bot to analyze the current state of the market through the sentiment of investors.

go to discord developer portal and create a new application
head to oauth and get your token, copy it and then assing TOKEN="your token" in a .env file
go to bot tab and enable message content intent
enable developer mode in discord and copy the channel_id you want your bot to read data from
paste it into current_channel="channel_id" in your .env file 
copy channel_id for the channel you want the bot to regularly post updates in
paste it into regular_update_channel="channel_id"
For a debian Based system run "sudo apt-get supervisor
to setup your config/etc/supervisor/conf.d and create a "appname".ini file
navigate to /etc/supervisor/conf.d and create a "your app name".ini file
if you're running python globally write into the file:
"""
nodaemon=true
command=python bot.py
autostart=true
autorestart=true
stderr_logfile= "pathforlogging/sentiment.err.log"
stdout_logfile= "pathforlogging/sentiment.out.log"
user=root
numprocs=1
directory= "path/bot.py"
"""
if you're running python through a pyenv write use the following command instead of command=python bot.py
" command=/bin/bash -l -c 'source /home/YOUR_USER/.pyenv/versions/VIRTUUALENV_NAME/bin/activate && python bot.py' "
with Changing YOUR_USER and VIRTUALENV_name
Open /etc/supervisor/supervisord.conf
At the bottom of the file under [INCLUDE]
add: "files = ./conf.d/*.ini"
now in your terminal run: 
1-sudo supervisorctl reread
2-sudo supervisorctl update
3-sudo supervisorctl reload
4- sudo systemctl restart supervisor.service
5-sudo systemctl status supervisor.service

the "systemctl status" command to check if your bot was added at the bottom
your bot should appear online on discord and can be called using !analyze

