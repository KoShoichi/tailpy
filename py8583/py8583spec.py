from py8583.py8583 import DT, LT, SpecError

            
class IsoSpec(object):
    __ValidContentTypes = ('a', 'n', 's', 'an', 'as', 'ns', 'ans', 'b', 'z','2b')
    
    Descriptions = {}
    ContentTypes = {}
    DataTypes = {}
    
    def __init__(self):
        self.SetDescriptions()
        self.SetContentTypes()
        self.SetDataTypes()
    
    def SetDescriptions(self):
        pass
    def SetContentTypes(self):
        pass
    def SetDataTypes(self):
        pass
         
    def Description(self, field, Description = None):
        if(Description == None):
            return self.Descriptions[field]
        else:
            self.Descriptions[field] = Description

    def DataType(self, field, DataType = None):
        if(DataType == None):
            return self.DataTypes[field]['Data']
        else:
            if(DataType not in DT):
                raise SpecError("Cannot set data type '{0}' for F{1}: Invalid data type".format(DataType, field))
            if(field not in self.DataTypes.keys()):
                self.DataTypes[field] = {}
            self.DataTypes[field]['Data'] = DataType
    
    def ContentType(self, field, ContentType = None):
        if(ContentType == None):
            return self.ContentTypes[field]['ContentType']
        else:
            if(ContentType not in self.__ValidContentTypes):
                raise SpecError("Cannot set Content type '{0}' for F{1}: Invalid content type".format(ContentType, field))
            self.ContentTypes[field]['ContentType'] = ContentType
            
    def MaxLength(self, field, MaxLength = None):
        if(MaxLength == None):
            return self.ContentTypes[field]['MaxLen']
        else:
            self.ContentTypes[field]['MaxLen'] = MaxLength
    
    def LengthType(self, field, LengthType = None):
        if(LengthType == None):
            return self.ContentTypes[field]['LenType']
        else:
            if(LengthType not in self.__ValidContentTypes):
                raise SpecError("Cannot set Length type '{0}' for F{1}: Invalid length type".format(LengthType, field))
            self.ContentTypes[field]['LenType'] = LengthType
    
    def LengthDataType(self, field, LengthDataType = None):
        if(LengthDataType == None):
            return self.DataTypes[field]['Length']
        else:
            if(LengthDataType not in DT):
                raise SpecError("Cannot set data type '{0}' for F{1}: Invalid data type".format(LengthDataType, field))
            if(field not in self.DataTypes.keys()):
                self.DataTypes[field] = {}
            self.DataTypes[field]['Length'] = LengthDataType
    
    
    
class IsoSpec1987(IsoSpec):
    def SetDescriptions(self):
        self.Descriptions = Descriptions['1987']
    def SetContentTypes(self):
        self.ContentTypes = ContentTypes['1987']
        
class IsoSpec1987M(IsoSpec):
    def SetDescriptions(self):
        self.Descriptions = Descriptions['1987M']
    def SetContentTypes(self):
        self.ContentTypes = ContentTypes['1987M']

class IsoSpec1987V(IsoSpec):
    def SetDescriptions(self):
        self.Descriptions = Descriptions['1987V']
    def SetContentTypes(self):
        self.ContentTypes = ContentTypes['1987V']

class IsoSpec1987Va(IsoSpec1987V):
    def SetContentTypes(self):
        super().SetContentTypes()
        self.ContentTypes[104]['ContentType'] = '2b'

class IsoSpec1993J(IsoSpec):
    def SetDescriptions(self):
        self.Descriptions = Descriptions['1993J']
    def SetContentTypes(self):
        self.ContentTypes = ContentTypes['1993J']

class IsoSpec1987ASCII(IsoSpec1987):
    def SetDataTypes(self):
        self.DataType('MTI', DT.ASCII)
        self.DataType(1, DT.ASCII) # bitmap
        
        for field in self.ContentTypes.keys():
            self.DataType(field, DT.ASCII)
            if(self.LengthType(field) != LT.FIXED):
                self.LengthDataType(field, DT.ASCII)
        
class IsoSpec1987MC(IsoSpec1987M):
    def SetDataTypes(self):
        self.DataType('MTI', DT.EBCDIC)
        self.DataType(1, DT.BIN) # bitmap
        
        for field in self.ContentTypes.keys():
            
            ContentType = self.ContentType(field)
            
            if('a' in ContentType or 'n' in ContentType or 's' in ContentType):
                self.DataType(field, DT.EBCDIC)
            else:
                self.DataType(field, DT.BIN)

            if(self.LengthType(field) != LT.FIXED):
                self.LengthDataType(field, DT.EBCDIC)
        
class IsoSpec1987VISA(IsoSpec1987V):
    def SetDataTypes(self):
        self.DataType('MTI', DT.BCD)
        self.DataType(1, DT.BIN) # bitmap 
        
        for field in self.ContentTypes.keys():
            
            ContentType = self.ContentType(field)
            
            if('a' in ContentType or 's' in ContentType):
                self.DataType(field, DT.EBCDIC)
            elif(ContentType == 'b' or ContentType == '2b'):
                self.DataType(field, DT.BIN)
            else:
                self.DataType(field, DT.BCD)
                
                
            if(self.LengthType(field) == LT.LLLVAR and ContentType == '2b'):
                self.LengthDataType(field, DT.TB)
            elif(self.LengthType(field) != LT.FIXED):
                self.LengthDataType(field, DT.BIN)

class IsoSpec1987VISAa(IsoSpec1987Va):
    def SetDataTypes(self):
        self.DataType('MTI', DT.BCD)
        self.DataType(1, DT.BIN) # bitmap 
        
        for field in self.ContentTypes.keys():
            
            ContentType = self.ContentType(field)
            
            if('a' in ContentType or 's' in ContentType):
                self.DataType(field, DT.EBCDIC)
            elif(ContentType == 'b' or ContentType == '2b'):
                self.DataType(field, DT.BIN)
            else:
                self.DataType(field, DT.BCD)
                
                
            if(self.LengthType(field) == LT.LLLVAR and ContentType == '2b'):
                self.LengthDataType(field, DT.TB)
            elif(self.LengthType(field) != LT.FIXED):
                self.LengthDataType(field, DT.BIN)

class IsoSpec1987BCD(IsoSpec1987):
    def SetDataTypes(self):
        self.DataType('MTI', DT.BCD)
        self.DataType(1, DT.BIN) # bitmap 
        
        # Most popular BCD implementations use the reserved/private fields
        # as binary, so we have to set them as such in contrast to the ISO spec
        for field in self.ContentTypes.keys():
            if(self.MaxLength(field) == 999):
                self.ContentType(field, 'b')
        
        
        for field in self.ContentTypes.keys():
            
            ContentType = self.ContentType(field)
            
            if('a' in ContentType or 's' in ContentType):
                self.DataType(field, DT.ASCII)
            elif(ContentType == 'b'):
                self.DataType(field, DT.BIN)
            else:
                self.DataType(field, DT.BCD)

            if(self.LengthType(field) != LT.FIXED):
                self.LengthDataType(field, DT.BCD)

