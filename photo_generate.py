from PIL import Image, ImageDraw, ImageFont
import os, sys
import threading

# size of the background
A4size_h = (3508, 2479)
A4size_v = (2479, 3508)
# margin length
margin = 200
# Replace with your font
font_path = "/System/Library/Fonts/STHeiti Medium.ttc"
# Replace with your font size
font_size = 80
font = ImageFont.truetype(font_path, font_size)


class Photo:

    def __init__(self, path, newpath):
        self.path = path
        self.content, self.ext = os.path.splitext(os.path.basename(self.path))
        self.new_path = newpath
        self.origin = Image.open(path) # original image
        self.ori_size = self.origin.size
        # create a blank canvas as the background
        if self.ori_size[0] > self.ori_size[1]:
            self.canvas = Image.new("RGB", A4size_h, "white")
            self.can_size = A4size_h
        else:
            self.canvas = Image.new("RGB", A4size_v, "white")
            self.can_size = A4size_v

    # resize the original photo by width
    # | margin_size | photo | margin_size |
    def resize_by_width(self):
        new_width = self.can_size[0] - 2 * margin
        scale = new_width/self.ori_size[0]
        new_height = int(scale * self.ori_size[1])
        return self.origin.resize((new_width, new_height), Image.ANTIALIAS), new_width, new_height

    def resize_by_height(self):
        new_height = self.can_size[1] - 2 * margin
        scale = new_height/self.ori_size[1]
        new_width = int(scale * self.ori_size[0])
        return self.origin.resize((new_width, new_height), Image.ANTIALIAS), new_width, new_height


    # copy resized image to the canvas
    def add_whitespace(self):
        new_origin, new_width, new_height = self.resize_by_width()
        y_cor = int(self.can_size[1]/2 - new_height/2)
        x_cor = margin
        if y_cor <= margin:
            new_origin, new_width, new_height = self.resize_by_height()
            y_cor = margin
            x_cor = int(self.can_size[0]/2 - new_width/2)
        self.canvas.paste(new_origin, (x_cor, y_cor))
        return y_cor, new_height

    # fetch the info of the photo from its filename
    def get_text(self):
        title, name = self.content.rsplit(maxsplit=1)
        return title, name
        
    # generate the new photo and save to the new folder
    def generate(self):
        yc, new_height = self.add_whitespace()
        title, name = self.get_text()
        msg = title +'  |  '+name # text to write
        draw = ImageDraw.Draw(self.canvas)
        w, h = draw.textsize(msg, font=font) # get the width of the text
        x = (self.can_size[0]/2 - w/2) # write the text to the center
        y = yc + new_height + 60
        draw.text((x, y), msg, font=font, fill="black")
        self.canvas.save(self.new_path)


# multiThread
class myThread(threading.Thread):
    def __init__(self, path, new_path):
        threading.Thread.__init__(self)
        self.path = path
        self.new_path = new_path

    def run(self):
        photo = Photo(self.path, self.new_path)
        photo.generate()


# correctly get the folder path
def getpath(path):
    if path[-1] == '/':
        return path
    else:
        return path+'/'


def main():
    # input prompt
    if len(sys.argv) != 3:
        print('The script accepts 2 arguments:\n')
        print('the folder path of the original photos\n')
        print('the folder path of the new photos')
        return 0
    #ori_folder = "/Users/charon/Downloads/Photos/"
    #new_folder = "/Users/charon/Downloads/new_Photos/"
    ori_folder = getpath(sys.argv[1])
    new_folder = getpath(sys.argv[2])
    pics = os.listdir(ori_folder)
    threads = []
    for pic in pics:
        path = ori_folder + pic
        new_path = new_folder + pic
        try:
            thread_this = myThread(path, new_path)
            thread_this.start()
            threads.append(thread_this)
        except:
            print('Error creating new thread')
    # wait for the threads to finish
    for t in threads:
        t.join()
    print('Finished')
    

if __name__ == "__main__":
    main()
