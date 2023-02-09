/**************************************************************************
 * (C) Copyright 2020-2021 by Ryan Stone. All Rights Reserved.            *
 *                                                                        *
 **************************************************************************/
 
#!/usr/bin/python3 -u
import argparse
import paramiko
import re
import time
import datetime
import os
import sys
import lib.arris
import lib.cisco
import lib.harmonic
import lib.error_check
import lib.thanos
import lib.api_aws
import ipaddress
from getpass import getpass
from argparse import RawTextHelpFormatter
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from curses import ascii


# Globals to capture final healthcheck results and output log
healthcheck_results = {}
log = {'Log': True, 'Output': []}

bucket_name_prod = 'rlcm-autobahn-rpdhealth-prod'
bucket_name_pre = 'rlcm-autobahn-rpdhealth-dev'

# Values to be used for usage log
toLogging = 'rpd_health_check.log'
timestamp = datetime.datetime.now().strftime("%Y-%m-%d__%H-%M-%S")


class Active:
    testing = False
    maintenance = False


def main():
    # clear screen
    os.system('clear')

    # Print out Logo
    toLogo = 'lib/HEALTHCHECKER_LOGO.txt'

    if not Active.testing:
        f = open(toLogo, 'r')
        print('\n' + '\033[1m' + f.read() + '\n' + '\033[0m')
        f.close()

    # Setup argument parser, look for the necessary RPD IP argument
    args = parser.parse_args()

    if Active.maintenance:
        if not args.maint:
            print('\nSystem is down for maintenance...Please try again later!\n')
            sys.exit()
        else:
            print('\n**************************\nMaintenance Mode is Active\n**************************\n\n')

    if Active.testing:
        print('\n**************************\nTesting Mode is Active\n**************************\n\n')

    if not args.rpd:
        print("Missing arguments, see --help for more information")
        exit(1)

    rpd = args.rpd

    for each_device in rpd:

        # Get RPD info from Thanos
        args.ipv6 = each_device
        addr = ipaddress.ip_address(args.ipv6)
        ipv6 = str(addr.exploded.upper())

        rpd_mac_address, vendor, hardware_version, daas_name, rpd_name = lib.thanos.api_get_rpd_info(ipv6)

        # Establish SSH connection to the RPD and record its shell output
        rpd_ssh_channel, login_output = establish_rpd_ssh_connection(each_device, rpd_name)

        # -------- Initial Information Gathering Section --------
        # Get passwd, based on vendor
        passwd = determine_vendor(vendor, rpd_name)

        # Determine model/type of RPD
        rpd_type = get_rpd_type_and_mac(vendor, rpd_ssh_channel, rpd_mac_address, hardware_version, rpd_name)

        # If the daas or d switch is specified
        if args.daas or args.daas_only:
            # Establish SSH connection to the DAAS and record its shell output
            daas_ssh_channel = establish_daas_ssh_connection(vendor, each_device, rpd_name)

        # If the log or l switch is specified
        if not args.log:
            log['Log'] = False
            lib.arris.log['Log'] = False
            lib.cisco.log['Log'] = False
            lib.harmonic.log['Log'] = False

        # If the daas or d switch is specified
        if args.daas or args.daas_only:
            print("DAAS:", daas_name, '\n')

        # Log to file
        if not Active.maintenance:
            with open(toLogging, 'a+') as logs:
                if not args.daas or args.daas_only:
                    logs.write(timestamp + ' ' + 'RPD Health Checker - Vendor: ' + vendor + '   TYPE: ' + rpd_type +
                               '   HW: ' + hardware_version + '   RPD: ' + rpd_name + '   MAC: ' + rpd_mac_address +
                               '   IPV6: ' + each_device + '\n')
                else:
                    logs.write(timestamp + ' ' + 'RPD Health Checker - Vendor: ' + vendor + '   TYPE: ' + rpd_type +
                               '   HW: ' + hardware_version + '   RPD: ' + rpd_name + '   MAC: ' + rpd_mac_address +
                               '   IPV6: ' + each_device + '   DAAS: ' + daas_name + '\n')

        # -------------- GOT/GOA Only Testing Section Start --------------
        # -------------- GOT/GOA Only Testing Section End --------------

        # -------- Standard/Shelf Testing Section Start --------
        if vendor == 'Arris' and rpd_type == 'Standard' or \
                vendor == 'Arris' and rpd_type == 'Shelf' or \
                vendor == 'Arris' and rpd_type == 'RFS' or \
                vendor == 'Arris' and rpd_type == 'GOT/GOA':

            # Context to screen
            if not args.video:
                print("\nBeginning Tests\n------------------------------------")
            if args.video:
                print("\nBeginning VIDEO ONLY Tests\n------------------------------------")
            if args.daas_only:
                print("\nBeginning DAAS ONLY Tests\n------------------------------------")

            if not args.daas_only:
                if not args.video:
                    # Check PTP status
                    lib.arris.arris_ptp_test(vendor, rpd_ssh_channel)

                    if vendor == 'Arris' and rpd_type != 'RFS':

                        # Check temperature and voltages
                        lib.arris.arris_environment_test(vendor, rpd_ssh_channel, rpd_type)

                    if vendor == 'Arris' and rpd_type == 'RFS':

                        # Check temperature and voltages
                        lib.arris.arris_environment_rfs_test(vendor, rpd_ssh_channel, rpd_type)

                    # Check ingress/egress packet/frame counts
                    lib.arris.arris_eth_traffic_test(vendor, rpd_ssh_channel)

                    # Enter Linux shell for the following tests
                    enter_arris_shell(rpd_ssh_channel)

                    # Arris Map packet test
                    lib.arris.arris_map_packet_test(vendor, rpd_ssh_channel)

                    # Upstream channel tests
                    lib.arris.arris_upstream_channel_test(vendor, rpd_ssh_channel)

                    # Exit shell back to CLISH
                    exit_arris_shell(rpd_ssh_channel)

                    # Test OFDM
                    lib.arris.arris_ofdm_test(vendor, rpd_ssh_channel)

                # Test OOB packet output
                carrier = lib.arris.arris_oob_test(vendor, rpd_ssh_channel, rpd_name)

                # Test Aux core connectivity
                lib.arris.arris_core_connectivity_test(vendor, rpd_ssh_channel, carrier, rpd_type)

                # Test each L2TP session
                lib.arris.arris_l2tp_test(vendor, rpd_ssh_channel, rpd_type)

                # Test each downstream ScQAM
                lib.arris.arris_ds_scqam_test(vendor, rpd_ssh_channel)

                # Test FPGA Sessions
                lib.arris.arris_fpga_test(vendor, rpd_ssh_channel, rpd_type)

        elif vendor == 'Cisco' and rpd_type == 'Standard':
            # Context to screen
            if not args.video:
                print("\nBeginning Tests\n------------------------------------")
            if args.video:
                print("\nBeginning VIDEO ONLY Tests\n------------------------------------")
            if args.daas_only:
                print("\nBeginning DAAS ONLY Tests\n------------------------------------")

            if not args.daas_only:
                if not args.video:

                    # Check PTP status
                    lib.cisco.cisco_ptp_test(vendor, rpd_ssh_channel)

                    # Get Map packet counts for the four US channels
                    lib.cisco.cisco_map_packet_test(vendor, rpd_ssh_channel)

                    # Test OFDM functionality
                    lib.cisco.cisco_ofdm_test(vendor, rpd_ssh_channel)

                    # Test environmental values
                    lib.cisco.cisco_environmental_test(vendor, rpd_ssh_channel)

                    # Test SFP on RPD
                    # lib.cisco.cisco_sfp_test(vendor, rpd_ssh_channel)

                    # Test the VBH0 interface
                    lib.cisco.cisco_vbh0_interface_test(vendor, rpd_ssh_channel)

                # Test OOB functionality
                carrier = lib.cisco.cisco_oob_test(vendor, rpd_ssh_channel)

                # Test all downstream l2tp sessions and channels
                lib.cisco.cisco_l2tp_session_test(vendor, rpd_ssh_channel)

                # Test core connectivity
                lib.cisco.cisco_core_connectivity_test(vendor, rpd_ssh_channel, carrier)

                # Test all enabled DS ScQams
                lib.cisco.cisco_ds_scqam_test(vendor, rpd_ssh_channel)

                # Test FPGA Sessions
                lib.cisco.cisco_fpga_test(vendor, rpd_ssh_channel)

        elif vendor == 'Harmonic' and rpd_type == 'Standard' or \
                vendor == 'Harmonic' and rpd_type == 'Shelf' or \
                vendor == 'Harmonic' and rpd_type == 'RFS' or \
                vendor == 'Harmonic' and rpd_type == 'BAU-H 2x4':

            # Enter the Linux administrative shell on the RPD securely
            enter_harmonic_shell(rpd_ssh_channel, passwd)

            # Context to screen
            if not args.video:
                print("\nBeginning Tests\n------------------------------------")
            if args.video:
                print("\nBeginning VIDEO ONLY Tests\n------------------------------------")
                if args.daas_only:
                    print("\nBeginning DAAS ONLY Tests\n------------------------------------")

            ''' SHELL - ONLY COMMANDS '''

            if not args.daas_only:
                if not args.video:
                    if vendor == 'Harmonic' and rpd_type == 'Standard':
                        # LMB parameter config validations - Standard only
                        lib.harmonic.harmonic_lmb_test(vendor, rpd_ssh_channel)

                    if vendor == 'Harmonic' and rpd_type == 'BAU-H 2x4':
                        # LMB parameter config validations - BAU-H 2x4 only
                        lib.harmonic.harmonic_lmb_bauh2x4_test(vendor, rpd_ssh_channel)

                    if vendor == 'Harmonic' and rpd_type == 'Standard' or vendor == 'Harmonic' and rpd_type == 'BAU-H 2x4':
                        # Check connectivity to LMB and RF Tray
                        lib.harmonic.harmonic_component_connectivity_test(vendor, rpd_ssh_channel)

                        # Ripple and Pebble configuration check
                        lib.harmonic.harmonic_ripple_pebble_test(vendor, rpd_ssh_channel)

                        # Light levels from RPD SFP
                        lib.harmonic.get_harmonic_sfp_info(rpd_ssh_channel, vendor)

                    # TE1 port info
                    lib.harmonic.harmonic_te1_test(vendor, rpd_ssh_channel)

                # OFDMA channel tests - High/Mid Split
                with open('high_mid_split.txt') as f:
                    for line in f:
                        if rpd_name == line.strip():
                            lib.harmonic.harmonic_ofdma_test(vendor, rpd_ssh_channel)

                # Out of band validations
                lib.harmonic.harmonic_oob_test(vendor, rpd_ssh_channel)

                # Test FPGA Sessions
                lib.harmonic.harmonic_fpga_test(vendor, rpd_ssh_channel)

                # Exit the Linux shell, back to the RPD CLI
                exit_harmonic_shell(rpd_ssh_channel)

                ''' NON-SHELL - SHOW ONLY COMMANDS '''

                if not args.video:

                    # PTP status test
                    lib.harmonic.harmonic_ptp_test(vendor, rpd_ssh_channel)

                    if vendor == 'Harmonic' and rpd_type == 'RFS':

                        # Environment validations (voltages, temperatures, tamper)
                        lib.harmonic.harmonic_environment_rfs_test(vendor, rpd_ssh_channel, rpd_name)

                    if vendor == 'Harmonic' and rpd_type != 'RFS':

                        # Environment validations (voltages, temperatures, tamper)
                        lib.harmonic.harmonic_environment_test(vendor, rpd_ssh_channel, rpd_name)

                    # Get Map packet counts for the four US channels and run validations
                    lib.harmonic.harmonic_map_packet_test(vendor, rpd_ssh_channel, rpd_name)

                    # OFDM channel tests
                    lib.harmonic.harmonic_ofdm_test(rpd_ssh_channel)

                # Test harmonic running rf configuration for each enabled scqam
                lib.harmonic.harmonic_ingress_packet_test(vendor, rpd_ssh_channel)

                # Get show RF session match counters
                lib.harmonic.harmonic_l2tp_session_test(vendor, rpd_ssh_channel)

        # -------- Standard/Shelf Testing Section End --------

        # -------- DAAS specific tests Start --------
        if args.daas or args.daas_only:
            # Determine DAAS port for rpd
            interface = get_daas_port_for_rpd(daas_ssh_channel, rpd_mac_address)

            # Check for Interface Input Errors
            daas_input_errors_test(daas_ssh_channel, interface)

            # Check for Interface Output Errors
            daas_output_errors_test(daas_ssh_channel, interface)

            # Check port status
            daas_interface_status_test(daas_ssh_channel, interface)

            # Gather interface diagnostics to be parsed by later tests
            interface_diagnostics = get_daas_interface_diagnostics(daas_ssh_channel, interface)

            # Check light levels on that interface against set warning and alarm thresholds
            daas_light_level_test(interface_diagnostics)

            # Check temperatures on that interface against set warning and alarm thresholds
            daas_temperature_test(interface_diagnostics)

            # Check laser bias on that interface against set warning and alarm thresholds
            daas_laser_bias_test(interface_diagnostics)

            # Check voltage on that interface against set warning and alarm thresholds
            daas_voltage_test(interface_diagnostics)

            # Print test results
            print_hc_results(healthcheck_results, daas_name, interface)

        # -------- DAAS specific tests End --------

        # Close the SSH connection to the RPD
        rpd_ssh_channel.close()

        if log['Log']:
            time_string = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S%f')[:-3]
            filename = "result-" + rpd_name + "-" + time_string + ".log"

            if not args.select:
                if vendor == 'Arris':
                    lib.arris.output_log_file(filename)
                    lib.api_aws.upload_to_aws_prod(filename, bucket_name_prod, filename)
                elif vendor == 'Cisco':
                    lib.cisco.output_log_file(filename)
                    lib.api_aws.upload_to_aws_prod(filename, bucket_name_prod, filename)
                elif vendor == 'Harmonic':
                    lib.harmonic.output_log_file(filename)
                    lib.api_aws.upload_to_aws_prod(filename, bucket_name_prod, filename)
            else:
                bucket_name = args.select
                bucket_name_select = ' '.join(map(str, bucket_name))

                if bucket_name_pre == bucket_name_select:
                    if vendor == 'Arris':
                        lib.arris.output_log_file(filename)
                        lib.api_aws.upload_to_aws_pre(filename,  bucket_name_select, filename)
                    elif vendor == 'Cisco':
                        lib.cisco.output_log_file(filename)
                        lib.api_aws.upload_to_aws_pre(filename,  bucket_name_select, filename)
                    elif vendor == 'Harmonic':
                        lib.harmonic.output_log_file(filename)
                        lib.api_aws.upload_to_aws_pre(filename,  bucket_name_select, filename)

                elif bucket_name_prod == bucket_name_select:
                    if vendor == 'Arris':
                        lib.arris.output_log_file(filename)
                        lib.api_aws.upload_to_aws_prod(filename,  bucket_name_select, filename)
                    elif vendor == 'Cisco':
                        lib.cisco.output_log_file(filename)
                        lib.api_aws.upload_to_aws_prod(filename,  bucket_name_select, filename)
                    elif vendor == 'Harmonic':
                        lib.harmonic.output_log_file(filename)
                        lib.api_aws.upload_to_aws_prod(filename,  bucket_name_select, filename)
                else:
                    print('S3 Bucket: ' + bucket_name_select + ' is not a recognized Pre or Post production Bucket Name')
                    print('Please check Bucket Name, and try again...')

            if args.daas or args.daas_only:
                daas_output_log_file(filename, log['Output'])

            ''' retainer days = 7 days '''
            cleanup_log_files(7, time.time())


