import base64

import cv2
import numpy as np
def generate_profile_image(c1=(16, 108, 179), c2=(10, 201, 175), size = 500):
    img = cv2.imread('templates/Hire tie logo BW.png')
    img = cv2.resize(img, (size, size), cv2.INTER_NEAREST)

    rot_mat = cv2.getRotationMatrix2D((size, size), 40, 1.0)

    ramp_l = np.linspace(1, 0, size*2)
    ramp_l = np.tile(np.transpose(ramp_l), (size*2, 1))
    ramp_l = cv2.merge([ramp_l, ramp_l, ramp_l]) / 255
    ramp_l = cv2.warpAffine(ramp_l, rot_mat, ramp_l.shape[1::-1], flags=cv2.INTER_LINEAR)

    color1 = ramp_l.copy()
    color1[:] = c1[::-1]
    color1 = color1 * ramp_l

    ramp_r = np.linspace(0, 1, size*2)
    ramp_r = np.tile(np.transpose(ramp_r), (size*2, 1))
    ramp_r = cv2.merge([ramp_r, ramp_r, ramp_r]) / 255
    ramp_r = cv2.warpAffine(ramp_r, rot_mat, ramp_r.shape[1::-1], flags=cv2.INTER_LINEAR)

    color2 = ramp_r.copy()
    color2[:] = c2[::-1]
    color2 = color2 * ramp_r

    #Making the image
    bg = 255*(color1 + color2)
    bg = bg[size//2:3*size//2, size//2:3*size//2, :]
    result = cv2.add(bg, img, dtype=cv2.CV_32F)
    #Converting to byte string
    _, buffer = cv2.imencode('.png', result)
    img_str = base64.b64encode(buffer)
    return img_str