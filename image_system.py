from detect_modules.detect_human import detect_human

from detect_modules.detect_sex import detect_sex

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from std_msgs.msg import String
from sensor_msgs.msg import Image

from cv_bridge import CvBridge


class ImageSystem(Node):
    def __init__(self):
        super(ImageSystem, self).__init__('ImageSystem')

        self.senses_publisher = self.create_publisher(String, 'Cerebrum/Command', qos_profile_sensor_data)
        self.create_subscription(String, '/image_system/command', self.command_callback, qos_profile_sensor_data)
        self.create_subscription(Image, '/camera/color/image_raw', self.get_image, qos_profile_sensor_data)
        self.message = None
        self.command = None
        self._trans_message = String()

        self.bridge = CvBridge()

    def command_callback(self, msg):
        if self.one_time_execute(msg.data, self.command):

            # contain command data
            self.command = msg.data

            # Command:speak , Content:hello!
            command = msg.data.split(',')

            if 'human' == command[0].replace('Command:', ''):
                self.message = self.detect_human()
                self.cerebrum_publisher('Return:1,Content:'+self.message)
            if 'sex' == command[0].replace('Command:', ''):
                self.message = self.detect_sex()
                self.cerebrum_publisher('Return:1,Content:'+self.message)
            if 'object' == command[0].replace('Command:', ''):
                self.detect_object()


    # detect number's human
    def detect_human(self):
        number = detect_human(self.image)
        return number


    # detect human sex
    def detect_sex(self):
        woman, man = detect_sex(self.image)
        return woman + '|' + man


    # [FUTURE] detect object with YOLO, SSD, R-DAD 
    def detect_object(self):
        # [TODO] sonouti yaru!
        print('[*] detect object')

    
    # send data to cerebrum
    def cerebrum_publisher(self, message):

        self._trans_message.data = message
        self.senses_publisher.publish(self._trans_message)


    # get image from realsense
    def get_image(self, msg):
        self.image = self.bridge.imgmsg_to_cv2(msg)


    # only one time execute
    def one_time_execute(self, now, previous):
        flag = False

        if now != previous:
            flag = True

        return flag


def main():
    rclpy.init()
    node = ImageSystem()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
