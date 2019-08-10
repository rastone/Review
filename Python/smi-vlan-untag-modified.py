/**************************************************************************
 * (C) Copyright 2015-2019 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/

import threading
from queue import Queue
import pexpect
import os
import sys
import time
import datetime

# Global variable declarations
get_epon_queue = Queue()
get_rur_queue = Queue()
smi_list = []
rur_list = []
username = str(os.popen("""getent passwd $USER | cut -d ':' -f 5 | cut -d ',' -f 1""").read())
home = '/home/' + username.split(' ')[0][0].lower() + username.split(' ')[1].lower().strip()

# CRANS used for determining which telnet login to use.
WD = ['az.pima','ca.ccal','ca.sfba','co.denver','ks.indepen','mn.minn','mo.indepen','nm.albuq','or.bverton','tx.houston','ut.utah','wa.bverton','wa.seattle','wi.minn']
CD = ['al.hunts','al.mobile','al.pancity','al.tusca','ar.lrock','ar.malt','fl.jacksvil','fl.lakecnty','fl.naples','fl.pancity','fl.pompano','fl.tallah','fl.westfl','ga.atlanta','ga.augusta','ga.chatta','ga.jacksvil','ga.savannah','ga.tallah','il.chicago','in.chicago','in.indiana','in.nash','in.sbend','ky.nash','la.malt','mi.michigan','mi.sbend','ms.malt','sc.chrlstn','tn.chatta','tn.knox','tn.malt','tn.nash','va.knox']
NED = ['ct.hartford','dc.bad','de.bad','de.panjde','ma.boston','md.bad','md.pitt','me.boston','nc.richmond','nh.boston','nj.panjde','ny.hartford','oh.pitt','pa.bo','pa.panjde','pa.pitt','va.bad','va.richmond','vt.boston','wv.bad','wv.pitt','wv.richmond']

# CMTS list is pulled pulled from a local file.
def get_cmts_list():
    with open('/home/username/olt/smi-upgrade','r') as cmtslist:
        for eachcmts in cmtslist:
            if 'smi' in eachcmts:
                smi_list.append(eachcmts.strip())

# RUR list is pulled pulled from a local file.
def get_rur_list():
    with open('/home/username/rur/rur-upgrade','r') as rurlist:
        for eachrur in rurlist:
            if 'rur' in eachrur:
                rur_list.append(eachrur.strip())

# Get list of EPONs
def get_epon(cmts):
    if cmts != '':
        try:
            # Telnet login is stored on a file locally and parsed based on CRAN.
            user = None
            password = None
            isis_down3 = 0
            isis_down4 = 0
            check_vlan3 = []
            check_vlan4 = []
            check_vlan3_status = []
            check_vlan4_status = []

            cran = cmts.split('.isp.net')[0].split('.', 2)[2]
            olt = cmts.split('.')
            if cran in WD:
                with open('/var/scripts/pass.txt', 'r') as code:
                    for i in code:
                        if 'WD,write' in i:
                            user = i.split(',')[2]
                            password = i.split(',')[3]
            print('Connecting to...' + cmts)
            telnet = pexpect.spawn('telnet ' + cmts)
            telnet.expect('login:', timeout=10)
            telnet.sendline(user)
            telnet.expect('Password:')
            telnet.sendline(password)
            telnet.expect('#')

            # Perform Pre-Snapshots on OLT
            print('Maintenance Started...')
            print('Performing Pre-Snapshot on OLT/RURs')
            telnet.sendline('set cli pagination off')
            telnet.sendline('show cable modem sum tot')
            telnet.expect('#')
            output1 = telnet.before.decode()
            telnet.sendline('show cable modem')
            telnet.expect('#')
            output2 = telnet.before.decode()
            telnet.sendline('show ip route')
            telnet.expect('#')
            output3 = telnet.before.decode()
            telnet.sendline('show ipv6 route')
            telnet.expect('#')
            output4 = telnet.before.decode()
            telnet.sendline('show card status')
            telnet.expect('#')
            output5 = telnet.before.decode()
            telnet.sendline('show redundancy all')
            telnet.expect('#')
            output6 = telnet.before.decode()
            telnet.sendline('show isis adjacencies')
            telnet.expect('#')
            output7 = telnet.before.decode()
            telnet.sendline('show running-config vlan 3')
            telnet.expect('end')
            output8 = telnet.before.decode()
            telnet.sendline('show running-config vlan 4')
            telnet.expect('end')
            output9 = telnet.before.decode()
            telnet.sendline('show running-config interface port-channel 1')
            telnet.expect('end')
            output10 = telnet.before.decode()
            telnet.sendline('show running-config interface port-channel 2')
            telnet.expect('end')
            output11 = telnet.before.decode()
            telnet.expect('#')

            for eachline in output1.splitlines():
                print(eachline.strip())

            for eachline in output2.splitlines():
                print(eachline.strip())

            for eachline in output3.splitlines():
                print(eachline.strip())

            for eachline in output4.splitlines():
                print(eachline.strip())

            for eachline in output5.splitlines():
                print(eachline.strip())

            for eachline in output6.splitlines():
                print(eachline.strip())

            for eachline in output7.splitlines():
                print(eachline.strip())

            for eachline in output8.splitlines():
                print(eachline.strip())

                if output8.splitlines()[35] == " Adjacency on interface vlan4":
                    check_vlan4 = output8.splitlines()[35].split(" Adjacency on interface ")[1]
                    check_vlan4_status = output8.splitlines()[48].split(" Adjacency State IS: ")[1]
                else:
                    continue

                if output8.splitlines()[59] == " Adjacency on interface vlan3":
                    check_vlan3 = output8.splitlines()[59].split(" Adjacency on interface ")[1]
                    check_vlan3_status = output8.splitlines()[72].split(" Adjacency State IS: ")[1]
                else:
                    continue

            for eachline in output9.splitlines():
                print(eachline.strip())

            for eachline in output10.splitlines():
                print(eachline.strip())

            for eachline in output11.splitlines():
                print(eachline.strip())

            # ISIS Verification Checks
            if check_vlan3 == "vlan3" and check_vlan3_status == "UP                ":
                isis_down3 += 1
            else:
                print('ISIS is DOWN on VLAN 3...Aborting, please FIX before continuing')
                print('!')
                exit()

            if check_vlan4 == "vlan4" and check_vlan4_status == "UP                ":
                isis_down4 += 1
            else:
                print('ISIS is DOWN on VLAN 4...Aborting, please FIX before continuing')
                print('!')
                exit()

            # wrapping up pre-snapshots for OLT
            print('\r\n' + 'Pre-Snapshots Completed on ' + cmts)
            print('\r\n' + 'Connecting to RUR devices...Please standby!')
            print('!')

            # Clearing buffer
            try:
                while True:
                    telnet.expect(r'.+', timeout=10)
            except:
                pass

            # Add VLAN untagging configuration to OLT - VLAN 3
            time.sleep(20)
            print('\r\n' + 'Preparing to configure OLT...Please standby!')
            print('Configuring VLAN 3...')
            time.sleep(4)
            telnet.sendline('conf t')
            telnet.expect('#')
            output12 = telnet.before.decode()
            telnet.sendline('switch  default')
            telnet.expect('#')
            output13 = telnet.before.decode()
            telnet.sendline('vlan 3')
            telnet.expect('#')
            output14 = telnet.before.decode()
            telnet.sendline('@ ports add port-channel 1 untagged port-channel 1')
            telnet.expect('#')
            output15 = telnet.before.decode()
            telnet.sendline('exit')
            telnet.expect('#')
            output16 = telnet.before.decode()
            telnet.sendline('exit')
            telnet.expect('#')
            output17 = telnet.before.decode()
            telnet.sendline('interface port-channel 1')
            telnet.expect('#')
            output18 = telnet.before.decode()
            telnet.sendline('@ switchport pvid 3')
            telnet.expect('#')
            output19 = telnet.before.decode()
            telnet.sendline('exit')
            telnet.expect('#')
            output20 = telnet.before.decode()


            # Add VLAN untagging configuration to OLT - VLAN 4
            print('Configuring VLAN 4...')
            telnet.sendline('switch  default')
            telnet.expect('#')
            output21 = telnet.before.decode()
            telnet.sendline('vlan 4')
            telnet.expect('#')
            output22 = telnet.before.decode()
            telnet.sendline('@ ports add port-channel 2 untagged port-channel 2')
            telnet.expect('#')
            output23 = telnet.before.decode()
            telnet.sendline('exit')
            telnet.expect('#')
            output24 = telnet.before.decode()
            telnet.sendline('exit')
            telnet.expect('#')
            output25 = telnet.before.decode()
            telnet.sendline('interface port-channel 2')
            telnet.expect('#')
            output26 = telnet.before.decode()
            telnet.sendline('@ switchport pvid 4')
            telnet.expect('#')
            output27 = telnet.before.decode()
            telnet.sendline('end')
            telnet.expect('#')
            output28 = telnet.before.decode()
            print('Saving OLT Config...')
            telnet.sendline('wr')
            telnet.expect('[OK]')
            output29 = telnet.before.decode()
            telnet.sendline('!')
            telnet.expect('#')
            output30 = telnet.before.decode()
            print('!')


            # Send Post-Snapshots to OLT
            print('Preparing to perform Post-Snaps on OLT...Standby!:')
            time.sleep(30)
            print('Performing Post-Snaps on ' + cmts)
            telnet.sendline('show cable modem sum tot')
            telnet.expect('#')
            output31 = telnet.before.decode()
            telnet.sendline('show cable modem')
            telnet.expect('#')
            output32 = telnet.before.decode()
            telnet.sendline('show ip route')
            telnet.expect('#')
            output33 = telnet.before.decode()
            telnet.sendline('show ipv6 route')
            telnet.expect('#')
            output34 = telnet.before.decode()
            telnet.sendline('show card status')
            telnet.expect('#')
            output35 = telnet.before.decode()
            telnet.sendline('show redundancy all')
            telnet.expect('#')
            output36 = telnet.before.decode()
            telnet.sendline('show isis adjacencies')
            telnet.expect('#')
            output37 = telnet.before.decode()
            telnet.sendline('show running-config vlan 3')
            telnet.expect('end')
            output38 = telnet.before.decode()
            telnet.sendline('show running-config vlan 4')
            telnet.expect('end')
            output39 = telnet.before.decode()
            telnet.sendline('show running-config interface port-channel 1')
            telnet.expect('end')
            output40 = telnet.before.decode()
            telnet.sendline('show running-config interface port-channel 2')
            telnet.expect('end')
            output41 = telnet.before.decode()
            telnet.expect('#')
            print('!')

            # Print untagging configuration for VLAN 3
            print('Results VLAN 3...')
            for eachline in output12.splitlines():
                print(eachline.strip())

            for eachline in output13.splitlines():
                print(eachline.strip())

            for eachline in output14.splitlines():
                print(eachline.strip())

            for eachline in output15.splitlines():
                print(eachline.strip())

            for eachline in output16.splitlines():
                print(eachline.strip())

            for eachline in output17.splitlines():
                print(eachline.strip())

            for eachline in output18.splitlines():
                print(eachline.strip())

            for eachline in output19.splitlines():
                print(eachline.strip())

            for eachline in output20.splitlines():
                print(eachline.strip())

            # Print untagging configuration for VLAN 4
            print('!')
            print('Results VLAN 4...')
            for eachline in output21.splitlines():
                print(eachline.strip())

            for eachline in output22.splitlines():
                print(eachline.strip())

            for eachline in output23.splitlines():
                print(eachline.strip())

            for eachline in output24.splitlines():
                print(eachline.strip())

            for eachline in output25.splitlines():
                print(eachline.strip())

            for eachline in output26.splitlines():
                print(eachline.strip())

            for eachline in output27.splitlines():
                print(eachline.strip())

            for eachline in output28.splitlines():
                print(eachline.strip())

            for eachline in output29.splitlines():
                print(eachline.strip())

            for eachline in output30.splitlines():
                print(eachline.strip())

            print('!')
            print('\r\n' + 'Configuration Completed on ' + cmts)
            print(datetime.datetime.now())
            print('!')

            # Print Post-Snapshots for OLT
            time.sleep(3)
            print(cmts.strip())
            print('Post-Snapshots:')
            print('!')

            time.sleep(1)
            for eachline in output31.splitlines():
                print(eachline.strip())

            for eachline in output32.splitlines():
                print(eachline.strip())

            for eachline in output33.splitlines():
                print(eachline.strip())

            for eachline in output34.splitlines():
                print(eachline.strip())

            for eachline in output35.splitlines():
                print(eachline.strip())

            for eachline in output36.splitlines():
                print(eachline.strip())

            for eachline in output37.splitlines():
                print(eachline.strip())

            for eachline in output38.splitlines():
                print(eachline.strip())

            for eachline in output39.splitlines():
                print(eachline.strip())

            for eachline in output40.splitlines():
                print(eachline.strip())

            for eachline in output41.splitlines():
                print(eachline.strip())

            # wrapping up post-snapshots for OLT
            print('\r\n' + 'Post-Snapshots Completed on ' + cmts)
            print('\r\n' + 'Preparing Post-Snapshots for RURs...Please standby!')
            print('!')

            # Closing connection to OLT
            telnet.sendline('exit')
            telnet.expect('$')

        except:
            print('System Exit Invoked or Unable to telnet into : ' + cmts.strip(), sys.exc_info()[0])
            exit()

# Get list of Arista RURs
def get_rur(rur):
    if rur != '':
        try:
            # Telnet login is stored on a file locally and parsed based on CRAN.
            user2 = None
            password2 = None
            cran2 = rur.split('.isp.net')[0].split('.', 2)[2]
            if cran2 in WD:
                with open('/var/scripts/pass.txt', 'r') as code:
                    for i in code:
                        if 'WD,write' in i:
                            user2 = i.split(',')[2]
                            password2 = i.split(',')[3]
            telnet2 = pexpect.spawn('telnet ' + rur)
            telnet2.expect('Username:')
            telnet2.sendline(user2)
            telnet2.expect('Password:')
            telnet2.sendline(password2)
            telnet2.expect('#')


            # Perform Pre-Snapshots on Arista RURs
            print('Performing Pre-Snaps on ' + rur)
            telnet2.send('\r')
            telnet2.sendline('terminal length 0')
            telnet2.expect('Pagination disabled.')
            telnet2.expect('#')
            telnet2.sendline('show running-config interfaces port-Channel 151' + '\r\n')
            telnet2.expect('#')
            output1 = telnet2.before.decode()
            telnet2.send('\r')
            telnet2.send('\r')
            telnet2.sendline('show ip interface port-Channel 151 brief' + '\r\n')
            telnet2.expect("2000")
            output2 = telnet2.before.decode()
            telnet2.send('\r')
            telnet2.sendline('show ip route isis | i Port-Channel151')
            telnet2.expect(",")
            output3 = telnet2.before.decode()

            print('!')
            print(rur.strip())
            print('!')
            for eachline in output1.splitlines():
                print(eachline.strip())

            print('!')
            for eachline in output2.splitlines():
                print(eachline.strip())

            print('!')
            for eachline in output3.splitlines():
                ip1 = eachline.strip()

            # Clearing buffer
            time.sleep(2)
            print('Initiating Ping Checks on ' + rur)
            try:
                while True:
                    telnet2.expect(r'.+', timeout=10)
            except:
                pass

            # Perform pre-ping checks to OLT
            print('!')
            telnet2.send('ping ' + ip1.split()[5] + '\r')
            telnet2.expect("ipg")
            output4 = telnet2.before.decode()

            # Output pre-ping checks
            for eachline in output4.splitlines():
                print(eachline.strip())

            # wrapping up pre-snapshots for RUR
            print('!')
            print('\r\n' + 'Pre-Snapshots Completed on ' + rur)
            print('!')

            # Add configuration to RUR
            time.sleep(27)
            print('\r\n' + 'Configuring ' + rur)
            print('!')
            telnet2.sendline('@ conf t')
            telnet2.expect('#')
            output42 = telnet2.before.decode()
            telnet2.sendline('@ interface Port-Channel151')
            telnet2.expect('#')
            output43 = telnet2.before.decode()
            telnet2.sendline('@ no encapsulation dot1q vlan 3')
            telnet2.expect('#')
            output44 = telnet2.before.decode()
            telnet2.sendline('@ no encapsulation dot1q vlan 4')
            telnet2.expect('#')
            output45 = telnet2.before.decode()
            telnet2.sendline('@ end')
            telnet2.expect('#')
            output46 = telnet2.before.decode()
            telnet2.sendline('@ wr')
            telnet2.expect('#')
            output47 = telnet2.before.decode()

            for eachline in output42.splitlines():
                print(eachline.strip())

            for eachline in output43.splitlines():
                print(eachline.strip())

            for eachline in output44.splitlines():
                print(eachline.strip())

            for eachline in output45.splitlines():
                print(eachline.strip())

            for eachline in output46.splitlines():
                print(eachline.strip())

            for eachline in output47.splitlines():
                print(eachline.strip())

            print('!')
            print(datetime.datetime.now())
            print('!')
            print('Preparing to take Post-Snapshots on OLT/RUR.')
            print('!')

            # Perform Post-Snapshots on Arista RURs
            time.sleep(33)
            telnet2.send('\r')
            telnet2.sendline('show running-config interfaces port-Channel 151' + '\r\n')
            telnet2.expect('#')
            output5 = telnet2.before.decode()
            telnet2.send('\r')
            telnet2.send('\r')
            telnet2.sendline('show ip interface port-Channel 151 brief' + '\r\n')
            telnet2.expect("2000")
            output6 = telnet2.before.decode()
            telnet2.send('\r')
            telnet2.sendline('show ip route isis | i Port-Channel151')
            telnet2.expect(",")
            output7 = telnet2.before.decode()

            print('!')
            print(rur.strip())
            print('!')
            for eachline in output5.splitlines():
                print(eachline.strip())

            print('!')
            for eachline in output6.splitlines():
                print(eachline.strip())

            print('!')
            for eachline in output7.splitlines():
                ip1 = eachline.strip()

            # Clearing buffer
            time.sleep(2)
            print('Initiating Ping Checks on ' + rur)
            try:
                while True:
                    telnet2.expect(r'.+', timeout=10)
            except:
                pass

            # Perform post-ping checks to OLT
            print('!')
            telnet2.send('ping ' + ip1.split()[5] + '\r')
            telnet2.expect("ipg")
            output8 = telnet2.before.decode()

            # Listing pre-ping checks
            for eachline in output8.splitlines():
                print(eachline.strip())

            # Closing connections to RURs
            telnet2.sendline('exit')
            telnet2.expect('#')
            print('!')
            print('Maintenance Complete')
            print(datetime.datetime.now())

        except:
            print('Unable to telnet into RUR: ' + rur.strip(), sys.exc_info()[0])
            exit()


# Multithreading for olt
def get_epon_thread():
    while True:
        cmts = get_epon_queue.get()
        get_epon(cmts)
        get_epon_queue.task_done()

# Multithreading for rur
def get_rur_thread():
    while True:
        rur = get_rur_queue.get()
        time.sleep(3)
        get_rur(rur)
        get_rur_queue.task_done()

def main():
    # Populate local files with OLT/RURs to be used
    get_cmts_list()
    get_rur_list()

    print(datetime.datetime.now())

    # Generate threads for for OLT and RURs.
    for eachcmts in smi_list:
        get_epon_queue.put(eachcmts)
    for eachrur in rur_list:
        get_rur_queue.put(eachrur)

    for eachThread in range(80):
        get_epon_threader = threading.Thread(target=get_epon_thread)
        get_epon_threader.daemon = True
        get_epon_threader.start()
    for eachThread2 in range(80):
        get_rur_threader = threading.Thread(target=get_rur_thread)
        get_rur_threader.daemon = True
        get_rur_threader.start()

    # Connect strings together in the queue
    get_epon_queue.join()
    get_rur_queue.join()

if __name__ == '__main__':
    main()

