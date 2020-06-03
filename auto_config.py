# -*- coding: utf-8 -*-

import re

from sw_config import H3C
from sw_config import HUAWEI
from sw_config import RUIJIE
import time

class cmd_config(object):
    def __init__(self, ip, username, password, netdev_manuf):
        self.ip = ip
        self.username = username
        self.password = password

        self.netdev_manuf = netdev_manuf

    def config_cmd(self, cmd_str):
        #通用交换机配置命令下发方法
        cmd = cmd_str.split(',')
        if 'HUAWEI' in self.netdev_manuf:
            huawei = HUAWEI(self.ip, self.username, self.password)
            huawei.connect()
            output = huawei.commands(cmd)
            huawei.close()
        if "H3C" in self.netdev_manuf:
            h3c = H3C(self.ip, self.username, self.password)
            h3c.connect()
            output = h3c.commands(cmd)
            h3c.close()
        if "Ruijie" in self.netdev_manuf or "RUIJIE" in self.netdev_manuf:
            ruijie = RUIJIE(self.ip, self.username, self.password)
            ruijie.connect()
            output = ruijie.commands(cmd)
            ruijie.close()
        return output

    def Recover_bgp_peer(self, remote_ip, bgp):
        #通用DCI及外网回滚方法，可适用ospf 和 bgp场景,remote_ip为list

        cmd_huawei = 'system-view immediately, bgp {bgp}'.format(bgp=bgp)
        cmd_h3c = 'system-view, bgp {bgp}'.format(bgp=bgp)
        cmd_ruijie = 'conf t , router bgp {bgp}'.format(bgp=bgp)

        for i in remote_ip:

            if 'HUAWEI' in self.netdev_manuf:
                tmp_cmd = 'undo peer {remote_ip} ignore'.format(remote_ip=i)
                cmd_huawei = cmd_huawei + ',' + tmp_cmd
            if 'H3C' in self.netdev_manuf:
                tmp_cmd = 'undo peer {remote_ip} ignore'.format(remote_ip=i)
                cmd_h3c = cmd_h3c + ',' + tmp_cmd
            if "Ruijie" in self.netdev_manuf or "RUIJIE" in self.netdev_manuf:
                tmp_cmd = 'no neighbor {remote_ip} shutdown'.format(remote_ip=i)
                cmd_ruijie = cmd_ruijie + ',' + tmp_cmd
        cmd_dict = {'HUAWEI': cmd_huawei, 'H3C': cmd_h3c, 'RUIJIE': cmd_ruijie}
        return cmd_dict

    def Get_ospf_cost(self,local_port):
        #local_port为list
        ospf_list = []
        ospf_dict ={}
        re_cost = ur'cost\s(.*?)\s'
        cost = '0'

        if 'HUAWEI' in self.netdev_manuf:
            huawei = HUAWEI(self.ip, self.username, self.password)
            huawei.connect()

            for port in local_port:
                try:
                    HUAWEI_cmd = 'dis cu int {local_port}'.format(local_port=port)
                    output = huawei.commands([HUAWEI_cmd])

                    tmp = re.search(re_cost, output)
                    cost = tmp.groups()[0]
                    ospf_dict[port] = cost
                except Exception as e:
                    ospf_dict[port] = cost
            huawei.close()
        if "H3C" in self.netdev_manuf:
            h3c = H3C(self.ip, self.username, self.password)
            h3c.connect()
            for port in local_port:
                try:
                    H3C_cmd = 'dis cu int {local_port}'.format(local_port=port)
                    output = h3c.commands([H3C_cmd])
                    tmp = re.search(re_cost, output)
                    cost = tmp.groups()[0]
                    ospf_dict[port] = cost
                except Exception as e:
                    ospf_dict[port] = cost
            h3c.close()

        if "Ruijie" in self.netdev_manuf or "RUIJIE" in self.netdev_manuf:
            ruijie = RUIJIE(self.ip, self.username, self.password)
            ruijie.connect()
            for port in local_port:
                try:
                    RUIJIE_cmd = 'show running-config int {local_port}'.format(local_port=port)
                    output = ruijie.commands([RUIJIE_cmd])
                    tmp = re.search(re_cost, output)
                    ospf_dict[port] = cost
                except Exception as e:
                    ospf_dict[port] = cost
            ruijie.close()

        return ospf_dict

    #查看路由下一跳，返回到目标ip的所有端口的list
    def show_ip_next_interface(self,dip_list):
        #通用交换机查看路由下一跳出接口方法，返回list
        temp_list = []
        port_list = []
        nhp_port_list = []
        nhp_port_dict = {}
        try:
            if 'HUAWEI' in self.netdev_manuf:
                huawei = HUAWEI(self.ip, self.username, self.password)
                huawei.connect()
                huawei.commands(['screen-length 0 temporary'])
                for dip in dip_list:

                    try:
                        output = huawei.commands(['dis ip ro '+dip+' verbose'])
                        temp_out = output.split('Destination')
                        temp_out.pop(0)

                        for i in temp_out:
                                temp_str = " ".join(i.split())
                                temp_list.append(temp_str)
                        for i in temp_list:
                                hw_pattern = ur'Interface:\s(.*?)\s'
                                re_obj = re.search(hw_pattern, i)
                                port = re_obj.groups()[0]
                                port_list.append(port)
                        nhp_port_list = list(set(port_list))
                    finally:
                        nhp_port_dict[dip] = nhp_port_list
                huawei.close()
            if "H3C" in self.netdev_manuf:
                h3c = H3C(self.ip, self.username, self.password)
                h3c.connect()
                h3c.commands(['screen-length disable'])
                for dip in dip_list:
                    try:
                        output = h3c.commands(['dis ip ro '+dip+' verbose'])
                        temp_out = output.split('Destination')
                        temp_out.pop(0)

                        for i in temp_out:
                                temp_str = " ".join(i.split())
                                temp_list.append(temp_str)
                        for i in temp_list:
                                hw_pattern = ur'Interface:\s(.*?)\s'
                                re_obj = re.search(hw_pattern, i)
                                port = re_obj.groups()[0]
                                port_list.append(port)
                        nhp_port_list = list(set(port_list))
                    finally:
                        nhp_port_dict[dip] = nhp_port_list
                h3c.close()

            if "Ruijie" in self.netdev_manuf or "RUIJIE" in self.netdev_manuf:
                ruijie = RUIJIE(self.ip, self.username, self.password)
                ruijie.connect()
                ruijie.commands(['terminal length 0'])
                for dip in dip_list:
                    try:

                        output = ruijie.commands(['show ip ro '+dip])
                        temp_out = output.split('\r')
                        for i in temp_out:
                            if 'via' in i:
                                    temp_list.append(i)
                        for i in temp_list:
                            hw_pattern = ur'via\s(.*?),'
                            re_obj = re.search(hw_pattern, i)
                            port = re_obj.groups()[0]
                            port_list.append(port)
                        nhp_port_list = list(set(port_list))
                    finally:
                        nhp_port_dict[dip] = nhp_port_list
                ruijie.close()
        except Exception as e:
            return nhp_port_dict

        return nhp_port_dict

    def show_interface_status(self,local_port):
        #local_port为list返回端口状态up\down\*down
        port_list = []
        port_dict ={}

        try:
            if 'HUAWEI' in self.netdev_manuf:

                huawei = HUAWEI(self.ip, self.username, self.password)
                huawei.connect()

                try:

                    for port in local_port:
                        output = huawei.commands(['dis int brie | in '+port])
                        temp_list = output.split('\n')
                        temp = temp_list.pop(-2)
                        temp_str = " ".join(temp.split())
                        status = temp_str.split(' ')[1]
                        port_dict[port] = status.lower()
                finally:
                    huawei.close()
            if "H3C" in self.netdev_manuf:
                h3c = H3C(self.ip, self.username, self.password)
                h3c.connect()

                try:
                    for port in local_port:
                        output = h3c.commands(['dis int  '+port+'  brief'])
                        temp_list = output.split('\n')
                        temp = temp_list.pop(-2)
                        temp_str = " ".join(temp.split())
                        status = temp_str.split(' ')[1]
                        port_dict[port] = status.lower()
                finally:
                    h3c.close()

            if "Ruijie" in self.netdev_manuf or "RUIJIE" in self.netdev_manuf:
                ruijie = RUIJIE(self.ip, self.username, self.password)
                ruijie.connect()
                try:
                    for port in local_port:
                        output = ruijie.commands(['show interface status | in '+port])
                        temp_list = output.split('\n')
                        temp = temp_list.pop(-2)
                        temp_str = " ".join(temp.split())
                        status = temp_str.split(' ')[2]
                        port_dict[port] = status.lower()
                finally:
                    ruijie.close()

        finally:

            return port_dict

    def Isolate_bgp_cmd(self, remote_ip,  bgp):
        #通用交换机流量隔离方法,remote_ip为list
        #返回三家厂商的回退命令rollback_cmd，隔离命令isolate_cmd，格式均如下：
        #{
        #        'HUAWEI': HUAWEI_cmd,
        #        'H3C': H3C_cmd,
        #        'RUIJIE': RUIJIE_cmd,
        #        'Ruijie': RUIJIE_cmd
        #    }
        #
        cmd_huawei= 'system-view immediately, bgp {bgp}'.format(bgp = bgp)
        cmd_h3c = 'system-view, bgp {bgp}'.format(bgp=bgp)
        cmd_ruijie = 'conf t , router bgp {bgp}'.format(bgp=bgp)

        for i in remote_ip:

            if 'HUAWEI' in self.netdev_manuf:
                tmp_cmd = 'peer {remote_ip} ignore'.format(remote_ip = i)
                cmd_huawei = cmd_huawei + ',' + tmp_cmd
            if 'H3C' in self.netdev_manuf:
                tmp_cmd = 'peer {remote_ip} ignore'.format(remote_ip = i)
                cmd_h3c = cmd_h3c + ',' + tmp_cmd
            if "Ruijie" in self.netdev_manuf or "RUIJIE" in self.netdev_manuf:
                tmp_cmd = 'neighbor {remote_ip} shutdown'.format(remote_ip = i)
                cmd_ruijie = cmd_ruijie + ',' + tmp_cmd
        cmd_dict = {'HUAWEI': cmd_huawei, 'H3C': cmd_h3c, 'RUIJIE': cmd_ruijie}
        return cmd_dict


    def Isolate_DCI_ospf_cmd(self, ospf_cost_dict):

        HUAWEI_cmd = 'system-view immediately'
        H3C_cmd = 'system-view'
        ruijie_cmd = 'conf t'
        for port, cost in ospf_cost_dict.items():


            isolate_cost = int(cost)*100
            if isolate_cost > 65535:
                isolate_cost = int(cost)*10
            isolate_cost = str(isolate_cost)
            if 'HUAWEI' in self.netdev_manuf:
                tmp_cmd = 'int {port},ospf cost {isolate_cost}'.format(port=port,isolate_cost=isolate_cost)
                HUAWEI_cmd = HUAWEI_cmd+','+tmp_cmd
            if 'H3C' in self.netdev_manuf:
                tmp_cmd = 'int {port},ospf cost {isolate_cost}'.format(port=port,isolate_cost=isolate_cost)
                H3C_cmd = H3C_cmd+tmp_cmd
            if "Ruijie" in self.netdev_manuf or "RUIJIE" in self.netdev_manuf:
                tmp_cmd = 'int {port},ip ospf cost {isolate_cost}'.format(port=port,isolate_cost=isolate_cost)
                ruijie_cmd = ruijie_cmd+tmp_cmd

        isolate_cmd  = {'HUAWEI': HUAWEI_cmd,'H3C': H3C_cmd,'RUIJIE': ruijie_cmd}

        return isolate_cmd

    def Recover_DCI_ospf_cmd(self, ospf_cost_dict):

        HUAWEI_cmd = 'system-view immediately'
        H3C_cmd = 'system-view'
        ruijie_cmd = 'conf t'
        for port, cost in ospf_cost_dict.items():

            if 'HUAWEI' in self.netdev_manuf:
                tmp_cmd = 'int {port},ospf cost {cost}'.format(port=port, cost=cost)
                HUAWEI_cmd = HUAWEI_cmd + ',' + tmp_cmd
            if 'H3C' in self.netdev_manuf:
                tmp_cmd = 'int {port},ospf cost {cost}'.format(port=port, cost=cost)
                H3C_cmd = H3C_cmd + tmp_cmd
            if "Ruijie" in self.netdev_manuf or "RUIJIE" in self.netdev_manuf:
                tmp_cmd = 'int {port},ip ospf cost {cost}'.format(port=port, cost=cost)
                ruijie_cmd = ruijie_cmd + tmp_cmd

        isolate_cmd = {'HUAWEI': HUAWEI_cmd, 'H3C': H3C_cmd, 'RUIJIE': ruijie_cmd}

        return isolate_cmd

    def operate_interface_cmd(self,port,action,ruijie_action):
        #port为list，返回各个厂商的cmd字典
        cmd_huawei= 'system-view immediately'
        cmd_h3c = 'system-view'
        cmd_ruijie = 'conf t'
        for i in port:
            if 'HUAWEI' in self.netdev_manuf:
                tmp_cmd = 'int {port} , {action}'.format(port = i,action = action)
                cmd_huawei  = cmd_huawei+','+tmp_cmd
            if 'H3C' in self.netdev_manuf:
                tmp_cmd = 'int {port} , {action}'.format(port = i,action = action)
                cmd_h3c  = cmd_h3c+','+tmp_cmd
            if "Ruijie" in self.netdev_manuf or "RUIJIE" in self.netdev_manuf:
                tmp_cmd = 'int {port} , {action}'.format(port = i, action=ruijie_action)
                cmd_ruijie = cmd_ruijie+','+tmp_cmd
        cmd_dict = {'HUAWEI': cmd_huawei, 'H3C': cmd_h3c, 'RUIJIE': cmd_ruijie}
        return cmd_dict

    def show_BGP_Peer_Status(self,peer_ip_list):

        peer_status = {}

        try :
            if 'HUAWEI' in self.netdev_manuf:
                huawei = HUAWEI(self.ip, self.username, self.password)
                huawei.connect()
                huawei.commands(['screen-length 0 temporary'])
                for peer_ip in peer_ip_list:
                    status = ''
                    try:
                        cmds = 'dis bgp peer  {peer_ip} verbose'.format(peer_ip = peer_ip)
                        output = huawei.commands(cmds.split(','))
                        tmp_str = output.split('\r')
                        for i in tmp_str:
                            if 'BGP current state' in i:
                                hw_pattern = ur'BGP current state:\s(.*?),'
                                re_obj = re.search(hw_pattern, i)
                                status = re_obj.groups()[0].lower()
                    finally:
                        peer_status[peer_ip] = status

        finally:
            return peer_status



