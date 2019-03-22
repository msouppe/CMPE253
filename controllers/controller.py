# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu import cfg

from threading import Timer

from threading import Timer

import ryu.app.ofctl.api as ofctl_api
import os
import time
import subprocess
import threading
from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayParameters
import json

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def send_role_request(self):       
        print "***********************************************************"
        print "Changing Master Controller to c"+str(self.controller_id)
        print "Listening on port "+ str(self.listen_port)
        DATA = self.convert_keys_to_string(json.loads(self.gateway.entry_point.getnib()))
        self.mac_to_port = DATA
        for i in range(1, 21):
            stri = 's'+str(i)
            os.popen('ovs-vsctl set-controller ' + stri + ' tcp:127.0.0.1:'+str(self.listen_port))

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        #print("CALLING START----------------------------")
        CONF = cfg.CONF
        CONF.register_opts([cfg.IntOpt('paramid_int')])
        CONF.register_opts([cfg.IntOpt('listen_port_int')])
        CONF.register_opts([cfg.IntOpt('client_port')])
        #print "---------------------> " + str(CONF.paramid_int)
        #print "---------------------> " + str(CONF.listen_port_int)
        #print "---------------------> " + str(CONF.client_port) 
        self.controller_id = CONF.paramid_int
        self.listen_port = CONF.listen_port_int
        self.client_port = CONF.client_port
        gateway_param = GatewayParameters(port=self.client_port)
        self.gateway = JavaGateway(gateway_parameters=gateway_param)
        thread_var = threading.Event()
        self.prev_leader = -1
        self.leader_election(thread_var,self.controller_id)
        

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP or eth.ethertype == ether_types.ETH_TYPE_IPV6:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(str(dpid), {})
        # self.logger.info("CALLED EVENT")
        # self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
        
        #STEP 1---------------------------------------------
        if not src in self.mac_to_port[str(dpid)]:
            self.logger.info("Adding to dictionary...")
            self.mac_to_port[str(dpid)][str(src)] = in_port
            self.btf_commit(self.mac_to_port)
            out_port = ofproto.OFPP_FLOOD
            actions = [parser.OFPActionOutput(out_port)]
        else:
            if self.mac_to_port[str(dpid)][str(src)] != in_port:
                # self.logger.info("In ELSE IF....")
                out_port = -1;
                actions = []
            else:
                # self.logger.info("In ELSE-ELSE....")
                out_port = ofproto.OFPP_FLOOD
                actions = [parser.OFPActionOutput(out_port)]
        #---------------------------------------------------
        # self.logger.info("----------------------------------------------")
        # self.logger.info(str(self.mac_to_port))
        # self.logger.info("----------------------------------------------")


        #----------------------------------------------------
        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)


    def leader_election(self, thread_var, server_id):
        #print("Calling Leader Election protocol:")
        ts = long(time.time())
        #print("Sending ID: ",server_id," timestamp: ", ts)
        leader_id = self.gateway.entry_point.leaderElect(server_id, ts)
        #print("LEADER :::",leader_id)
        print("Leader election of ID", self.controller_id)
        print("SELF NIB\n",self.mac_to_port)
        if int(leader_id) == server_id:
            if(self.prev_leader != leader_id):
                self.prev_leader = leader_id
                self.send_role_request()
                print("RECIEVED MAC TO PORT:",self.mac_to_port)
            else:
                pass

        threading.Timer(0.8, self.leader_election, [thread_var, server_id]).start()
    
    def btf_commit(self, nib):
        #print("Performing BFT commit::::::::::::::::::::::::::::::")
        #print(self.gateway.entry_point.BFTCommit(json.dumps(nib)))
        self.gateway.entry_point.BFTCommit(json.dumps(nib))

    def convert_keys_to_string(self, dictionary):
        """Recursively converts dictionary keys to strings."""
        if not isinstance(dictionary, dict):
            return dictionary
        return dict((str(k), self.convert_keys_to_string(v)) 
            for k, v in dictionary.items())