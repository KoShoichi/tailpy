#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import time
import math
import binascii
from struct import *
from datetime import datetime
from py8583.py8583 import Iso8583
from py8583.py8583spec import IsoSpec1993JCN, IsoSpec1987MC, IsoSpec1987VISA, IsoSpec1987VISAa
from pyCafis.pyCafis import pyCafis

def print_file_from(filename, pos, type, start, end, date, bitstr, liststr, continues):
    if int(date) == 0 and (int(start) != 0 or int(end) != 240000):
        date = datetime.now().strftime("%y%m%d")
    if len(bitstr) > 0:
        disp_type = print_gw_bit_hdr(type, bitstr, liststr)
    with open(filename, 'rb') as fh:
        fh.seek(pos)
        while True:
            chunk = fh.read(2251)
            if not chunk:
                break
            if int(date) != 0:
                if int(chunk[2:8]) != int(date):
                    fh.read(int(chunk[19:39])-84+1)
                    continue
                if int(chunk[8:14]) < int(start):
                    fh.read(int(chunk[19:39])-84+1)
                    continue
                if int(chunk[8:14]) > int(end):
                    break
            try:
                if len(bitstr) > 0:
                    if len(liststr) > 0:
                        msg_len = print_gw_hdr(chunk[39:2251], disp_type, ' ')
                    else:
                        msg_len = print_gw_hdr(chunk[39:2251], disp_type, ',')
                    chunk = fh.read(msg_len+1)
                    if type[-4:] == '-all' or type[-4:] == '-bin':
                        type = type[:-4]
                    if len(liststr) > 0:
                        print_list(chunk[0:msg_len],type,bitstr,liststr)
                    else:
                        print_csv(chunk[0:msg_len],type,bitstr)
                else:
                    print_oc_hdr(chunk[0:39])
                    msg_len = print_gw_hdr(chunk[39:2251])
                    chunk = fh.read(msg_len+1)
                    if type == 'hex':
                        print_hex(chunk[0:msg_len],' < Hexadecimal Dump >')
                    elif type == 'hex-e':
                        print_hex(chunk[0:msg_len],' < Hexadecimal Dump (EBCDIC) >', 'ebcdic')
                    elif type[0:3] == 'vci':
                        print_vci(chunk[0:msg_len],type)
                    elif type == 'cfs':
                        print_cfs(chunk[0:msg_len])
                    elif type[0:3] == 'jcn':
                        print_jcn(chunk[0:msg_len],type)
                    elif type == 'bkn':
                        print_bkn(chunk[0:msg_len])
                    elif type == 'bs1' or type == 'bs1a':
                        print_bs1(chunk[0:msg_len],type)
            except:
                if continues:
                    print(" !!! DECODE ERROR !!!")
                    continue
                else:
                    raise

def print_gw_bit_hdr(type, bitstr, liststr):
    if type[-3:] == 'all':
        disp_type = 'all'
    elif type[-3:] == 'bin':
        disp_type = 'bin'
    else:
        disp_type = 'normal'

    if len(liststr) > 0:
        if disp_type == 'all':
            printtxt = '----------------------------- ------------------- ---------------- --- -------- -------- -------- - ----------------------------- ---------------------------------------- ----------------------------- ------------------ ------------------- ------------------- ------------------- ------------------- ----'
        elif disp_type == 'bin':
            printtxt = '----------------------------- ------------------- --------'
        else:
            printtxt = '----------------------------- --------'

        if type[:3] == 'hex':
            pass
        elif type[:3] == 'cfs':
            printtxt += ' ---- ---- ---'
        else:
            printtxt += ' ----'
        bitmap = bitstr.split(',')
        col_size = [int(i) for i in liststr.split(',')]
        if len(bitmap) == len(col_size):
            for bit,length in zip(bitmap, col_size):
                printtxt += " " + bit + "-" * (length-len(bit))
        else:
            printtxt += ' ' + ' '.join(bitmap)
    else:
        if disp_type == 'all':
            printtxt = 'Timestamp,Timestamp[bin],ServiceId,InstanceId,ProcessId,ThreadId,I/O Type,MsgEncType,Incoming Req,Outgoing Req,Outgoing Rep,Incoming Rep,Incoming Req[bin],Outgoing Req[bin],Outgoing Rep[bin],Incoming Rep[bin],msg_len,'
        elif disp_type == 'bin':
            printtxt = 'Timestamp,Timestamp[bin],I/O Type,'
        else:
            printtxt = 'Timestamp,I/O Type,'

        if type[:3] == 'hex':
            printtxt += 'message'
        elif type[:3] == 'cfs':
            printtxt += 'MsgType,MasMsgType,ErrCode,' + bitstr
        else:
            printtxt += 'MTI,' + bitstr
    print(printtxt)

    return disp_type

