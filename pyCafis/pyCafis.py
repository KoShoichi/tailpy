#!/usr/bin/env python3
# coding: utf-8

# pyCafis.py
#
# date   : 201/03/07
# author : Arisa Kato
# summary: format I/O log in "tail" style for CAFIS

import struct

class ParseError(Exception):
        def __init__(self, value):
                self.str = value
        def __str__(self):
                return repr(self.str)
class pyCafis:

    # ｲﾝｽﾀﾝｽ作成時に展開まで行う
    # 展開結果をself.__Data内に入れる
    def __init__(self,BufMsg = None,):
        self.__StrCode    = ''
        self.__Buff       = {}
        self.__Content    = {}
        self.__DataInfo   = {}
        self.__MsgType    = ''
        self.__MasMsgType = ''
        self.__ErrCode    = ''
        self.__Data       = [] # [data_name][data_list]

        self.__StrCode  = 'shift_jis'
        self.__Buff     = BufMsg
        self.__Content  = ContentTypes
        self.__DataInfo = DataInfo
        self.__MsgType  = BufMsg[43:47].decode(self.__StrCode)
        self.__Separator= '@'.encode(self.__StrCode)
        self.__ProcessMsg = 0       # 処理対象電文種別
        self.__CorpCode = ''        # カウンタ用会社コード
        self.__CorpCodeProcessed = False
        self.ParseCafis()

    # '@'で分解して展開関数(ParseMsgHeader,ParseMsgFirstField,ParseMsgField)を呼ぶ
    def ParseCafis(self):
        self.ParseMsgHeader()

        sep = self.__Buff[63:].partition(self.__Separator)
        data = sep[0] + sep[1]
        if len(data) == 0:
            return
        self.ParseMsgFirstField(data)

        data = sep[2]
        while True:
            if len(data) == 0:
                break
            data_len = self.ParseMsgField(data)
            data = data[data_len:]

    # self.__Content内から取得してきた値を元に判定を行う
    # 基本的に長さで判定
    # 電文種別の判定が必要なデータ部の場合、電文種別一致後、長さ比較
    # 拡張データ部(9-x-xなど)は任意データ部種別で判定
    #（可変の場合、最低限の長さ以上であることを確認）
    # 引き当たらなかった場合データ部Eとする(照会電文の9-nもデータ部Eになるはず)
    # self.__Data内に格納
    def ParseMsgField(self, data):
        data_len = len(data)
        for dict_i in self.__Content.keys():
            if dict_i <= 5:
                continue
            min_len    = self.GetDictContentTypes(dict_i,'Len')
            comp       = self.GetDictContentTypes(dict_i,'Comp').encode(self.__StrCode)
            msg_type   = self.GetDictContentTypes(dict_i,'MsgType')
            format_str = self.GetDictContentTypes(dict_i,'Fmt')
            if format_str.find('[len]') == -1 and format_str.find('[4len]') == -1:
                if len(msg_type) > 0:
                    if data_len >= min_len and chr(data[min_len-1]) == '@':
                        if comp == data[:3] and msg_type == self.__MsgType[:len(msg_type)]:
                            # 1-4 
                            break
                        if msg_type == self.__MsgType[:len(msg_type)]:
                            # 1-2,1-4
                            break
                        if msg_type == self.__MasMsgType[:len(msg_type)]:
                            # 1-2,1-4
                            break
                elif len(comp) > 0:
                    if comp == data[:4] and data_len >= min_len and chr(data[min_len-1]) == '@':
                        # 9-1-2,9-1-3,9-3-1,9-6-1,9-6-3,9-7-6,9-10-1
                        break
                elif data_len >= min_len and chr(data[min_len-1]) == '@':
                    # 1-1,1-3,1-6,2-7,2-10
                    break
            else:
                if len(msg_type) > 0:
                    if msg_type == self.__MsgType[:len(msg_type)]:
                        # 2-n,9-n
                        break
                    if msg_type == self.__MasMsgType[:len(msg_type)]:
                        # 2-n,9-n
                        break
                elif comp == data[:4] and data_len >= min_len:
                    # 9-6-4,9-6-5,9-6-6,9-7-1,9-7-3,9-7-4,9-7-11,9-10-4,Z
                    break

        data_name  = self.GetDictContentTypes(dict_i,'Name')
        try:
            data_list, wklen = self.GetDataUnpack(data, min_len, format_str)
        except:
            raise ParseError("unpack error. MTI:[{0}] data_name:[{1}] data_len:[{2}] data:[{3}] fmt:[{4}]".format(self.__MsgType, data_name, data_len, data, format_str))
        self.__Data.append((data_name, data_list))
        return wklen

    # 初回のみ条件が違うため別関数
    # データ部Cとデータ部Mは取引区分(78桁目)が数値か否かで判定
    def ParseMsgFirstField(self, data):
        for dict_i in self.__Content.keys():
            data_name  = self.GetDictContentTypes(dict_i,'Name')
            data_len   = self.GetDictContentTypes(dict_i,'Len')
            format_str = self.GetDictContentTypes(dict_i,'Fmt')
            if format_str.find('[len]') == -1:
                if len(data) == data_len:
                    if self.__ProcessMsg != 4910:
                        break   # データ部1-0、データ部1-5、データ部1-9
                    elif data_name == '1-0(4910)':
                        break   # データ部1-0(4910)
            else:
                if len(data) >= data_len:
                    # カウンタ通知/照会の判別(データ部C/Mと区別)
                    if self.__ProcessMsg == 4110 or self.__ProcessMsg == 4120 or self.__ProcessMsg == 4920:
                        self.__CorpCode = data[:7].decode(self.__StrCode)   # 会社コード保管(先頭7桁)
                        continue
                    if data[77:78].isdigit() == True and data_name == "C":
                        break # データ部C
                    if data[77:78].isdigit() == False and data_name == "M":
                        break # データ部M

        try:
            data_list, wklen = self.GetDataUnpack(data, data_len, format_str)
        except:
            raise ParseError("unpack error. MTI:[{0}] data_name:[{1}] data_len:[{2}] data:[{3}] fmt:[{4}]".format(self.__MsgType, data_name, len(data), data, format_str))
        if self.__ProcessMsg == 4110 or self.__ProcessMsg == 4120:
            self.__Data.append(('E(41xx)', data_list))
        elif self.__ProcessMsg == 4910:
            self.__Data.append(('1-0(4910)', data_list))
        elif self.__ProcessMsg == 4920:
           self.__Data.append(('E(4920)', data_list))
        else:
            self.__Data.append((data_name, data_list))

        self.__ErrCode = data[0:3].decode(self.__StrCode)
        self.__MasMsgType = data[3:7].decode(self.__StrCode)

    # ヘッダ部
    def ParseMsgHeader(self):
        data = self.__Buff[:63]
        dict_i = 0
        data_name  = self.GetDictContentTypes(dict_i,'Name')
        data_len   = self.GetDictContentTypes(dict_i,'Len')
        format_str = self.GetDictContentTypes(dict_i,'Fmt')

        try:
            data_list, wklen = self.GetDataUnpack(data, data_len, format_str)
        except:
            raise ParseError("unpack error. MTI:[{0}] data_name:[{1}] data_len:[{2}] data:[{3}] fmt:[{4}]".format(self.__MsgType, data_name, len(data), data, format_str))
        self.__Data.append((data_name, data_list))
        # 処理対象電文種別保存
        self.__ProcessMsg = int(data_list[9])

    # format_strを元にデータ部を項目ごとに分解
    def GetDataUnpack(self, data, data_len, format_str):
        len_list = format_str.split('s')
        rtn_list = []
        offset = 0
        for i in range(len(len_list)-1):
            if len_list[i] == '[len]':
                len_list[i]  = data.find(self.__Separator)-data_len+1
            elif len_list[i+1] == '[4len]':
                len_list[i+1] = data[offset:offset + 4].decode(self.__StrCode)
                len_list[i] = int(len_list[i])
            else:
                len_list[i] = int(len_list[i])
            rtn_list.append(data[offset:offset + len_list[i]])
            offset += len_list[i]
        rtn_list = tuple(rtn_list)
        return rtn_list, offset

    # 先頭から検索した"[4len]"を置換(未使用)
    def GetReplace4len(self, data, format_str):
        len_list = format_str.split('s')
        offset = 0
        for i in range(len(len_list)-1):
            if len_list[i+1] == '[4len]':
                break
            offset += int(len_list[i])
        variable_length = data[offset:offset + 4].decode(self.__StrCode)
        format_str = format_str.replace('[4len]', variable_length, 1)
        return format_str

    # 辞書から値を取得する関数
    def GetDictContentTypes(self, idx, item_name):
        return self.__Content[idx][item_name]
    def GetDictDataInfo(self, data_name, idx, item_name):
        return self.__DataInfo[data_name][idx][item_name]

    # Byte型から変換する関数
    def ByteToAscii(self, data):
        text = ''
        for byte in bytes(data):
            text = text + (chr(byte) if byte >= 32 and byte <= 126 else ".")
        return text
    def ByteToHex(self, data):
        text = ''
        for byte in bytes(data):
            text += "%02X" % int(byte)
        return text

    ############################################################
    # 外部から呼び出す用の関数                                 #
    ############################################################

    # self.__Data内の内容からデータ部名出力後各項目を出力する関数
    # 通常使用する関数
    # ASCIIに変換できない文字ｺｰﾄﾞの場合は"."に置換して表示 + HEX表示
    def PrintData(self):
        for data_i in range(len(self.__Data)):
            data_name = self.__Data[data_i][0]
            data_list = self.__Data[data_i][1]

            if data_name == 'hdr':
                continue
            if self.__CorpCode == '':
                print(" < データ部" + data_name + " >")
            else:   # カウンタ通知では、会社コードを表示
                print(" < データ部" + data_name + " 会社コード:" + self.__CorpCode + ">")

            for i in range(len(data_list)):
                description = self.GetDictDataInfo(data_name, i+1, 'Description')
                for byte in bytes(data_list[i]):
                    if byte < 32 or byte > 126:
                        description = description.replace('     ', '(HEX)', 1)
                        print( " {0:>3d} - {1} : [{2}]".format(i+1, description, self.ByteToHex(data_list[i])))
                        break
                else:
                    if self.__ProcessMsg == 4110 or self.__ProcessMsg == 4120 or self.__ProcessMsg == 4920:
                        if self.__CorpCodeProcessed is False:
                            # 会社コード読み飛ばし
                            print( " {0:>3d} - {1} : [{2}]".format(i+1, description, self.ByteToAscii(data_list[i][7:])))
                            self.__CorpCodeProcessed = True
                        else:
                            print( " {0:>3d} - {1} : [{2}]".format(i+1, description, self.ByteToAscii(data_list[i])))
                    else:
                        print( " {0:>3d} - {1} : [{2}]".format(i+1, description, self.ByteToAscii(data_list[i])))

    # 指定された値をself.__Data内から取得する関数
    # data_name : データ部名
    # item      : 項目番号
    # itemの末尾がHの場合HEX表示、Jの場合SJIS表示
    def GetDataValue(self, data_name, item):
        for data_i in range(len(self.__Data)):
            if data_name == self.__Data[data_i][0]:
                data_list = self.__Data[data_i][1]
                type = ''
                if item.isdigit():
                    i = int(item) - 1
                else:
                    i = int(item[:-1])-1
                    type = item[-1:]
                if item[-1:] == 'h' or item[-1:] == 'H':
                    return self.ByteToHex(data_list[i])
                if item[-1:] == 'j' or item[-1:] == 'J':
                    return data_list[i].decode(self.__StrCode)
                return self.ByteToAscii(data_list[i])
        return ''

    # 電文種別を取得する関数
    def GetMsgType(self):
        return self.__MsgType

    # マスタ電文を取得する関数
    def GetMasMsgType(self):
        return self.__MasMsgType

    # エラーコードを取得する関数
    def GetErrCode(self):
        return self.__ErrCode