class IsoSpec1993JCN(IsoSpec1993J):
    def SetDataTypes(self):
        self.DataType('MTI', DT.ASCII)
        self.DataType(1, DT.BIN) # bitmap
        
        for field in self.ContentTypes.keys():
            
            ContentType = self.ContentType(field)
            
            if('a' in ContentType or 'n' in ContentType or 's' in ContentType):
                self.DataType(field, DT.ASCII)
            else:
                self.DataType(field, DT.BIN)

            if(self.LengthType(field) != LT.FIXED):
                self.LengthDataType(field, DT.ASCII)

Descriptions = {}

Descriptions['1987'] = {
    1 : 'Bitmap' ,
    2 : 'Primary account number (PAN)' ,
    3 : 'Processing code' ,
    4 : 'Amount, transaction' ,
    5 : 'Amount, settlement' ,
    6 : 'Amount, cardholder billing' ,
    7 : 'Transmission date & time' ,
    8 : 'Amount, cardholder billing fee' ,
    9 : 'Conversion rate, settlement' ,
    10 : 'Conversion rate, cardholder billing' ,
    11 : 'System trace audit number' ,
    12 : 'Time, local transaction (hhmmss)' ,
    13 : 'Date, local transaction (MMDD)' ,
    14 : 'Date, expiration' ,
    15 : 'Date, settlement' ,
    16 : 'Date, conversion' ,
    17 : 'Date, capture' ,
    18 : 'Merchant type' ,
    19 : 'Acquiring institution country code' ,
    20 : 'PAN extended, country code' ,
    21 : 'Forwarding institution. country code' ,
    22 : 'Point of service entry mode' ,
    23 : 'Application PAN sequence number' ,
    24 : 'Network International identifier (NII)' ,
    25 : 'Point of service condition code' ,
    26 : 'Point of service capture code' ,
    27 : 'Authorizing identification response length' ,
    28 : 'Amount, transaction fee' ,
    29 : 'Amount, settlement fee' ,
    30 : 'Amount, transaction processing fee' ,
    31 : 'Amount, settlement processing fee' ,
    32 : 'Acquiring institution identification code' ,
    33 : 'Forwarding institution identification code' ,
    34 : 'Primary account number, extended' ,
    35 : 'Track 2 data' ,
    36 : 'Track 3 data' ,
    37 : 'Retrieval reference number' ,
    38 : 'Authorization identification response' ,
    39 : 'Response code' ,
    40 : 'Service restriction code' ,
    41 : 'Card acceptor terminal identification' ,
    42 : 'Card acceptor identification code' ,
    43 : 'Card acceptor name/location' ,
    44 : 'Additional response data' ,
    45 : 'Track 1 data' ,
    46 : 'Additional data - ISO' ,
    47 : 'Additional data - national' ,
    48 : 'Additional data - private' ,
    49 : 'Currency code, transaction' ,
    50 : 'Currency code, settlement' ,
    51 : 'Currency code, cardholder billing' ,
    52 : 'Personal identification number data' ,
    53 : 'Security related control information' ,
    54 : 'Additional amounts' ,
    55 : 'Reserved ISO' ,
    56 : 'Reserved ISO' ,
    57 : 'Reserved national' ,
    58 : 'Reserved national' ,
    59 : 'Reserved national' ,
    60 : 'Reserved national' ,
    61 : 'Reserved private' ,
    62 : 'Reserved private' ,
    63 : 'Reserved private' ,
    64 : 'Message authentication code (MAC)' ,
    65 : 'Bitmap, extended' ,
    66 : 'Settlement code' ,
    67 : 'Extended payment code' ,
    68 : 'Receiving institution country code' ,
    69 : 'Settlement institution country code' ,
    70 : 'Network management information code' ,
    71 : 'Message number' ,
    72 : 'Message number, last' ,
    73 : 'Date, action (YYMMDD)' ,
    74 : 'Credits, number' ,
    75 : 'Credits, reversal number' ,
    76 : 'Debits, number' ,
    77 : 'Debits, reversal number' ,
    78 : 'Transfer number' ,
    79 : 'Transfer, reversal number' ,
    80 : 'Inquiries number' ,
    81 : 'Authorizations, number' ,
    82 : 'Credits, processing fee amount' ,
    83 : 'Credits, transaction fee amount' ,
    84 : 'Debits, processing fee amount' ,
    85 : 'Debits, transaction fee amount' ,
    86 : 'Credits, amount' ,
    87 : 'Credits, reversal amount' ,
    88 : 'Debits, amount' ,
    89 : 'Debits, reversal amount' ,
    90 : 'Original data elements' ,
    91 : 'File update code' ,
    92 : 'File security code' ,
    93 : 'Response indicator' ,
    94 : 'Service indicator' ,
    95 : 'Replacement amounts' ,
    96 : 'Message security code' ,
    97 : 'Amount, net settlement' ,
    98 : 'Payee' ,
    99 : 'Settlement institution identification code' ,
    100 : 'Receiving institution identification code' ,
    101 : 'File name' ,
    102 : 'Account identification 1' ,
    103 : 'Account identification 2' ,
    104 : 'Transaction description' ,
    105 : 'Reserved for ISO use' ,
    106 : 'Reserved for ISO use' ,
    107 : 'Reserved for ISO use' ,
    108 : 'Reserved for ISO use' ,
    109 : 'Reserved for ISO use' ,
    110 : 'Reserved for ISO use' ,
    111 : 'Reserved for ISO use' ,
    112 : 'Reserved for national use' ,
    113 : 'Reserved for national use' ,
    114 : 'Reserved for national use' ,
    115 : 'Reserved for national use' ,
    116 : 'Reserved for national use' ,
    117 : 'Reserved for national use' ,
    118 : 'Reserved for national use' ,
    119 : 'Reserved for national use' ,
    120 : 'Reserved for private use' ,
    121 : 'Reserved for private use' ,
    122 : 'Reserved for private use' ,
    123 : 'Reserved for private use' ,
    124 : 'Reserved for private use' ,
    125 : 'Reserved for private use' ,
    126 : 'Reserved for private use' ,
    127 : 'Reserved for private use' ,
    128 : 'Message authentication code'
}

