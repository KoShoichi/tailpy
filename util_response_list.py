#!/usr/bin/env python3
"""
util_response_list.py
レスポンス測定ツール
"""
import os
import sys
from datetime import datetime, timedelta
from influxdb import InfluxDBClient

# 最大表示幅（列数）
MAX_LINES = 10

NANO2SEC = 1e9
NANO2MSEC = 1e6
ONE_HR = 60  # 60 mins
NOT_USED = -1


def count_rec(val, hhmm_lines):
    """
    該当レンジのカウントアップ

    Parameters
    ----------
    val         レスポンス時間
    hhmm_lines  レンジ情報

    Returns
    -------

    """
    for idx in range(MAX_LINES):
        if hhmm_lines['ranges'][idx]['f'] <= val < hhmm_lines['ranges'][idx]['t']:
            hhmm_lines['ranges'][idx]['ct'] += 1
            hhmm_lines['ct_all'] += 1
            break
    else:
        if val != NOT_USED:
            hhmm_lines['over']['ct'] += 1
            hhmm_lines['ct_all'] += 1  # overも数える


def group_query_result(prms, iolog):
    """
    クエリー結果(iolog)を時間帯毎(HHMM)にグループ化

    Parameters
    ----------
    prms    起動パラメータ
    iolog   IOログ（クエリー結果）

    Returns
    -------
    hhmmでグループ化したクエリ結果データ(辞書)
    """
    hhmm_lines = {}
    for ifx in iolog:
        l = ifx.split(',')  # 'name,tags,time,reqSendTime,reqRecvTime,repSendTime,repRecvTime'
        d = datetime.fromtimestamp(int(l[2]) / NANO2SEC)  # timestamp in sec
        # 時間単位集計の分パートは、00
        if prms.interval_time == 'H' or prms.interval_time == 'h':
            hhmm = d.hour * 100  # HH
        else:
            hhmm = d.hour * 100  # HH
            hhmm += d.minute  # MM

        val = calc_response(prms, l)  # レスポンス時間を計算
        if hhmm in hhmm_lines:  # <- 既存レンジに追加
            hhmm_lines[hhmm]['sum'] += val if val != NOT_USED else 0
            count_rec(val, hhmm_lines[hhmm])  # レンジへカウント
        else:  # <- レンジがなければ新規に作成、各種初期化
            hhmm_lines[hhmm] = {}
            hhmm_lines[hhmm]['sum'] = val if val != NOT_USED else 0  # 平均値計算のため合算バッファ
            hhmm_lines[hhmm]['ct_all'] = 0  # 総件数
            hhmm_lines[hhmm]['ranges'] = [None] * MAX_LINES  # レンジ毎の情報バッファ
            in_range = False

            for idx in range(MAX_LINES):  # レンジ初期化
                hhmm_lines[hhmm]['ranges'][idx] = \
                    {'f': 0 if idx == 0 else hhmm_lines[hhmm]['ranges'][idx - 1]['t'],
                     't': (prms.min_response + (prms.interval_response * idx)) * 10 * NANO2MSEC, 'ct': 0}
                # 該当すればカウントアップ
                if hhmm_lines[hhmm]['ranges'][idx]['f'] <= val < hhmm_lines[hhmm]['ranges'][idx]['t'] \
                        and val != -1 and in_range is False:
                    hhmm_lines[hhmm]['ranges'][idx]['ct'] += 1
                    hhmm_lines[hhmm]['ct_all'] += 1
                    in_range = True

            hhmm_lines[hhmm]['over'] = {'ct': 0}  # レンジ外件数初期化

            if val != NOT_USED and in_range is False:
                hhmm_lines[hhmm]['over']['ct'] += 1  # overに数える
                hhmm_lines[hhmm]['ct_all'] += 1

    return hhmm_lines


