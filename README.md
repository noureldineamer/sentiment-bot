# sentiment-bot

Linux-based Discord bot to analyze the current state of the market through the sentiment of investors.

## Setup Instructions

### Step 1: Create a Discord Application
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.
2. Head to the **OAuth2** tab and get your token. Copy it and assign it to `TOKEN="your token"` in a `.env` file.

### Step 2: Configure Bot Settings
1. Go to the Bot tab and enable the "Message Content Intent."
2. Enable Developer Mode in Discord and copy the `channel_id` you want your bot to read data from.
3. Paste it into `current_channel="channel_id"` in your `.env` file.
4. Copy the `channel_id` for the channel you want the bot to regularly post updates in.
5. Paste it into `regular_update_channel="channel_id"` in your `.env` file.

### Step 3: Install and Configure Supervisor (Debian-based Systems)
1. Run the following command to install Supervisor:
    ```bash
    sudo apt-get install supervisor
    ```
2. Navigate to `/etc/supervisor/conf.d` and create a `your_app_name.ini` file.
3. If you're running Python globally, add the following content to the file:
    ```ini
    [program:sentiment-bot]
    nodaemon=true
    command=python bot.py
    autostart=true
    autorestart=true
    stderr_logfile=/pathforlogging/sentiment.err.log
    stdout_logfile=/pathforlogging/sentiment.out.log
    user=root
    numprocs=1
    directory=/path/to/bot
    ```
4. If you're using Python through a `pyenv`, replace the `command` line with:
    ```ini
    command=/bin/bash -l -c 'source /home/YOUR_USER/.pyenv/versions/VIRTUALENV_NAME/bin/activate && python bot.py'
    ```
    Replace `YOUR_USER` and `VIRTUALENV_NAME` with your actual username and virtual environment name.

### Step 4: Update Supervisor Configuration
1. Open `/etc/supervisor/supervisord.conf`.
2. At the bottom of the file, under `[include]`, add:
    ```ini
    files = ./conf.d/*.ini
    ```

### Step 5: Start Supervisor
Run the following commands in your terminal:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo systemctl restart supervisor.service
```

Your bot should now be running and ready to analyze market sentiment! sentiment-bot

Linux-based Discord bot to analyze the current state of the market through the sentiment of investors.

