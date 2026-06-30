# Postbot Ecosystem

Telegram bot system consisting of a Main Control Bot and dynamically spawned satellite posting bots to manage automatic content distribution, schedules, post queues, and promo-reaction triggers.

## Deployment on Linux Server

1. Transfer the directory to your server (e.g. `/root/postbot`).
2. Run the deployment script:
   ```bash
   sudo bash deploy.sh
   ```
3. Set your production tokens in `.env` and place your database `db.db` in the same directory.
