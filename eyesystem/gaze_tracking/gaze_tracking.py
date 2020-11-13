from __future__ import division
import os
import cv2
import dlib
import numpy as np
from .eye import Eye
from .calibration import Calibration

landmark = None
x1 = 0
x2 = 0
y1 = 0
y2 = 0

class GazeTracking(object):
    """
    This class tracks the user's gaze.
    It provides useful information like the position of the eyes
    and pupils and allows to know if the eyes are open or closed
    """

    def __init__(self):
        self.frame = None
        self.eye_left = None
        self.eye_right = None
        self.calibration = Calibration()

        # _face_detector is used to detect faces
        self._face_detector = dlib.get_frontal_face_detector()

        # _predictor is used to get facial landmarks of a given face
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)        

    @property
    def pupils_located(self):
        """Check that the pupils have been located"""
        try:
            int(self.eye_left.pupil.x)
            int(self.eye_left.pupil.y)
            int(self.eye_right.pupil.x)
            int(self.eye_right.pupil.y)
            return True
        except Exception:
            return False

    def _analyze(self):
        """Detects the face and initialize Eye objects"""
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)

        try:
            landmarks = self._predictor(frame, faces[0])
            #print(landmarks)
            self.eye_left = Eye(frame, landmarks, 0, self.calibration)
            self.eye_right = Eye(frame, landmarks, 1, self.calibration)

        except IndexError:
            self.eye_left = None
            self.eye_right = None

    def refresh(self, frame):
        """Refreshes the frame and analyzes it.

        Arguments:
            frame (numpy.ndarray): The frame to analyze
        """
        self.frame = frame
        self._analyze()

    def left_origin(self):
        if self.pupils_located:
            x = self.eye_left.origin[0]
            y = self.eye_left.origin[1]
            return (x, y)
        
    def right_origin(self):
        if self.pupils_located:
            x = self.eye_right.origin[0]
            y = self.eye_right.origin[1]
            return (x, y)

    def left_center(self):
        if self.pupils_located:
            x = self.eye_right.origin[0]
            y = self.eye_right.origin[1]
            return (x, y)

    def pupil_left_coords(self):
        """Returns the coordinates of the left pupil"""
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)

    def pupil_right_coords(self):
        """Returns the coordinates of the right pupil"""
        if self.pupils_located:
            x = self.eye_right.origin[0] + self.eye_right.pupil.x
            y = self.eye_right.origin[1] + self.eye_right.pupil.y
            return (x, y)

    def horizontal_ratio(self):
        """Returns a number between 0.0 and 1.0 that indicates the
        horizontal direction of the gaze. The extreme right is 0.0,
        the center is 0.5 and the extreme left is 1.0
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.x / (self.eye_left.center[0] * 2 - 10)
            pupil_right = self.eye_right.pupil.x / (self.eye_right.center[0] * 2 - 10)
            #print(str(self.eye_left.pupil.x) + "  " + str(self.eye_right.pupil.x) + " " + str(self.eye_left.center[0]))
            #print((pupil_left + pupil_right) / 2)
            return (pupil_left + pupil_right) / 2
        else:
            return 0.0
            

    def vertical_ratio(self):
        """Returns a number between 0.0 and 1.0 that indicates the
        vertical direction of the gaze. The extreme top is 0.0,
        the center is 0.5 and the extreme bottom is 1.0
        """
        if self.pupils_located:
            pupil_left = self.eye_left.pupil.y / (self.eye_left.center[1] * 2 - 10)
            pupil_right = self.eye_right.pupil.y / (self.eye_right.center[1] * 2 - 10)
            
            #print("vertical")
            #print(str(self.eye_left.pupil.y) + " " + str(self.eye_left.center[1]))
            #print('%.3f' % ((pupil_left + pupil_right) / 2))
            return (pupil_left + pupil_right) / 2
        else:
            return 0.0

    def vertical_eye(self):
        if self.pupils_located:
            eye_left = self.eye_left.center[1] * 2
            eye_right = self.eye_right.center[1] * 2
            return (eye_left + eye_right) / 2
        else:
            return 0.0
        
    def e_right(self):
        if self.pupils_located:
            return self.eye_right.center[1] * 2
        
    def e_left(self):
        if self.pupils_located:
            return self.eye_right.center[1] * 2

    def pupil_right(self):
        if self.pupils_located:
            return self.eye_right.pupil.y
        
    def pupil_left(self):
        if self.pupils_located:
            return self.eye_left.pupil.y

    def is_right(self, per):
        """Returns true if the user is looking to the right"""
        if self.pupils_located:
            return self.horizontal_ratio() <= per #mom 0.60 原0.55

    def is_left(self, per):
        """Returns true if the user is looking to the left"""
        if self.pupils_located:
            return self.horizontal_ratio() >= per #0.75

    def is_upside(self, per):
        """Returns true if the user is looking to the upside"""
        if self.pupils_located:
            return self.vertical_eye() >= per #0.85

    def is_bottom(self, per):
        """Returns true if the user is looking to the bottom"""
        if self.pupils_located:
            return self.vertical_eye() < per #0.95

    def is_xcenter(self, r_per, l_per):
        """Returns true if the user is looking to the center"""
        if self.pupils_located:
            return self.is_right(r_per) is not True and self.is_left(l_per) is not True
        
    def is_ycenter(self, u_per, b_per):
        """Returns true if the user is looking to the center"""
        if self.pupils_located:
            return self.is_upside(u_per) is not True and self.is_bottom(b_per) is not True

    def is_blinking(self):
        """Returns true if the user closes his eyes"""
        if self.pupils_located:
            blinking_ratio = (self.eye_left.blinking + self.eye_right.blinking) / 2
            return blinking_ratio > 3.8

    def drawFrame(self, frame, x1, x2, y1, y2, color, long):
        cv2.line(frame, (x1, y1), (x1+long, y1), color, 4)
        cv2.line(frame, (x1, y1), (x1, y1+long), color, 4)
        cv2.line(frame, (x2, y1), (x2-long, y1), color, 4)
        cv2.line(frame, (x2, y1), (x2, y1+long), color, 4)
        cv2.line(frame, (x1, y2), (x1+long, y2), color, 4)
        cv2.line(frame, (x1, y2), (x1, y2-long), color, 4)
        cv2.line(frame, (x2, y2), (x2-long, y2), color, 4)
        cv2.line(frame, (x2, y2), (x2, y2-long), color, 4)

    def annotated_frame(self):
        """Returns the main frame with pupils highlighted"""
        frame = self.frame.copy()
        global x1, x2, y1, y2 #因Python傳值不傳址，在這裡的x1,y1會跟Global的x1,y1位址不同，無法一起更動
        

        if self.pupils_located:
            face_rects = self._face_detector(frame, 0)
            for i, d in enumerate(face_rects):
                x1 = d.left()
                y1 = d.top()
                x2 = d.right()
                y2 = d.bottom()
            #cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4, cv2.LINE_AA)
            #cv2.putText(frame, str(int(self.eye_left.center[1])), (30, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
            if (int(self.eye_left.center[1]) < 7):
                self.drawFrame(frame, x1, x2, y1, y2, (0, 0, 255), 30)
                cv2.putText(frame, "You're too far.", (30, 60), cv2.FONT_HERSHEY_DUPLEX, 0.8, (237, 237, 237), 2, cv2.LINE_AA)
                
            elif (int(self.eye_left.center[1]) > 13):
                self.drawFrame(frame, x1, x2, y1, y2, (0, 0, 255), 30)
                cv2.putText(frame, "You're too close.", (30, 60), cv2.FONT_HERSHEY_DUPLEX, 0.8, (237, 237, 237), 2, cv2.LINE_AA)
                
            else:
                self.drawFrame(frame, x1, x2, y1, y2, (0, 255, 0), 20)
            
            
            x_left, y_left = self.pupil_left_coords()
            x_right, y_right = self.pupil_right_coords()
            #cv2.line(frame, (x_left - 2, y_left), (x_left + 2, y_left), color)
            #cv2.line(frame, (x_left, y_left - 2), (x_left, y_left + 2), color)
            #cv2.line(frame, (x_right - 2, y_right), (x_right + 2, y_right), color)
            #cv2.line(frame, (x_right, y_right - 2), (x_right, y_right + 2), color)

        else:
            self.drawFrame(frame, x1, x2, y1, y2, (0, 0, 255), 30)
            cv2.putText(frame, "Can't detect your pupil.", (30, 60), cv2.FONT_HERSHEY_DUPLEX, 0.8, (237, 237, 237), 2, cv2.LINE_AA)

        return frame
