#!/usr/bin/env python3
"""
dcu.py
DCU表示ツール
DCUツール(util_cmd_dcu)出力を設定ファイル(dcu.json)に則って表示する。

実行例:
util_cmd_dcu lrt -sep ; -conf ./dcu.json | dcu.py
"""
import sys
import json
import collections

# デフォルト・レイアウト・ファイル名
DCU_JSON_PATH = './conf/dcu.json'
# デフォルト項目セパレータ
DCU_SEPARATOR = ';'
# 有効テーブルID
VALID_TBLS = ['NET', 'LNK', 'TRN', 'LRT', 'SAF', 'CNT', 'CUT', 'SES', 'CFSK', "CNTEX"]
# 処理テーブルID
PROC_TBL = ''
# サイズデフォルト
MAX_SIZE_DEF = 10
# 終了コード
EX_CODE = 0


def read_csv_from_stdin(sep):
    """
    標準入力からDCUﾂｰﾙ出力ﾃﾞｰﾀ(;区切り)を読み取り、辞書にして返す

    Parameters
    ----------
    sep : str
        ｾﾊﾟﾚｰﾀ

    Returns
    -------
    dcu_items : dict
       辞書形式の表示データ
    """
    global PROC_TBL

    items_tmp = sys.stdin.readlines()
    if not items_tmp:
        return {}

    # 改行を消去、ｾﾐｺﾛﾝで分割
    items = [line.strip('\n').split(sep) for line in items_tmp]
    # ヘッダ（要素名）を取込み
    hdr = items[1]
    # ｽﾍﾟｰｽを削除しておく
    field_ids = [f.strip(' ') for f in hdr]

    # 各ﾃﾞｰﾀを辞書化
    dcu_items = collections.OrderedDict({})
    for idx, line in enumerate(items):
        if idx == 0:
            PROC_TBL = line[0]  # ｴｰﾌﾞﾙID保存（先頭行にIDがある前提）
            continue
        elif idx == 1 or idx == 2:  # 読み飛ばし（ﾍｯﾀﾞ、付箋の2行は読み飛ばす）
            continue

        # 1行ずつ保存
        items_wk = []
        for (key, val) in zip(field_ids, line):
            items_wk.append({key: val})
        dcu_items[idx - 3] = items_wk  # ﾘｽﾄのｲﾝﾃﾞｯｸｽ調整（読み飛ばした分）

    return dcu_items


def read_config(tbl_id, cpath):
    """
    処理対象のﾚｲｱｳﾄ情報を辞書にして返信

    Parameters
    ----------
    tbl_id : str
        対象ﾃｰﾌﾞﾙID
    cpath : str
        ｺﾝﾌｨｸﾞﾊﾟｽ

    Returns
    -------
    items : dict
        ﾚｲｱｳﾄﾌｧｲﾙから読込んだﾚｲｱｳﾄ情報
    """
    with open(cpath) as conf:
        conf_info = json.load(conf)

    # 対象ﾃｰﾌﾞﾙの表示仕様を取得
    items = collections.OrderedDict(conf_info.get(tbl_id, {}))

    return items


def dcu_layout(conf_path, sep):
    """
    ﾒｲﾝ処理
    DCUﾂｰﾙのｱｳﾄﾌﾟｯﾄ（;区切り）を読み取り、ﾚｲｱｳﾄﾌｧｲﾙ(dcu.json)に従って
    標準出力に表示する。

    Parameters
    ----------
    conf_path : str
        ｺﾝﾌｨｸﾞﾊﾟｽ
    sep : str
        項目ｾﾊﾟﾚｰﾀ
    """
    global EX_CODE
    # ツール出力を標準入力から読込
    items = read_csv_from_stdin(sep)
    if not items:
        EX_CODE = 1
        return

    # 知らないﾃｰﾌﾞﾙは処理しない
    if PROC_TBL not in VALID_TBLS:
        print('invalid tbl id [{}]'.format(PROC_TBL))
        EX_CODE = 2
        return
    # ﾃｰﾌﾞﾙ名を出力
    print('TBL : {}'.format(PROC_TBL))

    # ｺﾝﾌｨｸﾞを読んで、表示ﾌｨｰﾙﾄﾞ仕様を取得する
    field_names = read_config(PROC_TBL, conf_path)

    # 各要素を表示
    header = False
    for line in items.values():
        # header 表示（初回のみ)
        if header is False:
            for name in field_names.keys():
                fmt = \
                    '{:.'+str(field_names[name].get('size', MAX_SIZE_DEF))+'} '
                val = name.ljust(field_names[name].get('size', MAX_SIZE_DEF))
                print(fmt.format(val), end='')
            print('')  # 改行

            # 付箋
            for name in field_names.keys():
                frame = '-' * field_names[name].get('size', MAX_SIZE_DEF)
                print('{} '.format(frame), end='')
            print('')  # 改行
            header = True
        # 1行表示
        disp_items(line, field_names)


def disp_items(items, my_conf):
    """
    1行表示

    Parameters
    ----------
    items : list
        表示ﾃﾞｰﾀ（1行）
    my_conf: dict
        ﾚｲｱｳﾄ情報
    """
    # 表示対象を抽出
    names = [name for name in my_conf for fn in items if name in fn]
    # 表示
    for name in names:
        # 表示サイズ取得
        fmt = '{:.' + str(my_conf[name].get('size', MAX_SIZE_DEF)) + '} '
        # 表示要素取得
        target = [val.get(name) for val in items if name in val.keys()]
        # リストから文字列へ変換して表示
        disp_value = \
            ''.join(target).ljust(my_conf[name].get('size', MAX_SIZE_DEF))
        print(fmt.format(disp_value), end='')

    print('')  # 改行


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()
    # ｺﾝﾌｨｸﾞﾊﾟｽ
    parser.add_argument('-conf',
        help='Configuration File Path (%(default)s)', default=DCU_JSON_PATH)
    # ｾﾊﾟﾚｰﾀ
    parser.add_argument('-sep',
        help='Separator (%(default)s)', default=DCU_SEPARATOR)

    args = parser.parse_args()

    dcu_layout(args.conf, args.sep)

    sys.exit(EX_CODE)