def print_iolog(prms, iolog):
    """
    レスポンス情報の表示

    Parameters
    ----------
    prms    起動パラメータ
    iolog   IOログ（クエリー結果）

    Returns
    -------

    """
    p_lines = group_query_result(prms, iolog)
    if len(p_lines) == 0:
        print("no data")
        return

    avg_ct = 0
    ########
    # 表示 #
    #####################################################################################
    # ヘッダ #
    #####################################################################################
    print('TIME,AVERAGE', end='')
    for idx in range(MAX_LINES):  # レスポンスレンジを表示
        for t_line in p_lines.values():
            print(",-{:.2f}".format(t_line['ranges'][idx]['t'] / NANO2SEC), end='')  # in sec
            break
    print(',OVER,ALL')

    #####################################################################################
    # 各種件数 #
    #####################################################################################
    hhmm_prev = int(prms.start_time)  # 開始時間を初期値として設定
    # 表示時間帯間隔(分で設定)
    hhmm_interval = ONE_HR if prms.interval_time == 'H' or prms.interval_time == 'h' else 1
    ##########################################################################
    # 開始時間(-start_time)から最初のデータ時間帯まで"空き"がある場合は、空データ行を表示
    ##########################################################################
    first_range = next(iter(p_lines))  # データが現れる最初の時間帯
    start_time = int(int(prms.start_time) / 100)  # in hhmm
    if first_range - start_time > 0 and prms.interval_time is not None:
        disp_void_lines(start_time, first_range, hhmm_interval, MAX_LINES)  # 空データ行を表示

    total_time = 0      # 全レコードレスポンスタイムの合算値
    total_rec_ct = 0    # 全レコード数
    total_avg = float(0)  # 平均値の合算値
    total_ct = 0  # 有効データ行のカウント
    hhmm = 0
    for hhmm, item in p_lines.items():
        if prms.interval_time is None:  # 未指定時は個々の表示なし
            total_avg = sum([each_val['sum'] for each_val in p_lines.values()])  # 縦のレスポンスタイムの合算
            total_ct = sum([each_val['ct_all'] for each_val in p_lines.values()])  # 縦の件数の合算
            break

        # TOTAL行用の合算
        total_time += item['sum']   # new
        total_rec_ct += item['ct_all']
        total_avg += (item['sum'] / item['ct_all']) if item['ct_all'] else 0
        total_ct += 1 if item['ct_all'] else 0

        ##################################################
        # 次表示時間帯までの間が空く場合は、空行を時間帯ごとに表示 #
        ##################################################
        if hhmm_prev:
            disp_void_lines(hhmm_prev, hhmm, hhmm_interval, MAX_LINES)

        #############
        # 通常行の表示
        #############
        # HH:MM,平均値を表示
        print("{:02}:{:02},{:f}".format(int(hhmm / 100),
                                        int(hhmm % 100),
                                        float(item['sum']) / item['ct_all'] / NANO2MSEC if item['ct_all'] else 0),
              end='')  # in msec
        # レンジ毎の件数表示
        for idx, t_line in enumerate(item['ranges']):
            print(",{}".format(t_line['ct']), end='')
        # over, all表示
        print(",{},{}".format(item['over']['ct'], item['ct_all']))
        # 次時間帯計算
        hhmm_prev = hhmm + hhmm_interval

    ###################################################################
    # データを含む時間帯から終了時間(end_time)までギャップがある場合は、空行を表示
    ###################################################################
    if prms.interval_time is not None:
        end_range = next(iter(p_lines))
        end_time = int(int(prms.end_time) / 100)  # HHMM
        if end_time - end_range > 0:
            disp_void_lines(
                # 100 = 1hr
                hhmm + 100 if prms.interval_time == 'H' or prms.interval_time == 'h' else hhmm + hhmm_interval,
                end_time,
                hhmm_interval,
                MAX_LINES)

    #####################################################################################
    # フッタ(TOTAL) #
    #####################################################################################
    ct_rangeX = [0] * MAX_LINES  # 縦の合算カウンタ
    ct_over = 0  # OVERの総数
    for val in p_lines.values():
        avg_ct += val['ct_all']
        # 各レンジごとの合計件数
        for idx in range(len(val['ranges'])):
            ct_rangeX[idx] += val['ranges'][idx]['ct']
        ct_over += val['over']['ct']

    # トータル情報 #
    avg_ct = sum([val['ct_all'] for val in p_lines.values()])  # 縦の件数の合計

    ###
    # 1行サマリ表示(-interval_time未指定時のみ) #
    ###
    if prms.interval_time is None:  # 全行の合算を1行表示
        start_time = int(prms.start_time)
        print("{:02}:{:02},{:f}".format(int(start_time / 10000),
                                        int(start_time % 10000),
                                        (float(total_avg) / total_ct / NANO2MSEC) if avg_ct else 0),
              end='')
        # レンジごとの縦合計表示
        for idx in range(MAX_LINES):
            print(",{}".format(ct_rangeX[idx]), end='')
        # over, all
        print(",{},{}".format(ct_over, sum(ct_rangeX) + ct_over))
    ###
    # TOTAL行
    ###
    if prms.interval_time is None:  # 1行サマリ表示(-interval_time未指定時のみ) #
        print("TOTAL,{:f}".format((total_avg / total_ct / NANO2MSEC) if total_ct else 0), end='')
    else: # -interval_time指定時 #
        print("TOTAL,{:f}".format((total_time / total_rec_ct / NANO2MSEC) if total_rec_ct else 0), end='')

    # レンジごとの縦合計表示
    for idx in range(MAX_LINES):
        print(",{}".format(ct_rangeX[idx]), end='')

    # over, all
    print(",{},{}".format(ct_over, avg_ct))