Descriptions['1987M'] = {
    1   : 'Bitmap' ,
    2   : 'Primary Account Number (PAN)' ,
    3   : 'Processing Code' ,
    4   : 'Amount, Transaction' ,
    5   : 'Amount, Settlement' ,
    6   : 'Amount, Cardholder Billing' ,
    7   : 'Transmission Date and Time' ,
    8   : 'Amount, Cardholder Billing Fee' ,
    9   : 'Conversion Rate, Settlement' ,
    10  : 'Conversion Rate, Cardholder Billing' ,
    11  : 'System Trace Audit Number' ,
    12  : 'Time, Local Transaction' ,
    13  : 'Date, Local Transaction' ,
    14  : 'Date, Expiration' ,
    15  : 'Date, Settlement' ,
    16  : 'Date, Conversion' ,
    17  : 'Date, Capture' ,
    18  : 'Merchant Type' ,
    19  : 'Acquiring Institution Country Code' ,
    20  : 'Primary Account Number Country Code' ,
    21  : 'Forwarding Institution Country Code' ,
    22  : 'Point-of-Service Entry Mode' ,
    23  : 'Card Sequence Number' ,
    24  : 'Network International ID' ,
    25  : 'Point-of-Service Condition Code' ,
    26  : 'Point-of-Service PIN Capture Code' ,
    27  : 'Authorization ID Response Length' ,
    28  : 'Amount, Transaction Fee' ,
    29  : 'Amount, Settlement Fee' ,
    30  : 'Amount, Transaction Processing Fee' ,
    31  : 'Amount, Settlement Processing Fee' ,
    32  : 'Acquiring Institution ID Code' ,
    33  : 'Forwarding Institution ID Code' ,
    34  : 'Primary Account Number, Extended' ,
    35  : 'Track 2 Data' ,
    36  : 'Track 3 Data' ,
    37  : 'Retrieval Reference Number' ,
    38  : 'Authorization ID Response' ,
    39  : 'Response Code' ,
    40  : 'Service Restriction Code' ,
    41  : 'Card Acceptor Terminal ID' ,
    42  : 'Card Acceptor ID Code' ,
    43  : 'Card Acceptor Name/Location' ,
    44  : 'Additional Response Data' ,
    45  : 'Track 1 Data' ,
    46  : 'Additional Data - ISO Use' ,
    47  : 'Additional Data - National Use' ,
    48  : 'Additional Data - Private Use' ,
    49  : 'Currency Code, Transaction' ,
    50  : 'Currency Code, Settlement' ,
    51  : 'Currency Code, Cardholder Billing' ,
    52  : 'Personal ID Number (PIN) Data' ,
    53  : 'Security-Related Control Information' ,
    54  : 'Additional Amounts' ,
    55  : 'IC Card System-Related Data' ,
    56  : 'Reserved for ISO Use' ,
    57  : 'Reserved National Use' ,
    58  : 'Reserved National Use' ,
    59  : 'Reserved National Use' ,
    60  : 'Advice Reason Code' ,
    61  : 'Point-of-Service Data' ,
    62  : 'Intermediate Network Facility Data' ,
    63  : 'Network Date' ,
    64  : 'Message Authentication Code (MAC)' ,
    65  : 'Bit Map, Extended' ,
    66  : 'Settlement Code' ,
    67  : 'Extended Payment Code' ,
    68  : 'Receiving Institution Country Code' ,
    69  : 'Settlement Institution Country Code' ,
    70  : 'Network Management Information Code' ,
    71  : 'Message Number' ,
    72  : 'Message Number Last' ,
    73  : 'Date, Action' ,
    74  : 'Credits, Number' ,
    75  : 'Credits, Reversal Number' ,
    76  : 'Debits, Number' ,
    77  : 'Debits, Reversal Number' ,
    78  : 'Transfers, Number' ,
    79  : 'Transfers, Reversal Number' ,
    80  : 'Inquiries, Number' ,
    81  : 'Authorizations, Number' ,
    82  : 'Credits, Processing Fee Amount' ,
    83  : 'Credits, Transaction Fee Amount' ,
    84  : 'Debits, Processing Fee Amount' ,
    85  : 'Debits, Transaction Fee Amount' ,
    86  : 'Credits, Amount' ,
    87  : 'Credits, Reversal Amount' ,
    88  : 'Debits, Amount' ,
    89  : 'Debits, Reversal Amount' ,
    90  : 'Original Data Elements' ,
    91  : 'Issuer File Update Code' ,
    92  : 'File Security Code' ,
    93  : 'Response Indicator' ,
    94  : 'Service Indicator' ,
    95  : 'Replacement Amounts' ,
    96  : 'Message Security Code' ,
    97  : 'Amount, Net Settlement' ,
    98  : 'Payee' ,
    99  : 'Settlement Institution ID Code' ,
    100 : 'Receiving Institution ID Code' ,
    101 : 'File Name' ,
    102 : 'Account ID-1' ,
    103 : 'Account ID-2' ,
    104 : 'Digital Payment Data' ,
    105 : 'Multi-Use Transaction Identification Data' ,
    106 : 'Reserved for MasterCard Use' ,
    107 : 'Reserved for MasterCard Use' ,
    108 : 'MoneySend Reference Data' ,
    109 : 'Reserved for ISO Use' ,
    110 : 'Additional Data-2' ,
    111 : 'Reserved for ISO Use' ,
    112 : 'Additional Data - National Use' ,
    113 : 'Reserved for National Use' ,
    114 : 'Reserved for National Use' ,
    115 : 'Reserved for National Use' ,
    116 : 'Reserved for National Use' ,
    117 : 'Reserved for National Use' ,
    118 : 'Reserved for National Use' ,
    119 : 'Reserved for National Use' ,
    120 : 'Record Data' ,
    121 : 'Authorizing Agent ID Code' ,
    122 : 'Additional Record Data' ,
    123 : 'Receipt Free Text' ,
    124 : 'Member-defined Data' ,
    125 : 'New PIN Data' ,
    126 : 'Private Data' ,
    127 : 'Private Data' ,
    128 : 'Message Authentication Code (MAC)'
}