/*********************************
 * Omitted for brevity           *
 ********************************/


def determine_vendor(vendor, rpd_name):
    try:
        passwd = None

        if "Arris" or "Cisco" or "Harmonic" in vendor:
            pass
        else:
            vendor = "Unknown"
            print("VENDOR:", vendor)
            print("\nUnknown Vendor, exiting!")
            sys.exit()

        # Print for context, return type
        print_title("info", "Gather necessary information before testing")
        print("VENDOR:", vendor)

        # Get password for Harmonic Linux shell
        if vendor == "Harmonic":

            # Additional authentication required to enter Linux shell for Harmonic RPDs.
            from lib.logic import passwd as h_passwd
            passwd = h_passwd

    except AttributeError:
        print('Unable to determine Vendor, exiting...')
        lib.error_check.AttributeError(rpd_name)
        sys.exit()

    return passwd


/*********************************
 * Omitted for brevity           *
 ********************************/


def establish_rpd_ssh_connection(server, rpd_name):

    # Setup Paramiko client
    ssh = paramiko.SSHClient()

    # Don't worry about not having host keys for each RPD
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Attempt to log into the RPD
    try:
        # Log in with admin account, no password (uses jumpbox's present SSH keys)
        ssh.connect(server, username="admin", key_filename='/home/rpdadmin/.ssh/rpd_key', timeout=15)

        # Specifically, open an interactive SSH channel since the RPDs DO NOT support remote command execution
        channel = ssh.get_transport().open_session()
        channel.get_pty()
        channel.invoke_shell()

        output = ""

        # Loop to read shell output
        while True:
            # If shell is actively outputting data, append it and loop again
            if channel.recv_ready():
                output += channel.recv(1024).decode("utf-8")

            # If shell is not actively outputting data
            else:
                # Check for sentinel values for each vendor
                if output.endswith('] RPD# ') or output.endswith('\r\n# ') or output.endswith('\r\nR-PHY#') \
                        or output.endswith('ShelfRPD1:# ') or output.endswith('ShelfRPD2:# ') \
                        or output.endswith('ShelfRPD0:# '):
                    break
                # Cisco specific steps, since there is that long process to initially get to the RPD CLI
                elif output.endswith('Press Enter to skip:'):
                    channel.send("\n")
                elif output.endswith('\r\nR-PHY>'):
                    channel.send("en\n")
                    time.sleep(0.5)

    except paramiko.ssh_exception.NoValidConnectionsError:
        print_fail("Unable to connect to " + server + " . No route to host.")
        lib.error_check.NoValidConnectionsError(rpd_name)
        exit(1)
    except paramiko.ssh_exception.socket.timeout:
        print_fail("Unable to connect to " + server + ". The RPD is unreachable.")
        lib.error_check.sockettimeout(rpd_name)
        exit(1)

    return channel, output


