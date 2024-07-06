import requests


class PinterestMediaDownloader:
	info_url = "https://api.pinterest.com/v3/pidgets/pins/info/?pin_ids={}"
	
	def __init__(self, pin_url):
		self.session = requests.Session()
		self.pin_url = pin_url
		self.pin_id = None
		self.media = []
		self.data = None
		self.best_sizes = []

	def get_pin_id(self):
		history = self.session.get(self.pin_url).history
		self.pin_id = history[-1].headers["location"].split("/")[4] if history else self.pin_url.split("/")[4]

	def get_pin_data(self):
		self.data = self.session.get(self.__class__.info_url.format(self.pin_id)).json()["data"][0]
	  
	def get_pin_media(self): 
		if spd := self.data.get("story_pin_data"):
			for page in spd["pages"]:
				if v := page["blocks"][0].get("video"):
					self.media.append(v.get("video_list")) 

				elif i := page["blocks"][0].get("image"):
					self.media.append(i.get("images"))
				else:
					pass
		elif v := self.data.get("videos"):
			self.media.append(v.get("video_list"))
		elif i := self.data.get("images"):
			self.media.append(i)
		else:
			pass
		
	def get_best_sizes(self):
		for i, m in enumerate(self.media):
			for s in list(m):
				if m[s]["url"].strip().endswith(".m3u8"):
					m.pop(s)
			new_m = sorted(m.values(), key=lambda s: s["width"]*s["height"], reverse=True)
			
			self.best_sizes.append(new_m[0])
