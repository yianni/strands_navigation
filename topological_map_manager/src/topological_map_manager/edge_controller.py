#!/usr/bin/env python

import sys
import rospy
import math
import tf


from geometry_msgs.msg import Pose
from geometry_msgs.msg import Point

from visualization_msgs.msg import *
from interactive_markers.interactive_marker_server import *

from strands_navigation_msgs.msg import TopologicalNode
from topological_navigation.topological_map import *



class edge_controllers(object):

    def __init__(self, map_name) :
        print "init_controller"
        self.in_feedback=False
        #self.update_needed=False
        self.topo_map = topological_map(map_name)
        self._edge_server = InteractiveMarkerServer(map_name+"_edges")

        for node in self.topo_map.nodes :
            for i in node.edges :
                ind = self.topo_map._get_node_index(i['node'])
                V1=Point()
                V2=Point()
                V1= (node._get_pose()).position
                V2= (self.topo_map.nodes[ind]._get_pose()).position
                edge_name=node.name+"_"+self.topo_map.nodes[ind].name
                self._edge_marker(edge_name, V1, V2, edge_name)        
    
    
    def makeEmptyMarker(self, dummyBox=True ):
        int_marker = InteractiveMarker()
        int_marker.header.frame_id = "/map"
        int_marker.scale = 1
        return int_marker

    def makeBox(self, msg ):
        marker = Marker()
    
        marker.type = Marker.ARROW
        marker.scale.x = msg.scale * 0.45
        marker.scale.y = msg.scale * 0.25
        marker.scale.z = msg.scale * 0.15
        marker.lifetime.secs = 3
        marker.color.r = 0.8
        marker.color.g = 0.1
        marker.color.b = 0.0
        marker.color.a = 1.0
    
        return marker

    def _edge_marker(self, marker_name, point1, point2, marker_description="edge marker") :
        # create an interactive marker for our server
        
        marker = self.makeEmptyMarker()
        marker.name = marker_name
        #marker.description = marker_description

        control = InteractiveMarkerControl()
    
        control.interaction_mode = InteractiveMarkerControl.BUTTON
        control.always_visible = True

        control.markers.append( self.makeBox( marker ) )
        marker.controls.append(control)
    
        self._edge_server.insert(marker, self.feedback_cb)
        self._edge_server.applyChanges()

        pose = Pose()
        
        pose.position.x = (point1.x+point2.x)/2
        pose.position.y = (point1.y+point2.y)/2
        pose.position.z = (point1.z+point2.z)/2
        angle = math.atan2((point2.y-point1.y),(point2.x-point1.x))
        qat = tf.transformations.quaternion_from_euler(0, 0, angle)
        pose.orientation.w = qat[3]
        pose.orientation.x = qat[0]
        pose.orientation.y = qat[1]
        pose.orientation.z = qat[2]

        if pose is not None:
            #pose.position.z=pose.position.z+0.15
            self._edge_server.setPose( marker.name, pose )
            self._edge_server.applyChanges()

       
    def reset_update(self) :
        self.reset_feedback()
        self.update_needed=False
        print "1"

    def reset_feedback(self) :
        self.in_feedback=False
        print "2"

    def feedback_cb(self, feedback):
        print "3"
        if not self.in_feedback and not self.update_needed :
            print "4"
            self.in_feedback=True
            self.topo_map.remove_edge(feedback.marker_name)
            self.update_needed=True
                        
