#!/usr/bin/env python

import sys
import rospy
import pymongo
import json
import sys
import math


from time import sleep

from threading import Timer
from geometry_msgs.msg import Pose
from geometry_msgs.msg import Point

from ros_datacentre.message_store import MessageStoreProxy

from interactive_markers.interactive_marker_server import *
from interactive_markers.menu_handler import *
from visualization_msgs.msg import *

from strands_navigation_msgs.msg import TopologicalNode
from topological_navigation.topological_map import *
from topological_map_manager.marker_arrays import *
from topological_map_manager.node_controller import *
from topological_map_manager.edge_controller import *
from topological_map_manager.vertex_controller import *


class TopologicalMapVis(object):
    _killall_timers=False

    def __init__(self, name, filename) :

        rospy.on_shutdown(self._on_node_shutdown)

        self.update_needed=False
        self.in_feedback=False
        self._point_set=filename
        self.map_pub = rospy.Publisher('/topological_nodes_array', MarkerArray)
        self.map_zone_pub = rospy.Publisher('/topological_node_zones_array', MarkerArray)
        self.map_edge_pub = rospy.Publisher('/topological_edges_array', MarkerArray)

        self.menu_handler = MenuHandler()
        self._update_everything()
      
        t = Timer(1.0, self.timer_callback)
        t.start()
        rospy.loginfo("All Done ...")
        rospy.spin()


    def _update_everything(self) :
        print "updating ..."
        print "loading file from map %s" %self._point_set
        self.topo_map = topological_map(self._point_set)
        print "Done"
        self.node_cont = waypoint_controllers(self._point_set)
        self.edge_cont = edge_controllers(self._point_set)
        self.vert_cont = vertex_controllers(self._point_set)
        self.wayp_marker = waypoints_markers(self.topo_map)
        self.map_edges = edges_marker(self.topo_map)
        self.node_zone = vertices_marker(self.topo_map)
        self.reset_update()

        
    def _delete_everything(self) :
        print "deleting"
        self.reset_feedback()
        self.reset_update()
        del self.node_cont
        del self.edge_cont
        del self.vert_cont
        del self.map_edges
        del self.wayp_marker
        del self.node_zone
        del self.topo_map
        
        
    def check_feedback(self) :
        self.in_feedback = self.node_cont.in_feedback | self.in_feedback
        self.in_feedback = self.vert_cont.in_feedback | self.in_feedback
        self.in_feedback = self.edge_cont.in_feedback | self.in_feedback


    def check_update(self) :
        self.update_needed = self.node_cont.update_needed | self.update_needed
        self.update_needed = self.vert_cont.update_needed | self.update_needed
        self.update_needed = self.edge_cont.update_needed | self.update_needed
    
    
    def reset_feedback(self) :
        self.in_feedback=False
        self.node_cont.reset_feedback()
        self.vert_cont.reset_feedback()
        self.edge_cont.reset_feedback()


    def reset_update(self) :
        self.update_needed=False
        self.node_cont.reset_update()
        self.vert_cont.reset_update()
        self.edge_cont.reset_update()


    def timer_callback(self):
        self.check_feedback()
        self.check_update()

        #print "F: "+str(self.in_feedback)+" U: "+str(self.update_needed)

        if self.update_needed and not self.in_feedback :
            print "updating ..."
            self._delete_everything()
            self._update_everything()
        else :
            if self.in_feedback :
                self.reset_feedback()
                print "no more feedback ..."
            self.map_pub.publish(self.wayp_marker.map_nodes)
            self.map_edge_pub.publish(self.map_edges.map_edges)
            self.map_zone_pub.publish(self.node_zone.node_zone)
        
        if not self._killall_timers :
            t = Timer(2.0, self.timer_callback)
            t.start()


    def _on_node_shutdown(self):
        self._killall_timers=True
        #sleep(2)


if __name__ == '__main__':
    mapname=str(sys.argv[1])
    rospy.init_node('topological_visualisation')
    server = TopologicalMapVis(rospy.get_name(),mapname)
