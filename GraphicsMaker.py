from GIFUtils import write_gif
import os
import magic
from PIL import Image, ImageDraw, ImageFont
import textwrap
from math import ceil
import zipfile
import tempfile


class GraphicsMaker:
    def __init__(self, width, height, week):
        self.players = dict()
        self.key_frame_all = None
        self.key_frame_sans_first = None
        self.width = width
        self.height = height
        self.week_num = week

    @staticmethod
    def expand2square(pil_img, background_color):
        width, height = pil_img.size
        if width == height:
            return pil_img
        elif width > height:
            result = Image.new(pil_img.mode, (width, width), background_color)
            result.paste(pil_img, (0, (width - height) // 2))
            return result
        else:
            result = Image.new(pil_img.mode, (height, height), background_color)
            result.paste(pil_img, ((height - width) // 2, 0))
            return result

    @staticmethod
    def create_text_image(text_image_path, msg, image_width, image_height):
        # todo get/set right ratio of image size to font and padding for wrap text width
        # todo make sure graphics
        try:
            font = ImageFont.truetype('Androgyne_TB.otf', 40)
        except Exception:
            print("Warning no Androgyne_TB.otf. Using default instead.")
            font = ImageFont.load_default()

        msg_lines = textwrap.wrap(msg, width=30)
        ascent, descent = font.getmetrics()
        (width, baseline), (offset_x, offset_y) = font.font.getsize(msg)
        img = Image.new('RGB', (image_width, image_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        current_h, pad = (image_height - ((ascent - offset_y) * msg_lines.__len__())) / 2, 10
        for line in msg_lines:
            w, h = draw.textsize(line, font=font)

            draw.text(((image_width - w) / 2, current_h), line, font=font, fill=(255, 255, 255))
            current_h += h + pad
        img.save(text_image_path)

    @staticmethod
    def create_key_image(text_image_path, msg_lines, image_width, image_height):
        # todo handle larger amount of players
        # todo get/set right ratio of image size to font and padding for wrap text width
        # todo new line separate and draw ellipses
        # todo ellipses under numbers?
        try:
            font = ImageFont.truetype('Androgyne_TB.otf', 40)
        except Exception:
            print("Warning no Androgyne_TB.otf. Using default instead.")
            font = ImageFont.load_default()
        ascent, descent = font.getmetrics()
        (width, baseline), (offset_x, offset_y) = font.font.getsize(msg_lines[0])
        img = Image.new('RGB', (image_width, image_height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        current_h, pad = (image_height - (ascent * msg_lines.__len__())), 10
        current_h = 25
        w_offset = 25
        for line in msg_lines:
            w, h = draw.textsize(line, font=font)

            # todo start at top and start at same width

            draw.text((w_offset, current_h), line, font=font, fill=(255, 255, 255))
            current_h += h + pad
        img.save(text_image_path)

    def resize_and_center_image_in_frame(self, output_image_path, input_image_path, width, height):
        image = Image.open(input_image_path)
        im_new = self.expand2square(image, (255, 255, 255)).resize((width, height))
        im_new.save(output_image_path)

    @staticmethod
    def create_scroller_image(output_image_path, output_images, width):
        height = width*output_images.__len__()
        long_image = Image.new('RGB', (width, height), color=(0, 0, 0))
        for i, im_path in enumerate(output_images):
            im = Image.open(im_path)
            position = (0, width*i)
            long_image.paste(im, position)
        long_image.save(output_image_path)

    @staticmethod
    def draw_ellipse(image, bounds, width=1, fill='red', outline='red', antialias=4):
        """Improved ellipse drawing function, based on PIL.ImageDraw."""
        # https://stackoverflow.com/questions/32504246/draw-ellipse-in-python-pil-with-line-thickness
        # Use a single channel image (mode='L') as mask.
        # The size of the mask can be increased relative to the imput image
        # to get smoother looking results.
        mask = Image.new(
            size=[int(dim * antialias) for dim in image.size],
            mode='L', color='red')
        draw = ImageDraw.Draw(mask)

        # draw outer shape in white (color) and inner shape in black (transparent)
        for offset, fill in (width/-2.0, 'white'), (width/2.0, 'black'):
            left, top = [(value + offset) * antialias for value in bounds[:2]]
            right, bottom = [(value - offset) * antialias for value in bounds[2:]]
            draw.ellipse([left, top, right, bottom], fill=fill)

        # downsample the mask using PIL.Image.LANCZOS
        # (a high-quality downsampling filter).
        mask = mask.resize(image.size, Image.LANCZOS)
        # paste outline color to input image through the mask
        image.paste(outline, mask=mask)

    def create_all_view_image(self, output_image_path, output_images, single_image_width, numbered_labels=True):
        # todo handle correct numbers
        # todo handle double digit numbers
        # add numbers
        if output_images.__len__() % 2 == 1:
            width = ceil((output_images.__len__() + 1) * single_image_width / 2)
            # what to put in end square?
        else:
            width = ceil(output_images.__len__() * single_image_width / 2)
        height = single_image_width * 2
        sideways_image = Image.new('RGB', (width, height), color=(0, 0, 0))
        x = 0
        for i, im_path in enumerate(output_images):
            im = Image.open(im_path)
            paste_top_left_coordinates = (single_image_width * x, (i % 2) * single_image_width)
            sideways_image.paste(im, paste_top_left_coordinates)

            # draw number label
            if 0 < i < len(output_images)-1 and numbered_labels:
                draw = ImageDraw.Draw(sideways_image)
                # (x1, y1, x2, y2)
                offset = 10
                diameter = 70
                draw_circle_coordinates = ((single_image_width * x) + offset, ((i % 2) * single_image_width) + offset,
                                           (single_image_width * x) + (offset + diameter),
                                           ((i % 2) * single_image_width) + (offset + diameter))
                # if even amount of numbers then i = 0
                if len(self.players.keys()) == len(output_images) - 2:
                    num = str(i-1)
                else:
                    num = str(i)
                # todo fix drawing circle
                # draw_ellipse(im, draw_circle_coordinates, width=10, antialias=8)
                draw.ellipse(draw_circle_coordinates, outline='red', fill='red')
                try:
                    font = ImageFont.truetype('TitilliumWeb-Bold.ttf', 40)
                except Exception:
                    print("Warning no TitilliumWeb-Bold.ttf. Using default instead.")
                    font = ImageFont.load_default()
                ascent, descent = font.getmetrics()
                (text_width, baseline), (offset_x, offset_y) = font.font.getsize(num)
                # todo fix centering of text in circle
                number_coordinate = ((single_image_width * x) + ((offset + diameter) / 2) - (text_width / 4),
                                     ((i % 2) * single_image_width) + ((offset + diameter) / 2) - 28)
                draw.text(number_coordinate, num, font=font, fill='white')
            if (i % 2) == 1:
                x += 1
        sideways_image.save(output_image_path)

    def assemble_drawing_key(self, path):
        msg = []
        with open(path, 'r') as f:
            res = f.read().splitlines()
            for i, r in enumerate(res):
                if i > 0:
                    person = r.split('\t')
                    self.players[person[0]] = person[1]
                    msg.append('{}. {}\n'.format(str(int(person[0])), person[1]))

        all_card_path = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        sans_first_card_path = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        self.create_key_image(all_card_path, msg, self.width, self.height)
        msg.pop(0)
        self.create_key_image(sans_first_card_path, msg, self.width, self.height)
        self.key_frame_all = all_card_path.name
        self.key_frame_sans_first = sans_first_card_path.name

    @staticmethod
    def get_ordered_responses(input_dir_path):
        """
        returns list of tuples of submission number, type, path, timestamp ordered by file name number
        ex. ('0', 'image/jpeg', '/Users/USERNAME/Desktop/Telestrations/week 2/Items/06/0.jpg', 1589811365.8658662)
        :param input_dir_path:
        :return:
        """
        ordered_response_files = sorted([(f.split('.', 1)[0], magic.from_file(os.path.join(input_dir_path, f),
                                                                              mime=True),
                        os.path.join(input_dir_path, f),
                        os.path.getmtime(os.path.join(input_dir_path, f))) for f in os.listdir(input_dir_path)
                       if (os.path.isfile(os.path.join(input_dir_path, f))
                            and (magic.from_file(os.path.join(input_dir_path, f), mime=True)[:4] == 'text'
                                 or magic.from_file(os.path.join(input_dir_path, f), mime=True)[:5] == 'image'))],
                      key=lambda x: x[0])
        topic = ordered_response_files.pop(-1)
        ordered_response_files.insert(0, topic)
        return ordered_response_files

    @staticmethod
    def get_ordered_tasks(input_dir_path):
        return sorted([(os.path.join(input_dir_path, f), f) for f in os.listdir(input_dir_path) if
                       os.path.isdir(os.path.join(input_dir_path, f))], key=lambda x: x[1])

    @staticmethod
    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file),
                                                                     os.path.join(path, '..')))

    def create_result_medias(self, input_path, output_path):

        self.assemble_drawing_key(os.path.join(input_path, "key.txt"))

        file_items = self.get_ordered_tasks(input_path)
        media_output_path = os.path.join(output_path, 'media')

        for res_dir_file_path, i in file_items:
            files = self.get_ordered_responses(res_dir_file_path)
            output_images = list()

            for j, submission in enumerate(files):
                if j == 0:
                    # create_title card that is used with each gif
                    with open(submission[2], 'rt') as text_file:
                        title_msg = 'The Gang Draws: {}'.format(text_file.read())
                    title_card_path = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                    self.create_text_image(title_card_path, title_msg, self.width, self.height)
                    output_images.append(title_card_path.name)
                else:
                    if submission[1][:4] == 'text':
                        # check if rtf
                        try:
                            with open(submission[2], 'r') as text_file:
                                # first one "the gang draws"
                                msg = text_file.read()
                        except UnicodeDecodeError:
                            with open(submission[2], 'r', encoding='ISO-8859-1') as text_file:
                                # first one "the gang draws"
                                msg = text_file.read()
                        text_image_path = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                        self.create_text_image(text_image_path, msg, self.width, self.height)
                        output_images.append(text_image_path.name)
                    else:
                        output_image_path = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                        self.resize_and_center_image_in_frame(output_image_path, submission[2], self.width, self.height)
                        output_images.append(output_image_path.name)
            if len(files) == len(self.players.keys()):
                output_images.append(self.key_frame_sans_first)
            else:
                output_images.append(self.key_frame_all)

            os.makedirs(media_output_path, exist_ok=True)

            all_view_path = os.path.join(media_output_path, '{}_all_view.png'.format(i))
            self.create_all_view_image(all_view_path, output_images, self.width)

            output_images.pop(-1)

            gif_path = os.path.join(media_output_path, '{}_motion'.format(i))
            write_gif(output_images, gif_path, 3)

            scroller_path = os.path.join(media_output_path, '{}_scroller.png'.format(i))
            self.create_scroller_image(scroller_path, output_images, self.width)

            for x, temp_file in enumerate(output_images):
                if x != len(output_images)-1:
                    os.unlink(temp_file)

        zip_output_path = os.path.join(output_path, 'week_{}_results.zip'.format(self.week_num))
        with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as z:
            self.zipdir(media_output_path, z)
        os.unlink(self.key_frame_all)
        os.unlink(self.key_frame_sans_first)
        print("All graphics generated and can be found in the zip located here:\n{}".format(zip_output_path))
