import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest
from com.l2jserver.gameserver.network.serverpackets import ExShowUsmVideo

class PlayUsmVideo(JQuest):
	qID = -1
	qn = "playUsmVideo"
	qDesc = "custom"
	
	command_split_char = "_#_"
	
	
	usmvideo = [1,2,3,4,5,6,7,8,9,10,11,12,139,140,141,142,143,144,145,146]
	
	
	NPCID = [100] #觸發任務的 NPC 可修改.. 可以多 ID 例如 [100,102,103]
	htm_header = "<html><body><title>觀看 USM 影片</title>"
	htm_footer = "</body></html>"

	def firstpage(self, **kv):
		return self.list_scene()

	def list_scene(self, event=None, npc=None, player=None):
		r = ""
		for id in self.usmvideo:
			r += "<a action=\"bypass -h Quest %(qn)s play %(scene_id)d\">%(desc)s</a><BR1>" % {"desc":"%d" % (id), "qn":self.qn, "scene_id":id}
		return self.htm_header + r + self.htm_footer
		
	def play_scene(self, event, npc, player):
		id = int(event[0])
		player.sendPacket(ExShowUsmVideo(id))
		
	htm_commands = {"list":list_scene, "play":play_scene}
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		JQuest.__init__(self, id, name, descr)
		for id in self.NPCID:
			self.addStartNpc(id)
			self.addFirstTalkId(id)
			self.addTalkId(id)
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
		
PlayUsmVideo()