def print_hex(buf,hdr_text,enc='ascii'):
    print(hdr_text)
    text = ""
    offset = 0
    cnt = 0
    print(" %06x:" % offset, end=' ')
    for byte in bytes(buf):
        print("%02x" % int(byte), end=' ')
        if enc == 'ebcdic':
            text = text + ebcdic_decode(byte)
        else:
            text = text + (chr(byte) if byte >= 32 and byte <= 126 else ".")
        offset = offset +1
        if cnt < 15:
            cnt = cnt + 1
        else:
            print(" |%s|" % text)
            cnt = 0
            text = ""
            print(" %06x:" % offset, end=' ')
    if cnt <= 15:
        print("   " * (16 - cnt) + " |%s" % text + " " * (16 - cnt) + "|")
    else:
        print("")    

def ebcdic_decode(byte):
    ebcmap = {
        0x40:' ',         0x4a:'[',0x4b:'.',0x4c:'<',0x4d:'(',0x4e:'+',0x4f:'!',
        0x50:'&',        0x5a:']',0x5b:'\\',0x5c:'*',0x5d:')',0x5e:';',0x5f:'^',
        0x60:'-',0x61:'/',0x6a:'|',0x6b:',',0x6c:'%',0x6d:'_',0x6e:'>',0x6f:'?',
        0x79:'`',         0x7a:':',0x7b:'#',0x7c:'@',0x7d:"'",0x7e:'=',0x7f:'"',
        0xc0:'{',0xd0:'}',0xe0:'$' }

    if byte in ebcmap:
        ret = ebcmap[byte]
    elif byte >= 193 and byte <= 201: # A to I
        ret = (chr(byte-128))
    elif byte >= 209 and byte <= 217: # J to R
        ret = (chr(byte-135))
    elif byte >= 226 and byte <= 233: # S to Z
        ret = (chr(byte-143))
    elif byte >= 240 and byte <= 249: # 0 to 9
        ret = (chr(byte-192))
    else:
        ret = "."
    return ret

def print_oc_hdr(buf):
    hdr = unpack('18sc20s',buf)
    print(" " + "-" * 78)
    print(" < OnCore Log Header >")
    print(" Write Timestamp: " + hdr[0][0:4].decode() + "/" + hdr[0][4:6].decode() + "/" + hdr[0][6:8].decode() + " " + hdr[0][8:10].decode() + ":" + hdr[0][10:12].decode() + ":" + hdr[0][12:18].decode())
    print(" Data Length: " + hdr[2].decode().lstrip('0'))

