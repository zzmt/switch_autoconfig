# -*- coding: utf-8 -*-

import paramiko
import time
import re


class SSH(object):

    def __init__(self, device_name, username, password, buffer="65535", delay="1", port="22"):
        self.paramiko = paramiko
        self.time = time
        self.re = re
        self.device_name = device_name
        self.username = username
        self.password = password
        self.buffer = int(buffer)
        self.delay = int(delay)
        self.port = int(port)

    def connect(self):
        res = ''
        self.pre_conn = self.paramiko.SSHClient()
        self.pre_conn.set_missing_host_key_policy(
            self.paramiko.AutoAddPolicy())
        self.pre_conn.connect(self.device_name, username=self.username,
                              password=self.password, allow_agent=False,
                              look_for_keys=False, port=self.port)
        self.client_conn = self.pre_conn.invoke_shell()
        # self.time.sleep(self.delay)
        # return self.client_conn.recv(self.buffer)
        while 1:
            temp = self.client_conn.recv(self.buffer)
            res = res + temp
            if '>' in res or '#' in res or '~' in res:
                break
        return res

    def close(self):
        return self.pre_conn.close()

    def clear_buffer(self):
        if self.client_conn.recv_ready():
            return self.client_conn.recv(self.buffer).decode('utf-8', 'ignore')
        else:
            return None

    def set_enable(self, enable_password):
        if self.re.search('>$', self.command('\n')):
            enable = self.command('enable')
            if self.re.search('Password', enable):
                send_pwd = self.command(enable_password)
                return send_pwd
        elif self.re.search('#$', self.command('\n')):
            return "Action: None. Already in enable mode."
        else:
            return "Error: Unable to determine user privilege status."

    def disable_paging(self, command='term len 0'):
        self.client_conn.sendall(command + "\n")
        self.clear_buffer()

    def command(self, command, delay=1):
        self.client_conn.sendall(command + "\n")
        not_done = True
        output = str()
        res = ''
        while not_done:

            #self.time.sleep(delay)

            print not_done
            if self.client_conn.recv_ready():
                self.time.sleep(delay)
                output += self.client_conn.recv(self.buffer).decode('utf-8')
                print output
            else:
                not_done = False
        return output

    def commands(self, commands_list, delay=2.5):
        output = str()
        if list(commands_list):
            for command in commands_list:
                output += self.command(command, delay)
        else:
            output += self.command(commands_list)
        return output


class HUAWEI(SSH):
    def set_system(self):
        try:
            self.commands('system-view immediately')
        except Exception as e:
            return "config mode is error"

    def set_save(self):
        try:
            cmd = ['return', 'save', 'y']
            self.commands(cmd)
        except Exception as e:
            return "save is error"

    def set_dispage(self):
        try:
            cmd = ['screen-length 0 temporary ']
            self.commands(cmd)
        except Exception as e:
            return "disage is error"


class H3C(SSH):
    def set_system(self):
        try:
            self.commands('system-view')
        except Exception as e:
            return "config mode is error"

    def set_save(self):
        try:
            cmd = ['save force']
            self.commands(cmd)
        except Exception as e:
            return "save is error"

    def set_dispage(self):
        try:
            cmd = ['screen-length disable']
            self.commands(cmd)
        except Exception as e:
            return "disage is error"


class RUIJIE(SSH):

    def set_save(self):
        try:
            cmd = ['end', 'wri']
            self.commands(cmd)
        except Exception as e:
            return "save is error"

    def set_dispage(self):
        try:
            cmd = ['terminal length 0']
            self.commands(cmd)
        except Exception as e:
            return "disage is error"


class MELLANOX(SSH):

    def linux(self):
        pass
