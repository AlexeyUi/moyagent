#!/bin/bash
echo "Останавливаю Danny..."
sudo fuser -k 8011/tcp 2>/dev/null
pkill -9 -f "start_all|uvicorn|ap_agent|telegram_bot|reminder_bot" 2>/dev/null
echo "Danny остановлен."
