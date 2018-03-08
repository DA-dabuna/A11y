from __future__ import print_function

import time

import caffe
import cv2
import dlib
import matplotlib.pyplot as plt
import numpy as np
import pyautogui
from scipy.spatial import distance as dist
from PyQt5 import QtCore, QtGui, QtWidgets
from speech_to_text.database import QueueModel
from speech_to_text.database import db
import os

from blink_detect import blink

CUDA = True
step = 30  # pixels per step TODO Adjust according to device DPI
duration = 0.1  # mouse movement duration

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def load_img():
    global lc_png, rc_png, d_png, u_png, l_png, r_png
    lc_png = QtGui.QPixmap('img/lc.png')
    rc_png = QtGui.QPixmap('img/rc.png')
    d_png = QtGui.QPixmap('img/d.png')
    u_png = QtGui.QPixmap('img/u.png')
    l_png = QtGui.QPixmap('img/l.png')
    r_png = QtGui.QPixmap('img/r.png')


def mouse_control(face_point, head_pose, w):
    if not head_pose.any():
        png = QtGui.QPixmap('img/m.png')
        w.img.setPixmap(png)
        return
    # for a in [w.left, w.right, w.up, w.down]:
    #    a.setVisible(False)

    db.connect()
    if not os.path.exists(os.path.join(BASEDIR, 'lock.db')) or True:
        db.create_tables([QueueModel])
        k = QueueModel.pop()
        if k == 'l':
            w.img.setPixmap(lc_png)
        elif k == 'r':
            w.img.setPixmap(rc_png)
    db.close()

    # determine pitch for up & down
    print('pose pitch ' + str(head_pose[0, 0]))
    # TODO laptop screen angle adjustment
    if 0 < head_pose[0, 0] < 30:
        pyautogui.moveRel(0, step, duration=duration)
        # w.down.setVisible(True)
        w.img.setPixmap(d_png)
    if -30 < head_pose[0, 0] < -20:
        pyautogui.moveRel(0, -step, duration=duration)
        # w.up.setVisible(True)
        w.img.setPixmap(u_png)

    # determine yaw for left & right
    print('pose yaw ' + str(head_pose[0, 1]))
    if 10 < head_pose[0, 1] < 30:
        pyautogui.moveRel(-step, 0, duration=duration)
        # w.left.setVisible(True)
        w.img.setPixmap(l_png)
    if -30 < head_pose[0, 1] < -10:
        pyautogui.moveRel(step, 0, duration=duration)
        # w.right.setVisible(True)
        w.img.setPixmap(r_png)


pointNum = 68
vgg_height = 224
vgg_width = 224
M_left = -0.15
M_right = +1.15
M_top = -0.10
M_bottom = +1.25
pose_names = ['Pitch', 'Yaw', 'Roll']  # respect to  ['head down','out of plane left','in plane right']


def show_image(img, face_points, boxes, head_pose):
    plt.clf()
    for faceNum in range(0, face_points.shape[0]):
        cv2.rectangle(img, (int(boxes[faceNum, 0]), int(boxes[faceNum, 2])),
                      (int(boxes[faceNum, 1]), int(boxes[faceNum, 3])), (0, 0, 255), 2)
        for p in range(0, 3):
            plt.text(int(boxes[faceNum, 0]), int(boxes[faceNum, 2]) - p * 30,
                     '{:s} {:.2f}'.format(pose_names[p], head_pose[faceNum, p]),
                     bbox=dict(facecolor='blue', alpha=0.5), fontsize=12, color='white')
        for i in range(0, int(face_points.shape[1] / 2)):
            # points defined at https://ibug.doc.ic.ac.uk/resources/facial-point-annotations/
            key_points = [37, 38, 40, 41,  # left eye
                          43, 44, 46, 47,  # right eye
                          61, 62, 63, 65, 66, 67  # mouth
                          ]
            color = (255, 0, 0) if i in key_points else (0, 255, 0)
            cv2.circle(img, (int(round(face_points[faceNum, i * 2])), int(round(face_points[faceNum, i * 2 + 1]))), 1,
                       color, 2)
    img = img[:, :, [2, 1, 0]]
    plt.imshow(img)
    plt.draw()
    plt.pause(0.001)


def recover_coordinate(largest_box, face_point, width, height):
    point = np.zeros(np.shape(face_point))
    cut_width = largest_box[1] - largest_box[0]
    cut_height = largest_box[3] - largest_box[2]
    scale_x = cut_width * 1.0 / width
    scale_y = cut_height * 1.0 / height
    point[0::2] = [float(j * scale_x + largest_box[0]) for j in face_point[0::2]]
    point[1::2] = [float(j * scale_y + largest_box[2]) for j in face_point[1::2]]
    return point


def recover_part(point, box, left, right, top, bottom, img_height, img_width, height, width):
    large_box = get_cut_size(box, left, right, top, bottom)
    large_box = rectify_box_size(img_height, img_width, large_box)
    recover = recover_coordinate(large_box, point, height, width)
    return recover.astype('float32')


def get_rgb_test_part(box, left, right, top, bottom, img, height, width):
    large_box = get_cut_size(box, left, right, top, bottom)
    large_box = rectify_box(img, large_box)
    face = img[int(large_box[2]):int(large_box[3]), int(large_box[0]):int(large_box[1]), :]
    face = cv2.resize(face, (height, width), interpolation=cv2.INTER_AREA)
    return face.astype('float32')


