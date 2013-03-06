import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.gameserver.datatables import SkillTable #技能中文名相關
from com.l2jserver.gameserver.datatables import SkillTreesData #學習技能相關
from com.l2jserver.gameserver.model import L2SkillLearn #學習技能相關
from com.l2jserver.gameserver.model.skills import L2Skill #技能相關



class EasySkillLearn(JQuest):
	qID = -1
	qn = "easySkillLearn"
	qDesc = "custom"
	
	NPCID = [103] #觸發任務的 NPC 可修改.. 可以多 ID 例如 [100,102,103]
	
	includeByFs = True #是否包括遺忘秘傳技能
	includeAutoGet = True
	
	htm_header = "<html><body><title>簡易技能學習系統</title>"
	htm_footer = "</body></html>"
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		JQuest.__init__(self, id, name, descr)
		for id in self.NPCID:
			self.addStartNpc(id)
			self.addFirstTalkId(id)
			self.addTalkId(id)
		print "Init:" + self.qn + " loaded"

	def getAvailableSkill(self, player):
		return SkillTreesData.getInstance().getAvailableSkills(player, player.getClassId(), self.includeByFs, self.includeAutoGet)
		
	def listAvailableSkill(self, player):
		sl = self.getAvailableSkill(player)
		r = "可學習的技能清單<br1>"
		r += '<a action="bypass -h Quest %s learn_all">全部學習</a><br1>' % self.qn
		skillTable = SkillTable.getInstance()
		for s in sl:
			r += "<a action=\"bypass -h Quest " + self.qn + " learn " + str(s.getSkillId()) + " " + str(s.getSkillLevel()) + "\">" + skillTable.getInfo(s.getSkillId(), s.getSkillLevel()).getName() + " Lv " + str(s.getSkillLevel()) + "</a><BR1>"
		return r

	def myAddSkill(self, player, id):
		sl = self.getAvailableSkill(player)
		for s in sl:
			if s.getSkillId() == id:
				player.addSkill(SkillTable.getInstance().getInfo(s.getSkillId(), s.getSkillLevel()), True)
				self.myAddSkill(player, id)
				break

	def onAdvEvent(self, event, npc, player):
		if event == 'learn_all':
			sl = self.getAvailableSkill(player)
			c = 0
			while sl:
				player.addSkill(SkillTable.getInstance().getInfo(sl[0].getSkillId(), sl[0].getSkillLevel()), True)
				sl = self.getAvailableSkill(player)
				c += 1
				if c > 5000:
					return self.htm_header + "未能全部技能學完 請再試一次 或與 GM 聯絡" + self.htm_footer #技能資料出現問題 請回報
			player.sendSkillList()
			return self.htm_header + "全部技能學完 %s" % ["(不包括遺忘秘傳技能)","(包括遺忘秘傳技能)"][self.includeByFs] + self.htm_footer
		if event.startswith('learn '):
			sid, slv = event[6:].split()
			sid = int(sid)
			slv = int(slv)
			self.myAddSkill(player, sid)
			player.sendSkillList()
		return self.onFirstTalk(npc, player)
		
	def onFirstTalk(self, npc, player):
		st = player.getQuestState(self.qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		return self.htm_header + self.listAvailableSkill(player) + self.htm_footer
		
EasySkillLearn()
