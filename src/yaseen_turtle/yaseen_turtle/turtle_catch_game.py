#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from turtlesim.srv import Spawn,Kill
import random
from functools import partial
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
import math
import time


class SpawnTurtleCatch(Node):
       def __init__(self):
            super().__init__("turtle_catch_game")
            self.get_logger().info("Node has been intialized !!")
            self.numberOfTurtles = 0
            self.numberOfTurtlesInSim = 0
            self.flag = 0
            self.killedKey = 4
            self.Limit = 4
            self.x = 0
            self.prevDistance = 0
            self.y = 9
            self.dictionary = {}
          #  self.spawnTurtleGeneration()
            self.cmd_vel_publisher =  self.create_publisher(Twist,"/turtle1/cmd_vel",10)
            self.pose_subscriber = self.create_subscription(Pose,"/turtle1/pose",self.control_callback,10)




       def control_callback(self,catcherPose : Pose):
            cmd = Twist()
           
            
            if(self.numberOfTurtles != self.Limit):
                self.spawnTurtleGeneration()
            else:
                 if(self.killedKey == 0):
                     self.killedKey = self.Limit
                
                 a = self.dictionary.get(self.killedKey)
                 x2 = a[0]
                 y2 = a[1]
                 
                 theta = math.atan(y2/x2)*180/3.14
                 
                 
                #  if(y2<0 and x2>0):
                #       theta+=360    
                #  elif(y2>0 and x2<0):
                #       theta+=180
                 
                 name = a[3]
                 catcherTheta = (catcherPose.theta*180)/3.14
                 refrenceTHeta = 0    
                 if(x2>catcherPose.x and y2>catcherPose.y):
                      refrenceTHeta = theta
                 elif(x2<catcherPose.x and y2>catcherPose.y):
                      refrenceTHeta = theta+90
                 elif(x2<catcherPose.x and y2<catcherPose.y):
                      refrenceTHeta = theta+180
                 elif(x2<catcherPose.x and y2<catcherPose.y):
                      refrenceTHeta = theta=+270
                
                 
                #  if(catcherPose.y<0 and catcherPose.x>0):
                #       theta+=360    
                #  elif(catcherPose.y>0 and catcherPose.x<0):
                #       theta+=180
                 
                #  if(self.flag == 0):
                #       self.x = catcherPose.x
                #       self.y = catcherPose.y
                #       self.flag = 1
                #     #   self.get_logger().info("theta"+str(theta))
                #     #   self.get_logger().info("turtule theta"+str(catcherPose.theta*180/3.14))
                #       self.prevDistance =  math.sqrt((y2-self.y)*(y2-self.y)+(x2-self.x)*(x2-self.x))
                      
                    
                #  distance = math.sqrt((self.y-catcherPose.y)*(self.y-catcherPose.y)+(self.x-catcherPose.x)*(self.x-catcherPose.x))

                 
                 
                 if(round(catcherTheta)<round(refrenceTHeta)+4 and round(catcherTheta)>round(refrenceTHeta)-5):
                      cmd.linear.x = 1.0
                      cmd.angular.z = 0.0 
                      if(catcherPose.x>x2-1 and catcherPose.x<x2+1 and catcherPose.y>y2-1 and catcherPose.y<y2+1):
                        cmd.linear.x = 0.0
                        cmd.angular.z = 0.0 
                        self.killTurtle(name)

                 
                 else :
                      cmd.linear.x = 0.0
                      cmd.angular.z = 0.5

                 
                 
                 
                      
                    
                 self.cmd_vel_publisher.publish(cmd)    
                #  self.get_logger().info("theta"+str(theta))
                #  self.get_logger().info("turtule theta"+str(catcherPose.theta))
                #  time.sleep(1)
                 

            
                

       def killTurtle(self,turtleName):
            client =  self.create_client(Kill,"/kill")
            while not client.wait_for_service(1.0):
                 self.get_logger().warn("Witing for service")

            request =  Kill.Request()
            request.name = turtleName
            self.dictionary.pop(self.numberOfTurtles)
            self.numberOfTurtles-=1
            self.killedKey-=1
            self.flag = 0

            future = client.call_async(request)  ## return the reply immediately   ## prevent threading and waiting in queue problems

            future.add_done_callback(partial(self.callback_set_pen))

                
       def spawnTurtleGeneration(self):
            client =  self.create_client(Spawn,"/spawn")
            while not client.wait_for_service(1.0):
                 self.get_logger().warn("Witing for service")

            request =  Spawn.Request()
            request.x = random.uniform(1,10)
            request.y = random.uniform(1,10)
            request.theta = random.uniform(0,360)
            theta = math.atan(request.y/request.x)*180/3.14
            if(request.y<0 and request.x>0):
                      theta+=360    
            elif(request.y>0 and request.x<0):
                      theta+=180
        
            self.numberOfTurtles+=1
            self.numberOfTurtlesInSim+=1
            request.name = "turtle_"+str(self.numberOfTurtlesInSim)

            a = [request.x,request.y,request.theta,request.name]

            self.dictionary[self.numberOfTurtles] = a

            future = client.call_async(request)  ## return the reply immediately   ## prevent threading and waiting in queue problems

            future.add_done_callback(partial(self.callback_set_pen))


       def callback_set_pen(self,future):
                try:
                    response = future
                except Exception as e :
                     self.get_logger().error("service call failed !!")
                 
            










def main(args = None):
    rclpy.init(args=args)

    node = SpawnTurtleCatch()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
