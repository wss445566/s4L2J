import sys
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.gameserver.datatables import SkillTable #技能中文名相關
from com.l2jserver.gameserver.datatables import SkillTreesData #學習技能相關
from com.l2jserver.gameserver.model import L2SkillLearn #學習技能相關
from com.l2jserver.gameserver.model.skills import L2Skill #技能相關

import math

class EasySkillRemove(JQuest):
	qID = -1
	qn = "easySkillRemove"
	qDesc = "custom"
	NPCID = [100] #觸發任務的 NPC 可修改.. 可以多 ID 例如 [100,102,103]
	rpp = 10 #每頁顯示多少個記錄

	htm_header = "<html><body><title>簡易技能刪除腳本</title>"
	htm_search = "輸入技能名稱或ID作搜尋<table><tr><td><edit var=\"value\" width=150 height=12></td><td><button value=\"搜尋\" width=50 height=20  action=\"bypass -h Quest " + qn + " search $value\"></td></tr></table>"
	htm_footer = "</body></html>"
	htm_list_header = "已學習的技能清單<br1>"
	htm_warning = "<font color=ff0000>(注意!點擊技能連結 即時刪除)</font><BR1>"

	def __init__(self, id=qID, name=qn, descr=qDesc):
		qID, qn, qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		for id in self.NPCID:
			self.addStartNpc(id)
			self.addFirstTalkId(id)
			self.addTalkId(id)
		print "Init:" + self.qn + " loaded"

	def onAdvEvent(self, event, npc, player):
		if event.startswith('page '):
			page = event[len('page '):]
			return self.htm_header + self.htm_search + self.listSkills(player, int(page)) + self.htm_footer
		elif event.startswith('remove '):
			sid, slv = event[len('remove '):].split()
			sid = int(sid)
			slv = int(slv)
			player.removeSkill(SkillTable.getInstance().getInfo(sid, slv))
			player.sendSkillList()
		elif event.startswith('search '):
			kw = event[len('search '):]
			r = self.htm_warning
			skillTable = SkillTable.getInstance()
			for s in player.getAllSkills():
				if kw in skillTable.getInfo(s.getId(), s.getLevel()).getName() or kw == str(s.getId()):
					r += self.makeRemoveLink(s)
			return self.htm_header + self.htm_search + r + self.htm_footer
		return self.onFirstTalk(npc, player)
		
	def onFirstTalk(self, npc, player):
		return self.htm_header + self.htm_search + self.listSkills(player, 1) + self.htm_footer

	def makeRemoveLink(self, skill):
		return "<a action=\"bypass -h Quest " + self.qn + " remove " + str(skill.getId()) + " " + str(skill.getLevel()) + "\">" + SkillTable.getInstance().getInfo(skill.getId(), skill.getLevel()).getName() + "(%d)" % str(skill.getId()) + " Lv " + str(skill.getLevel()) + "</a><BR1>"
		
	def listSkills(self, player, page):
		#sl = player.getAllSkills() #GS 890 或以前
		sl = player.getAllSkills().toArray() #GS 891 或以後

		total_page = int(math.ceil(len(sl) / (self.rpp + 0.0)))
		r = self.htm_list_header
		r += "第&nbsp;"
		for i in xrange(1,total_page + 1):
			r += "<a action=\"bypass -h Quest " + self.qn + " page " + str(i) + "\">" + str(i) + "</a>&nbsp;"
		r += "頁<BR1>"
		r += self.htm_warning

		start = self.rpp * (page - 1)
		stop = self.rpp * page
		for s in sl[start:stop]:
			r += self.makeRemoveLink(s)
		return r
		
EasySkillRemove()