def print_gw_hdr(buf, disptype=None, sep=None):
    hdr = unpack('19s10s8s31sI19s19s19s19s2048sIIII',buf)
    if disptype == None:
        print(" < Gateway Log Header >")
        print(" Timestamp  : " + get_timestamp_str(int(hdr[0].decode())) + " [" + hdr[0].decode() + "]")
        print(" ServiceId  : " + hdr[3].decode())
        print(" InstanceId : " + str(hdr[4]))
        print(" ProcessId  : " + str(hdr[11]))
        print(" ThreadId   : " + str(hdr[12]))
        print(" MsgEncType : " + str(hdr[10]))
        print(" I/O Type   : " + hdr[2].decode())
        print(" Incoming REQ Timestamp : " + get_timestamp_str(int(hdr[5].decode())) + " [" + hdr[5].decode() + "]")
        print(" Outgoing REQ Timestamp : " + get_timestamp_str(int(hdr[6].decode())) + " [" + hdr[6].decode() + "]")
        print(" Outgoing REP Timestamp : " + get_timestamp_str(int(hdr[7].decode())) + " [" + hdr[7].decode() + "]")
        print(" Incoming REP Timestamp : " + get_timestamp_str(int(hdr[8].decode())) + " [" + hdr[8].decode() + "]")
        print(" PassingInfo : ", end='\n ')
        for p in hdr[9].decode().split(','):
            print("    " + p)
        print(" Message Length : " + str(hdr[13]))

    elif disptype == 'all':
        print(get_timestamp_str(int(hdr[0])) + sep, end='')
        print(hdr[0] + sep, end='')
        if sep == ' ':
            print(hdr[3].decode().ljust(16) + sep, end='')
            print(str(hdr[4]).ljust(3) + sep, end='')
            print(str(hdr[11]).ljust(8) + sep, end='')
            print(str(hdr[12]).ljust(8) + sep, end='')
            print(hdr[2].decode() + sep, end='')
            print(str(hdr[10]) + sep, end='')
            print(get_timestamp_str(int(hdr[5].decode())) + sep, end='')
            print(get_timestamp_str(int(hdr[6].decode())) + sep, end='')
            print(get_timestamp_str(int(hdr[7].decode())) + sep, end='')
            print(get_timestamp_str(int(hdr[8].decode())) + sep, end='')
            print(hdr[5].decode().ljust(19) + sep, end='')
            print(hdr[6].decode().ljust(19) + sep, end='')
            print(hdr[7].decode().ljust(19) + sep, end='')
            print(hdr[8].decode().ljust(19) + sep, end='')
        else:
            print(hdr[3].decode() + sep, end='')
            print(str(hdr[4]) + sep, end='')
            print(str(hdr[11]) + sep, end='')
            print(str(hdr[12]) + sep, end='')
            print(hdr[2].decode() + sep, end='')
            print(str(hdr[10]) + sep, end='')
            print(get_timestamp_str(int(hdr[5].decode())) + sep, end='')
            print(get_timestamp_str(int(hdr[6].decode())) + sep, end='')
            print(get_timestamp_str(int(hdr[7].decode())) + sep, end='')
            print(get_timestamp_str(int(hdr[8].decode())) + sep, end='')
            print(hdr[5].decode() + sep, end='')
            print(hdr[6].decode() + sep, end='')
            print(hdr[7].decode() + sep, end='')
            print(hdr[8].decode() + sep, end='')
        print(str(hdr[13]).ljust(4) + sep, end='')

    elif disptype == 'bin':
        print(get_timestamp_str(int(hdr[0].decode())) + sep, end='')
        print(hdr[0].decode() + sep, end='')
        print(hdr[2].decode() + sep, end='')

    else:
        print(get_timestamp_str(int(hdr[0].decode())) + sep, end='')
        print(hdr[2].decode() + sep, end='')

    return int(hdr[13])

def print_cfs(buf):
    print(" < CAFIS共通制御ヘッダ >")
    trailer_len = int(buf[60:63])
    if trailer_len == 0:
        hdr = unpack('4s6s2s3s6s7s4s7s4s4s4s1s2s2s3s1s3s',buf[0:63])
    else:
        hdr = unpack('4s6s2s3s6s7s4s7s4s4s4s1s2s2s3s1s3s',buf[:-trailer_len])
    print("   1 - 経路番号           : [{0}]".format(hdr[0].decode()))
    print("   2 - 仕向処理通番       : [{0}]".format(hdr[1].decode()))
    print("   3 - センタ識別番号     : [{0}]".format(hdr[2].decode()))
    print("   4 - 回線番号           : [{0}]".format(hdr[3].decode()))
    print("   5 - CAFIS処理通番      : [{0}]".format(hdr[4].decode()))
    print("   6 - 仕向会社コード     : [{0}]".format(hdr[5].decode() + "-" + hdr[6].decode()))
    print("   8 - 被仕向会社コード   : [{0}]".format(hdr[7].decode() + "-" + hdr[8].decode()))
    print("  10 - 電文種別           : [{0}]".format(hdr[9].decode()))
    print("  11 - CAFIS処理月日      : [{0}]".format(hdr[10].decode()))
    print("  12 - CAT送信状態表示    : [{0}]".format(hdr[11].decode()))
    print("  13 - 仕向処理日付       : [{0}]".format(hdr[12].decode()))
    print("  14 - 代行電文報告表示   : [{0}]".format(hdr[13].decode()))
    print("  15 - 代行電文エラー表示 : [{0}]".format(hdr[14].decode()))
    print("  16 - 代行再仕向表示     : [{0}]".format(hdr[15].decode()))
    print("  17 - トレーラ・レングス : [{0}]".format(hdr[16].decode()))
    if trailer_len > 0:
        cfsdata = pyCafis(buf)
        cfsdata.PrintData()

