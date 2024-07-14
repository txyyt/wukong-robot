# -*- coding: utf-8 -*-

import os
import subprocess
import time
import cv2
from robot import config, constants, logging
from robot.sdk.AbstractPlugin import AbstractPlugin

logger = logging.getLogger(__name__)

class Plugin(AbstractPlugin):

    SLUG = "camera"

    def handle(self, text, parsed):
        quality = config.get("/camera/quality", 100)
        count_down = config.get("/camera/count_down", 3)
        dest_path = config.get("/camera/dest_path", os.path.expanduser("~/pictures"))
        vertical_flip = config.get("/camera/vetical_flip", False)
        horizontal_flip = config.get("/camera/horizontal_flip", False)
        sound = config.get("/camera/sound", True)
        camera_type = config.get("/camera/type", 0)
        if config.has("/camera/usb_camera") and config.get("/camera/usb_camera"):
            camera_type = 0
        if any(word in text for word in ["安静", "偷偷", "悄悄"]):
            sound = False
        try:
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
        except Exception:
            self.say("抱歉，照片目录创建失败", cache=True)
            return
        dest_file = os.path.join(dest_path, "%s.jpg" % time.time()).replace(".", "", 1)
        if camera_type == 0:
            # usb camera
            logger.info("usb camera")
            command = ["fswebcam", "--no-banner", "-r", "1024x765", "-q", "-d", "/dev/video0"]
            if vertical_flip:
                command.extend(["-s", "v"])
            if horizontal_flip:
                command.extend(["-s", "h"])
            command.append(dest_file)
        elif camera_type == 1:
            # Raspberry Pi 5MP
            logger.info("Raspberry Pi 5MP camera")
            command = ["raspistill", "-o", dest_file, "-q", str(quality)]
            if count_down > 0 and sound:
                command.extend(["-t", str(count_down * 1000)])
            if vertical_flip:
                command.append("-vf")
            if horizontal_flip:
                command.append("-hf")
        elif camera_type == 2:
            # notebook camera
            logger.info("notebook camera")
            command = ["imagesnap", dest_file]
            if count_down > 0 and sound:
                command.extend(["-w", str(count_down)])
        elif camera_type == 4:
            # Windows notebook camera using OpenCV
            logger.info("Windows notebook camera")
            # if sound and count_down > 0:
            #     self.say("收到，%d秒后启动拍照" % (count_down), cache=True)
            #     time.sleep(count_down)
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if vertical_flip:
                frame = cv2.flip(frame, 0)
            if horizontal_flip:
                frame = cv2.flip(frame, 1)
            cv2.imwrite(dest_file, frame)
            cap.release()
        else:
            self.say("不支持的摄像头类型", cache=True)
            return

        # if sound and count_down > 0:
        #     self.say("收到，%d秒后启动拍照" % (count_down), cache=True)
        #     # if camera_type in [0, 2]:
        #     #     time.sleep(count_down)
        #     time.sleep(count_down)

        try:
            if camera_type in [0, 1, 2]:
                subprocess.run(command, shell=False, check=True)
            if sound:
                self.play(constants.getData("camera.wav"))
                photo_url = "http://{}:{}/photo/{}".format(
                    config.get("/server/host"),
                    config.get("/server/port"),
                    os.path.basename(dest_file),
                )
                self.say("拍照成功", cache=True)
                self.say(photo_url)
        except subprocess.CalledProcessError as e:
            logger.error(e, stack_info=True)
            if sound:
                self.say("拍照失败，请检查相机是否连接正确", cache=True)

    def isValid(self, text, parsed):
        return any(word in text for word in ["拍照", "拍张照"]) and not any(
            word in text for word in ["拍照成功", "拍照失败", "后启动拍照"]
        )
