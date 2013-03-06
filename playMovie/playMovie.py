import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

class SceneNameTable:
	sceneNameTable = {}
	def __init__(self):
		f = open("data/scripts/custom/playMovie/sceneplayerdata.txt", "r")
		f.readline()
		for line in f:
			temp = line.split("\t")
			if temp[0].isdigit():
				self.sceneNameTable[int(temp[0])] = [temp[1], float(temp[2]),[]]
		f.close()
		for i in self.sceneNameTable:
			self.sceneNameTable[i][2] = [0,0,0]
		for i in [1]:
			self.sceneNameTable[i][2] = [-184258, 243061, 1581]
		for i in [2, 3, 4]:
			self.sceneNameTable[i][2] = [-179548, 209584, -15499]
		for i in [5, 6, 7]:
			self.sceneNameTable[i][2] = [-250403, 207273, -11852]
		#8,9,10
		for i in [11]:
			self.sceneNameTable[i][2] = [-80041,205866,-7889]
		for i in [12, 13]:
			self.sceneNameTable[i][2] = [-89543,216031,-7490]
		for i in [14]:
			self.sceneNameTable[i][2] = [-23769,-8961,-5387]
		for i in xrange(15, 24):
			self.sceneNameTable[i][2] = [114720,-114798,-11199]
		for i in [24, 25]:
			self.sceneNameTable[i][2] = [85798, -249624, -8300]
		for i in [26, 27]:
			self.sceneNameTable[i][2] = [45415, -248188, -6739]
		#28
		for i in [30]:
			self.sceneNameTable[i][2] = [76954, -240590, -10836]

	def getTable(self):
		return self.sceneNameTable
			
	def getName(self, id):
		assert type(id) == type(0)
		return self.sceneNameTable[id][0]

	def getDuration(self, id):
		assert type(id) == type(0)
		return self.sceneNameTable[id][1]

	def getXYZ(self, id):
		assert type(id) == type(0)
		return self.sceneNameTable[id][2]


class PlayMovie(JQuest):
	qID = -1
	qn = "playMovie"
	qDesc = "custom"
	
	command_split_char = "_#_"
	
	NPCID = [102] #觸發任務的 NPC 可修改.. 可以多 ID 例如 [100,102,103]
	htm_header = "<html><body><title>觀看系統影片</title>"
	htm_footer = "</body></html>"

	def firstpage(self, **kv):
		return self.list_scene()

	def list_scene(self, event=None, npc=None, player=None):
		scene_list = self.sceneNameTable.getTable().keys()
		scene_list.sort()
		r = ""
		for id in scene_list:
			r += "<a action=\"bypass -h Quest %(qn)s play %(scene_id)d\">%(desc)s</a><BR1>" % {"desc":"%d %s %d秒" % (id, self.sceneNameTable.getName(id), self.sceneNameTable.getDuration(id)/1000), "qn":self.qn, "scene_id":id}
		return self.htm_header + r + self.htm_footer
		
	def teleToLocation(self, event, npc, player):
		x, y, z = event
		player.teleToLocation(int(x), int(y), int(z))

	def play_scene2(self, event, npc, player):
		x, y, z, id = event
		id = int(id)
		player.showQuestMovie(id)
		self.startQuestTimer(" ".join(["tele", x, y, z]), int(self.sceneNameTable.getDuration(id)+15000), npc, player)
		
	def play_scene(self, event, npc, player):
		id = int(event[0])
		x, y, z = player.getX(), player.getY(), player.getZ()
		x2, y2, z2 = self.sceneNameTable.getXYZ(id)
		if x2 or y2 or z2:
			player.teleToLocation(x2, y2, z2)
		self.startQuestTimer(" ".join(["play2", str(x), str(y), str(z), str(id)]), 1000, npc, player)
		# player.showQuestMovie(id)
		# self.startQuestTimer(" ".join(["tele", str(x), str(y), str(z)]), int(self.sceneNameTable.getDuration(id)+15000), npc, player)
		
	htm_commands = {"list":list_scene, "play":play_scene, "tele":teleToLocation, "play2":play_scene2}
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		JQuest.__init__(self, id, name, descr)
		for id in self.NPCID:
			self.addStartNpc(id)
			self.addFirstTalkId(id)
			self.addTalkId(id)
		self.sceneNameTable = SceneNameTable()
		print "Init:" + self.qn + " loaded"

	def process_command(self, event, npc, player):
		t = event.split()
		if t and t[0] in self.htm_commands.keys():
			return self.htm_commands[t[0]](self, t[1:], npc, player)
		return self.firstpage()
	
	def onAdvEvent(self, event, npc, player):
		r = self.firstpage()
		for t in event.split(self.command_split_char):
			r = self.process_command(t, npc, player)
		return r
		
	def onFirstTalk(self, npc, player):
		st = player.getQuestState(self.qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		return self.firstpage()
		
PlayMovie()