def print_vci(buf,type):
    print_vci.msg_type = {
        b'1':'Outgoing REQ', b'2':'Outgoing REP',
        b'3':'Incoming REQ', b'4':'Incoming REP',
        b'A':'Echo REQ',     b'B':'Echo REP' }
    print_vci.fmt_type = { b'1':'TLV', b'2':'ISO8583', b'3':'Fixed-Length' }
    print(" < VCI Header >")
    msg_len = int(buf[0:5])
    if msg_len == 48:
        hdr = unpack('5s2scc8s6s11s15s4s',buf)
    else:
        hdr = unpack('5s2scc8s6s11s15s4s',buf[:-msg_len+48])
    print(" Total Message Length: " + hdr[0].decode(), end=' ')
    print("  Header Version: " + hdr[1].decode())
    print(" Message Type: " + print_vci.msg_type[hdr[2]], end=' ')
    print("  Format Type: " + print_vci.fmt_type[hdr[3]]) 
    print(" Request Date and Time: " + hdr[4][0:4].decode() + "/" + hdr[4][4:6].decode() + "/" + hdr[4][6:8].decode() + " " + hdr[5][0:2].decode() + ":" + hdr[5][2:4].decode() + ":" + hdr[5][4:6].decode(), end=' ')
    print("  Sequence Number: " + hdr[6].decode())
    print(" Transaction Key: " + hdr[7].decode(), end=' ')
    print("  Reply Wait Timer: " + hdr[8].decode())
    if msg_len > 0:
        if type == 'vci':
            print_hex(buf[53:]," < Message [Hexadecimal Dump] >")
        elif type == 'vci-jcn':
            print_iso(buf[53:], 'jcn')

def print_bkn(buf):
    print(" < MasterCard BANKNET Header >")
    print(" Total Message Length: " + str(int(binascii.hexlify(buf[0:2]), 16)))
    print_iso(buf[2:], 'bkn')

def print_bs1(buf,type):
    hdr_dict = {}
    offset  = 4
    hdr_len = 26
    reject_check = unpack('B',buf[offset:offset+1])
    if reject_check[0] == hdr_len:
        hdr_dict = hdr_parse(hdr_dict, buf[offset:offset+hdr_len],'bs1_r')
        print(" < VISA BASE1 Reject Header >")
        print(" RH01 - Header Length           : " + hdr_dict['RH01'])
        print(" RH02 - Header Format           : " + hdr_dict['RH02'])
        print(" RH03 - Text Format             : " + hdr_dict['RH03'])
        print(" RH04 - Total Message Length    : " + hdr_dict['RH04'])
        print(" RH05 - Destination Station ID  : " + hdr_dict['RH05'])
        print(" RH06 - Source Station ID       : " + hdr_dict['RH06'])
        print(" RH07 - Round-Trip Control Info : " + hdr_dict['RH07'])
        print(" RH08 - BASE-I Flags            : " + hdr_dict['RH08'])
        print(" RH09 - Message Status Flags    : " + hdr_dict['RH09'])
        print(" RH10 - Batch Number            : " + hdr_dict['RH10'])
        print(" RH11 - Reserved                : " + hdr_dict['RH11'])
        print(" RH12 - User Information        : " + hdr_dict['RH12'])
        print(" RH13 - Bitmap                  : " + hdr_dict['RH13'])
        print(" RH14 - Reject Code             : " + hdr_dict['RH14'])
        offset += hdr_len

    hdr_len = 22
    hdr_dict = hdr_parse(hdr_dict, buf[offset:offset+hdr_len],'bs1_s')
    print(" < VISA BASE1 Standard Header >")
    print(" SH01 - Header Length           : " + hdr_dict['SH01'])
    print(" SH02 - Header Format           : " + hdr_dict['SH02'])
    print(" SH03 - Text Format             : " + hdr_dict['SH03'])
    print(" SH04 - Total Message Length    : " + hdr_dict['SH04'])
    print(" SH05 - Destination Station ID  : " + hdr_dict['SH05'])
    print(" SH06 - Source Station ID       : " + hdr_dict['SH06'])
    print(" SH07 - Round-Trip Control Info : " + hdr_dict['SH07'])
    print(" SH08 - BASE-I Flags            : " + hdr_dict['SH08'])
    print(" SH09 - Message Status Flags    : " + hdr_dict['SH09'])
    print(" SH10 - Batch Number            : " + hdr_dict['SH10'])
    print(" SH11 - Reserved                : " + hdr_dict['SH11'])
    print(" SH12 - User Information        : " + hdr_dict['SH12'])
    offset += hdr_len

    print_iso(buf[offset:], type)

