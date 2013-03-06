import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.gameserver.model import L2World
from com.l2jserver.gameserver.model.actor import L2Character

from com.l2jserver.gameserver.datatables import SkillTable
from com.l2jserver.gameserver.network.serverpackets import MagicSkillUse

import time

class OnlineGift(JQuest):
	qID = -1
	qn = "onlineGift"
	qDesc = "custom"

	canFireWorks = True #在線送禮 中獎玩家是否放煙火
	
	timepass_check = True #是否記錄及檢測個別玩家得獎後, 需要多久才能再有機會得獎
	timepass = 60 * 10  #個別玩家得獎後, 時間之內沒有得獎機會, 單位 秒, 預設 10分鐘
	
	sgifts = {
		"xmas":{"start":[2012,05,20,0,0,0], "end":[2012,05,21,0,0,0], "delay":1000*60*2, "gifts":[
			[57,10000,99999,100]
			,[57,10,100,100]
			,[57,1,1,100]		
		]}
		,"new_year":{"start":[2012,05,20,0,0,0], "end":[2013,05,20,0,0,0], "delay":1000*60*5, "gifts":[
			[57,10000,99999,100]
			,[57,10,100,100]
			,[57,2,2,100]		
		]}
	}
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		for key in self.sgifts.keys():
			self.init_timer(key)
		print "Init:" + self.qn + " loaded"

	def init_timer(self, key):
		sy,sm,sd,sh,smm,ss = self.sgifts[key]["start"]
		ey,em,ed,eh,emm,es = self.sgifts[key]["end"]
		starttime = int(time.mktime((sy,sm,sd,sh,smm,ss,0,1,-1)))
		endtime = int(time.mktime((ey,em,ed,eh,emm,es,0,1,-1)))
		curr_time = int(time.time())
		if  curr_time > starttime and curr_time < endtime:
			self.startQuestTimer(key, self.sgifts[key]["delay"], None, None, False)
		
	def firework(self, player):
		skill = SkillTable.FrequentSkill.FIREWORK.getSkill()
		if skill:
			player.broadcastPacket(MagicSkillUse(player, player, skill.getId(), skill.getLevel(), skill.getHitTime(), skill.getReuseDelay()))

	def checkCondition(self, player):
		if player.isInsideZone(L2Character.ZONE_PEACE): return False
		if not player.isInCombat(): return False
		if self.timepass_check:
			st = player.getQuestState(self.qn)
			if not st:
				st = self.newQuestState(player)
				st.setState(State.STARTED)
			last = st.get('last_gift_time')
			if last and time.time() - float(last) < self.timepass: return False
		return True

	def give_gift(self, gifts):
		l2world = L2World.getInstance()
		pl = [x for x in l2world.getAllPlayers().values() if self.checkCondition(x)]
		pc = len(pl)
		if pc < 1: return
		lucky_player = pl[self.getRandom(pc)]
		for item_id, min_c, max_c, chance in gifts:
			if self.getRandom(100) < chance:
				lucky_player.addItem(self.qn, item_id, min_c + self.getRandom(max_c - min_c), None, True)
		if self.timepass_check:
			st = lucky_player.getQuestState(self.qn)
			if not st:
				st = self.newQuestState(lucky_player)
				st.setState(State.STARTED)
			st.set('last_gift_time', str(time.time()))
		if self.canFireWorks:
			self.firework(lucky_player)

	def onAdvEvent(self, event, npc, player):
		if event in self.sgifts.keys():
			self.give_gift(self.sgifts[event]["gifts"])
			self.init_timer(event)

OnlineGift()