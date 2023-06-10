from PIL import Image, ImageFont, ImageDraw
import requests
from io import BytesIO
import textwrap


class Image_Data:
    #lol = 22
    def __init__(self, title,year,description,rating,link,genre,language):
        self.title = title
        self.year= year
        self.description = description
        self.rating = float(f"{rating:.1f}")
        self.link = link
        self.genre = genre
        self.language = language


    @staticmethod
    def rgb(p):
        d = [255,0,0]
        d[1] = int((510*p)/100)
        if d[1]>255:
            d[0] -= d[1]-255
            d[1] = 255
        return tuple(d)


    def make_image(self):
        try:
            url = requests.get(self.link)
            imgbytes = BytesIO(url.content)
            poster = Image.open(imgbytes)
        except:
            imgbytes = "error.png"
            poster = Image.open(imgbytes)
        image = Image.new('RGB',(2400,1000),color=(38,38,38))
        poster = poster.resize((898,1012))
        image.paste(poster,(image.size[0]-poster.size[0],0))
        blurman = Image.open("Blurman.png")
        image.paste(blurman,(0,0),mask=blurman)
        draw = ImageDraw.Draw(image)
        title_font = ImageFont.truetype("fonts/ubuntu.ttf",105)
        desc_font = ImageFont.truetype("fonts/arial.ttf",55)
        year_font = ImageFont.truetype("fonts/arial.ttf",60)
        actor_font = ImageFont.truetype("fonts/coco.ttf",55)
        rate_font = ImageFont.truetype("fonts/ubuntu.ttf",90)
        if self.title is not None:
            draw.text((1,1),self.title,(255,238,0),font=title_font) # TITLE
        if self.year is not None:
            draw.text((5,title_font.getsize(self.title)[1]+5),str(self.year),(255,238,0),font=year_font)
        txt_x, txt_y = 3, 230
        alignment = 60
        if self.description is not None:
            wrapper = textwrap.wrap(self.description,width=65)
            try:
                wrapper_limit = wrapper[:4]
            except IndexError:
                wrapper_limit = wrapper
            for i in wrapper_limit:
                draw.text((txt_x,txt_y),i,(255,255,255),font=desc_font)
                txt_y+=alignment
        txt_y += 45
        if self.rating is not None:
            draw.text((txt_x,txt_y),"Rating:",(255,238,0),font=actor_font)
            draw.text((actor_font.getsize("Rating:")[0]+20,txt_y-17),str(self.rating),self.rgb(float(self.rating)*10),font=rate_font)
            txt_y += 135
        if self.genre is not None:
            draw.text((txt_x,txt_y),"Genre:",(255,238,0),font=actor_font)
            draw.text((actor_font.getsize("Genre:")[0]+20,txt_y+7),', '.join(self.genre),(255,255,255),font=desc_font)
            txt_y += 135
        if self.language is not None:
            draw.text((txt_x,txt_y),"Language:",(255,238,0),font=actor_font)
            draw.text((actor_font.getsize("Language:")[0]+20,txt_y+7),', '.join(self.language),(255,255,255),font=desc_font)
        image.show()