def print_jcn(buf, type):
    hdr_dict = {}
    hdr_dict = hdr_parse(hdr_dict, buf[:80],'jcn')
    print(" < CARDNET共通制御ヘッダ >")
    print(" CH01 ヘッダータイプ　　　　: " + hdr_dict['CH01'])
    print(" CH02 全体電文長　　　　　　: " + hdr_dict['CH02'])
    print(" CH03 差出センターＩＤ　　　: " + hdr_dict['CH03'])
    print(" CH04 宛先センターＩＤ　　　: " + hdr_dict['CH04'])
    print(" CH05 加盟店契約会社コード　: " + hdr_dict['CH05'])
    print(" CH06 送信日時　　　　　　　: " + hdr_dict['CH06'])
    print(" CH07 モードフラグ　　　　　: " + hdr_dict['CH07'])
    print(" CH08 予備　　　　　　　　　: " + hdr_dict['CH08'])
    print(" < CARDNET業務共通ヘッダ >")
    print(" BH01 ヘッダータイプ　　　　: " + hdr_dict['BH01'])
    print(" BH02 電文種別コード　　　　: " + hdr_dict['BH02'])
    print(" BH03 電文認証値　　　　　　: " + hdr_dict['BH03'])
    print(" BH04 チェックディジット　　: " + hdr_dict['BH04'])
    print(" BH05 仕向区分　　　　　　　: " + hdr_dict['BH05'])
    print(" BH06 カット対象日付　　　　: " + hdr_dict['BH06'])
    print(" BH07 ＢＯＤＹ部電文長　　　: " + hdr_dict['BH07'])
    print(" BH08 カードネット取引識別　: " + hdr_dict['BH08'])
    print(" BH09 カードネット取引通番　: " + hdr_dict['BH09'])
    print(" BH10 カードネット使用域　　: " + hdr_dict['BH10'])
    print(" BH11 予備　　　　　　　　　: " + hdr_dict['BH11'])
    if type == 'jcn':
        print_iso(buf[80:], 'jcn')
    # jcn-cipはISO出力しない