Descriptions['1987V'] = {
    1   : 'Bitmap' ,
    2   : 'Primary Account Number (PAN)' ,
    3   : 'Processing Code' ,
    4   : 'Amount, Transaction' ,
    6   : 'Amount, Cardholder Billing' ,
    7   : 'Transmission Date and Time' ,
    8   : 'Amount, Cardholder Billing Fee' ,
    10  : 'Conversion Rate, Cardholder Billing' ,
    11  : 'System Trace Audit Number' ,
    12  : 'Time, Local Transaction' ,
    13  : 'Date, Local Transaction' ,
    14  : 'Date, Expiration' ,
    17  : 'Date, Capture' ,
    18  : 'Merchant Type' ,
    19  : 'Acquiring Institution Country Code' ,
    20  : 'PAN Extended, Country Code' ,
    22  : 'Point-of-Service Entry Mode Code' ,
    23  : 'Card Sequence Number' ,
    24  : 'Network International Identifier' ,
    25  : 'Point-of-Service Condition Code' ,
    26  : 'Point-of-Service PIN Capture Code' ,
    27  : 'Authorization ID Response Length' ,
    28  : 'Amount, Transaction Fee' ,
    29  : 'Amount, Settlement Fee' ,
    30  : 'Amount, Transaction Processing Fee' ,
    31  : 'Amount, Settlement Processing Fee' ,
    32  : 'Acquiring Institution ID Code' ,
    33  : 'Forwarding Institution ID Code' ,
    34  : 'Electronic Commerce Data' ,
    35  : 'Track 2 Data' ,
    36  : 'Track 3 Data' ,
    37  : 'Retrieval Reference Number' ,
    38  : 'Authorization ID Response' ,
    39  : 'Response Code' ,
    41  : 'Card Acceptor Terminal ID' ,
    42  : 'Card Acceptor ID Code' ,
    43  : 'Card Acceptor Name/Location' ,
    44  : 'Additional Response Data' ,
    45  : 'Track 1 Data' ,
    46  : 'Additional Data - ISO' ,
    47  : 'Additional Data - National' ,
    48  : 'Additional Data - Private' ,
    49  : 'Currency Code, Transaction' ,
    51  : 'Currency Code, Cardholder Billing' ,
    52  : 'Personal ID Number (PIN) Data' ,
    53  : 'Security-Related Control Information' ,
    54  : 'Additional Amounts' ,
    55  : 'IC Card Related Data' ,
    56  : 'Customer Related Data' ,
    57  : 'Reserved - National' ,
    58  : 'Reserved - National' ,
    59  : 'National POS Geographic Data' ,
    60  : 'Additional POS Information' ,
    61  : 'Other Amounts' ,
    62  : 'Custom Payment Service Fields' ,
    63  : 'V.I.P. Private-Use Field' ,
    67  : 'Extended Payment Code' ,
    68  : 'Receiving Institution Country Code' ,
    70  : 'Network Management Information Code' ,
    71  : 'Message Number' ,
    72  : 'Message Number Last' ,
    73  : 'Date, Action' ,
    78  : 'Transfers, Number' ,
    79  : 'Transfers, Reversal Number' ,
    80  : 'Inquiries, Number' ,
    81  : 'Authorizations, Number' ,
    82  : 'Credits, Processing Fee Amount' ,
    83  : 'Credits, Transaction Fee Amount' ,
    84  : 'Debits, Processing Fee Amount' ,
    85  : 'Debits, Transaction Fee Amount' ,
    90  : 'Original Data Elements' ,
    91  : 'File Update Code' ,
    92  : 'File Security Code' ,
    94  : 'Service Indicator' ,
    95  : 'Replacement Amounts' ,
    98  : 'Payee' ,
    100 : 'Receiving Institution ID Code' ,
    101 : 'File Name' ,
    102 : 'Account ID 1' ,
    103 : 'Account ID 2' ,
    104 : 'Transaction Description' ,
    105 : 'Reserved ISO' ,
    106 : 'Reserved ISO' ,
    107 : 'Reserved ISO' ,
    108 : 'Reserved ISO' ,
    109 : 'Reserved ISO' ,
    110 : 'Encryption Data' ,
    111 : 'Reserved ISO' ,
    112 : 'Reserved National' ,
    113 : 'Reserved National' ,
    114 : 'Domestic and Localized Data' ,
    115 : 'Reserved National' ,
    116 : 'Card Issuer Reference Data' ,
    117 : 'National Use' ,
    118 : 'Intra-Country Data' ,
    120 : 'Auxiliary Transaction Data' ,
    121 : 'Issuing Institution ID Code' ,
    123 : 'Verification' ,
    125 : 'Supporting Information' ,
    126 : 'Visa Private-Use Fields',
    127 : 'File Maintenance',
    130 : 'Terminal Capability Profile',
    131 : 'Terminal Verification Results (TVR)',
    132 : 'Unpredictable Number',
    133 : 'Terminal Serial Number',
    134 : 'Visa Discretionary Data',
    135 : 'Issuer Discretionary Data',
    136 : 'Cryptogram',
    137 : 'Application Transaction Counter',
    138 : 'Applicaion Interchange Profile',
    139 : 'ARPC Response Cryptogram & Code',
    140 : 'Issuer Authentication Data',
    142 : 'Issuer Script',
    143 : 'Issuer Script Results',
    144 : 'Cryptogram Transaction Type',
    145 : 'Terminal Country Code',
    146 : 'Terminal Transaction Date',
    147 : 'Cryptogram Amount',
    148 : 'Cryptogram Currency Code',
    149 : 'Cryptogram Cashback Amount',
    152 : 'Secondary PIN Block'
}

Descriptions['1993J'] = {
    1   : 'Bitmap' ,
    2   : '会員番号　　　　　　　　　　　　　　' ,
    3   : 'プロセシングコード　　　　　　　　　' ,
    4   : '取引金額　　　　　　　　　　　　　　' ,
    6   : '外貨建て取引金額　　　　　　　　　　' ,
    10  : '換算レート　　　　　　　　　　　　　' ,
    11  : 'システムトレースオーディットナンバー' ,
    12  : '現地取引日時　　　　　　　　　　　　' ,
    14  : '有効期限　　　　　　　　　　　　　　' ,
    17  : '収集日　　　　　　　　　　　　　　　' ,
    18  : '商品コード　　　　　　　　　　　　　' ,
    19  : '国コード　　　　　　　　　　　　　　' ,
    22  : 'ＰＯＳデータコード　　　　　　　　　' ,
    24  : 'ファンクションコード　　　　　　　　' ,
    25  : 'メッセージ理由コード　　　　　　　　' ,
    26  : '加盟店業種コード　　　　　　　　　　' ,
    28  : '精査日　　　　　　　　　　　　　　　' ,
    30  : 'オリジナル金額　　　　　　　　　　　' ,
    32  : '加盟店会社コード　　　　　　　　　　' ,
    35  : 'ＪＩＳ１第２トラック情報　　　　　　' ,
    37  : 'リトリーバルリファレンスナンバー　　' ,
    38  : '承認コード　　　　　　　　　　　　　' ,
    39  : 'アクションコード　　　　　　　　　　' ,
    41  : '加盟店端末番号　　　　　　　　　　　' ,
    42  : '加盟店番号　　　　　　　　　　　　　' ,
    43  : '加盟店名／所在地　　　　　　　　　　' ,
    46  : '手数料金額　　　　　　　　　　　　　',
    47  : 'ＪＩＳ２トラック情報　　　　　　　　' ,
    48  : '国内レスポンスコード　　　　　　　　' ,
    49  : '取引通貨コード　　　　　　　　　　　' ,
    50  : '精査通貨コード　　　　　　　　　　　' ,
    51  : '外貨建て取引通貨コード　　　　　　　' ,
    52  : '入力暗証番号　　　　　　　　　　　　' ,
    53  : 'セキュリティ関連制御情報　　　　　　' ,
    54  : '残高その他金額　　　　　　　　　　　',
    55  : 'ＩＣカード関連データ　　　　　　　　' ,
    56  : 'オリジナルデータエレメント　　　　　' ,
    58  : 'オーソリ判定センターＩＤ　　　　　　' ,
    59  : '端末出力データ　　　　　　　　　　　' ,
    60  : '国内使用予約域　　　　　　　　　　　' ,
    62  : '個社使用予約域　　　　　　　　　　　' ,
    63  : 'カードネット拡張使用域　　　　　　　' ,
    72  : '通知レコード　　　　　　　　　　　　' ,
    74  : '売上取消／返品件数　　　　　　　　　' ,
    75  : '売上障害取消件数　　　　　　　　　　' ,
    76  : '売上件数　　　　　　　　　　　　　　' ,
    77  : '売上取消／返品障害取消件数　　　　　' ,
    80  : '照会件数　　　　　　　　　　　　　　' ,
    81  : 'オーソリ件数　　　　　　　　　　　　' ,
    82  : '照会障害取消件数　　　　　　　　　　' ,
    86  : '売上取消／返品金額　　　　　　　　　' ,
    87  : '売上障害取消金額　　　　　　　　　　' ,
    88  : '売上金額　　　　　　　　　　　　　　' ,
    89  : '売上取消／返品障害取消金額　　　　　' ,
    90  : 'オーソリ障害取消件数　　　　　　　　' ,
    93  : '電文送信先センターＩＤ　　　　　　　' ,
    94  : '電文送信元センターＩＤ　　　　　　　' ,
    96  : 'キーマネジメントデータ　　　　　　　' ,
    97  : '精査合計金額　　　　　　　　　　　　' ,
    100 : '精査対象センターＩＤ　　　　　　　　' ,
    109 : '被仕向徴収手数料金額　　　　　　　　' ,
    110 : '仕向徴収手数料金額　　　　　　　　　'
}
    
