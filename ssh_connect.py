#! /usr/bin/python
# -*- coding: utf-8 -*-
# +-------------------------------------------+
# +                                           +
# +                                           +
# +-------------------------------------------+
 
##################
# モジュール読込 #
##################
from __future__ import division  #You don't need this in Python3
import curses
from math import *
import os
import pexpect
import locale
locale.setlocale(locale.LC_ALL, "")
from datetime import datetime
import subprocess
import platform
 
########
# 関数 #
########
 
def ssh_connect(line_no):
    # ターミナルのウィンドウサイズを取得
    curses.setupterm()
    term_lines = int(curses.tigetnum("lines"))
    term_cols  = int(curses.tigetnum("cols"))

    # 接続時に使用する情報を取得
    connect_host_name      = "".join(map(str,host_name_list[line_no]))
    connect_host_ip        = "".join(map(str,host_ip_list[line_no]))
    connect_key_file       = "".join(map(str,key_file_list[line_no]))
    connect_host_root_user = "".join(map(str,host_root_user_list[line_no]))
    connect_host_root_pass = "".join(map(str,host_root_pass_list[line_no]))
    connect_host_user      = "".join(map(str,host_user_list[line_no]))
    connect_host_pass      = "".join(map(str,host_pass_list[line_no]))
    connect_sudo_flag      = "".join(map(str,sudo_flag_list[line_no]))
 
    # 一時ログファイル、正規ログファイル定義
    pid          = str(os.getpid())
    tmp_log      = tmp_dir + '.' + pid + '.' + connect_host_name + '.' + now_time
    terminal_log = log_dir + now_time + '_' + connect_host_name + '.log'
 
    # ログインユーザーの指定有無を確認
    if connect_host_user == "":
        connect_user = connect_host_root_user
        connect_pass = connect_host_root_pass
    else:
        connect_user = connect_host_user
        connect_pass = connect_host_pass
    if connect_key_file == "":
        foo = pexpect.spawn('ssh -o "StrictHostKeyChecking=no" %s@%s' % (connect_user, connect_host_ip))
    else:
        foo = pexpect.spawn('ssh -o "StrictHostKeyChecking=no" -i %s %s@%s' % (connect_key_file, connect_user, connect_host_ip))
    
    # ターミナル画面サイズを修正
    foo.setwinsize(term_lines,term_cols)
    
    # ログの取得開始
    foo.logfile_read = open(tmp_log,"w")
    
    # OSの種類を取得
    os_type = platform.system()
    if os_type == "Darwin":
        log_tail = 'tail -f ' + tmp_log
        log_awk  = 'gawk \'{ print strftime("[%Y/%m/%d %H:%M:%S]") " " $0 } {system (" ")}\' >' + terminal_log
    else:
        log_tail = 'tail -f ' + tmp_log
        log_awk  = 'gawk \'{ print strftime("[%Y/%m/%d %H:%M:%S]") " " $0 } {system (" ")}\' >' + terminal_log

    get_log_command  = log_tail + ' | ' + log_awk + ' &'
    #subprocess.Popen(get_log_command, shell=True)
    os.system(get_log_command)
 
    if not connect_pass == "":
        foo.expect(['.*ssword:','パスワード:'])
        print foo.before.rstrip()
        print foo.after.rstrip()
        foo.sendline(connect_pass)
    if not connect_host_user == "":
        foo.expect(['$','#'])
        print foo.before.strip()
        print foo.after.strip()
        foo.sendline('su - %s' % (connect_host_root_user))
 
        foo.expect(['.*ssword:','パスワード:'])
        print foo.before.strip()
        print foo.after.strip()
        foo.sendline(connect_host_root_pass)
    foo.interact()
    #os.system('kill ' + log_pid + ' &')
    os.system('ps -f| grep [t]ail | grep "' + log_tail + '" | awk \'{ print $2\'} | xargs kill')
    os.remove(tmp_log)
 
############
# 設定関連 #
############
max_row      = 20
list_file    = './data.csv'
command_file = ''
log_dir      = './log/'
tmp_dir      = './tmp/'
now_time     = datetime.now().strftime('%Y%m%d_%H%M%S')
 
##################
# curses関連設定 #
##################
# リスト表示件数
screen        = curses.initscr()
curses.noecho()
curses.cbreak()
curses.start_color()
screen.keypad( 1 )
curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_CYAN)
highlightText = curses.color_pair( 1 )
normalText    = curses.A_NORMAL
screen.border( 0 )
curses.curs_set( 0 )
box           = curses.newwin( max_row + 2, 100, 1, 1 )
box.box()
 