def hdr_parse(hdr_dict, hbuf, type):
    if type == 'jcn': 
        hdr = unpack('2s2s11s11s11s7sc2s2s4s4s4sc4s2s2s6s2s2s',hbuf[:80])
        hdr_dict.update({
            'CH01':hdr[0].decode(),
            'CH02':binascii.hexlify(hdr[1]).decode(),
            'CH03':hdr[2].decode(),
            'CH04':hdr[3].decode(),
            'CH05':hdr[4].decode(),
            'CH06':binascii.hexlify(hdr[5]).decode(),
            'CH07':binascii.hexlify(hdr[6]).decode(),
            'CH08':hdr[7].decode(),
            'BH01':hdr[8].decode(),
            'BH02':hdr[9].decode(),
            'BH03':binascii.hexlify(hdr[10]).decode(),
            'BH04':binascii.hexlify(hdr[11]).decode(),
            'BH05':binascii.hexlify(hdr[12]).decode(),
            'BH06':binascii.hexlify(hdr[13]).decode(),
            'BH07':binascii.hexlify(hdr[14]).decode(),
            'BH08':binascii.hexlify(hdr[15]).decode(),
            'BH09':binascii.hexlify(hdr[16]).decode(),
            'BH10':binascii.hexlify(hdr[17]).decode(),
            'BH11':hdr[18].decode()
        })
    elif type == 'bs1_r': 
        hdr = unpack('BBBBB3s3sBBBBBBB3sBBBBB',hbuf)
                    # 012345 6 78901234 56789
        hdr_dict.update({
            'RH01':str(hdr[0]),
            'RH02':format(hdr[1],'08b'),
            'RH03':format(hdr[2],'02x'),
            'RH04':str(int.from_bytes(hdr[3:5],'big')),
            'RH05':binascii.hexlify(hdr[5]).decode(),
            'RH06':binascii.hexlify(hdr[6]).decode(),
            'RH07':format(hdr[7],'08b'),
            'RH08':format(hdr[8],'08b') + format(hdr[9],'08b'),
            'RH09':format(hdr[10],'08b') + format(hdr[11],'08b') + format(hdr[12],'08b'),
            'RH10':str(hdr[13]),
            'RH11':binascii.hexlify(hdr[14]).decode(),
            'RH12':format(hdr[15],'02x'),
            'RH13':format(hdr[16],'08b') + format(hdr[17],'08b'),
            'RH14':format(hdr[18],'02x') + format(hdr[19],'02x')
            })
    elif type == 'bs1_s': 
        hdr = unpack('BBBBB3s3sBBBBBBB3sB',hbuf)
                    # 012345 6 78901234 5
        hdr_dict.update({
            'SH01':str(hdr[0]),
            'SH02':format(hdr[1],'08b'),
            'SH03':format(hdr[2],'02x'),
            'SH04':str(int.from_bytes(hdr[3:5],'big')),
            'SH05':binascii.hexlify(hdr[5]).decode(),
            'SH06':binascii.hexlify(hdr[6]).decode(),
            'SH07':format(hdr[7],'08b'),
            'SH08':format(hdr[8],'08b') + format(hdr[9],'08b'),
            'SH09':format(hdr[10],'08b') + format(hdr[11],'08b') + format(hdr[12],'08b'),
            'SH10':str(hdr[13]),
            'SH11':binascii.hexlify(hdr[14]).decode(),
            'SH12':format(hdr[15],'02x'),
            })

    return hdr_dict

def print_iso(buf, type):
    if type == 'jcn':
        print(" < ISO8583データ部 >")
        isodata = Iso8583(buf, IsoSpec1993JCN())
    elif type == 'bkn':
        print(" < ISO8583 Data Elements >")
        isodata = Iso8583(buf, IsoSpec1987MC())
    elif type == 'bs1':
        print(" < ISO8583 Data Elements >")
        isodata = Iso8583(buf, IsoSpec1987VISA())
    elif type == 'bs1a':
        print(" < ISO8583 Data Elements >")
        isodata = Iso8583(buf, IsoSpec1987VISAa())
    isodata.PrintMessage()

def print_list(buf, type, bitstr, liststr):
    if type == 'hex':
        printtxt = [chr(byte) if byte >= 32 and byte <= 126 else "." for byte in bytes(buf)]
        print(''.join(printtxt))
    elif type == 'hex-e':
        printtxt = [ebcdic_decode(byte) for byte in bytes(buf)]
        print(''.join(printtxt))
    elif type == 'cfs':
        print_list_cfs(buf, bitstr, liststr)
    else:
        print_list_iso(buf, type, bitstr, liststr)

def print_list_cfs(buf, bitstr, liststr):
    sep = ' '
    cfsdata = pyCafis(buf)
    printtxt = cfsdata.GetMsgType().ljust(4)
    printtxt += sep + cfsdata.GetMasMsgType().replace(' ', '^').ljust(4)
    printtxt += sep + cfsdata.GetErrCode().replace(' ', '^').ljust(3)
    bitmap = bitstr.split(',')
    col_size = [int(i) for i in liststr.split(',')]
    for i in range(len(bitmap)):
        tmp = bitmap[i].partition(':')
        data_name = tmp[0]
        item = tmp[2]
        value = cfsdata.GetDataValue(data_name,item).replace(' ', '^')
        if len(col_size) > i:
            if len(bitmap[i]) > col_size[i]:
                printtxt += sep + value.ljust(len(bitmap[i]))
            else:
                printtxt += sep + value.ljust(col_size[i])
        else:
            if len(bitmap[i]) > len(value):
                printtxt += sep + value.ljust(len(bitmap[i]))
            else:
                printtxt += sep + value
    print(printtxt)