# Name    : < データ部XXX > に使用
# Len     : データ部の判定、GetDataUnpackでFmtの[len]の置換に使用
# Comp    : 拡張データ部、9-nの判定に使用
# Msgtype : 長さのみでは判定できないデータ部で使用
# Fmt     : 各データ部の展開(unpack)に使用
ContentTypes = {
    0 :   { 'Name':'hdr',       'Len': 63,      'Comp':'',      'MsgType':'',       'Fmt':'4s6s2s3s6s7s4s7s4s4s4s1s2s2s3s1s3s'},
    1 :   { 'Name':'1-0',       'Len': 47,      'Comp':'',      'MsgType':'',       'Fmt':'3s4s4s1s7s5s2s1s5s5s6s1s1s1s1s'},
    2 :   { 'Name':'1-5',       'Len': 110,     'Comp':'',      'MsgType':'',       'Fmt':'3s4s1s69s1s2s2s4s4s4s4s5s3s1s1s1s1s'},
    3 :   { 'Name':'1-9',       'Len': 122,     'Comp':'',      'MsgType':'',       'Fmt':'3s4s1s69s1s2s2s4s4s4s4s5s3s3s8s2s1s1s1s'},
    4 :   { 'Name':'C',         'Len': 133,     'Comp':'',      'MsgType':'',       'Fmt':'3s4s1s69s1s2s2s4s4s4s4s5s3s1s1s1s1s4s4s6s4s4s[len]s1s'},
    5 :   { 'Name':'M',         'Len': 159,     'Comp':'',      'MsgType':'',       'Fmt':'3s4s1s69s1s2s2s4s4s4s4s5s3s3s8s2s1s1s1s9s8s9s4s6s[len]s1s'},
    6 :   { 'Name':'9-1-2',     'Len': 111,     'Comp':'0102',  'MsgType':'',       'Fmt':'4s4s1s11s10s28s1s1s28s2s19s1s1s'},
    7 :   { 'Name':'9-1-3',     'Len': 138,     'Comp':'0103',  'MsgType':'',       'Fmt':'4s4s36s36s56s1s1s'},
    8 :   { 'Name':'9-3-1',     'Len': 130,     'Comp':'0301',  'MsgType':'',       'Fmt':'4s10s10s10s10s4s4s14s10s10s4s7s4s4s14s10s1s'},
    9 :   { 'Name':'9-6-1',     'Len': 30,      'Comp':'0601',  'MsgType':'',       'Fmt':'4s1s1s4s1s1s1s1s4s10s1s1s'},
   10 :   { 'Name':'9-6-3',     'Len': 92,      'Comp':'0603',  'MsgType':'',       'Fmt':'4s1s1s1s10s1s1s2s4s10s8s1s16s16s9s5s1s1s'},
   11 :   { 'Name':'9-6-4',     'Len': 38,      'Comp':'0604',  'MsgType':'',       'Fmt':'4s5s2s3s1s10s1s1s2s4s[4len]s4s[4len]s1s'},
   12:    { 'Name':'9-6-5',     'Len': 41,      'Comp':'0605',  'MsgType':'',       'Fmt':'4s1s10s1s1s2s16s4s[4len]s1s1s'},
   13 :   { 'Name':'9-6-6',     'Len': 39,      'Comp':'0606',  'MsgType':'',       'Fmt':'4s1s10s1s12s5s4s[4len]s1s1s'},
   14 :   { 'Name':'9-7-1',     'Len': 119,     'Comp':'0701',  'MsgType':'',       'Fmt':'4s32s2s1s11s11s4s8s6s2s2s1s9s1s2s3s10s1s1s2s4s[4len]s1s1s'},
   15 :   { 'Name':'9-7-3',     'Len': 434,     'Comp':'0703',  'MsgType':'',       'Fmt':'4s32s11s11s2s1s1s1s1s1s2s3s1s72s10s64s7s13s5s6s1s1s69s7s8s7s83s1s1s2s4s[4len]s1s1s'},
   16 :   { 'Name':'9-7-4',     'Len': 227,     'Comp':'0704',  'MsgType':'',       'Fmt':'4s32s11s11s2s1s1s1s1s1s2s3s1s1s71s10s64s1s1s2s4s[4len]s1s1s'},
   17 :   { 'Name':'9-7-6',     'Len': 142,     'Comp':'0706',  'MsgType':'',       'Fmt':'4s4s13s5s6s1s1s69s7s8s7s2s4s10s1s'},
   18 :   { 'Name':'9-7-11',    'Len': 79,      'Comp':'0711',  'MsgType':'',       'Fmt':'4s32s2s1s2s2s10s1s2s3s10s1s1s2s4s[4len]s1s1s'},
   19 :   { 'Name':'9-10-1',    'Len': 166,     'Comp':'1001',  'MsgType':'',       'Fmt':'4s11s11s5s6s10s6s6s4s4s6s2s7s8s16s4s4s6s10s11s11s1s1s1s1s8s1s1s'},
   20 :   { 'Name':'9-10-2',    'Len': 220,     'Comp':'1002',  'MsgType':'',       'Fmt':'4s2s2s12s2s40s5s6s6s6s10s6s3s80s12s6s2s1s1s10s1s1s1s1s'},
   21 :   { 'Name':'9-10-4',    'Len': 16,      'Comp':'1004',  'MsgType':'',       'Fmt':'4s1s5s1s3s[len]s1s1s'},
   22 :   { 'Name':'9-50-1',    'Len': 5,       'Comp':'5001',  'MsgType':'',       'Fmt':'4s[len]s1s'},
   23 :   { 'Name':'Z',         'Len': 9,       'Comp':'F001',  'MsgType':'',       'Fmt':'4s4s[len]s1s'},
   24 :   { 'Name':'1-1',       'Len': 98,      'Comp':'',      'MsgType':'',       'Fmt':'1s1s69s4s7s8s7s1s'},
   25 :   { 'Name':'1-4',       'Len': 4,       'Comp':'5D2',   'MsgType':'8970',   'Fmt':'1s2s1s'},
   26 :   { 'Name':'1-2',       'Len': 4,       'Comp':'',      'MsgType':'34',     'Fmt':'1s2s1s'},
   27 :   { 'Name':'1-2',       'Len': 4,       'Comp':'',      'MsgType':'8970',   'Fmt':'1s2s1s'},
   28 :   { 'Name':'1-4',       'Len': 4,       'Comp':'',      'MsgType':'35',     'Fmt':'1s2s1s'},
   29 :   { 'Name':'1-4',       'Len': 4,       'Comp':'',      'MsgType':'8970',   'Fmt':'1s2s1s'},
   30 :   { 'Name':'1-3',       'Len': 10,      'Comp':'',      'MsgType':'33',     'Fmt':'5s1s3s1s'},
   31 :   { 'Name':'1-3',       'Len': 10,      'Comp':'',      'MsgType':'8970',   'Fmt':'5s1s3s1s'},
   32 :   { 'Name':'1-6',       'Len': 30,      'Comp':'',      'MsgType':'61',     'Fmt':'1s16s1s4s2s5s1s'},
   33 :   { 'Name':'1-6',       'Len': 30,      'Comp':'',      'MsgType':'8970',   'Fmt':'1s16s1s4s2s5s1s'},
   34 :   { 'Name':'2-7',       'Len': 8,       'Comp':'',      'MsgType':'33',     'Fmt':'7s1s'},
   35 :   { 'Name':'2-7',       'Len': 8,       'Comp':'',      'MsgType':'8970',   'Fmt':'7s1s'},
   36 :   { 'Name':'2-10',      'Len': 75,      'Comp':'',      'MsgType':'34',     'Fmt':'1s69s4s1s'},
   37 :   { 'Name':'2-10',      'Len': 75,      'Comp':'',      'MsgType':'8970',   'Fmt':'1s69s4s1s'},
   38 :   { 'Name':'2-n',       'Len': 3,       'Comp':'',      'MsgType':'32',     'Fmt':'2s[len]s1s'},
   39 :   { 'Name':'2-n',       'Len': 3,       'Comp':'',      'MsgType':'8970',   'Fmt':'2s[len]s1s'},
   40 :   { 'Name':'9-n',       'Len': 3,       'Comp':'',      'MsgType':'35',     'Fmt':'2s[len]s1s'},
   41 :   { 'Name':'9-n',       'Len': 3,       'Comp':'',      'MsgType':'8970',   'Fmt':'2s[len]s1s'},
   42 :   { 'Name':'1-9(42xx)', 'Len': 16,      'Comp':'',      'MsgType':'42',     'Fmt':'3s3s5s4s1s'},
   43 :   { 'Name':'1-0(4910)', 'Len': 47,      'Comp': '',     'MsgType':'4910',   'Fmt':'3s4s4s1s7s13s5s6s1s1s1s1s'},
   44 :   { 'Name':'E(Continue)','Len': 3,      'Comp':'',      'MsgType':'41',     'Fmt':'1s1s1s'},
   45 :   { 'Name':'E(Continue)','Len': 3,      'Comp':'',      'MsgType':'49',     'Fmt':'1s1s1s'},
   46 :   { 'Name':'E(41xx)',   'Len': 0,       'Comp':'',      'MsgType':'41',     'Fmt':'[len]s'},
   47 :   { 'Name':'E(4920)',   'Len': 0,       'Comp':'',      'MsgType':'4920',   'Fmt':'[len]s'},
   48 :   { 'Name':'E',         'Len': 0,       'Comp':'',      'MsgType':'',       'Fmt':'[len]s'}
}
DataInfo = {
    'hdr' : {
        1 : { 'Description' : '経路番号                                 ' },
        2 : { 'Description' : '仕向処理通番                             ' },
        3 : { 'Description' : 'センタ識別番号                           ' },
        4 : { 'Description' : '回線番号                                 ' },
        5 : { 'Description' : 'CAFIS処理通番                            ' },
        6 : { 'Description' : '仕向会社コード                           ' },
        7 : { 'Description' : '仕向会社サブコード                       ' },
        8 : { 'Description' : '被仕向会社コード                         ' },
        9 : { 'Description' : '被仕向会社サブコード                     ' },
       10 : { 'Description' : '電文識別                                 ' },
       11 : { 'Description' : 'CAFIS処理月日                            ' },
       12 : { 'Description' : 'CAFIS送信状態表示                        ' },
       13 : { 'Description' : '仕向処理日付                             ' },
       14 : { 'Description' : '代行電文報告表示                         ' },
       15 : { 'Description' : '代行電文エラー表示                       ' },
       16 : { 'Description' : '代行再仕向表示                           ' },
       17 : { 'Description' : 'トレーラレングス                         ' }},
    '1-0' : {
        1 : { 'Description' : 'エラーコード                             ' },
        2 : { 'Description' : 'マスター電文種別コード                   ' },
        3 : { 'Description' : '予備                                     ' },
        4 : { 'Description' : '電文送信区分                             ' },
        5 : { 'Description' : '承認番号                                 ' },
        6 : { 'Description' : '端末識別番号：設置会社コード             ' },
        7 : { 'Description' : '端末識別番号：メーカーコード             ' },
        8 : { 'Description' : '端末識別番号：機種コード                 ' },
        9 : { 'Description' : '端末識別番号：端末通番                   ' },
       10 : { 'Description' : '端末処理通番                             ' },
       11 : { 'Description' : '処理年月日                               ' },
       12 : { 'Description' : '直収CAT取扱区分/追加データ部表示         ' },
       13 : { 'Description' : 'サービス識別                             ' },
       14 : { 'Description' : '取引種別                                 ' },
       15 : { 'Description' : 'セパレータ                               ' }},
    '1-0(4910)' : {
        1 : {'Description': 'エラーコード                             '},
        2 : {'Description': 'マスター電文種別コード                   '},
        3 : {'Description': '予備                                     '},
        4 : {'Description': '電文送信区分                             '},
        5 : {'Description': '承認番号                                 '},
        6 : {'Description': '端末機識別番号                           '},
        7 : {'Description': '端末処理通番                             '},
        8 : {'Description': '処理年月日                               '},
        9 : {'Description': '追加データ部表示                         '},
       10 : {'Description': '継続表示                                 '},
       11 : {'Description': '回数                                     '},
       12 : {'Description': 'セパレータ                               '}},
    '1-1' : {
        1 : { 'Description' : '業務区分コード                           ' },
        2 : { 'Description' : 'カード区分                               ' },
        3 : { 'Description' : 'カードエンコード内容                     ' },
        4 : { 'Description' : '暗証番号                                 ' },
        5 : { 'Description' : '商品コード                               ' },
        6 : { 'Description' : '金額                                     ' },
        7 : { 'Description' : '税送料                                   ' },
        8 : { 'Description' : 'セパレータ                               ' }},
    '1-2' : {
        1 : { 'Description' : '業務区分コード                           ' },
        2 : { 'Description' : '照会区分コード                           ' },
        3 : { 'Description' : 'セパレータ                               ' }},
    '1-3' : {
        1 : { 'Description' : '伝票番号                                 ' },
        2 : { 'Description' : '取消区分コード                           ' },
        3 : { 'Description' : '取扱区分コード                           ' },
        4 : { 'Description' : 'セパレータ                               ' }},
    '1-4' : {
        1 : { 'Description' : '業務区分コード                           ' },
        2 : { 'Description' : '取扱区分コード                           ' },
        3 : { 'Description' : 'セパレータ                               ' }},
    '1-5' : {
        1 : { 'Description' : 'エラーコード                             ' },
        2 : { 'Description' : 'マスター電文種別コード                   ' },
        3 : { 'Description' : 'カード区分                               ' },
        4 : { 'Description' : 'カードエンコード内容                     ' },
        5 : { 'Description' : '取引区分                                 ' },
        6 : { 'Description' : '支払区分                                 ' },
        7 : { 'Description' : '分割回数                                 ' },
        8 : { 'Description' : '仕向銀行コード                           ' },
        9 : { 'Description' : '仕向支店コード                           ' },
       10 : { 'Description' : '請求金額                                 ' },
       11 : { 'Description' : 'お客様入力暗証                           ' },
       12 : { 'Description' : '端末番号                                 ' },
       13 : { 'Description' : '時間延長手数料                           ' },
       14 : { 'Description' : '取引パターン                             ' },
       15 : { 'Description' : '認証実施区分                             ' },
       16 : { 'Description' : 'スクランブル有無表示/追加データ部表示    ' },
       17 : { 'Description' : 'セパレータ                               ' }},
    '1-6' : {
        1 : { 'Description' : 'データ区分                               ' },
        2 : { 'Description' : '会員番号                                 ' },
        3 : { 'Description' : '年号区分                                 ' },
        4 : { 'Description' : '有効期限                                 ' },
        5 : { 'Description' : '無効理由                                 ' },
        6 : { 'Description' : '貴社任意                                 ' },
        7 : { 'Description' : 'セパレータ                               ' }},
    '1-9' : {
        1 : { 'Description' : 'エラーコード                             ' },
        2 : { 'Description' : 'マスター電文種別コード                   ' },
        3 : { 'Description' : 'カード区分                               ' },
        4 : { 'Description' : 'カードエンコード内容                     ' },
        5 : { 'Description' : '取引区分                                 ' },
        6 : { 'Description' : '入金区分                                 ' },
        7 : { 'Description' : '予備                                     ' },
        8 : { 'Description' : '仕向銀行コード                           ' },
        9 : { 'Description' : '仕向支店コード                           ' },
       10 : { 'Description' : '予備                                     ' },
       11 : { 'Description' : '入力暗証番号                             ' },
       12 : { 'Description' : '端末番号                                 ' },
       13 : { 'Description' : '時間延長手数料                           ' },
       14 : { 'Description' : 'その他手数料                             ' },
       15 : { 'Description' : '入金金額                                 ' },
       16 : { 'Description' : '予備                                     ' },
       17 : { 'Description' : '認証実施区分                             ' },
       18 : { 'Description' : 'スクランブル有無表示/追加データ部表示    ' },
       19 : { 'Description' : 'セパレータ                               ' }},
    '2-7' : {
        1 : { 'Description' : '承認番号                                 ' },
        2 : { 'Description' : 'セパレータ                               ' }},
    '2-10' : {
        1 : { 'Description' : 'カード区分                               ' },
        2 : { 'Description' : 'エンコード内容                           ' },
        3 : { 'Description' : '暗証番号                                 ' },
        4 : { 'Description' : 'セパレータ                               ' }},
    '2-n' : {
        1 : { 'Description' : '支払区分コード                           ' },
        2 : { 'Description' : '支払方法                                 ' },
        3 : { 'Description' : 'セパレータ                               ' }},
    '9-n' : {
        1 : { 'Description' : '制御コード                               ' },
        2 : { 'Description' : 'カウンタ情報                             ' },
        3 : { 'Description' : 'セパレータ                               ' }},
    '9-6-1' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : 'セキュリティコード：端末入力可否         ' },
        3 : { 'Description' : 'セキュリティコード：店員入力有無         ' },
        4 : { 'Description' : 'セキュリティコード：セキュリティコード   ' },
        5 : { 'Description' : 'JIS2面情報：端末入力機能有無             ' },
        6 : { 'Description' : 'JIS2面情報：JIS2面情報有無               ' },
        7 : { 'Description' : 'JIS2面情報：JIS2カード情報1              ' },
        8 : { 'Description' : 'JIS2面情報：JIS2カード情報2              ' },
        9 : { 'Description' : 'JIS2面情報：JIS2カード情報3              ' },
       10 : { 'Description' : '予備                                     ' },
       11 : { 'Description' : '後続データ部表示                         ' },
       12 : { 'Description' : 'セパレータ                               ' }},
    '9-7-1' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : 'AID                                      ' },
        3 : { 'Description' : 'POSエントリモード：PAN入力モード         ' },
        4 : { 'Description' : 'POSエントリモード：PIN入力機能           ' },
        5 : { 'Description' : '加盟店会社コード                         ' },
        6 : { 'Description' : '加盟店契約会社コード                     ' },
        7 : { 'Description' : '加盟店分類コード                         ' },
        8 : { 'Description' : '端末処理日付                             ' },
        9 : { 'Description' : '端末処理時間                             ' },
       10 : { 'Description' : 'PANシーケンスナンバー                    ' },
       11 : { 'Description' : 'レスポンスコード                         ' },
       12 : { 'Description' : 'IC対応端末フラグ                         ' },
       13 : { 'Description' : '予備1                                    ' },
       14 : { 'Description' : 'CAFIS認証代行エリア：認証代行フラグ      ' },
       15 : { 'Description' : 'CAFIS認証代行エリア：代行結果コード      ' },
       16 : { 'Description' : 'CAFIS認証代行エリア：詳細コード          ' },
       17 : { 'Description' : 'CAFIS認証代行エリア：予備2               ' },
       18 : { 'Description' : 'IC関連データ：フォーマット種別           ' },
       19 : { 'Description' : 'IC関連データ：エンコード種別             ' },
       20 : { 'Description' : 'IC関連データ：予備                       ' },
       21 : { 'Description' : 'IC関連データ：格納データレングス         ' },
       22 : { 'Description' : 'IC関連データ：格納データ                 ' },
       23 : { 'Description' : '後続データ部表示                         ' },
       24 : { 'Description' : 'セパレータ                               ' }},
    '9-7-3' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : 'AID                                      ' },
        3 : { 'Description' : '加盟店会社コード                         ' },
        4 : { 'Description' : '加盟店契約会社コード                     ' },
        5 : { 'Description' : 'MS/IC情報取得区分                        ' },
        6 : { 'Description' : 'オン/オフ区分                            ' },
        7 : { 'Description' : '取引結果                                 ' },
        8 : { 'Description' : '強制オンライン                           ' },
        9 : { 'Description' : '強制承認                                 ' },
       10 : { 'Description' : '処理レベル                               ' },
       11 : { 'Description' : 'ブランド識別                             ' },
       12 : { 'Description' : 'POSエントリモード                        ' },
       13 : { 'Description' : 'チップコンディションコード               ' },
       14 : { 'Description' : '予備1                                    ' },
       15 : { 'Description' : '予備2                                    ' },
       16 : { 'Description' : '予備3                                    ' },
       17 : { 'Description' : '取引情報：データ部1-0.承認番号           ' },
       18 : { 'Description' : '取引情報：データ部1-0.端末機識別番号     ' },
       19 : { 'Description' : '取引情報：データ部1-0.端末機処理通番     ' },
       20 : { 'Description' : '取引情報：データ部1-0.処理年月日         ' },
       21 : { 'Description' : '取引情報：データ部1-1.業務区分コード     ' },
       22 : { 'Description' : '取引情報：データ部1-1.カード区分         ' },
       23 : { 'Description' : '取引情報：データ部1-1.エンコード内容     ' },
       24 : { 'Description' : '取引情報：データ部1-1.商品コード         ' },
       25 : { 'Description' : '取引情報：データ部1-1.金額               ' },
       26 : { 'Description' : '取引情報：データ部1-1.税送料             ' },
       27 : { 'Description' : '取引情報：データ部2-X情報                ' },
       28 : { 'Description' : 'IC関連データ：フォーマット種別           ' },
       29 : { 'Description' : 'IC関連データ：エンコード種別             ' },
       30 : { 'Description' : 'IC関連データ：予備                       ' },
       31 : { 'Description' : 'IC関連データ：格納データレングス         ' },
       32 : { 'Description' : 'IC関連データ：格納データ                 ' },
       33 : { 'Description' : '後続データ部表示                         ' },
       34 : { 'Description' : 'セパレータ                               ' }},
    '9-7-4' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : 'AID                                      ' },
        3 : { 'Description' : '加盟店会社コード                         ' },
        4 : { 'Description' : '加盟店契約会社コード                     ' },
        5 : { 'Description' : 'MS/IC情報取得区分                        ' },
        6 : { 'Description' : 'オン/オフ区分                            ' },
        7 : { 'Description' : '取引結果                                 ' },
        8 : { 'Description' : '強制オンライン                           ' },
        9 : { 'Description' : '強制承認                                 ' },
       10 : { 'Description' : '処理レベル                               ' },
       11 : { 'Description' : 'ブランド識別                             ' },
       12 : { 'Description' : 'POSエントリモード                        ' },
       13 : { 'Description' : 'チップコンディションコード               ' },
       14 : { 'Description' : 'IC対応端末フラグ                         ' },
       15 : { 'Description' : '予備1                                    ' },
       16 : { 'Description' : '予備2                                    ' },
       17 : { 'Description' : '予備3                                    ' },
       18 : { 'Description' : 'IC関連データ：フォーマット種別           ' },
       19 : { 'Description' : 'IC関連データ：エンコード種別             ' },
       20 : { 'Description' : 'IC関連データ：予備                       ' },
       21 : { 'Description' : 'IC関連データ：格納データレングス         ' },
       22 : { 'Description' : 'IC関連データ：格納データ                 ' },
       23 : { 'Description' : '後続データ部表示                         ' },
       24 : { 'Description' : 'セパレータ                               ' }},
    '9-1-2' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : 'データ部レングス                         ' },
        3 : { 'Description' : '3-DSecure2用データ部表示                 '},
        4 : { 'Description' : '予備                                     ' },
        5 : { 'Description' : '3-D secure：Message Version No           ' },
        6 : { 'Description' : '3-D secure：Transaction Identifier       ' },
        7 : { 'Description' : '3-D secure：Transaction Status           ' },
        8 : { 'Description' : '3-D secure：CAVV Algorithm               ' },
        9 : { 'Description' : '3-D secure：CAVV                         ' },
       10 : { 'Description' : '3-D secure：EC Indicator                 ' },
       11 : { 'Description' : '3-D secure：Cardholder PAN               ' },
       12 : { 'Description' : '後続データ部表示                         ' },
       13 : { 'Description' : 'セパレータ                               ' }},
    '9-1-3' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : 'データ部レングス                         ' },
        3 : { 'Description' : 'DS Transaction ID                        ' },
        4 : { 'Description' : '3DS Server Transaction ID                ' },
        5 : { 'Description' : '3DSecure 拡張領域                        ' },
        6 : { 'Description' : '後続データ部表示                         ' },
        7 : { 'Description' : 'セパレータ                               ' }},
    '9-6-6' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : '暗号アルゴリズム                         ' },
        3 : { 'Description' : '予備                                     ' },
        4 : { 'Description' : '属性関連データ：エンコード種別           ' },
        5 : { 'Description' : '属性関連データ：マッチング結果           ' },
        6 : { 'Description' : '属性関連データ：予備                     ' },
        7 : { 'Description' : '属性関連データ：格納データレングス       ' },
        8 : { 'Description' : '属性関連データ：格納データ               ' },
        9 : { 'Description' : '後続データ部表示                         ' },
       10 : { 'Description' : 'セパレータ                               ' }},
    '9-6-3' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : 'PIN暗号認証値算出方式                    ' },
        3 : { 'Description' : 'PIN暗号アルゴリズム                      ' },
        4 : { 'Description' : 'PINフォーマット                          ' },
        5 : { 'Description' : '予備                                     ' },
        6 : { 'Description' : 'PIN関連データ：フォーマット種別          ' },
        7 : { 'Description' : 'PIN関連データ：エンコード種別            ' },
        8 : { 'Description' : 'PIN関連データ：予備                      ' },
        9 : { 'Description' : 'PIN関連データ：格納データレングス        ' },
       10 : { 'Description' : 'PIN関連データ：PIN暗号認証値             ' },
       11 : { 'Description' : 'PIN関連データ：PIN暗号鍵チェックデジット ' },
       12 : { 'Description' : 'PIN関連データ：PINチェンジフラグ         ' },
       13 : { 'Description' : 'PIN関連データ：現行PIN                   ' },
       14 : { 'Description' : 'PIN関連データ：新PIN                     ' },
       15 : { 'Description' : 'PIN関連データ：予備                      ' },
       16 : { 'Description' : '予備                                     ' },
       17 : { 'Description' : '後続データ部表示                         ' },
       18 : { 'Description' : 'セパレータ                               ' }},
    '9-6-4' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : 'スキームID                               ' },
        3 : { 'Description' : '鍵種別                                   ' },
        4 : { 'Description' : 'メーカコード                             ' },
        5 : { 'Description' : '世代                                     ' },
        6 : { 'Description' : '予備1                                    ' },
        7 : { 'Description' : '鍵情報：フォーマット種別                 ' },
        8 : { 'Description' : '鍵情報：エンコード種別                   ' },
        9 : { 'Description' : '鍵情報：予備2                            ' },
       10 : { 'Description' : '鍵情報：新鍵データレングス               ' },
       11 : { 'Description' : '鍵情報：新鍵データ                       ' },
       12 : { 'Description' : '鍵情報：旧鍵データレングス               ' },
       13 : { 'Description' : '鍵情報：旧鍵データ                       ' },
       14 : { 'Description' : 'セパレータ                               ' }},
    '9-6-5' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : 'PEK暗号アルゴリズム                      ' },
        3 : { 'Description' : '予備                                     ' },
        4 : { 'Description' : 'PEK関連データ:フォーマット種別           ' },
        5 : { 'Description' : 'PEK関連データ:エンコード種別             ' },
        6 : { 'Description' : 'PEK関連データ:予備                       ' },
        7 : { 'Description' : 'PEK関連データ:鍵ブロックヘッダ           ' },
        8 : { 'Description' : 'PEK関連データ:鍵レングス                 ' },
        9 : { 'Description' : 'PEK関連データ:鍵情報                     ' },
       10 : { 'Description' : '後続データ部表示                         ' },
       11 : { 'Description' : 'セパレータ                               ' }},
    '9-7-6' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : '後続データレングス                       ' },
        3 : { 'Description' : '取引情報：端末機識別番号                 ' },
        4 : { 'Description' : '取引情報：端末機処理通番                 ' },
        5 : { 'Description' : '取引情報：処理年月日                     ' },
        6 : { 'Description' : '取引情報：業務区分コード                 ' },
        7 : { 'Description' : '取引情報：カード区分                     ' },
        8 : { 'Description' : '取引情報：エンコード内容                 ' },
        9 : { 'Description' : '取引情報：商品コード                     ' },
       10 : { 'Description' : '取引情報：金額                           ' },
       11 : { 'Description' : '取引情報：税送料                         ' },
       12 : { 'Description' : '取引情報：支払区分                       ' },
       13 : { 'Description' : '拒否理由                                 ' },
       14 : { 'Description' : '予備                                     ' },
       15 : { 'Description' : 'セパレータ                               ' }},
    '9-3-1' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : '通帳印字：加盟店名固定部                 ' },
        3 : { 'Description' : '通帳印字：予備                           ' },
        4 : { 'Description' : '通帳印字：加盟店名任意部                 ' },
        5 : { 'Description' : '通帳印字：予備                           ' },
        6 : { 'Description' : '伝票印字：銀行コード                     ' },
        7 : { 'Description' : '伝票印字：支店コード                     ' },
        8 : { 'Description' : '伝票印字：口座番号                       ' },
        9 : { 'Description' : '伝票印字：発行銀行名                     ' },
       10 : { 'Description' : '伝票印字：予備                           ' },
       11 : { 'Description' : 'クリアリング：発行銀行コード             ' },
       12 : { 'Description' : 'クリアリング：加盟店コード               ' },
       13 : { 'Description' : 'クリアリング：加盟店サブコード           ' },
       14 : { 'Description' : 'クリアリング：障害電文処理日付           ' },
       15 : { 'Description' : '利用可能金額                             ' },
       16 : { 'Description' : '予備                                     ' },
       17 : { 'Description' : 'セパレータ                               ' }},
    '9-10-1' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : 'CUPSヘッダ部：送信元ID                   ' },
        3 : { 'Description' : 'CUPSヘッダ部：アクワイヤラID             ' },
        4 : { 'Description' : 'CUPSヘッダ部：拒否コード                 ' },
        5 : { 'Description' : 'CUPSデータ部：処理コード                 ' },
        6 : { 'Description' : 'CUPSデータ部：送信日時                   ' },
        7 : { 'Description' : 'CUPSデータ部：処理通番                   ' },
        8 : { 'Description' : 'CUPSデータ部：取引時間(現地取引)         ' },
        9 : { 'Description' : 'CUPSデータ部：取引月日(現地取引)         ' },
       10 : { 'Description' : 'CUPSデータ部：精査日付                   ' },
       11 : { 'Description' : 'CUPSデータ部：承認識別応答               ' },
       12 : { 'Description' : 'CUPSデータ部：レスポンスコード           ' },
       13 : { 'Description' : 'CUPSデータ部：加盟店会社コード           ' },
       14 : { 'Description' : 'CUPSデータ部：シーケンスナンバ           ' },
       15 : { 'Description' : 'CUPSデータ部：PINデータ                  ' },
       16 : { 'Description' : 'CUPSデータ部：メッセージ理由コード       ' },
       17 : { 'Description' : 'CUPSデータ部：元MTI                      ' },
       18 : { 'Description' : 'CUPSデータ部：元処理通番                 ' },
       19 : { 'Description' : 'CUPSデータ部：元送信日時                 ' },
       20 : { 'Description' : 'CUPSデータ部：元取扱機関コード           ' },
       21 : { 'Description' : 'CUPSデータ部：元送信機関コード           ' },
       22 : { 'Description' : 'CUPSデータ部：クレジット/デビット識別ﾌﾗｸﾞ' },
       23 : { 'Description' : 'CUPSデータ部：売上識別フラグ             ' },
       24 : { 'Description' : 'CUPSデータ部：暗号化キーインデックス     ' },
       25 : { 'Description' : 'CUPSデータ部：チップコンディションコード ' },
       26 : { 'Description' : 'CUPSデータ部：予備                       ' },
       27 : { 'Description' : '後続データ部表示                         ' },
       28 : { 'Description' : 'セパレータ                               ' }},
    '9-10-2': {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : 'ブランド識別                             ' },
        3 : { 'Description' : '口座種別                                 ' },
        4 : { 'Description' : 'POSエントリモード                        ' },
        5 : { 'Description' : 'PIN 最大入力桁数                         ' },
        6 : { 'Description' : 'ATM設置場所情報                          ' },
        7 : { 'Description' : '端末処理番号                             ' },
        8 : { 'Description' : '取引発生日付                             ' },
        9 : { 'Description' : '取引発生時刻                             ' },
       10 : { 'Description' : '取引通番                                 ' },
       11 : { 'Description' : '被仕向センタ送信日時                     ' },
       12 : { 'Description' : '承認番号                                 ' },
       13 : { 'Description' : 'レスポンスコード                         ' },
       14 : { 'Description' : '残高                                     ' },
       15 : { 'Description' : '取引特定情報                             ' },
       16 : { 'Description' : '取引決済日                               ' },
       17 : { 'Description' : 'プロダクト詳細情報                       ' },
       18 : { 'Description' : 'ヨーロッパ地域発行カード情報             ' },
       19 : { 'Description' : 'クレジット/デビット情報                  ' },
       20 : { 'Description' : '詳細エラーコード                         ' },
       21 : { 'Description' : 'POSカード改修機能                        ' },
       22 : { 'Description' : '予備                                     ' },
       23 : { 'Description' : '後続データ部表示                         ' },
       24 : { 'Description' : 'セパレータ                               ' }},
    '9-10-4': {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : 'ブランド識別                             ' },
        3 : { 'Description' : '予備                                     ' },
        4 : { 'Description' : 'エンコード種別                           ' },
        5 : { 'Description' : '情報レングス                             ' },
        6 : { 'Description' : 'ブランド情報                             ' },
        7 : { 'Description' : '後続データ部表示                         ' },
        8 : { 'Description' : 'セパレータ                               ' }},
    '9-7-11' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : 'AID                                      ' },
        3 : { 'Description' : 'POSエントリモード：PAN入力モード         ' },
        4 : { 'Description' : 'POSエントリモード：PIN入力機能           ' },
        5 : { 'Description' : 'PANシーケンスナンバー                    ' },
        6 : { 'Description' : 'レスポンスコード                         ' },
        7 : { 'Description' : '予備1                                    ' },
        8 : { 'Description' : 'CAFIS認証代行エリア：認証代行フラグ      ' },
        9 : { 'Description' : 'CAFIS認証代行エリア：代行結果コード      ' },
       10 : { 'Description' : 'CAFIS認証代行エリア：詳細コード          ' },
       11 : { 'Description' : 'CAFIS認証代行エリア：予備2               ' },
       12 : { 'Description' : 'IC関連データ：フォーマット種別           ' },
       13 : { 'Description' : 'IC関連データ：エンコード種別             ' },
       14 : { 'Description' : 'IC関連データ：予備                       ' },
       15 : { 'Description' : 'IC関連データ：格納データレングス         ' },
       16 : { 'Description' : 'IC関連データ：格納データ                 ' },
       17 : { 'Description' : '後続データ部表示                         ' },
       18 : { 'Description' : 'セパレータ                               ' }},
    '9-50-1' : {
        1 : { 'Description' : '任意データ部種別                         ' },
        2 : { 'Description' : '個社データ                               ' },
        3 : { 'Description' : 'セパレータ                               ' }},
    'E' : {
        1 : { 'Description' : '貴社任意                                 ' }},
    'E(41xx)' : {
        1 : { 'Description' : 'カウンタ                                  ' }},
    'E(4920)' : {
        1 : { 'Description' : 'カウンタ                                  ' }},
    'E(Continue)' : {
        1 : { 'Description' : '継続表示                                  ' },
        2 : { 'Description' : '回数                                      '},
        3 : { 'Description' : 'セパレータ                                ' }},
    'Z' : {
        1 : { 'Description' : 'ユーザ任意                               ' },
        2 : { 'Description' : '全体レングス                             ' },
        3 : { 'Description' : '個社データ                               ' },
        4 : { 'Description' : 'セパレータ                               ' }},
    'C' : {
        1 : { 'Description' : 'エラーコード                             ' },
        2 : { 'Description' : 'マスター電文種別コード                   ' },
        3 : { 'Description' : 'カード区分                               ' },
        4 : { 'Description' : 'カードエンコード内容                     ' },
        5 : { 'Description' : '取引区分                                 ' },
        6 : { 'Description' : '支払区分                                 ' },
        7 : { 'Description' : '分割回数                                 ' },
        8 : { 'Description' : '仕向銀行コード                           ' },
        9 : { 'Description' : '仕向支店コード                           ' },
       10 : { 'Description' : '請求金額                                 ' },
       11 : { 'Description' : 'お客様入力暗証                           ' },
       12 : { 'Description' : '端末番号                                 ' },
       13 : { 'Description' : '時間延長手数料                           ' },
       14 : { 'Description' : '取引パターン                             ' },
       15 : { 'Description' : '認証実施区分                             ' },
       16 : { 'Description' : 'スクランブル有無表示/追加データ部表示    ' },
       17 : { 'Description' : '有効性更新コード                         ' },
       18 : { 'Description' : '支払可能残高                             ' },
       19 : { 'Description' : '支払限度                                 ' },
       20 : { 'Description' : '支払利息                                 ' },
       21 : { 'Description' : '最新利用年月                             ' },
       22 : { 'Description' : '会員PCコード                             ' },
       23 : { 'Description' : '貴社任意                                 ' },
       24 : { 'Description' : 'セパレータ                               ' }},
    'M' : {
        1 : { 'Description' : 'エラーコード                             ' },
        2 : { 'Description' : 'マスター電文種別コード                   ' },
        3 : { 'Description' : 'カード区分                               ' },
        4 : { 'Description' : 'カードエンコード内容                     ' },
        5 : { 'Description' : '取引区分                                 ' },
        6 : { 'Description' : '入金区分                                 ' },
        7 : { 'Description' : '予備                                     ' },
        8 : { 'Description' : '仕向銀行コード                           ' },
        9 : { 'Description' : '仕向支店コード                           ' },
       10 : { 'Description' : '予備                                     ' },
       11 : { 'Description' : '入力暗証番号                             ' },
       12 : { 'Description' : '端末番号                                 ' },
       13 : { 'Description' : '時間延長手数料                           ' },
       14 : { 'Description' : 'その他手数料                             ' },
       15 : { 'Description' : '入金金額                                 ' },
       16 : { 'Description' : '予備                                     ' },
       17 : { 'Description' : '認証実施区分                             ' },
       18 : { 'Description' : 'スクランブル有無表示/追加データ部表示    ' },
       19 : { 'Description' : '有効性更新コード                         ' },
       20 : { 'Description' : '入金後残債                               ' },
       21 : { 'Description' : '入金可能額                               ' },
       22 : { 'Description' : '入金利息                                 ' },
       23 : { 'Description' : '極度額                                   ' },
       24 : { 'Description' : '予備                                     ' },
       25 : { 'Description' : '貴社任意                                 ' },
       26 : { 'Description' : 'セパレータ                               ' }},
    '1-9(42xx)' : {
        1 : {'Description': 'エラーコード                             '},
        2 : {'Description': '予備                                     '},
        3 : {'Description': '代行電文数                               '},
        4 : {'Description': '予備                                     '},
        5 : {'Description': 'セパレータ                               '}}
}