##################
# リスト情報取得 #
##################
f = open(list_file)
line = f.readline()
i = 0
host_name_list      = []
host_ip_list        = []
key_file_list       = []
host_root_user_list = []
host_root_pass_list = []
host_user_list      = []
host_pass_list      = []
sudo_flag_list      = []
while line:
    line = line.strip()
    # コメント・空行を除外
    if line.startswith( "#" ) or len( line ) == 0:
        line = f.readline()
        continue
    # リストの各要素を取得
    line_column = len( line.split(',') )
    if line_column == 5:
        host_name      = line.split(',')[0]
        host_ip        = line.split(',')[1]
        key_file       = line.split(',')[2]
        host_root_user = line.split(',')[3]
        host_root_pass = line.split(',')[4]
        host_user      = ""
        host_pass      = ""
        sudo_flag      = ""
    elif line_column == 7:
        host_name      = line.split(',')[0]
        host_ip        = line.split(',')[1]
        key_file       = line.split(',')[2]
        host_root_user = line.split(',')[3]
        host_root_pass = line.split(',')[4]
        host_user      = line.split(',')[5]
        host_pass      = line.split(',')[6]
        sudo_flag      = ""
    elif line_column == 8:
        host_name      = line.split(',')[0]
        host_ip        = line.split(',')[1]
        key_file       = line.split(',')[2]
        host_root_user = line.split(',')[3]
        host_root_pass = line.split(',')[4]
        host_user      = line.split(',')[5]
        host_pass      = line.split(',')[6]
        sudo_flag      = line.split(',')[7]
    else:
        curses.endwin()
        print "リストに誤りがあります。"
        print line
        exit(1)
    host_name_list      += [[host_name]]
    host_ip_list        += [[host_ip]]
    key_file_list       += [[key_file]]
    host_root_user_list += [[host_root_user]]
    host_root_pass_list += [[host_root_pass]]
    host_user_list      += [[host_user]]
    host_pass_list      += [[host_pass]]
    sudo_flag_list      += [[sudo_flag]]
    line = f.readline()
f.close
row_num = len( host_name_list )
 
##############
# リスト表示 #
##############
pages = int( ceil( row_num / max_row ) )
position = 1
page = 1
for i in range( 1, max_row + 1 ):
    if row_num == 0:
        box.addstr( 1, 1, "There aren't host_name_list", highlightText )
    else:
        if (i == position):
            box.addstr( i, 2, str( i ) + " - " + "".join(map(str,host_name_list[ i - 1 ])), highlightText )
        else:
            box.addstr( i, 2, str( i ) + " - " + "".join(map(str,host_name_list[ i - 1 ])), normalText )
        if i == row_num:
            break
screen.refresh()
box.refresh()
 
##########################
# ホスト選択画面キー操作 #
##########################
x = screen.getch()
while x != 27:
 
    # 下キー押下時の動作
    if x == curses.KEY_DOWN:
        if page == 1:
            if position < i:
                 position = position + 1
            else:
                 if pages > 1:
                    page = page + 1
                    position = 1 + ( max_row * ( page - 1 ) )
        elif page == pages:
            if position < row_num:
                position = position + 1
        else:
            if position < max_row + ( max_row * ( page - 1 ) ):
                 position = position + 1
            else:
                 page = page + 1
                 position = 1 + ( max_row * ( page - 1 ) )
    # 上キー押下時の動作
    if x == curses.KEY_UP:
        if page == 1:
            if position > 1:
                position = position - 1
        else:
            if position > ( 1 + ( max_row * ( page - 1 ) ) ):
                position = position - 1
            else:
                page = page - 1
                position = max_row + ( max_row * ( page - 1 ) )
 
    # 左キー押下時の動作
    if x == curses.KEY_LEFT:
        if page > 1:
            page = page - 1
            position = 1 + ( max_row * ( page - 1 ) )
 
    # 右キー押下時の動作
    if x == curses.KEY_RIGHT:
        if page < pages:
            page = page + 1
            position = ( 1 + ( max_row * ( page - 1 ) ) )
 
    # Enter押下時(決定)の処理
    if x == ord( "\n" ) and row_num != 0:
        screen.erase()
        screen.border( 0 )
 
        curses.endwin()
        ssh_connect(position - 1)
        exit()
 
    box.erase()
    screen.border( 0 )
    box.border( 0 )
 
    for i in range( 1 + ( max_row * ( page - 1 ) ), max_row + 1 + ( max_row * ( page - 1 ) ) ):
        if row_num == 0:
            box.addstr( 1, 1, "There aren't host_name_list",  highlightText )
        else:
            if ( i + ( max_row * ( page - 1 ) ) == position + ( max_row * ( page - 1 ) ) ):
                box.addstr( i - ( max_row * ( page - 1 ) ), 2, str( i ) + " - " + "".join(map(str,host_name_list[ i - 1 ])), highlightText )
            else:
                box.addstr( i - ( max_row * ( page - 1 ) ), 2, str( i ) + " - " + "".join(map(str,host_name_list[ i - 1 ])), normalText )
            if i == row_num:
                break
 
    screen.refresh()
    box.refresh()
    x = screen.getch()
 
curses.endwin()
exit()