def disp_void_lines(hhmm1, hhmm2, interval, max_lines):
    """
    空行の表示（取引データがない時間帯を各値0で表示)

    Parameters
    ----------
    hhmm1       表示時間
    hhmm2       次表示自時間
    interval    時間間隔(分）
    max_lines   表示レンジ数

    Returns
    -------

    """
    # 空行表示要否チェック
    void_lines = int(calc_hhmm_delta(hhmm1, hhmm2) / ONE_HR) if interval == ONE_HR else int(
        calc_hhmm_delta(hhmm1, hhmm2))

    for idx in range(void_lines):
        gap_in_sec = \
            timedelta(hours=int(hhmm1 / 100),
                      minutes=int(hhmm1 % 100) + interval * idx).total_seconds()
        # HH:MM
        h = int(gap_in_sec / 3600)
        print("{:02}:{:02},{}".format(h if h <= 24 else 0, int(gap_in_sec % 3600 / ONE_HR), 0), end='')
        # Values
        for i in range(max_lines):
            print(",{}".format(0), end='')
        # over, all
        print(",{},{}".format(0, 0))


def calc_hhmm_delta(hhmm1, hhmm2):
    """
    時間差(hhmm2 - hhmm1)を分で計算

    Parameters
    ----------
    hhmm1   from時間
    hhmm2   to時間

    Returns
    -------
    時間差（分)
    """
    d1 = timedelta(hours=int(hhmm1 / 100), minutes=int(hhmm1 % 100))
    d2 = timedelta(hours=int(hhmm2 / 100), minutes=int(hhmm2 % 100))
    return int((d2.total_seconds() - d1.total_seconds()) / ONE_HR)


def calc_response(prms, rec):
    """
    レスポンス時間の計算
    ①パススルー取引　  (repSendTime - reqRecvTime) - (repRecvTime - reqSendTime)　但し、左記4値が0でないレコード
    ②折り返し取引     (repSendTime - reqRecvTime)　但し、reqSendTime,repRecvTime == 0のレコード

    Parameters
    ----------
    prms 起動パラメータ
    rec 計算対象レコード

    Returns
    -------
    レスポンス時間
    -1 未使用レコード
    """
    reqSendT = int(rec[3]) if rec[3] else 0  # reqSendTime 仕向要求送信時刻(Outgoing REQ Timestamp)
    reqRecvT = int(rec[4]) if rec[4] else 0  # reqRecvTime 被仕向要求受信時刻(Incoming REQ Timestamp)
    repSendT = int(rec[5]) if rec[5] else 0  # repSendTime 被仕向応答送信時刻(Incoming REP Timestamp)
    repRecvT = int(rec[6]) if rec[6] else 0  # repRecvTime 仕向応答受信時刻(Outgoing REP Timestamp)
    # パススルー取引
    if reqSendT and reqRecvT and repSendT and repRecvT and prms.path_through:
        return (repSendT - reqRecvT) - (repRecvT - reqSendT)
    # 折り返し取引
    elif repSendT and reqRecvT and not reqSendT and not repRecvT and prms.turn:
        return repSendT - reqRecvT

    # 計算対象外
    return NOT_USED


