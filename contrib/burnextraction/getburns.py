#!/usr/bin/python3
import os
import json
import sys
import getopt
import datetime
import csv

includeZeroValue="false"

writer = csv.writer(open('burns.csv', 'w'), delimiter=',', lineterminator='\n', quoting=csv.QUOTE_MINIMAL, escapechar='\\')
row=["blockheight", "time", "value", "txid", "destination", "type", "message"]
writer.writerow(row);


NOPRINT_TRANS_TABLE = {
    i: None for i in range(0, sys.maxunicode + 1) if not chr(i).isprintable()
}
def make_printable(s):
    """Replace non-printable characters in a string."""

    # the translate method on str removes characters
    # that map to None from the string
    return s.translate(NOPRINT_TRANS_TABLE)

def get_block_burns(blocknumber):
    command=f"{exe} getburnsblock \"{blocknumber}\" {includeZeroValue}"
    if(0==blocknumber % 100):
        print(command)
    stream = os.popen(command)
    output = stream.read()
    parsed=json.loads(output)
    if(parsed.get('time') is None):
        return
    dt = datetime.datetime.fromtimestamp(parsed['time'])
    blocktime = dt.strftime("%Y%m%d %H:%M:%S")
    blockheight=blocknumber
    blockhash=parsed['hash']
    for burn in parsed['burns']:
        value=burn['value']
        txid = burn['txid'];
        destination = burn['destination']
        destinationType = burn['type']
        rawmessage = burn['message']
        message = make_printable(bytes.fromhex(rawmessage).decode('utf-8', errors='ignore'))
        row=[blockheight, blocktime, value, txid, destination, destinationType, message]
        writer.writerow(row)
    return

def usage(retval):
    print('getburns.py -s <startblock> -e <endblock> -d <datadir> -c <clidir> [-z]\n')
    print('\tnote datadir refers to the datadir of bitcoin core and clidir refers to the dir where bitcoin-cli is located')
    sys.exit(retval)
    return

def main(argv):
    global includeZeroValue
    global datadir
    global clidir
    global exe
    try:
        opts, args = getopt.getopt(argv,"hzs:e:d:c:",["startblock=", "endblock=", "datadir=", "clidir="])
    except:
        print('getburns.py -s <startblock> -e <endblock> -d <datadir> -c <clidir> [-z]')
        usage(2)
    for opt, arg in opts:
        if opt == '-h':
            usage(0)
        elif opt in ("-s", "--startblock"):
            startblock=int(arg)
        elif opt in ("-e", "--endblock"):
            endblock=int(arg)
        elif opt in ("-d", "--datadir"):
            datadir=arg
        elif opt in ("-c", "--clidir"):
            clidir=arg
        elif opt in ("-z"):
            includeZeroValue="true"
    try: 
        startblock
        endblock
        datadir
        clidir
    except NameError: usage(3)

    rawexe=F"{clidir}/bitcoin-cli"
    exe=f"{rawexe} -datadir={datadir}"

    print(f"start block is {startblock} end block is {endblock}")

    blockrange=range(startblock, endblock+1)
    for height in reversed(blockrange):
        get_block_burns(height)


if __name__ == "__main__":
    main(sys.argv[1:])

