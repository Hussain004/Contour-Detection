import cv2
import numpy as np
import time
import robomaster
from robomaster import robot
from math import radians, atan

def detect_object(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_green = np.array([35, 100, 100])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return x, y, w, h, mask
    return None, None, None, None, None


if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    ep_camera = ep_robot.camera
    ep_chassis = ep_robot.chassis
    ep_gripper = ep_robot.gripper
    ep_arm = ep_robot.robotic_arm
    ep_camera.start_video_stream(display=False)

    img = ep_camera.read_cv2_image(strategy="newest", timeout=0.1)

    x, y, w, h, mask = detect_object(img)

    center_x = x
    center_y = y

    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), 2)
    cv2.imshow("Detected Object", img)
    cv2.imshow("Mask", mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    img_width = 1280
    img_height = 720

    camera_fov = 120 
 
    angle = (center_x / img_width) * camera_fov - (camera_fov / 2)
    
    focal_length = 630 
    real_height = 0.225
    distance = (real_height * focal_length) / h

    goal_x = distance * np.cos(radians(angle))
    goal_y = distance * np.sin(radians(angle))

    print(f"Distance: {distance}")
    print (f"x angle: {angle}")
    print (f"x goal: {goal_x} and y goal: {goal_y}")

    ep_chassis.move(x=0, y=0, z=-angle, z_speed=45).wait_for_completed()
    time.sleep(2)
    ep_chassis.move(x=goal_x + 0.1, y=0, z=0, xy_speed=0.8).wait_for_completed()
    time.sleep(2)

    ep_arm.move(x=150, y=0).wait_for_completed()
    time.sleep(1)

    ep_gripper.close(power=60)
    time.sleep(2)

    ep_arm.move(x=-200, y=50).wait_for_completed()
    time.sleep(1)

    ep_chassis.move(x= - goal_x - 0.1, y=0, z=0, xy_speed=0.8).wait_for_completed()
    ep_chassis.move(x=0, y=0, z=angle, z_speed=45).wait_for_completed()

    ep_gripper.open()
    time.sleep(2)

    ep_arm.move(x=50, y=-50).wait_for_completed()
    time.sleep(1)

    ep_gripper.unsub_status()
    ep_camera.stop_video_stream()
    ep_robot.close()