def ifx_query(prms):
    """
    起動パラメータでクエリーを実行

    Parameters
    ----------
    prms    起動パラメータ

    Returns
    -------
    IOログ（クエリー結果）
    """
    host = os.environ.get('INFLUX_HOST')
    port = os.environ.get('INFLUX_PORT')
    db = os.environ.get('INFLUX_DATABASE')
    user = os.environ.get('INFLUX_USERNAME')
    password = os.environ.get('INFLUX_PASSWORD')
    if host is None:
        print("INFLUX_HOST Not Found")
        exit(1)
    if port is None:
        print("INFLUX_PORT Not Found")
        exit(1)
    if db is None:
        print("INFLUX_DATABASE Not Found")
        exit(1)
    if user is None:
        print("INFLUX_USERNAME Not Found")
        exit(1)
    if password is None:
        print("INFLUX_PASSWORD Not Found")
        exit(1)

    # IfxDbクライアントオブジェクト
    client = InfluxDBClient(host, port, user, password, db)

    # クエリー作成
    query = 'select reqSendTime,reqRecvTime,repSendTime,repRecvTime from '
    query += prms.log_name
    # 開始時間
    start_time = datetime(year=int(prms.log_date[0:4]),
                          month=int(prms.log_date[4:6]),
                          day=int(prms.log_date[6:8]),
                          hour=int(prms.start_time[0:2]),
                          minute=int(prms.start_time[2:4]),
                          second=int(prms.start_time[4:6]))
    start_time = str(start_time.timestamp())[:10] + prms.start_time[7:].ljust(9, '0')
    # 終了時間
    if prms.end_time == '240000':
        # 翌0時とする
        current_date = datetime(year=int(prms.log_date[0:4]),
                                month=int(prms.log_date[4:6]),
                                day=int(prms.log_date[6:8]))
        end_time = current_date + timedelta(days=1)
    else:
        end_time = datetime(year=int(prms.log_date[0:4]),
                            month=int(prms.log_date[4:6]),
                            day=int(prms.log_date[6:8]),
                            hour=int(prms.end_time[0:2]),
                            minute=int(prms.end_time[2:4]),
                            second=int(prms.end_time[4:6]))
    end_time = str(end_time.timestamp())[:10] + prms.end_time[7:].ljust(9, '0')

    query += " WHERE time >= {} and time < {} and extCommType = 'Outgoing'".format(start_time, end_time)
    # タイムゾーン
    query += " tz('Asia/Tokyo')"

    # クエリー実行
    iolog = client.request('query',
                           headers={"Accept": "application/csv"},
                           params={"q": query, "db": db, "epoch": "ns", "precision": "rfc3339"})
    client.close()

    return iolog.text.splitlines()[1:]  # ヘッダ削除


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser(description='### iolog response list generator ###')
    # 集計対象のI/O ﾛｸﾞを指定する。
    parser.add_argument('log_name',
                        help='Name of I/O Log (ex. cfslog)', type=str)
    # 集計対象ﾛｸﾞの日付を指定する。
    parser.add_argument('-log_date',
                        help='Target Date(YYYYMMDD) (%(default)s)', default=format(datetime.today(), '%Y%m%d'),
                        type=str)
    # 集計対象ﾛｸﾞの開始時間を指定する。
    parser.add_argument('-start_time',
                        help='Start Time(hhmmss) (%(default)s)', default='000000', type=str)
    # 集計対象ﾛｸﾞの終了時間を指定する。
    parser.add_argument('-end_time',
                        help='End Time(hhmmss) (%(default)s)', default='240000', type=str)
    # 出力時間単位を指定する。h(時間単位), m(分単位)
    parser.add_argument('-interval_time',
                        help='Interval Time(h or m) (%(default)s)', type=str)
    # 出力の最小ﾚｽﾎﾟﾝｽ値を指定する。
    parser.add_argument('-min_response',
                        help='response unit of time in 10ms (%(default)d)', type=int, default=50)
    # 出力のｲﾝﾀｰﾊﾞﾙを指定する。
    parser.add_argument('-interval_response',
                        help='interval unit of time in 10ms (%(default)d)', default=50, type=int)
    # ﾊﾟｽｽﾙｰの取引を処理対象とする。
    parser.add_argument('-path_through',
                        help='count path-through transactions (%(default)d)', default=1, type=int)
    # 折り返しの取引を処理対象とする。
    parser.add_argument('-turn',
                        help='count turn back transactions (%(default)d)', default=1, type=int)
    args = parser.parse_args()

    # パラメータチェック
    if args.log_date.isdecimal() is False or len(args.log_date) != len('YYYYMMDD'):
        print('invalid parameter {}'.format(args.log_date))
        sys.exit(1)
    if args.start_time.isdecimal() is False or len(args.start_time) != len('HHMMSS'):
        print('invalid parameter {}'.format(args.start_time))
        sys.exit(1)
    if args.end_time.isdecimal() is False or len(args.end_time) != len('HHMMSS'):
        print('invalid parameter {}'.format(args.end_time))
        sys.exit(1)

    try:
        print('querying...')
        iolog = ifx_query(args)
        if iolog:
            print('aggregating {} items.'.format(len(iolog)))
            print_iolog(args, iolog)
        else:
            print('no data')
    except:
        import traceback

        print(traceback.format_exc())
        sys.exit(1)

    sys.exit(0)