class network_workflow_cmd(object):
    def BGP_Isolate_workflow_cmd(self,BGP_Peer,BGP_traffic_port):
        #BGP_Peer={'POP1':{'sw_ip':'','bgp_peer_ip':[''],'dev_man':'','bgp_as':''},'POP2':{'sw_ip':'','bgp_peer_ip':[''],'dev_man':'','bgp_as':''}}
        #BGP_traffic_port = {'POP1':['port1','port2'],'POP2':['port1','port2']}
        sw_pop1 = BGP_Peer.get('POP1').get('sw_ip')
        sw_pop2 = BGP_Peer.get('POP2').get('sw_ip')

        dev_pop1_man = BGP_Peer.get('POP1').get('dev_man')
        dev_pop2_man = BGP_Peer.get('POP2').get('dev_man')

        dev_pop1_bgp_as =  BGP_Peer.get('POP1').get('bgp_as')
        dev_pop2_bgp_as = BGP_Peer.get('POP2').get('bgp_as')

        bgp_peer_ip_pop1 = BGP_Peer.get('POP1').get('bgp_peer_ip')
        bgp_peer_ip_pop2 = BGP_Peer.get('POP2').get('bgp_peer_ip')

        dev_pop1_bgp_traffic_port = BGP_traffic_port.get('POP1')
        dev_pop2_bgp_traffic_port = BGP_traffic_port.get('POP2')

        dev_pop1_config = cmd_config(sw_pop1,'sankuai','Netadmin00@mt',dev_pop1_man)
        dev_pop2_config = cmd_config(sw_pop2,'sankuai','Netadmin00@mt',dev_pop2_man)

        #ignore bgp邻居命令
        dev_pop1_Isolate_bgp_cmd = dev_pop1_config.Isolate_bgp_cmd(bgp_peer_ip_pop1,dev_pop1_bgp_as).get(dev_pop1_man)
        dev_pop2_Isolate_bgp_cmd = dev_pop2_config.Isolate_bgp_cmd(bgp_peer_ip_pop2,dev_pop2_bgp_as).get(dev_pop2_man)

        #关闭bgp 流量端口命令
        dev_pop1_shutdown_traffic_port_cmd = dev_pop1_config.operate_interface_cmd(dev_pop1_bgp_traffic_port,'shutdown','shutdown').get(dev_pop1_man)
        dev_pop2_shutdown_traffic_port_cmd = dev_pop2_config.operate_interface_cmd(dev_pop2_bgp_traffic_port,'shutdown','shutdown').get(dev_pop2_man)

        """
        #下配置
        dev_pop1_config.config_cmd(dev_pop1_Isolate_bgp_cmd)
        dev_pop2_config.config_cmd(dev_pop2_Isolate_bgp_cmd)
        # 下配置
        dev_pop1_config.config_cmd(dev_pop1_shutdown_traffic_port_cmd)
        dev_pop2_config.config_cmd(dev_pop2_shutdown_traffic_port_cmd)
        """

        #恢复命令
        dev_pop1_recover_bgp_peer_cmd = dev_pop1_config.Recover_bgp_peer(bgp_peer_ip_pop1,dev_pop1_bgp_as).get(dev_pop1_man)
        dev_pop2_recover_bgp_peer_cmd = dev_pop2_config.Recover_bgp_peer(bgp_peer_ip_pop2,dev_pop2_bgp_as).get(dev_pop2_man)
        dev_pop1_open_traffic_port_cmd = dev_pop1_config.operate_interface_cmd(dev_pop1_bgp_traffic_port,'undo shutdown','no shutdown').get(dev_pop1_man)
        dev_pop2_open_traffic_port_cmd = dev_pop2_config.operate_interface_cmd(dev_pop2_bgp_traffic_port,'undo shutdown','no shutdown').get(dev_pop2_man)

        return  {'BGP_Peer_Isolate':{sw_pop1:dev_pop1_Isolate_bgp_cmd,sw_pop2:dev_pop2_Isolate_bgp_cmd},\
                 'Traffic_port_shutdown':{sw_pop1:dev_pop1_shutdown_traffic_port_cmd,sw_pop2:dev_pop2_shutdown_traffic_port_cmd},\
                 'BGP_Peer_Recover':{sw_pop1:dev_pop1_recover_bgp_peer_cmd,sw_pop2:dev_pop2_recover_bgp_peer_cmd},\
                 'Traffic_port_Recover':{sw_pop1:dev_pop1_open_traffic_port_cmd,sw_pop2:dev_pop2_open_traffic_port_cmd}}


    def OSPF_Isolate_workflow_cmd(self,port_list,sw_info):
        #sw_info= {'sw_ip':'','dev_man':''}
        dev_config = cmd_config(sw_info.get('sw_ip'),'sankuai','Netadmin00@mt',sw_info.get('dev_man'))

        ospf_cost_dict_recover = dev_config.Get_ospf_cost(port_list)
        dev_Isolate_ospf_cmd = dev_config.Isolate_DCI_ospf_cmd(ospf_cost_dict_recover)
        dev_Recover_ospf_cmd = dev_config.Recover_DCI_ospf_cmd(ospf_cost_dict_recover)
        return {'DCI_Isolate_ospf_cmd':dev_Isolate_ospf_cmd,'DCI_Recover_ospf_cmd':dev_Recover_ospf_cmd}

    def Show_Ip_Next_Interface(self,dip_list,sw_info):
        dev_config = cmd_config(sw_info.get('sw_ip'), 'sankuai', 'Netadmin00@mt', sw_info.get('dev_man'))
        result = dev_config.show_ip_next_interface(dip_list)
        return  result

    def Show_Interface_Status(self,port_list,sw_info):
        dev_config = cmd_config(sw_info.get('sw_ip'), 'sankuai', 'Netadmin00@mt', sw_info.get('dev_man'))
        result = dev_config.show_interface_status(port_list)
        return  result

    def Show_Bgp_Peer_Status(self,peer_list,sw_info):
        dev_config = cmd_config(sw_info.get('sw_ip'), 'sankuai', 'Netadmin00@mt', sw_info.get('dev_man'))
        result = dev_config.show_BGP_Peer_Status(peer_list)
        return  result

    def Shutdown_Interface_cmd(self,portlist,sw_info):
        dev_config = cmd_config(sw_info.get('sw_ip'), 'sankuai', 'Netadmin00@mt', sw_info.get('dev_man'))

        cmd  = dev_config.operate_interface_cmd(portlist, 'shutdown', 'shutdown')
        return cmd

    def Up_Interface_cmd(self,portlist,sw_info):
        dev_config = cmd_config(sw_info.get('sw_ip'), 'sankuai', 'Netadmin00@mt', sw_info.get('dev_man'))
        cmd  = dev_config.operate_interface_cmd(portlist, 'undo shutdown', 'no shutdown')
        return cmd


if __name__ == '__main__':

    BGP_info = {'POP1': {'sw_ip': '1.1.1.1', 'bgp_peer_ip': ['10.10.10.10','3.3.3.3'], 'dev_man': 'HUAWEI', 'bgp_as': '12345'},
                'POP2': {'sw_ip': '2.2.2.2', 'bgp_peer_ip': ['20.20.20.20'], 'dev_man': 'HUAWEI', 'bgp_as': '67899'}}

    BGP_traffic_port = {'POP1':['100GE1/0/1','100GE1/0/2'],'POP2':['100GE2/0/1','100GE2/0/2']}
    sw_info = {'sw_ip':"10.21.1.32",'dev_man':'H3C'}

    a = network_workflow_cmd()
    b = a.BGP_Isolate_workflow_cmd(BGP_info,BGP_traffic_port)
    c = a.OSPF_Isolate_workflow_cmd(['FGE1/0/49','FGE1/0/51','FGE2/0/49 '],sw_info)

    print a.Up_Interface_cmd(['1/0/1'],sw_info)