def print_list_iso(buf, type, bitstr, liststr):
    sep = ' '
    hdr_dict = {}
    if type == 'jcn':
        hdr_dict = hdr_parse(hdr_dict, buf[:80],'jcn')
        isodata = Iso8583(buf[80:], IsoSpec1993JCN())
    elif type == 'bkn':
        isodata = Iso8583(buf[2:], IsoSpec1987MC())
    elif type == 'bs1' or type == 'bs1a':
        offset  = 4
        hdr_len = 26
        reject_check = unpack('B',buf[offset:offset+1])
        if reject_check[0] == hdr_len:
            hdr_dict = hdr_parse(hdr_dict, buf[offset:offset+hdr_len],'bs1_r')
            offset += hdr_len
            hdr_len = 22
            hdr_dict = hdr_parse(hdr_dict, buf[offset:offset+hdr_len],'bs1_s')
            offset += hdr_len
        else:
            hdr_len = 22
            hdr_dict = hdr_parse(hdr_dict, buf[offset:offset+hdr_len],'bs1_s')
            offset += hdr_len
        isodata = Iso8583(buf[offset:], IsoSpec1987VISA())
    printtxt = isodata.GetMti()
    bitmap   = [i.upper() for i in bitstr.split(',')]
    col_size = [int(i) for i in liststr.split(',')]
    for i in range(len(bitmap)):
        if bitmap[i].isdigit():
            value = str(isodata.GetField(int(bitmap[i])))
        else:
            if  bitmap[i] in hdr_dict:
                value = hdr_dict[bitmap[i]]
            else:
                value = ''
        value = value.replace(' ', '^')
        if len(col_size) > i:
            if len(str(bitmap[i])) > col_size[i]:
                printtxt += sep + value.ljust(len(bitmap[i]))
            else:
                printtxt += sep + value.ljust(col_size[i])
        else:
            if len(str(bitmap[i])) > len(value):
                printtxt += sep + value.ljust(len(bitmap[i]))
            else:
                printtxt += sep + value
    print(printtxt)

def print_csv(buf, type, bitstr):
    if type == 'hex':
        printtxt = [chr(byte) if byte >= 32 and byte <= 126 else "." for byte in bytes(buf)]
        print(''.join(printtxt))
    elif type == 'hex-e':
        printtxt = [ebcdic_decode(byte) for byte in bytes(buf)]
        print(''.join(printtxt))
    elif type == 'cfs':
        print_csv_cfs(buf, bitstr)
    else:
        print_csv_iso(buf, type, bitstr)

def print_csv_cfs(buf, bitstr):
    sep = ','
    cfsdata = pyCafis(buf)
    printtxt = cfsdata.GetMsgType()
    printtxt += sep + cfsdata.GetMasMsgType()
    printtxt += sep + cfsdata.GetErrCode()
    bitmap = bitstr.split(',')
    for i in range(len(bitmap)):
        tmp = bitmap[i].partition(':')
        data_name = tmp[0]
        item = tmp[2]
        printtxt += sep + cfsdata.GetDataValue(data_name,item)
    print(printtxt)

def print_csv_iso(buf, type, bitstr):
    sep = ','
    hdr_dict = {}
    if type == 'jcn':
        hdr_dict = hdr_parse(hdr_dict, buf[:80],'jcn')
        isodata = Iso8583(buf[80:], IsoSpec1993JCN())
    elif type == 'bkn':
        isodata = Iso8583(buf[2:], IsoSpec1987MC())
    elif type == 'bs1' or type == 'bs1a':
        offset  = 4
        hdr_len = 26
        reject_check = unpack('B',buf[offset:offset+1])
        if reject_check[0] == hdr_len:
            hdr_dict = hdr_parse(hdr_dict, buf[offset:offset+hdr_len],'bs1_r')
            offset += hdr_len
            hdr_len = 22
            hdr_dict = hdr_parse(hdr_dict, buf[offset:offset+hdr_len],'bs1_s')
            offset += hdr_len
        else:
            hdr_len = 22
            hdr_dict = hdr_parse(hdr_dict, buf[offset:offset+hdr_len],'bs1_s')
            offset += hdr_len
        isodata = Iso8583(buf[offset:], IsoSpec1987VISA())
    printtxt = isodata.GetMti()
    bitmap   = [i.upper() for i in bitstr.split(',')]
    for i in range(len(bitmap)):
        if bitmap[i].isdigit():
            printtxt += sep + str(isodata.GetField(int(bitmap[i])))
        else:
            if  bitmap[i] in hdr_dict:
                printtxt += sep + hdr_dict[bitmap[i]]
            else:
                printtxt += sep
    print(printtxt)

