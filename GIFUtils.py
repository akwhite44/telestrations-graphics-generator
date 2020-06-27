import imageio
from PIL import Image
from os import listdir
from os.path import isfile, join


def write_gif(file_names, output_name, frame_duration=1):
    # if not .gif on end change to that and inform user
    images = []
    if output_name[-4:] != '.gif':
        output_name += '.gif'
        print("Added gif extension to output file path: {}".format(output_name))
    for file_name in file_names:
        try:
            img = Image.open(file_name)  # open the image file
            img.verify()  # verify that it is, in fact an image
            images.append(imageio.imread(file_name))
        except (IOError, SyntaxError) as e:
            print('Bad file:', file_name)
    imageio.mimsave(output_name, images, format='GIF', duration=frame_duration)


def get_file_names(directory):
    return [directory + '/' + f for f in listdir(directory) if isfile(join(directory, f))]


def create_gif(output_name, input_dir, frame_duration=1):
    """

    :param output_name:
    :param input_dir:
    :param frame_duration: integer -- seconds frame should be displayed
    :return:
    """
    file_names = get_file_names(input_dir)
    write_gif(file_names, output_name, frame_duration)

