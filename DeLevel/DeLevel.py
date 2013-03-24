from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest

class Quest(JQuest):
	qID = -1
	qn = "DeLevel"
	qDesc = "custom"
	NPCID = 100 #砞﹚牟祇 NPC ID
	
	min_level = 20 #砞﹚. 程ぶ. 
	max_level = 80 #砞﹚. 程蔼ぶ. 

	htm_header = """<html><title>单竲セ</title><body>"""
	htm_footer = """</body></html>"""
	
	htm_intro = """块饼单ぶ<br>块絛瞅 程蔼 %d 程 %d <BR>礛 单 硈挡/秙 絋粄 """ % (min_level, max_level)
	htm_input = """<edit var="value"><a action="bypass -h Quest %s show_confirm $value">璶―单</a>""" % qn
	htm_confirm = """<a action="bypass -h Quest %s confirm %d">絋粄单 %d </a>"""
	htm_level_error = """块单岿粇.<BR> 叫块ゑ单耕单ㄓ单. """
	htm_delevel_done = """单ЧΘ"""
	htm_level_outOfRange = """单块计 禬絛瞅 程蔼 %d 程 %d """ % (min_level, max_level)
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		self.addStartNpc(self.NPCID)
		self.addFirstTalkId(self.NPCID)
		self.addTalkId(self.NPCID)
		print "%s loaded" % self.qn

	def onAdvEvent(self, event, npc, player):
		if event.startswith("show_confirm "):
			wantedLevel = int(event[len("show_confirm "):]) or 999
			if player.getLevel() > wantedLevel:
				if self.min_level <= wantedLevel <= self.max_level:
					return self.returnHTML(self.htm_confirm % (self.qn, wantedLevel, wantedLevel))
				else:
					return self.returnHTML(self.htm_level_outOfRange)
			else:
				return self.returnHTML(self.htm_level_error)
		elif event.startswith("confirm "):
			wantedLevel = int(event[len("confirm "):]) or 999
			self.delevel(player, wantedLevel)
			return self.returnHTML(self.htm_delevel_done)

	def onFirstTalk(self, npc, player):
		return self.returnHTML(self.htm_intro + self.htm_input)
		
	def returnHTML(self, s):
		return self.htm_header + s + self.htm_footer
		
	def delevel(self, player, level):
		if player.getLevel() > level:
			player.getStat().addLevel(level - player.getLevel())
		
Quest()	
