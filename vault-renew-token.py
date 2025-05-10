#!/usr/bin/python3
import time
import hvac
import os
import logging
import logging.handlers

time.sleep(10)

LOG_FILENAME = '/var/log/vault/renew-token.log'

handler = logging.handlers.RotatingFileHandler(filename=LOG_FILENAME, maxBytes=2000, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', '%Y-%m-%d %H:%M:%S'))

my_logger = logging.getLogger()
my_logger.setLevel(logging.INFO)
my_logger.addHandler(handler)

try:
	client = hvac.Client(url = os.environ['VAULT_ADDR'], token = os.environ['VAULT_TOKEN'])
	renewed_data = client.renew_token()
	logging.info(renewed_data)
except Exception as e:
	logging.exception(repr(e))

## This script is meant to reside in /usr/local/bin/
## Create directory /var/log/vault and give permissions to the user in charge of this log
## Then update the root's crontab with the following lines:
## @reboot /usr/bin/python3 /usr/local/bin/vault-renew-token.py
## 0 12 * * 0 /usr/bin/python3 /usr/local/bin/vault-renew-token.py
