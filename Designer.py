from PIL import Image, ImageFont, ImageDraw,ImageFilter
import requests
import asyncio
from io import BytesIO
import textwrap
from old import Image_Data

#what the dog doing
class Designer(Image_Data):
	def __init__(self,resval,title,year,description,rating,link,genre,language,backdrop):
		super().__init__(title,year,description,rating,link,genre,language)
		self.backdrop = backdrop
		self.w = 420*resval
		self.h = 220*resval
		self.fontsizes = (self.w+self.h)//64
		self.genresizes = (self.w+self.h)//100
	async def design(self):
		try:
			url = requests.get(self.link)
			poster = Image.open(BytesIO(url.content))
		except Exception:
			poster = Image.open(r"exception_images/error.jpeg")
		background = Image.new("RGB",(self.w,self.h),color=(0,)*3)
		background = await self.make_background(background,poster)
		await asyncio.wait([self.deploy_text(background,(self.w+self.h)//96,(self.w+self.h)//96),self.genre_generator(background,x=(self.w+self.h)//96,y=self.h-self.h//12)])
		return background
	async def make_background(self,background,poster):
		fposter = poster.resize((background.size[0]//3, background.size[1]))
		await self.paste_poster(background,fposter)
		if self.link is not None:
			await self.bg(background,poster,fposter)
		return background
	async def deploy_text(self,bg,text_w,text_h):
		draw = ImageDraw.Draw(bg)
		font = ImageFont.truetype("fonts/lemon.otf",size=self.fontsizes)
		if all([self.year is not None,self.year != '']):
			draw.text((text_w,text_h),self.year,(182,182,182),font=font)
		if all([self.title is not None,self.title != '']):
			text_h += font.getsize("a")[1]
			fontlang = ImageFont.truetype("fonts/lemon.otf", size=font.size*2)
			for i in textwrap.wrap(self.title,width=22)[:2]:
				draw.text((text_w,text_h),i.upper(),(255,255,255),font=fontlang)
				text_h += fontlang.getsize("a")[1]
		if all([self.language is not None,self.language != '']):
			draw.text((text_w,text_h),self.language.upper(),(182,182,182),font=font)
		if all([self.description is not None,self.description != '']):
			text_h += font.getsize("a")[1]*3
			fontdesc = ImageFont.truetype("fonts/robotoo.ttf", size=font.size)
			wrapper = textwrap.wrap(self.description,width=60)
			try:
				wrapper_limit = wrapper[:4]
			except IndexError:
				wrapper_limit = wrapper
			wrapper_limit[-1] += " »"
			for i in wrapper_limit:
				draw.text((text_w,text_h),i,(255,255,255),font=fontdesc)
				text_h += fontdesc.size
		if all([self.rating is not None,self.rating != '']):
			text_h += font.size*2
			ratfont = ImageFont.truetype("fonts/lemon.otf", size=font.size*2)
			draw.text((text_w,text_h),str(self.rating),self.rgb(float(self.rating)*10),font=ratfont)
		return bg
	async def bg(self,background,poster,origpost):
		if self.backdrop is not None:
			bg_poster = Image.open(BytesIO(requests.get(self.backdrop).content))
		else:
			bg_poster = await self.crop_centre(poster)
		bg_poster = bg_poster.filter(ImageFilter.GaussianBlur(radius=25))
		bg_poster = bg_poster.resize((background.size[0],background.size[1]))
		bg_poster = await self.reduce_opac(bg_poster)
		masker = await self.image_mask(origpost)
		background.paste(bg_poster, (0,0), masker)
	async def paste_poster(self,background,poster):
		background.paste(poster,(background.size[0]-background.size[0]//3,0))
	async def image_mask(self,post:Image):
		mask = Image.new("L",(self.w,self.h),0)
		draw = ImageDraw.Draw(mask)
		draw.polygon(((0,0),(self.w-self.w//3+post.size[0]//6,0),(self.w-self.w//3,self.h),(0,self.h)),fill=255)
		mask.resize((self.w,self.h),resample=Image.ANTIALIAS)
		return mask
	async def crop_centre(self,img:Image):
		return img.crop((0,img.size[1]//3,img.size[0],img.size[1]-img.size[1]//3))
	async def reduce_opac(self,img):
		img = img.convert("RGB")
		black = Image.new("RGB",(img.size[0],img.size[1]),color=(0,0,0))
		blended = Image.blend(img,black,alpha=0.7)
		return blended
	async def genre_generator(self,im,x,y,radius=None):
		gefont = ImageFont.truetype("fonts/robotoo.ttf", size=self.genresizes)
		# print(self.genresizes)
		width = gefont.getsize("A")[1]*2
		draw = ImageDraw.Draw(im)
		radius = width//2
		for i in self.genre:
			font_w = gefont.getsize(i)[0]
			rect_w = (font_w)+radius*2
			rect = draw.rounded_rectangle((x, y, x + rect_w, y + width), radius, (204,) * 3)
			draw.text((x+radius,y+width//4.5), i, (0,) * 3, font=gefont)
			x = x + rect_w + radius
		return im



