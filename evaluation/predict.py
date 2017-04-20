from lipnet.lipreading.videos import Video
from lipnet.lipreading.visualization import show_video_subtitle
from lipnet.core.decoders import decode_batch_beam as decode_batch
from lipnet.lipreading.helpers import alphabets
from lipnet.model import LipNet
from keras.optimizers import Adam
from keras import backend as K
import numpy as np
import sys
import os

np.random.seed(55)

def predict(weight_path, video_path, absolute_max_string_len=32, output_size=28):
    print "\nLoading data from disk..."
    dir_path = os.path.dirname(os.path.realpath(__file__))
    face_predictor_path = os.path.join(dir_path,'models','shape_predictor_68_face_landmarks.dat')
    video = Video(vtype='face', face_predictor_path=face_predictor_path)
    if os.path.isfile(video_path):
        video.from_video(video_path)
    else:
        video.from_frames(video_path)
    print "Data loaded.\n"

    if K.image_data_format() == 'channels_first':
        img_c, frames_n, img_w, img_h = video.data.shape
    else:
        frames_n, img_w, img_h, img_c = video.data.shape


    lipnet = LipNet(img_c=img_c, img_w=img_w, img_h=img_h, frames_n=frames_n,
                    absolute_max_string_len=absolute_max_string_len, output_size=output_size)

    adam = Adam(lr=0.0001, beta_1=0.9, beta_2=0.999, epsilon=1e-08)

    lipnet.model.compile(loss={'ctc': lambda y_true, y_pred: y_pred}, optimizer=adam)
    lipnet.model.load_weights(weight_path)

    X_data = np.array([video.data]).astype(np.float32) / 255
    result = decode_batch(lipnet.test_function, X_data, alphabets)[0]

    return (video, result)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        video, result = predict(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        video, result = predict(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 5:
        video, result = predict(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        video, result = None, ""

    if video is not None:
        show_video_subtitle(video.face, result)

    stripe = "-" * len(result)
    print ""
    print " __                   __  __          __      "
    print "/\\ \\       __        /\\ \\/\\ \\        /\\ \\__   "
    print "\\ \\ \\     /\\_\\  _____\\ \\ `\\\\ \\     __\\ \\ ,_\\  "
    print " \\ \\ \\  __\\/\\ \\/\\ '__`\\ \\ , ` \\  /'__`\\ \\ \\/  "
    print "  \\ \\ \\L\\ \\\\ \\ \\ \\ \\L\\ \\ \\ \\`\\ \\/\\  __/\\ \\ \\_ "
    print "   \\ \\____/ \\ \\_\\ \\ ,__/\\ \\_\\ \\_\\ \\____\\\\ \\__\\"
    print "    \\/___/   \\/_/\\ \\ \\/  \\/_/\\/_/\\/____/ \\/__/"
    print "                  \\ \\_\\                       "
    print "                   \\/_/                       "
    print ""
    print "             --{}- ".format(stripe)
    print "[ DECODED ] |> {} |".format(result)
    print "             --{}- ".format(stripe)