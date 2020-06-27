import argparse
from GraphicsMaker import GraphicsMaker
from os import path
from sys import exit

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate result graphics for a completed drawtf game.')

    parser.add_argument('inputPath', type=str,
                        help='the path to directory of submissions')

    parser.add_argument('outputPath', type=str,
                        help='the path to directory where the output directory and zip will be saved')

    parser.add_argument('gameNumber', action='store_const', const=0,
                        help="game number so output zip name is unique")

    # these ones are optional

    parser.add_argument('-d', '--dimensions', type=int,
                        help='dimensions for the frame of each submission square')

    args = parser.parse_args()
    input_path = args.inputPath

    if not path.isdir(input_path):
        print('The input path specified does not exist')
        exit()

    output_path = args.outputPath

    if not path.isdir(output_path):
        print('The output path specified does not exist')
        exit()

    game_number = args.gameNumber
    if args.dimensions and args.dimensions > 0:
        image_width = args.dimensions
        image_height = args.dimensions
    else:
        image_width, image_height = 800, 800

    maker = GraphicsMaker(image_width, image_height, game_number)
    maker.create_result_medias(input_path, output_path)

    # TODO
    # break up and reorg graphics maker methods
    # add more documentation
    # add documentaiton on how input should look
    # add example images to docs
    # delete folder where temporarily stored