/*********************************
 * Omitted for brevity           *
 ********************************/


def test_template(vendor, rpd_ssh_channel):
    if not Active.testing:
        test_name = "DAAS Interface Light Level Check"
        print_title("test", test_name)
        print("Check laser output and receive levels for this RPD's interface against DAAS error and warning thresholds")
        test_results = []
        command = ''

        # Run the command on the open SSH channel
        output = single_rpd_command(rpd_ssh_channel, command, vendor)

        try:
            # DEBUG
            print(repr(output))

            # Try to parse out the data values from the command output
            print()

            # Get full results of test suite
            if 'Fail' in test_results:
                test_results = 'Fail'
            elif 'Warn' in test_results:
                test_results = 'Warn'
            else:
                test_results = 'Pass'

            # Add result to final report
            append_to_hc_results(test_name, test_results)

            # If log switch was specified, append this/these command(s) output(s) to the running log
            if log['Log']:
                append_log_test_title(test_name)
                log['Output'].append(output)

        except AttributeError:
            append_to_hc_results(test_name, 'Fail')
            print('\x1b[1;31mFAIL\x1b[0m : Unable to determine DAAS Light levels')
            pass


# ----------------------------------------
# -            DAAS Tests                -
# ----------------------------------------

def daas_light_level_test(interface_diagnostics):
    if not Active.testing:
        test_results = []
        test_name = "DAAS Interface Light Level Check"
        print_title("test", test_name)
        print("Check laser output and receive levels for this RPD's interface against DAAS error and warning thresholds")

        try:
            # Parse out info we want from diagnostic output
            laser_output = float(re.search('[ \t]+:[ \t]+.*\/([\S\s]*)dBm\n[ \t]+Module temperature[ \t]+:',
                                           interface_diagnostics).group(1).strip())

            laser_output_high_alarm = float(re.search('reshold.*\/([\S\s]*)dBm\n[ \t]+.*Laser output power low a',
                                                      interface_diagnostics).group(1).strip())

            laser_output_low_alarm = float(re.search('low alarm.*\/([\S\s]*)dBm\n[ \t]+.*Laser output power high w',
                                                     interface_diagnostics).group(1).strip())

            laser_output_high_warn = float(re.search('power high w.*\/([\S\s]*)dBm\n[ \t]+.*Laser o',
                                                     interface_diagnostics).group(1).strip())

            laser_output_low_warn = float(re.search('ower low warning th.*\/([\S\s]*)dBm\n[ \t]+.*Mod',
                                                    interface_diagnostics).group(1).strip())

            laser_receive = float(re.search('receiver power.*\/([\S\s].[\d]*.[\d]*)',
                                            interface_diagnostics).group(1).strip())

            laser_receive_high_alarm = float(re.search('rx power high alarm t.*\/([\S\s]*)dBm\n.*low a',
                                                       interface_diagnostics).group(1).strip())

            laser_receive_low_alarm = float(re.search('rx power low alarm t.*\/([\S\s]*)dBm\n.* h',
                                                      interface_diagnostics).group(1).strip())

            laser_receive_high_warn = float(re.search('rx power high warning t.*\/([\S\s]*)dBm\n[ \t]+L',
                                                      interface_diagnostics).group(1).strip())

            laser_receive_low_warn = float(re.search('rx power low w.*\/([\S\s].[\d]*.[\d]*)',
                                                     interface_diagnostics).group(1).strip())

            # Output checks
            # Check if our value is within good range or if it exceeds warning/alarm thresholds
            if laser_output >= laser_output_high_alarm:
                print_fail("Laser output power is " + str(laser_output) + " dBm which exceeds high alarm threshold of "
                           + str(laser_output_high_alarm) + " dBm")
                test_results.append("Fail")
            elif laser_output <= laser_output_low_alarm:
                print_fail("Laser output power is " + str(laser_output) + " dBm which is less than low alarm threshold of "
                           + str(laser_output_low_alarm) + " dBm")
                test_results.append("Fail")
            elif laser_output_high_warn <= laser_output < laser_output_high_alarm:
                print_warn("Laser output power is " + str(laser_output) + " dBm which exceeds high warning threshold of "
                           + str(laser_output_high_warn) + " dBm")
                test_results.append("Warn")
            elif laser_output_low_warn >= laser_output > laser_output_low_alarm:
                print_warn("Laser output power is " + str(laser_output) + " dBm which is less than low warning threshold of "
                           + str(laser_output_low_warn) + " dBm")
                test_results.append("Warn")
            else:
                print_pass("Laser output power is " + str(laser_output) + " dBm which is an okay value")
                test_results.append("Pass")

            # Receive checks
            # Check if our value is within good range or if it exceeds warning/alarm thresholds
            if laser_receive >= laser_receive_high_alarm:
                print_fail("Laser receive power is " + str(laser_receive) + " dBm which exceeds high alarm threshold of "
                           + str(laser_receive_high_alarm) + " dBm")
                test_results.append("Fail")
            elif laser_receive <= laser_receive_low_alarm:
                print_fail("Laser receive power is " + str(laser_receive) + " dBm which is less than low alarm threshold of "
                           + str(laser_receive_low_alarm) + " dBm")
                test_results.append("Fail")
            elif laser_receive_high_warn >= laser_receive > laser_receive_high_alarm:
                print_warn("Laser receive power is " + str(laser_receive) + " dBm which exceeds high warning threshold of "
                           + str(laser_receive_high_warn) + " dBm")
                test_results.append("Warn")
            elif laser_receive_low_warn <= laser_receive < laser_receive_low_alarm:
                print_warn("Laser receive power is " + str(laser_receive) + " dBm which is less than low warning threshold of "
                           + str(laser_receive_low_warn) + " dBm")
                test_results.append("Warn")
            else:
                print_pass("Laser receive power is " + str(laser_receive) + " dBm which is an okay value")
                test_results.append("Pass")

            # Get full results of test suite
            if 'Fail' in test_results:
                test_results = 'Fail'
            elif 'Warn' in test_results:
                test_results = 'Warn'
            else:
                test_results = 'Pass'

            # Add result to final report
            append_to_hc_results(test_name, test_results)

        except AttributeError:
            append_to_hc_results(test_name, 'Fail')
            print('\x1b[1;31mFAIL\x1b[0m : Unable to determine DAAS Light levels')
            pass


