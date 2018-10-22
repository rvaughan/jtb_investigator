#!/usr/bin/env python3

import os, sys, argparse

def parse_args():
        parser = argparse.ArgumentParser(description='Investigate from the command line')
        parser.add_argument('-i', '--ip', type=str, help = 'IPs or range to investigate separated by spaces (enclose in quotes)')
        parser.add_argument('-n', '--hostname', type=str, help ='Hostnames to investigate separated by spaces (enclose in quotes)')
        parser.add_argument('-f', '--format', type=str, help='Format to export file to (csv (default), json, txt)')
        parser.add_argument('-r', '--read', type=str, help='File to read ips or hostnames from. (start filename with ips or hostnames e.g. hostnames_10282018.txt)')
        parser.add_argument('-c', '--combine', action='store_true', help='Combine reports into 1 report')
        args = parser.parse_args()
        return args

def main():
    args = parse_args()
    ipL = []
    hostL = []
    if args.ip:
        ipL = args.ip.split(' ')
    elif args.hostname:
        hostL = args.hostname.split(' ')
    elif args.read:
        readFile = args.read
        with open(readFile, 'r') as f:
            if 'hostnames' in readFile:
                hosts = f.readlines()
                for h in hosts:
                    hostL.append(h.strip('\n'))
            elif 'ips' in readFile:
                hosts = f.readlines()
                for h in hosts:
                    ipL.append(h)
            else:
                print('[!] I don\'t understand that file type! Make sure it starts with ips or hostnames!')
        f.close
        print(hostL)
    else:
        print('[!] No arguments... Exiting!')
        sys.exit(0)
    myPath = os.path.realpath(__file__).split('/')
    pathLen = len(myPath) - 2
    jtbPath = '/' + '/'.join(myPath[1:pathLen])
    os.chdir(jtbPath)
    sys.path.insert(0, jtbPath)
    import jtb
    import investigation
    
    if ipL:
        print('[*] Got IPs, running investigations.')
        for ip in ipL:
            host = investigation.Host
            host.ip = ip
            newInvestigation = investigation.Investigate()
            host = newInvestigation.autoSherlock(host)
            if args.format:
                newInvestigation.exportReport(host, args.format)
            else:
                newInvestigation.exportReport(host)
    if hostL:
        print('[*] Got hosts, running investigaitons.')
        for inHost in hostL:
            host = investigation.Host()
            host.domainName = inHost
            newInvestigation = investigation.Investigate()
            host = newInvestigation.autoSherlock(host)
            if args.format:
                newInvestigation.exportReport(host, args.format)
            else:
                newInvestigation.exportReport(host, 'csv')
    else:
        print('[!] Couldn\'t get targets from cli!')

if __name__ == '__main__':
    try:
        args = parse_args()
        prog = main()

    except KeyboardInterrupt:
        print('\r[!] Quitting!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)