ContentTypes = {}

ContentTypes['1987'] = {
    1 :   { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    2 :   { 'ContentType':'n',     'MaxLen': 19,  'LenType': LT.LLVAR },
    3 :   { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    4 :   { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    5 :   { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    6 :   { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    7 :   { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    8 :   { 'ContentType':'n',     'MaxLen': 8,   'LenType': LT.FIXED },
    9 :   { 'ContentType':'n',     'MaxLen': 8,   'LenType': LT.FIXED },
    10 :  { 'ContentType':'n',     'MaxLen': 8,   'LenType': LT.FIXED },
    11 :  { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    12 :  { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    13 :  { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    14 :  { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    15 :  { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    16 :  { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    17 :  { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    18 :  { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    19 :  { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    20 :  { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    21 :  { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    22 :  { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    23 :  { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    24 :  { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    25 :  { 'ContentType':'n',     'MaxLen': 2,   'LenType': LT.FIXED },
    26 :  { 'ContentType':'n',     'MaxLen': 2,   'LenType': LT.FIXED },
    27 :  { 'ContentType':'n',     'MaxLen': 1,   'LenType': LT.FIXED },
    28 :  { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    29 :  { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    30 :  { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    31 :  { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    32 :  { 'ContentType':'n',     'MaxLen': 11,  'LenType': LT.LLVAR },
    33 :  { 'ContentType':'n',     'MaxLen': 11,  'LenType': LT.LLVAR },
    34 :  { 'ContentType':'ns',    'MaxLen': 28,  'LenType': LT.LLVAR },
    35 :  { 'ContentType':'z',     'MaxLen': 37,  'LenType': LT.LLVAR },
    36 :  { 'ContentType':'n',     'MaxLen': 104, 'LenType': LT.LLLVAR},
    37 :  { 'ContentType':'an',    'MaxLen': 12,  'LenType': LT.FIXED },
    38 :  { 'ContentType':'an',    'MaxLen': 6,   'LenType': LT.FIXED },
    39 :  { 'ContentType':'an',    'MaxLen': 2,   'LenType': LT.FIXED },
    40 :  { 'ContentType':'an',    'MaxLen': 3,   'LenType': LT.FIXED },
    41 :  { 'ContentType':'ans',   'MaxLen': 8,   'LenType': LT.FIXED },
    42 :  { 'ContentType':'ans',   'MaxLen': 15,  'LenType': LT.FIXED },
    43 :  { 'ContentType':'ans',   'MaxLen': 40,  'LenType': LT.FIXED },
    44 :  { 'ContentType':'an',    'MaxLen': 25,  'LenType': LT.LLVAR },
    45 :  { 'ContentType':'an',    'MaxLen': 76,  'LenType': LT.LLVAR },
    46 :  { 'ContentType':'an',    'MaxLen': 999, 'LenType': LT.LLLVAR},
    47 :  { 'ContentType':'an',    'MaxLen': 999, 'LenType': LT.LLLVAR},
    48 :  { 'ContentType':'an',    'MaxLen': 999, 'LenType': LT.LLLVAR},
    49 :  { 'ContentType':'an',    'MaxLen': 3,   'LenType': LT.FIXED },
    50 :  { 'ContentType':'an',    'MaxLen': 3,   'LenType': LT.FIXED },
    51 :  { 'ContentType':'an',    'MaxLen': 3,   'LenType': LT.FIXED },
    52 :  { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    53 :  { 'ContentType':'n',     'MaxLen': 16,  'LenType': LT.FIXED },
    54 :  { 'ContentType':'an',    'MaxLen': 120, 'LenType': LT.LLLVAR},
    55 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    56 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    57 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    58 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    59 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    60 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    61 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    62 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    63 :  { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    64 :  { 'ContentType':'b',     'MaxLen' : 8,  'LenType': LT.FIXED },
    65 :  { 'ContentType' : 'b',   'MaxLen' : 1,  'LenType': LT.FIXED },
    66 :  { 'ContentType' : 'n',   'MaxLen' : 1,  'LenType': LT.FIXED },
    67 :  { 'ContentType' : 'n',   'MaxLen' : 2,  'LenType': LT.FIXED },
    68 :  { 'ContentType' : 'n',   'MaxLen' : 3,  'LenType': LT.FIXED },
    69 :  { 'ContentType' : 'n',   'MaxLen' : 3,  'LenType': LT.FIXED },
    70 :  { 'ContentType' : 'n',   'MaxLen' : 3,  'LenType': LT.FIXED },
    71 :  { 'ContentType' : 'n',   'MaxLen' : 4,  'LenType': LT.FIXED },
    72 :  { 'ContentType' : 'n',   'MaxLen' : 4,  'LenType': LT.FIXED },
    73 :  { 'ContentType' : 'n',   'MaxLen' : 6,  'LenType': LT.FIXED },
    74 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    75 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    76 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    77 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    78 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    79 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    80 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    81 :  { 'ContentType' : 'n',   'MaxLen' : 10, 'LenType': LT.FIXED },
    82 :  { 'ContentType' : 'n',   'MaxLen' : 12, 'LenType': LT.FIXED },
    83 :  { 'ContentType' : 'n',   'MaxLen' : 12, 'LenType': LT.FIXED },
    84 :  { 'ContentType' : 'n',   'MaxLen' : 12, 'LenType': LT.FIXED },
    85 :  { 'ContentType' : 'n',   'MaxLen' : 12, 'LenType': LT.FIXED },
    86 :  { 'ContentType' : 'n',   'MaxLen' : 16, 'LenType': LT.FIXED },
    87 :  { 'ContentType' : 'n',   'MaxLen' : 16, 'LenType': LT.FIXED },
    88 :  { 'ContentType' : 'n',   'MaxLen' : 16, 'LenType': LT.FIXED },
    89 :  { 'ContentType' : 'n',   'MaxLen' : 16, 'LenType': LT.FIXED },
    90 :  { 'ContentType' : 'n',   'MaxLen' : 42, 'LenType': LT.FIXED },
    91 :  { 'ContentType' : 'an',  'MaxLen' : 1,  'LenType': LT.FIXED },
    92 :  { 'ContentType' : 'an',  'MaxLen' : 2,  'LenType': LT.FIXED },
    93 :  { 'ContentType' : 'an',  'MaxLen' : 5,  'LenType': LT.FIXED },
    94 :  { 'ContentType' : 'an',  'MaxLen' : 7,  'LenType': LT.FIXED },
    95 :  { 'ContentType' : 'an',  'MaxLen' : 42, 'LenType': LT.FIXED },
    96 :  { 'ContentType' : 'b',   'MaxLen' : 8,  'LenType': LT.FIXED },
    97 :  { 'ContentType' : 'an',  'MaxLen' : 17, 'LenType': LT.FIXED },
    98 :  { 'ContentType' : 'ans', 'MaxLen' : 25, 'LenType': LT.FIXED },
    99 :  { 'ContentType' : 'n',   'MaxLen' : 11, 'LenType': LT.LLVAR },
    100 : { 'ContentType' : 'n',   'MaxLen' : 11, 'LenType': LT.LLVAR },
    101 : { 'ContentType' : 'ans', 'MaxLen' : 17, 'LenType': LT.LLVAR },
    102 : { 'ContentType' : 'ans', 'MaxLen' : 28, 'LenType': LT.LLVAR },
    103 : { 'ContentType' : 'ans', 'MaxLen' : 28, 'LenType': LT.LLVAR },
    104 : { 'ContentType' : 'ans', 'MaxLen' : 100, 'LenType': LT.LLLVAR },
    105 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    106 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    107 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    108 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    109 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    110 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    111 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    112 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    113 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    114 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    115 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    116 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    117 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    118 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    119 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    120 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    121 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    122 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    123 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    124 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    125 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    126 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    127 : { 'ContentType' : 'ans', 'MaxLen' : 999, 'LenType': LT.LLLVAR },
    128 : { 'ContentType' : 'b',   'MaxLen' : 8,  'LenType': LT.FIXED }
}

ContentTypes['1987M'] = {
    1   : { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    2   : { 'ContentType':'n',     'MaxLen': 19,  'LenType': LT.LLVAR },
    3   : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    4   : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    5   : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    6   : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    7   : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    8   : { 'ContentType':'n',     'MaxLen': 8,   'LenType': LT.FIXED },
    9   : { 'ContentType':'n',     'MaxLen': 8,   'LenType': LT.FIXED },
    10  : { 'ContentType':'n',     'MaxLen': 8,   'LenType': LT.FIXED },
    11  : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    12  : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    13  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    14  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    15  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    16  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    17  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    18  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    19  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    20  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    21  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    22  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    23  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    24  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    25  : { 'ContentType':'n',     'MaxLen': 2,   'LenType': LT.FIXED },
    26  : { 'ContentType':'n',     'MaxLen': 2,   'LenType': LT.FIXED },
    27  : { 'ContentType':'n',     'MaxLen': 1,   'LenType': LT.FIXED },
    28  : { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    29  : { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    30  : { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    31  : { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    32  : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.LLVAR },
    33  : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.LLVAR },
    34  : { 'ContentType':'ans',   'MaxLen': 28,  'LenType': LT.LLVAR },
    35  : { 'ContentType':'ans',   'MaxLen': 37,  'LenType': LT.LLVAR },
    36  : { 'ContentType':'ans',   'MaxLen': 104, 'LenType': LT.LLLVAR},
    37  : { 'ContentType':'an',    'MaxLen': 12,  'LenType': LT.FIXED },
    38  : { 'ContentType':'ans',   'MaxLen': 6,   'LenType': LT.FIXED },
    39  : { 'ContentType':'an',    'MaxLen': 2,   'LenType': LT.FIXED },
    40  : { 'ContentType':'an',    'MaxLen': 3,   'LenType': LT.FIXED },
    41  : { 'ContentType':'ans',   'MaxLen': 8,   'LenType': LT.FIXED },
    42  : { 'ContentType':'ans',   'MaxLen': 15,  'LenType': LT.FIXED },
    43  : { 'ContentType':'ans',   'MaxLen': 40,  'LenType': LT.FIXED },
    44  : { 'ContentType':'ans',   'MaxLen': 25,  'LenType': LT.LLVAR },
    45  : { 'ContentType':'ans',   'MaxLen': 76,  'LenType': LT.LLVAR },
    46  : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    47  : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    48  : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    49  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    50  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    51  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    52  : { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    53  : { 'ContentType':'n',     'MaxLen': 16,  'LenType': LT.FIXED },
    54  : { 'ContentType':'an',    'MaxLen': 120, 'LenType': LT.LLLVAR},
    55  : { 'ContentType':'b',     'MaxLen': 255, 'LenType': LT.LLLVAR},
    56  : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    57  : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    58  : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    59  : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    60  : { 'ContentType':'ans',   'MaxLen': 60,  'LenType': LT.LLLVAR},
    61  : { 'ContentType':'an',    'MaxLen': 26,  'LenType': LT.LLLVAR},
    62  : { 'ContentType':'ans',   'MaxLen': 100, 'LenType': LT.LLLVAR},
    63  : { 'ContentType':'an',    'MaxLen': 50,  'LenType': LT.LLLVAR},
    64  : { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    65  : { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    66  : { 'ContentType':'n',     'MaxLen': 1,   'LenType': LT.FIXED },
    67  : { 'ContentType':'n',     'MaxLen': 2,   'LenType': LT.FIXED },
    68  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    69  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    70  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    71  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    72  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    73  : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    74  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    75  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    76  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    77  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    78  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    79  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    80  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    81  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    82  : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    83  : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    84  : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    85  : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    86  : { 'ContentType':'n',     'MaxLen': 16,  'LenType': LT.FIXED },
    87  : { 'ContentType':'n',     'MaxLen': 16,  'LenType': LT.FIXED },
    88  : { 'ContentType':'n',     'MaxLen': 16,  'LenType': LT.FIXED },
    89  : { 'ContentType':'n',     'MaxLen': 16,  'LenType': LT.FIXED },
    90  : { 'ContentType':'n',     'MaxLen': 42,  'LenType': LT.FIXED },
    91  : { 'ContentType':'an',    'MaxLen': 1,   'LenType': LT.FIXED },
    92  : { 'ContentType':'an',    'MaxLen': 2,   'LenType': LT.FIXED },
    93  : { 'ContentType':'an',    'MaxLen': 5,   'LenType': LT.FIXED },
    94  : { 'ContentType':'an',    'MaxLen': 7,   'LenType': LT.FIXED },
    95  : { 'ContentType':'an',    'MaxLen': 42,  'LenType': LT.FIXED },
    96  : { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    97  : { 'ContentType':'an',    'MaxLen': 17,  'LenType': LT.FIXED },
    98  : { 'ContentType':'ans',   'MaxLen': 25,  'LenType': LT.FIXED },
    99  : { 'ContentType':'n',     'MaxLen': 11,  'LenType': LT.LLVAR },
    100 : { 'ContentType':'n',     'MaxLen': 11,  'LenType': LT.LLVAR },
    101 : { 'ContentType':'ans',   'MaxLen': 17,  'LenType': LT.LLVAR },
    102 : { 'ContentType':'ans',   'MaxLen': 28,  'LenType': LT.LLVAR },
    103 : { 'ContentType':'ans',   'MaxLen': 28,  'LenType': LT.LLVAR },
    104 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    105 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    106 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    107 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    108 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    109 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    110 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    111 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    112 : { 'ContentType':'ans',   'MaxLen': 195, 'LenType': LT.LLLVAR},
    113 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    114 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    115 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    116 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    117 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    118 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    119 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    120 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    121 : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.LLLVAR},
    122 : { 'ContentType':'ans',   'MaxLen': 999, 'LenType': LT.LLLVAR},
    123 : { 'ContentType':'ans',   'MaxLen': 512, 'LenType': LT.LLLVAR},
    124 : { 'ContentType':'ans',   'MaxLen': 299, 'LenType': LT.LLLVAR},
    125 : { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    126 : { 'ContentType':'ans',   'MaxLen': 100, 'LenType': LT.LLLVAR},
    127 : { 'ContentType':'ans',   'MaxLen': 100, 'LenType': LT.LLLVAR},
    128 : { 'ContentType':'b',     'MaxLen' : 8,  'LenType': LT.FIXED }
}

ContentTypes['1987V'] = {
    1   : { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    2   : { 'ContentType':'n',     'MaxLen': 19,  'LenType': LT.LLVAR },
    3   : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    4   : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    6   : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    7   : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    8   : { 'ContentType':'n',     'MaxLen': 8,   'LenType': LT.FIXED },
    10  : { 'ContentType':'n',     'MaxLen': 8,   'LenType': LT.FIXED },
    11  : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    12  : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    13  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    14  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    17  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    18  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    19  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    20  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    22  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    23  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    24  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    25  : { 'ContentType':'n',     'MaxLen': 2,   'LenType': LT.FIXED },
    26  : { 'ContentType':'n',     'MaxLen': 2,   'LenType': LT.FIXED },
    27  : { 'ContentType':'n',     'MaxLen': 1,   'LenType': LT.FIXED },
    28  : { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    29  : { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    30  : { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    31  : { 'ContentType':'an',    'MaxLen': 9,   'LenType': LT.FIXED },
    32  : { 'ContentType':'n',     'MaxLen': 11,  'LenType': LT.LLVAR },
    33  : { 'ContentType':'n',     'MaxLen': 11,  'LenType': LT.LLVAR },
    34  : { 'ContentType':'2b',    'MaxLen': 999, 'LenType': LT.LLLVAR},
    35  : { 'ContentType':'z',     'MaxLen': 37,  'LenType': LT.LLVAR },
    36  : { 'ContentType':'ans',   'MaxLen': 104, 'LenType': LT.LLLVAR},
    37  : { 'ContentType':'an',    'MaxLen': 12,  'LenType': LT.FIXED },
    38  : { 'ContentType':'ans',   'MaxLen': 6,   'LenType': LT.FIXED },
    39  : { 'ContentType':'an',    'MaxLen': 2,   'LenType': LT.FIXED },
    41  : { 'ContentType':'ans',   'MaxLen': 8,   'LenType': LT.FIXED },
    42  : { 'ContentType':'ans',   'MaxLen': 15,  'LenType': LT.FIXED },
    43  : { 'ContentType':'ans',   'MaxLen': 40,  'LenType': LT.FIXED },
    44  : { 'ContentType':'ans',   'MaxLen': 25,  'LenType': LT.LLVAR },
    45  : { 'ContentType':'ans',   'MaxLen': 76,  'LenType': LT.LLVAR },
    46  : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    47  : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    48  : { 'ContentType':'b',     'MaxLen': 255, 'LenType': LT.LLLVAR},
    49  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    51  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    52  : { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    53  : { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    54  : { 'ContentType':'an',    'MaxLen': 120, 'LenType': LT.LLLVAR},
    55  : { 'ContentType':'b',     'MaxLen': 255, 'LenType': LT.LLLVAR},
    56  : { 'ContentType':'b',     'MaxLen': 255, 'LenType': LT.LLLVAR},
    57  : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    58  : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    59  : { 'ContentType':'ans',   'MaxLen': 14,  'LenType': LT.LLLVAR},
    60  : { 'ContentType':'b',     'MaxLen': 6,   'LenType': LT.LLLVAR},
    61  : { 'ContentType':'b',     'MaxLen': 26,  'LenType': LT.LLLVAR},
    62  : { 'ContentType':'b',     'MaxLen': 255, 'LenType': LT.LLLVAR},
    63  : { 'ContentType':'b',     'MaxLen': 255, 'LenType': LT.LLLVAR},
    67  : { 'ContentType':'n',     'MaxLen': 2,   'LenType': LT.FIXED },
    68  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    70  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    71  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    72  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    73  : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    78  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    79  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    80  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    81  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    82  : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    83  : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    84  : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    85  : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    90  : { 'ContentType':'n',     'MaxLen': 42,  'LenType': LT.FIXED },
    91  : { 'ContentType':'an',    'MaxLen': 1,   'LenType': LT.FIXED },
    92  : { 'ContentType':'an',    'MaxLen': 2,   'LenType': LT.FIXED },
    94  : { 'ContentType':'an',    'MaxLen': 7,   'LenType': LT.FIXED },
    95  : { 'ContentType':'an',    'MaxLen': 42,  'LenType': LT.FIXED },
    98  : { 'ContentType':'an',    'MaxLen': 25,  'LenType': LT.FIXED },
    100 : { 'ContentType':'n',     'MaxLen': 11,  'LenType': LT.LLVAR },
    101 : { 'ContentType':'ans',   'MaxLen': 17,  'LenType': LT.LLVAR },
    102 : { 'ContentType':'ans',   'MaxLen': 28,  'LenType': LT.LLVAR },
    103 : { 'ContentType':'ans',   'MaxLen': 28,  'LenType': LT.LLVAR },
    104 : { 'ContentType':'b',     'MaxLen': 255, 'LenType': LT.LLLVAR},
    105 : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    106 : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    107 : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    108 : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    109 : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    110 : { 'ContentType':'2b',    'MaxLen': 999, 'LenType': LT.LLLVAR},
    111 : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    112 : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    113 : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    114 : { 'ContentType':'2b',    'MaxLen': 999, 'LenType': LT.LLLVAR},
    115 : { 'ContentType':'ans',   'MaxLen': 24,  'LenType': LT.LLLVAR},
    116 : { 'ContentType':'b',     'MaxLen': 255, 'LenType': LT.LLLVAR},
    117 : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    118 : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    120 : { 'ContentType':'2b',    'MaxLen': 999, 'LenType': LT.LLLVAR},
    121 : { 'ContentType':'an',    'MaxLen': 11,  'LenType': LT.LLLVAR},
    123 : { 'ContentType':'ans',   'MaxLen': 29,  'LenType': LT.LLLVAR},
    125 : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    126 : { 'ContentType':'b',     'MaxLen': 255, 'LenType': LT.LLLVAR},
    127 : { 'ContentType':'ans',   'MaxLen': 255, 'LenType': LT.LLLVAR},
    130 : { 'ContentType':'b',     'MaxLen': 3,   'LenType': LT.FIXED },
    131 : { 'ContentType':'b',     'MaxLen': 5,   'LenType': LT.FIXED },
    132 : { 'ContentType':'b',     'MaxLen': 4,   'LenType': LT.FIXED },
    133 : { 'ContentType':'ans',   'MaxLen': 8,   'LenType': LT.FIXED },
    134 : { 'ContentType':'b',     'MaxLen': 255, 'LenType': LT.LLLVAR},
    135 : { 'ContentType':'b',     'MaxLen': 15,  'LenType': LT.LLLVAR},
    136 : { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    137 : { 'ContentType':'b',     'MaxLen': 2,   'LenType': LT.FIXED },
    138 : { 'ContentType':'b',     'MaxLen': 2,   'LenType': LT.FIXED },
    139 : { 'ContentType':'b',     'MaxLen': 10,  'LenType': LT.FIXED },
    140 : { 'ContentType':'b',     'MaxLen': 255, 'LenType': LT.LLLVAR},
    142 : { 'ContentType':'b',     'MaxLen': 255, 'LenType': LT.LLLVAR},
    143 : { 'ContentType':'b',     'MaxLen': 20,  'LenType': LT.LLLVAR},
    144 : { 'ContentType':'n',     'MaxLen': 2,   'LenType': LT.FIXED },
    145 : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    146 : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    147 : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    148 : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    149 : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    152 : { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED }
}

ContentTypes['1993J'] = {
    1   : { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    2   : { 'ContentType':'n',     'MaxLen': 19,  'LenType': LT.LLVAR },
    3   : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    4   : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    6   : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    10  : { 'ContentType':'n',     'MaxLen': 8,   'LenType': LT.FIXED },
    11  : { 'ContentType':'n',     'MaxLen': 6,   'LenType': LT.FIXED },
    12  : { 'ContentType':'n',     'MaxLen': 12,  'LenType': LT.FIXED },
    14  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    17  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    18  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    19  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    22  : { 'ContentType':'an',    'MaxLen': 12,  'LenType': LT.FIXED },
    24  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    25  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    26  : { 'ContentType':'n',     'MaxLen': 4,   'LenType': LT.FIXED },
    28  : { 'ContentType':'an',    'MaxLen': 6,   'LenType': LT.FIXED },
    30  : { 'ContentType':'n',     'MaxLen': 24,  'LenType': LT.FIXED },
    32  : { 'ContentType':'ans',   'MaxLen': 11,  'LenType': LT.LLVAR },
    35  : { 'ContentType':'ans',   'MaxLen': 37,  'LenType': LT.LLVAR },
    37  : { 'ContentType':'ans',   'MaxLen': 12,  'LenType': LT.FIXED },
    38  : { 'ContentType':'ans',   'MaxLen': 6,   'LenType': LT.FIXED },
    39  : { 'ContentType':'an',    'MaxLen': 3,   'LenType': LT.FIXED },
    41  : { 'ContentType':'n',     'MaxLen': 8,   'LenType': LT.FIXED },
    42  : { 'ContentType':'ans',   'MaxLen': 15,  'LenType': LT.FIXED },
    43  : { 'ContentType':'ans',   'MaxLen': 40,  'LenType': LT.LLVAR },
    46  : { 'ContentType':'an',    'MaxLen': 102, 'LenType': LT.LLLVAR},
    47  : { 'ContentType':'ans',   'MaxLen': 69,  'LenType': LT.LLLVAR},
    48  : { 'ContentType':'ans',   'MaxLen': 5,   'LenType': LT.LLLVAR},
    49  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    50  : { 'ContentType':'an',    'MaxLen': 3,   'LenType': LT.FIXED },
    51  : { 'ContentType':'n',     'MaxLen': 3,   'LenType': LT.FIXED },
    52  : { 'ContentType':'b',     'MaxLen': 8,   'LenType': LT.FIXED },
    53  : { 'ContentType':'an',    'MaxLen': 14,  'LenType': LT.LLVAR },
    54  : { 'ContentType':'ans',   'MaxLen': 65,  'LenType': LT.LLLVAR},
    55  : { 'ContentType':'b',     'MaxLen': 255, 'LenType': LT.LLLVAR},
    56  : { 'ContentType':'ans',   'MaxLen': 35,  'LenType': LT.LLVAR },
    58  : { 'ContentType':'ans',   'MaxLen': 11,  'LenType': LT.LLVAR },
    59  : { 'ContentType':'ans',   'MaxLen': 147, 'LenType': LT.LLLVAR},
    60  : { 'ContentType':'ans',   'MaxLen': 121, 'LenType': LT.LLLVAR},
    62  : { 'ContentType':'ans',   'MaxLen': 124, 'LenType': LT.LLLVAR},
    63  : { 'ContentType':'ans',   'MaxLen': 200, 'LenType': LT.LLLVAR},
    72  : { 'ContentType':'b',     'MaxLen': 340, 'LenType': LT.LLLVAR},
    74  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    75  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    76  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    77  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    80  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    81  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    82  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    86  : { 'ContentType':'n',     'MaxLen': 16,  'LenType': LT.FIXED },
    87  : { 'ContentType':'n',     'MaxLen': 16,  'LenType': LT.FIXED },
    88  : { 'ContentType':'n',     'MaxLen': 16,  'LenType': LT.FIXED },
    89  : { 'ContentType':'n',     'MaxLen': 16,  'LenType': LT.FIXED },
    90  : { 'ContentType':'n',     'MaxLen': 10,  'LenType': LT.FIXED },
    93  : { 'ContentType':'ans',   'MaxLen': 11,  'LenType': LT.LLVAR },
    94  : { 'ContentType':'ans',   'MaxLen': 11,  'LenType': LT.LLVAR },
    96  : { 'ContentType':'b',     'MaxLen': 19,  'LenType': LT.LLLVAR},
    97  : { 'ContentType':'an',    'MaxLen': 17,  'LenType': LT.FIXED },
    100 : { 'ContentType':'ans',   'MaxLen': 11,  'LenType': LT.LLVAR },
    109 : { 'ContentType':'n',     'MaxLen': 72,  'LenType': LT.LLLVAR},
    110 : { 'ContentType':'n',     'MaxLen': 72,  'LenType': LT.LLLVAR}
}
