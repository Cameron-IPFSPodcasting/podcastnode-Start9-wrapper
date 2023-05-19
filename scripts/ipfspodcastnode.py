#!/usr/local/bin/python3
import subprocess
import json
import yaml
import requests
import time
import logging
import os
import socket

#bin Paths
ipfspath = '/usr/local/bin/ipfs'
wgetpath = '/usr/bin/wget'
wcpath = '/usr/bin/wc'

#Setup logging to console
logging.basicConfig(level=logging.INFO, format="%(message)s")

#Init IPFS (if necessary)
if not os.path.exists('ipfs/config'):
  logging.info('Initializing IPFS')
  ipfs_init = subprocess.run(ipfspath + ' init', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#IP Addresses may change between reboots, so reconfigure every reboot.
api_cors = subprocess.run(ipfspath + ' config --json API.HTTPHeaders.Access-Control-Allow-Origin \'["*"]\'', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
api_meth = subprocess.run(ipfspath + ' config --json API.HTTPHeaders.Access-Control-Allow-Methods \'["PUT", "POST"]\'', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
swarmnat = subprocess.run(ipfspath + ' config --json Swarm.RelayClient.Enabled true', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#Open the port on the $LOCAL_IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 1))
LOCAL_IP = s.getsockname()[0]
listen_addr = subprocess.run(ipfspath + ' config --json Addresses.API \'["/ip4/127.0.0.1/tcp/5001", "/ip4/' + LOCAL_IP + '/tcp/5001"]\'', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#Start IPFS
daemon = subprocess.run(ipfspath + ' daemon >/dev/null 2>&1 &', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
logging.info('Starting IPFS Daemon')
time.sleep(10)

#Get IPFS ID
with open('ipfs/config', 'r') as ipcfg:
  ipconfig = ipcfg.read()
  jtxt = json.loads(ipconfig)
  logging.info('IPFS ID : ' + jtxt['Identity']['PeerID'])

#Main loop
while True:

  #Request payload
  payload = { 'version': '0.6s', 'ipfs_id': jtxt['Identity']['PeerID'] }

  #Read Start9 Config
  email = ''
  toraddress = 'N/A'
  lanaddress = 'N/A'
  with open('ipfs/start9/config.yaml', 'r') as ecf:
    s9cfg = yaml.safe_load(ecf)
    email = s9cfg['email-address']
    toraddress = 'http://' + s9cfg['tor-address'] + '/webui'
    lanaddress = 'https://' + s9cfg['lan-address'] + '/webui'
    if email == '':
      email = 'user@example.com'
  payload['email'] = email

  #Check if IPFS is running, restart if necessary.
  payload['online'] = False
  diag = subprocess.run(ipfspath + ' diag sys', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if diag.returncode == 0:
    ipfs = json.loads(diag.stdout)
    payload['ipfs_ver'] = ipfs['ipfs_version']
    payload['online'] = ipfs['net']['online']
  if payload['online'] == False:
    #Start the IPFS daemon
    daemon = subprocess.run(ipfspath + ' daemon >/dev/null 2>&1 &', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info('@@@ IPFS NOT RUNNING !!! Restarting Daemon @@@')

  #Get Peer Count
  peercnt = 0
  speers = subprocess.run(ipfspath + ' swarm peers|wc -l', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if speers.returncode == 0:
    peercnt = speers.stdout.decode().strip()
  payload['peers'] = peercnt

  #Get Usage/Available
  repostat = subprocess.run(ipfspath + ' repo stat -s|grep RepoSize', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if repostat.returncode == 0:
    repolen = repostat.stdout.decode().strip().split(':')
    used = int(repolen[1].strip())
  else:
    used = 0

  ipfsloc = os.getenv('IPFS_PATH')
  if ipfsloc == None:
    ipfsloc = '/'
  df = os.statvfs(ipfsloc)
  avail = df.f_bavail * df.f_frsize

  #Request work
  logging.info('Requesting Work...')
  try:
    response = requests.post("https://IPFSPodcasting.net/Request", timeout=120, data=payload)
    work = json.loads(response.text)
    logging.info('Response : ' + str(work))
  except requests.RequestException as e:
    logging.info('Error during request : ' + str(e))
    work = { 'message': 'Request Error' }

  if work['message'] == 'Request Error':
    logging.info('Error requesting work from IPFSPodcasting.net (check internet / firewall / router).')

  elif work['message'][0:7] != 'No Work':
    if work['download'] != '' and work['filename'] != '':
      logging.info('Downloading ' + str(work['download']))
      #Download any "downloads" and Add to IPFS (1hr48min timeout)
      try:
        hash = subprocess.run(wgetpath + ' -q --no-check-certificate "' + work['download'] + '" -O - | ' + ipfspath + ' add -q -w --stdin-name "' + work['filename'] + '"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=6500)
        hashcode = hash.returncode
      except subprocess.SubprocessError as e:
        logging.info('Error downloading/pinning episode : ' + str(e))
        #Clean up any other wget/add commands that may have spawned
        cleanup = subprocess.run('kill `ps aux|grep -E \'(ipfs ad[d]|no-check-certificat[e])\'|awk \'{ print $2 }\'`', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        hashcode = 99

      if hashcode == 0:
        #Get file size (for validation)
        downhash=hash.stdout.decode().strip().split('\n')
        size = subprocess.run(ipfspath + ' cat ' + downhash[0] + ' | ' + wcpath + ' -c', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        downsize=size.stdout.decode().strip()
        logging.info('Added to IPFS ( hash : ' + str(downhash[0]) + ' length : ' + str(downsize) + ')')
        payload['downloaded'] = downhash[0] + '/' + downhash[1]
        payload['length'] = downsize
      else:
        payload['error'] = hashcode

    if work['pin'] != '':
      #Directly pin if already in IPFS
      logging.info('Pinning hash (' + str(work['pin']) + ')')
      try:
        pin = subprocess.run(ipfspath + ' pin add ' + work['pin'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=6500)
        pincode = pin.returncode
      except subprocess.SubprocessError as e:
        logging.info('Error direct pinning : ' + str(e))
        #Clean up any other pin commands that may have spawned
        cleanup = subprocess.run('kill `ps aux|grep "ipfs pin ad[d]"|awk \'{ print $2 }\'`', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pincode = 98

      if pincode == 0:
        #Verify Success and return full CID & Length
        pinchk = subprocess.run(ipfspath + ' ls ' + work['pin'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if pinchk.returncode == 0:
          hashlen=pinchk.stdout.decode().strip().split(' ')
          payload['pinned'] = hashlen[0] + '/' + work['pin']
          payload['length'] = hashlen[1]
        else:
          payload['error'] = pinchk.returncode
      else:
        payload['error'] = pincode

    if work['delete'] != '':
      #Delete/unpin any expired episodes
      logging.info('Unpinned old/expired hash (' + str(work['delete']) + ')')
      delete = subprocess.run(ipfspath + ' pin rm ' + work['delete'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      payload['deleted'] = work['delete']

    #Report Results
    logging.info('Reporting results...')

    #Send usage data to website
    payload['used'] = used
    payload['avail'] = avail

    try:
      response = requests.post("https://IPFSPodcasting.net/Response", timeout=120, data=payload)
    except requests.RequestException as e:
      logging.info('Error sending response : ' + str(e))

  elif 'cleanup' in work and work['cleanup'] != '':
    logging.info('Running Garbage Collection (Clean Up)')
    gcrun = subprocess.run(ipfspath + ' repo gc --silent >/dev/null 2>&1 &', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  else:
    logging.info('No work.')

  #Update properties

  #Calculate human readable disk usage
  percent = round(used/(used+avail)*100, 1)

  if used < (1024*1024*1024):
    used = str(round(used/1024/1024, 1)) + ' MB'
  elif used < (1024*1024*1024*1024):
    used = str(round(used/1024/1024/1024, 1)) + ' GB'
  else:
    used = str(round(used/1024/1024/1024/1024, 2)) + ' TB'

  if avail < (1024*1024*1024):
    avail = str(round(avail/1024/1024, 1)) + ' MB'
  elif avail < (1024*1024*1024*1024):
    avail = str(round(avail/1024/1024/1024, 1)) + ' GB'
  else:
    avail = str(round(avail/1024/1024/1024/1024, 2)) + ' TB'

  #Calculate Peer status. 0-100 peers = Red/Poor. 100-400 peers = Yellow/Good. 400+ peers = Green/Best
  peertxt = str(payload['peers'])
  if int(payload['peers']) > 400:
    peertxt += ' - Excellent! ✅'
  elif int(payload['peers']) > 100:
    peertxt += ' - Good 🟡'
  else:
    peertxt += ' - Poor 🔴 (visit https://ipfspodcasting.net/Help/Network for tips to improve your network performance)'

  #Build YAML String
  stats='''version: 2
data:
  IPFS UI (Tor):
    type: string
    value: ''' + toraddress + '''
    description: IPFS Web UI over Tor.
    copyable: true
    qr: false
    masked: false
  IPFS UI (Lan):
    type: string
    value: ''' + lanaddress + '''
    description: IPFS Web UI over Lan.
    copyable: true
    qr: false
    masked: false
  IPFS ID:
    type: string
    value: ''' + payload['ipfs_id'] + '''
    description: Your IPFS Node ID on the IPFS Network.
    copyable: true
    qr: false
    masked: false
  Peer Count:
    type: string
    value: ''' + peertxt + '''
    description: Number of IPFS peers connected to your node. More nodes mean better performance. Peer count fluctuates based on your network connectivity. If you have a low peer count visit https://ipfspodcasting.net/Help/Network for tips to improve performance.
    copyable: true
    qr: false
    masked: false
  Disk Usage:
    type: string
    value: ''' + str(used) + ''' Used (''' + str(percent) + '''%) of ''' + str(avail) + ''' Available
    description: Disk used by IPFS. This is the size of your IPFS Datastore which may include files not used for IPFS Podcasting.
    copyable: true
    qr: false
    masked: false'''

  with open('ipfs/start9/stats.yaml', 'w') as yaml_file:
    yaml_file.write(stats)

  #wait 10 minutes then start again
  logging.info('Sleeping 10 minutes...')
  time.sleep(600)