def get_timestamp_str(timestamp):
    if timestamp == 0:
        return "----/--/-- --:--:--.---------"
    else:
        unixtime = math.floor(timestamp / 1000000000)
        nanosec = timestamp - unixtime * 1000000000
        return datetime.fromtimestamp(unixtime).strftime('%Y/%m/%d %H:%M:%S') + "." + '%09d' % nanosec

def _fstat(filename):
    st_results = os.stat(filename)
    return (st_results.st_size, st_results.st_mtime)


def _print_if_needed(filename, last_stats, no_fn, last_fn, type, start, end, date, bitstr, liststr, continues):
    changed = False
    #Find the size of the file and move to  the end
    tup = _fstat(filename)
    # print tup
    if last_stats[filename] != tup:
        changed = True
        if not no_fn and last_fn != filename:
            print('\n<%s>' % filename)
        print_file_from(filename, last_stats[filename][0], type, start, end, date, bitstr, liststr, continues)
        last_stats[filename] = tup
    return changed


def multi_tail(filenames, stdout=sys.stdout, interval=1, follow=False, no_fn=False, type='hex', start=0, end=240000, date=0000, bitstr='', liststr=False, continues=False):
    S = lambda st_size_st_mtime: (0, st_size_st_mtime[1])
    last_stats = dict((fn, S(_fstat(fn))) for fn in filenames)
    last_fn = None
    last_print = 0
    while 1:
        # print last_stats
        changed = False
        for filename in filenames:
            if _print_if_needed(filename, last_stats, no_fn, last_fn, type, start, end, date, bitstr, liststr, continues):
                changed = True
                last_fn = filename
        if not follow:
            break
        if not changed:
            time.sleep(interval)

if '__main__' == __name__:
    from optparse import OptionParser
    op = OptionParser()
    op.add_option('-F', '--no-fn', help="don't print filename when changes",
        default=False, action='store_true')
    op.add_option('-f', '--follow', help='print appended data as the logs grow',
        default=False, action='store_true')
    op.add_option('-i', '--interval', help='check interval(sec)', type='int',
        default=1)
    op.add_option('-t', '--type',
        help="type of message format [hdr:HEADER / hex:HEXdump /     " \
             "hex-e:HEXdump(EBCDIC) / cfs:CAFIS / vci:VCI /          " \
             "bkn:BANKNET / jcn:CARDNET /                            " \
             "bs1:BASE-I F104 BINARY two-byte format /               " \
             "bs1a:BASE-I F104 BINARY one-byte format /              " \
             "vci-jcn:VCI+ISO8583(JCN) / jcn-cip:CARDNET(cipher)]    " \
             "Timestamp type change for CSV/LIST [<type>[-bin/-all]] ",
        type='str', default='hex')
    op.add_option('-s', '--start',
        help="start time to print logs [hhmmss]",
        type='str', default='000000')
    op.add_option('-e', '--end',
        help="end time to print logs [hhmmss]",
        type='str', default='240000')
    op.add_option('-d', '--date',
        help="date to print logs [YYMMDD]",
        type='str', default=0)
    op.add_option('-b', '--bit',
        help="bit select for CSV/LIST [<bit>,...]                    " \
             "CAFIS:[<data_name>:<item_number>,...]",
        type='str', default='')
    op.add_option('-l', '--liststr',
        help="list desplay for LIST [<length>,...]",
        type='str',default='')
    op.add_option('-c', '--continues', help='processing continues',
        default=False, action='store_true')
    opts, args = op.parse_args()
    try:
        multi_tail(args, interval=opts.interval, 
            follow=opts.follow, no_fn=opts.no_fn,
            type=opts.type, start=opts.start, end=opts.end,
            date=opts.date, bitstr=opts.bit, liststr=opts.liststr,
            continues=opts.continues)
    except KeyboardInterrupt:
        pass
