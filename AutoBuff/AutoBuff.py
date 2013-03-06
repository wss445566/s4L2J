import sys
from com.l2jserver.gameserver.model.quest import State
from com.l2jserver.gameserver.model.quest import QuestState
from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest

from com.l2jserver.gameserver.util import Util		#計算距離
from com.l2jserver.gameserver.datatables import SkillTable	#技能相關
from com.l2jserver.gameserver.network.serverpackets import NpcHtmlMessage	#對話框
from com.l2jserver.gameserver.datatables import SpawnTable

from com.l2jserver.gameserver.model.actor.instance import L2PcInstance

class SkillIconTable:
	skillIconTable = {}
	def __init__(self):
		f = open("data/scripts/custom/autobuff/skillgrp.txt", "r")
		f.readline()
		for line in f:
			temp = line.split("\t")
			self.skillIconTable[temp[0]] = temp[11] #HighFive
			#self.skillIconTable[temp[0]] = temp[19] #GoD
		
	def getIconName(self, skill_id):
		return self.skillIconTable[str(skill_id)]

class AutoBuff(JQuest):
	qID = -1
	qn = "AutoBuff"
	qDesc = "custom"

	wait_time = 1000 * 20 # 每 20 秒自動 ++
	radius = 400 # 半徑
	
	isShowIcon = True
	#isShowIcon = False #如不需要圖示 設為 False

	default_buff_list = []

	gm_mix=["23241","7091","7090","7089","7088","7093","7092","23239","23238"] + ["7064","7063","7062","7061","23240"]
	gm_attack=["7094","23243","23242","7041","7042","7043","7044","7048","7050","7053","7054","7056","7057","7059","23246"]
	gm_defend=["7095","23244","23245","7045","7046","7047","7049","7051","7052","7055","7058","23247","23248","7060","7096"]
	
	song = ["264","265","266","267","268","269","270","304","305","306","308","349","363","364","529","764","914","988-3"]
	dance = ["271","272","273","274","275","276","277","307","309","310","311","365","366","530","765","915","989"]
	other1 = ["1356","1352","1542","1388-3","1389-3","1182-3","1189-3","1191-3","1392-3","1393-3","1548-3","1032","1501","1499","1043","1045-6","1048-6","1086-2","1085-3","1078-6","1077-3","1073-2","1068-3","1062-2","1243-3","1242-3","1044-3","1240-3","1040-3","1036-2","1035-4","1033-3","1204-2"]
	other2 = ["1073-2","1304-3","1068-3","1044-3","1043","1040-3","1397-3","1393-3","1033-3","1355","1354","1353","1303-2","1259-4","1257-3","1243-6","1204-2","1504","1503","1035-4","1460","1087-3","1078-6"]
	other3 = ["1068-3","1059-3","1502","1240-3","1242-3","1073-2","1035-4","1392-3","1204-2","1189-3","1357","1531-7","1500","1303-2","1354","1268-4","1040-3","1078-6","1077-3"]
	allowBuffList = gm_mix + gm_attack + gm_defend + song + dance + other1 + other2 + other3 #白名單, GM 允許技能++清單 在名單上的技能 才可以++ (防封包修改 hack)
	buff_pages = [["GM1", gm_mix],["GM2", gm_attack],["GM3", gm_defend],["歌", song],["舞", dance],["昭", other1],["伊", other2],["席", other3]]
	page_col = {"GM1":2,"GM2":2,"GM3":2,"歌":3,"舞":3,"昭":3,"伊":3,"席":3}

	#32496 欲界 脫逃裝置
	#32705 札肯 木桶
	#32658-32663 夢幻結界管理員
	#32762 希露
	instances_npcid = [32496,32705] + [32658,32659,32660,32661,32662,32663] + [32762]
	BuffCEOs = [100]	#處理設定自訂狀態的 NPC
	teleporters = [30006,30059,30080,30134,30146,30162,30177,30233,30256,30320,30427,30429,30483,30484,30485,30486,30487,30540,30576,30716,30719,30722,30727,30836,30848,30878,30899,31275,31320,31376,31383,31698,31699,31964,32163,32181,32184,32186,32189,32378,32477,32614,32714,32740]
	NPCIDs = instances_npcid + BuffCEOs + teleporters #自動放狀態的 npcid 可以多個 ID [30080, 31756] 

	htm_header = "<html><body><title>自動++系統設定</title>"
	htm_footer = "</body></html>"
	
	htm_intro_reset = "<a action=\"bypass -h Quest " + qn + " reset\">重置設定</a><BR>"
	htm_intro_reset_effect = "<a action=\"bypass -h Quest " + qn + " reset_effect\">清除狀態</a><BR>"
	htm_intro_preset1 = "<a action=\"bypass -h Quest " + qn + " reset 7063 7088 7089 7090 7091 7092 7093 23241 23238 7048 7056 7057 23246 7049 7060 7096 23247 23248\">戰系預設</a><BR>"
	htm_intro_preset2 = "<a action=\"bypass -h Quest " + qn + " reset 7088 7089 7090 7091 7092 7093 23241 23238 7061 7048 7056 7059 7049 7060 7096 23247 23248 7058\">法系預設</a><BR>"
	htm_intro_list = "<a action=\"bypass -h Quest " + qn + "\">進入設定畫面</a><BR>"
	htm_menu = htm_intro_reset + htm_intro_reset_effect + htm_intro_preset1 + htm_intro_preset2 + htm_intro_list

	htm_intro = "簡介<BR>.............<BR>" + htm_menu
	htm_reset = "設定已清除<br>" + htm_menu
	htm_reset_effect = "狀態已清除<BR>" + htm_menu
	htm_multi = "多指令執行完成<BR>" + htm_menu

	def __init__(self, id = qID, name = qn, descr = qDesc):
		JQuest.__init__(self, id, name, descr)
		for id in self.BuffCEOs:
			self.addStartNpc(id)
			self.addFirstTalkId(id)
			self.addTalkId(id)
		self.startQuestTimer('buff_time', self.wait_time, None, None, True)
		if self.isShowIcon:
			self.si_table = SkillIconTable()
		print self.qn + " loaded"
	
	def getTabHtm(self, selected_tab):
		r = "<table border=0 cellpadding=0 cellspacing=0><tr>"
		for id, bufflist in self.buff_pages:
			r += "<td><button width=30 height=20 fore=\"L2UI_CT1.Tab_DF_Tab"
			if selected_tab == id:
				r += "_Selected"
			else:
				r += "_Unselected"
			r += "\" value=\"" + id + "\" action=\"bypass -h Quest " + self.qn + " " + id + "\"></td>"
		r += "</tr></table>"
		return r
		
	def getBuffPage(self, selected_tab, col=1):
		dialog_width = 270
		c = 0
		skillTable = SkillTable.getInstance()
		r = "<table border=0 cellpadding=0 cellspacing=0 width=" + str(dialog_width) + ">"
		for id, bufflist in self.buff_pages:
			if id == selected_tab:
				r += "<tr>"
				for buff in bufflist:
					skill_id, skill_lv = self.buffToList(buff)
					# r += "<td><button width=16 height=16 fore=\"L2UI.CheckBox%" + buff + "%\"></td>"
					r += "<td><table border=0 cellpadding=0 cellspacing=0  height=38 width="+str(dialog_width/col)+" %" + buff + "%><tr><td>"
					if self.isShowIcon:
						r += "<img src=\"" + self.si_table.getIconName(skill_id) + "\" width=32 height=32></td><td>"
					r += "<a action=\"bypass -h Quest " + self.qn + " " + buff + " " + id + "\">" + skillTable.getInfo(skill_id, skill_lv).getName() + "</a></td></tr></table></td>"
					c += 1
					if c % col == 0:
						r += "</tr><tr>"
				r += "</tr>"
				break
		r += "</table>"
		return self.htm_header + self.getTabHtm(selected_tab) + r + self.htm_footer

	def resetBuff(self, player):
		for e in player.getAllEffects():
			e.exit()
	
	def giveBuff(self, npc, player, skill_id, skill_lv):
		skill = str(skill_id) + "-" + str(skill_lv)
		if skill_lv > 1:
			if skill not in self.allowBuffList: return
		if skill_lv == 1:
			if str(skill_id) not in self.allowBuffList and skill not in self.allowBuffList: return
		#if player.getFirstEffect(skill_id): return
		skill = SkillTable.getInstance().getInfo(skill_id, skill_lv)
		if skill:
			skill.getEffects(npc, player)

	def buffToList(self, buff):
		buff = buff.split("-")
		if len(buff) < 2:
			return [int(buff[0]), 1]
		return [int(buff[0]), int(buff[1])]

	def getMyBuffList(self, st):
		myBuffList = ""
		for id, bufflist in self.buff_pages:
			temp = st.get(id)
			if temp:
				myBuffList += " " + temp
		return myBuffList.strip()
	
	def onBuffTime(self):
		def check(p):
			if p.isInCombat() or p.isDead(): return False
			if isinstance(p, L2PcInstance):
				if p.isInStoreMode() or p.isInCraftMode() or p.isFakeDeath() or not p.isOnline() or p.isFishing(): return False
			return True
		def process(target):
			if check(target):
				myBuffList = None
				if isinstance(target, L2PcInstance):
					st = target.getQuestState(self.qn)
				else:
					st = target.getOwner().getQuestState(self.qn)
				if st:
					myBuffList = self.getMyBuffList(st)
				if myBuffList:
					map(lambda (skill_id, skill_lv): self.giveBuff(npc, target, skill_id, skill_lv), map(lambda b: self.buffToList(b), myBuffList.split()))
				else:
					map(lambda (skill_id, skill_lv): self.giveBuff(npc, target, skill_id, skill_lv), self.default_buff_list)
				target.setCurrentHpMp(target.getMaxHp(), target.getMaxMp())
		spawnTable = SpawnTable.getInstance()
		for npc_id in self.NPCIDs:
			for spawn in spawnTable.getSpawnTable():
				if spawn.getNpcid() == npc_id:
					npc = spawn.getLastSpawn()
					map(process, filter(lambda p: Util.checkIfInShortRadius(self.radius, npc, p, True), npc.getKnownList().getKnownPlayers().values()))
					map(process, filter(lambda p: Util.checkIfInShortRadius(self.radius, npc, p, True), npc.getKnownList().getKnownSummons().values()))
	
	def getPageIdAndList(self, buff_id):
		for id, bufflist in self.buff_pages:
			if buff_id in bufflist:
				return [id, bufflist]
		return None

	def reset(self, st):
		for id, bufflist in self.buff_pages:
			st.unset(id)
			
	def onAdvEvent(self, event, npc, player):
		event = event.split(" ")
		event_count = len(event)
		if event_count > 1:
			self.onAdvEvent(" ".join(event[:-1]), npc, player)
		event = event[-1]
		if event == 'buff_time':
			self.onBuffTime()
			return ''
		st = player.getQuestState(self.qn)
		if event == "reset":
			self.reset(st)
			return self.htm_header + self.htm_reset + self.htm_footer
		if event == "reset_effect":
			self.resetBuff(player)
			return self.htm_header + self.htm_reset_effect + self.htm_footer
		if event.endswith('.htm'):
			return event
		if event in self.allowBuffList:
			page = self.getPageIdAndList(event)
			if not page: return
			page_id, page_bufflist = page
			if event in page_bufflist:
				myBuffList = st.get(page_id)
				if myBuffList:
					myBuffList = myBuffList.split()
					myBuffList = filter(lambda b: b in page_bufflist, myBuffList)
				else:
					myBuffList = []
				if event in myBuffList:
					myBuffList.remove(event)
				else:
					myBuffList.append(event)
				st.set(page_id, ' '.join(myBuffList))
				# if event_count > 1: return self.htm_header + self.htm_multi + self.htm_footer
		try:
			if sys._getframe(1):
				return
		except ValueError:
			pass
		for id, bufflist in self.buff_pages:
			if event == id or event in bufflist:
				return self.getBuffPage(id, self.page_col[id])
		return self.getBuffPage(self.buff_pages[0][0], self.page_col[self.buff_pages[0][0]])

	def onFirstTalk(self, npc, player):
		st = player.getQuestState(self.qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		return self.htm_header + self.htm_intro + self.htm_footer

	#自訂處理 HTM 增加變數轉換
	def showResult(self, player, htmString):
		if not player or not htmString or len(htmString) == 0: return True
		if htmString.endswith(".htm") or htmString.endswith(".html"):
			htmString = JQuest.getHtm(self, player.getHtmlPrefix(), htmString)
		if len(htmString) != 0:
			st = player.getQuestState(self.qn)
			if player.getTarget():
				htmString.replace("%objectId%", str(player.getTarget().getObjectId()))
			htmString = htmString.replace("%playername%", player.getName())		

			myBuffList = self.getMyBuffList(st)
			if myBuffList:
				myBuffList = myBuffList.split()
				myBuffList = filter(lambda b: b in self.allowBuffList, myBuffList)
				for i in myBuffList:
					# htmString = htmString.replace('%'+i+'%', '_checked')
					htmString = htmString.replace('%'+i+'%', 'bgcolor=903000')
			for i in self.allowBuffList:
				htmString = htmString.replace('%'+i+'%', '')
			html = NpcHtmlMessage(player.getTarget().getObjectId())
			html.setHtml(htmString)
			player.sendPacket(html)
		return htmString
AutoBuff()

