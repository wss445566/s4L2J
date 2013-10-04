import sys
from com.l2jserver.gameserver.model.quest import State
from com.l2jserver.gameserver.model.quest import QuestState
from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest

from com.l2jserver.gameserver.datatables import SkillTable	#技能相關
from com.l2jserver.gameserver.model.actor.instance import L2PcInstance

from com.l2jserver.gameserver.handler import VoicedCommandHandler
from com.l2jserver.gameserver.handler import IVoicedCommandHandler

class SkillIconTable:
	skillIconTable = {}
	def __init__(self):
		#f = open("data/scripts/custom/vcbuff/skillgrp.txt", "r") #highFive
		f = open("data/scripts/custom/vcbuff/skillgrp_448.txt", "r") #GoD
		f.readline()
		for line in f:
			temp = line.split("\t")
			#self.skillIconTable[temp[0]] = temp[11] #HighFive
			self.skillIconTable[temp[0]] = temp[19] #GoD
		f.close()
		
	def getIconName(self, skill_id):
		return self.skillIconTable[str(skill_id)]

class VCBuff(JQuest, IVoicedCommandHandler):
	qID = -1
	qn = "vcBuff"
	qDesc = "custom"

	command_split_char = " "

	isShowIcon = True
	#isShowIcon = False #如不需要圖示 設為 False

	default_buff_list = "23241 7091 7090 7089 7088 7093 7092" #如果玩家沒設.. 預設使用 .buff 時 ++的技能 例子 "264 1085-3 7088"

	gm_mix=["23241","7091","7090","7089","7088","7093","7092","23239","23238"] + ["7064","7063","7062","7061","23240"]
	gm_attack=["7094","23243","23242","7041","7042","7043","7044","7048","7050","7053","7054","7056","7057","7059","23246"]
	gm_defend=["7095","23244","23245","7045","7046","7047","7049","7051","7052","7055","7058","23247","23248","7060","7096"]
	
	song = ["264","265","266","267","268","269","270","304","305","306","308","349","363","364","529","764","914","988-3"]
	dance = ["271","272","273","274","275","276","277","307","309","310","311","365","366","530","765","915","989"]
	other1 = ["1356","1352","1542","1388-3","1389-3","1182-3","1189-3","1191-3","1392-3","1393-3","1548-3","1032","1501","1499","1043","1045-6","1048-6","1086-2","1085-3","1078-6","1077-3","1073-2","1068-3","1062-2","1243-3","1242-3","1044-3","1240-3","1040-3","1036-2","1035-4","1033-3","1204-2"]
	other2 = ["1073-2","1304-3","1068-3","1044-3","1043","1040-3","1397-3","1393-3","1033-3","1355","1354","1353","1303-2","1259-4","1257-3","1243-6","1204-2","1504","1503","1035-4","1460","1087-3","1078-6"]
	other3 = ["1068-3","1059-3","1502","1240-3","1242-3","1073-2","1035-4","1392-3","1204-2","1189-3","1357","1531-7","1500","1303-2","1354","1268-4","1040-3","1078-6","1077-3"]
	awaking = ["11830","11820","11821","11822","11823","11824","11825"] + ["11565","11519-4","11523","11530","11521-4","11522","11518-3","11529","11532","11517-4","11525","11520-4","11566","11524"]
	allowBuffList = gm_mix + gm_attack + gm_defend + song + dance + other1 + other2 + other3 + awaking #白名單, GM 允許技能++清單 在名單上的技能 才可以++ (防封包修改 hack)
	buff_pages = [["GM1", gm_mix],["GM2", gm_attack],["GM3", gm_defend],["歌", song],["舞", dance],["昭", other1],["伊", other2],["席", other3],["覺", awaking]]
	page_col = {"GM1":2,"GM2":2,"GM3":2,"歌":3,"舞":3,"昭":3,"伊":3,"席":3,"覺":3}

	BuffCEOs = [100]	#處理設定自訂狀態的 NPC

	htm_header = "<html><body><title>自助++系統設定</title>"
	htm_footer = "</body></html>"
	
	htm_intro_reset = "<a action=\"bypass -h Quest " + qn + " reset\">重置設定</a><BR>"
	htm_intro_full = '<a action="bypass -h Quest %s full">補滿</a><br1>' % qn
	htm_intro_empty = '<a action="bypass -h Quest %s empty">壓血</a><br>' % qn
	htm_intro_reset_effect = "<a action=\"bypass -h Quest " + qn + " reset_effect\">清除狀態</a><BR>"
	htm_intro_preset1 = "<a action=\"bypass -h Quest " + qn + " reset 7063 7088 7089 7090 7091 7092 7093 23241 23238 7048 7056 7057 23246 7049 7060 7096 23247 23248\">戰系預設</a><BR>"
	htm_intro_preset2 = "<a action=\"bypass -h Quest " + qn + " reset 7088 7089 7090 7091 7092 7093 23241 23238 7061 7048 7056 7059 7049 7060 7096 23247 23248 7058\">法系預設</a><BR>"
	htm_intro_list = "<a action=\"bypass -h Quest " + qn + " " + buff_pages[0][0] + "\">進入設定畫面</a><BR>"
	htm_menu = htm_intro_full + htm_intro_empty + htm_intro_reset_effect + htm_intro_preset1 + htm_intro_preset2 + htm_intro_reset + htm_intro_list

	htm_intro = "簡介<BR>.............<BR>" + htm_menu
	htm_reset = "設定已清除<br>" + htm_menu
	htm_reset_effect = "狀態已清除<BR>" + htm_menu

	commands = ["buff", "BUFF"] # 玩家輸入 .buff 觸發
	
	def useVoicedCommand(self, command, player, params):
		def check(p):
			if p.isInCombat():
				p.sendMessage("%s 戰鬥中 不能++" % p.getName())
				return False
			if p.isDead():
				p.sendMessage("%s 已死亡 不能++" % p.getName())
				return False
			if isinstance(p, L2PcInstance):
				if p.isInOlympiadMode():
					p.sendMessage("奧P 不能++")
					return False
				if p.isFakeDeath():
					p.sendMessage("假死中 不能++")
					return False
				if p.isFishing():
					p.sendMessage("釣魚中 不能++")
					return False
				# if not p.isOnline():
					# p.sendMessage("離線能用 .buff? 鬼啊")
					# return False
				if p.isInStoreMode() or p.isInCraftMode():
					p.sendMessage("開店/工房 不能++")
					return False
				if p.getInstanceId() != 0:
					p.sendMessage("副本中 不能++")
					return False
			return True
			
		def process(target):
			if not check(target):
				return
			myBuffList = ""
			if isinstance(target, L2PcInstance):
				st = target.getQuestState(self.qn)
			else:
				st = target.getOwner().getQuestState(self.qn)
			if st:
				myBuffList = self.getMyBuffList(st)
			if len(myBuffList) == 0:
				myBuffList = self.default_buff_list
			map(lambda (skill_id, skill_lv): self.giveBuff(target, target, skill_id, skill_lv), map(lambda b: self.buffToList(b), myBuffList.split()))
				
		process(player)
		pet = player.getPet()
		if pet:
			process(pet)
			
	def getVoicedCommandList(self):
		return self.commands
		
	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		for id in self.BuffCEOs:
			self.addStartNpc(id)
			self.addFirstTalkId(id)
			self.addTalkId(id)
		if self.isShowIcon:
			self.si_table = SkillIconTable()
		VoicedCommandHandler.getInstance().registerHandler(self)
		print "vcBuff registered"
		print "玩家可用 .%s" % " .".join(self.commands)
		print "%s loaded" % self.qn
	
	def getTabHtm(self, selected_tab):
		r = "<table border=0 cellpadding=0 cellspacing=0><tr>"
		for id, bufflist in self.buff_pages:
			r += '<td><button width=30 height=20 fore="%(img)s" value="%(id)s" action="bypass -h Quest %(qn)s %(id)s"></td>' % {'img':['L2UI_CT1.Tab_DF_Tab_Unselected','L2UI_CT1.Tab_DF_Tab_Selected'][selected_tab == id], 'id':id, 'qn':self.qn}
		r += "</tr></table>"
		return r
		
	def getBuffPage(self, selected_tab, col=1):
		dialog_width = 270
		c = 0
		skillTable = SkillTable.getInstance()
		r = "<table border=0 cellpadding=0 cellspacing=0 width=%d>" % dialog_width
		for id, bufflist in self.buff_pages:
			if id == selected_tab:
				r += "<tr>"
				for buff in bufflist:
					skill_id, skill_lv = self.buffToList(buff)
					r += "<td><table border=0 cellpadding=0 cellspacing=0 height=38 width=%d %%%s%%><tr><td>" % (dialog_width/col, buff)
					if self.isShowIcon:
						r += '<img src="%s" width=32 height=32></td><td>' % self.si_table.getIconName(skill_id)
					r += '<a action="bypass -h Quest %s %s %s">%s</a></td></tr></table></td>' % (self.qn, buff, selected_tab, skillTable.getInfo(skill_id, skill_lv).getName())
					c += 1
					if c % col == 0:
						r += "</tr><tr>"
				r += "</tr>"
				break
		r += "</table>"
		return self.htm_header + self.getTabHtm(selected_tab) + r + self.htm_footer

	def giveBuff(self, npc, player, skill_id, skill_lv):
		skill = str(skill_id) + "-" + str(skill_lv)
		if skill_lv > 1:
			if skill not in self.allowBuffList: return
		if skill_lv == 1:
			if str(skill_id) not in self.allowBuffList and skill not in self.allowBuffList: return
		skill = SkillTable.getInstance().getInfo(skill_id, skill_lv)
		if skill:
			skill.getEffects(npc, player)

	def buffToList(self, buff):
		buff = buff.split("-")
		if len(buff) < 2:
			return [int(buff[0]), 1]
		return [int(buff[0]), int(buff[1])]

	def getMyBuffList(self, st):
		l = []
		for id, dummy in self.buff_pages:
			l += [st.get(id)]
		return ' '.join(filter(lambda a: a, l))
	
	def getPageIdAndList(self, buff_id):
		for id, bufflist in self.buff_pages:
			if buff_id in bufflist:
				return [id, bufflist]
		return None
		
	def reset(self, event, npc, player):
		st = player.getQuestState(self.qn)
		for id, bufflist in self.buff_pages:
			st.unset(id)
		return self.htm_header + self.htm_reset + self.htm_footer

	def resetBuff(self, event, npc, player):
		for e in player.getAllEffects():
			e.exit()
		return self.htm_header + self.htm_reset_effect + self.htm_footer

	def setBuff(self, event, npc, player):
		event = event[0]
		try:
			page_id, page_bufflist = self.getPageIdAndList(event)
		except:
			print self.qn, "技能不在允許清單中", event, npc, player
			return
		st = player.getQuestState(self.qn)
		myBuffList = st.get(page_id)
		if myBuffList:
			myBuffList = filter(lambda b: b in page_bufflist, myBuffList.split())
		else:
			myBuffList = []
		if event in myBuffList:
			myBuffList.remove(event)
		else:
			myBuffList.append(event)
		st.set(page_id, ' '.join(myBuffList))
				
	def genBuffPage(self, event, npc, player):
		event = event[0]
		for id, bufflist in self.buff_pages:
			if event == id:
				return self.getBuffPage(id, self.page_col[id])
		print self.qn, "不明請求", event, npc, player
		
	def full(self, event, npc, player):
		player.setCurrentCp(player.getMaxCp())
		player.setCurrentHpMp(player.getMaxHp(), player.getMaxMp())
		return self.firstpage()

	def empty(self, event, npc, player):
		player.setCurrentCp(1)
		player.setCurrentHp(1)
		return self.firstpage()
		
	htm_commands = {"reset":reset, "reset_effect":resetBuff, "full":full, "empty":empty}
	for c in allowBuffList:
		htm_commands[c] = setBuff
	for c, dummy in buff_pages:
		htm_commands[c] = genBuffPage
		
	def firstpage(self):
		return self.htm_header + self.htm_intro + self.htm_footer

	def process_command(self, event, npc, player):
		t = event.split()
		if t and t[0] in self.htm_commands.keys():
			return self.htm_commands[t[0]](self, t, npc, player)
		return self.firstpage()
	
	def onAdvEvent(self, event, npc, player):
		if event.endswith('.htm'):
			return event
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
		
	def showResult(self, player, htmString):
		if htmString and len(htmString):
			st = player.getQuestState(self.qn)
			myBuffList = self.getMyBuffList(st)
			if myBuffList:
				myBuffList = filter(lambda b: b in self.allowBuffList, myBuffList.split())
				for i in myBuffList:
					htmString = htmString.replace('%'+i+'%', 'bgcolor=903000')
			for i in self.allowBuffList:
				htmString = htmString.replace('%'+i+'%', '')
		return JQuest.showResult(self, player, htmString)

VCBuff()