def batch_recover_part(predict_point, total_box, total_size, left, right, top, bottom, height, width):
    recover_point = np.zeros(predict_point.shape)
    for i in range(0, predict_point.shape[0]):
        recover_point[i] = recover_part(predict_point[i], total_box[i], left, right, top, bottom, total_size[i, 0],
                                        total_size[i, 1], height, width)
    return recover_point


def rectify_box(img, box):
    img_height = np.shape(img)[0] - 1
    img_width = np.shape(img)[1] - 1
    return rectify_box_size(img_height, img_width, box)


def rectify_box_size(img_height, img_width, box):
    if box[0] < 0:
        box[0] = 0
    if box[1] < 0:
        box[1] = 0
    if box[2] < 0:
        box[2] = 0
    if box[3] < 0:
        box[3] = 0
    if box[0] > img_width:
        box[0] = img_width
    if box[1] > img_width:
        box[1] = img_width
    if box[2] > img_height:
        box[2] = img_height
    if box[3] > img_height:
        box[3] = img_height
    return box


def get_cut_size(box, left, right, top, bottom):
    box_width = box[1] - box[0]
    box_height = box[3] - box[2]
    cut_size = np.zeros((4))
    cut_size[0] = box[0] + left * box_width
    cut_size[1] = box[1] + (right - 1) * box_width
    cut_size[2] = box[2] + top * box_height
    cut_size[3] = box[3] + (bottom - 1) * box_height
    return cut_size


def detect_face(detector, img):
    r = detector(img, 1)
    boxes = np.zeros((len(r), 4))
    for i, d in enumerate(r):
        boxes[i, 0] = d.left()
        boxes[i, 1] = d.right()
        boxes[i, 2] = d.top()
        boxes[i, 3] = d.bottom()
    return boxes


def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # compute the euclidean distance between the horizontal eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])
    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    # return the eye aspect ratio
    return ear


def start_recognition(w):
    detector = dlib.get_frontal_face_detector()
    predictor_blink = dlib.shape_predictor('model/shape_predictor_68_face_landmarks.dat')

    vgg_point_proto = 'model/deploy.prototxt'
    vgg_point_model = 'model/68point_dlib_with_pose.caffemodel'
    mean_filename = 'model/VGG_mean.binaryproto'
    vgg_point_net = caffe.Net(vgg_point_proto, vgg_point_model, caffe.TEST)
    if CUDA:
        caffe.set_mode_gpu()
        caffe.set_device(0)
    else:
        caffe.set_mode_cpu()
    proto_data = open(mean_filename, "rb").read()
    a = caffe.io.caffe_pb2.BlobProto.FromString(proto_data)
    mean = caffe.io.blobproto_to_array(a)[0]

    plt.ion()
    plt.figure(num=1, figsize=(8, 4))
    plt.show()

    blink_counter, blink_total = 0, 0

    load_img()

    index = 0
    vc = cv2.VideoCapture(0)
    if vc.isOpened():  # try to get the first frame
        ret, frame = vc.read()
    else:
        ret = False
    while ret:
        print(index)
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (256, 192))

        t = time.time()
        boxes = detect_face(detector, frame)
        print('face used ' + str(time.time() - t) + 's')
        t = time.time()

        face_num = boxes.shape[0]
        faces = np.zeros((1, 3, vgg_height, vgg_width))
        predict_points = np.zeros((face_num, pointNum * 2))
        head_pose = np.zeros((face_num, 3))
        image_size = np.zeros((2))
        image_size[0] = frame.shape[0] - 1
        image_size[1] = frame.shape[1] - 1
        total_size = np.zeros((face_num, 2))
        for i in range(0, face_num):
            total_size[i] = image_size
        for i in range(0, face_num):
            box = boxes[i]
            color_face = get_rgb_test_part(box, M_left, M_right, M_top, M_bottom, frame, vgg_height, vgg_width)
            normal_face = np.zeros(mean.shape)
            normal_face[0] = color_face[:, :, 0]
            normal_face[1] = color_face[:, :, 1]
            normal_face[2] = color_face[:, :, 2]
            normal_face = normal_face - mean
            faces[0] = normal_face

            blob_name = '68point'
            inputs = np.zeros([faces.shape[0], 1, 1, 1])
            vgg_point_net.set_input_arrays(faces.astype(np.float32), inputs.astype(np.float32))
            vgg_point_net.forward()
            predict_points[i] = vgg_point_net.blobs[blob_name].data[0]

            blob_name = 'poselayer'
            pose_prediction = vgg_point_net.blobs[blob_name].data
            head_pose[i] = pose_prediction * 50

        predict_points = predict_points * vgg_height / 2 + vgg_width / 2
        face_points = batch_recover_part(predict_points, boxes, total_size, M_left, M_right, M_top, M_bottom,
                                         vgg_height, vgg_width)

        print('points used ' + str(time.time() - t) + 's')
        t = time.time()

        # blink_counter, blink_total = blink(detector, predictor_blink, frame, blink_counter, blink_total)
        # print('blink used ' + str(time.time() - t) + 's')

        show_image(frame, face_points, boxes, head_pose)
        mouse_control(face_points, head_pose, w)
        index = index + 1
        ret, frame = vc.read()