/*********************************
 * Omitted for brevity           *
 ********************************/


# Command line arguments
parser = argparse.ArgumentParser(description="Script for automated health checking of the RPD, by checking outputs of "
                                             "various commands directly on the RPD itself."
                                             "\nArguments:\n"
                                             "-r, --rpd\t\t RPD IP address\n"
                                             "-d, --daas\t\t Run DAAS related tests\n"
                                             "-do, --daas_only\t\t Run DAAS ONLY related tests\n"
                                             "-l, --log\t\t Generate a log and upload output to AWS\n"
                                             "-v, --video\t\t Run RPD Video Check ONLY"
                                 , formatter_class=RawTextHelpFormatter)

parser.add_argument("-r", "--rpd",
                    nargs="+",
                    help="rpd to check",
                    metavar='',
                    )

parser.add_argument("-d", "--daas",
                    action='store_true',
                    help="run daas related tests"
                    )

parser.add_argument("-do", "--daas_only",
                    action='store_true',
                    help="run daas related tests"
                    )

parser.add_argument("-l", "--log",
                    action='store_true',
                    help="generate a log of all commands run with their output"
                    )

parser.add_argument("-m", "--maint",
                    action='store_true',
                    help=argparse.SUPPRESS
                    )

parser.add_argument("-v", "--video",
                    action='store_true',
                    help="Run video only checks"
                    )

parser.add_argument("-i", "--ipv6",
                    type=str,
                    help="rpd to check",
                    )

parser.add_argument("-s", "--select",
                    nargs="+",
                    metavar='',
                    help=argparse.SUPPRESS
                    )

if __name__ == '__main__':
    main()
