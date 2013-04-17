import sys
from com.l2jserver.gameserver.model.quest		import State
from com.l2jserver.gameserver.model.quest		import QuestState
from com.l2jserver.gameserver.model.quest.jython	import QuestJython as JQuest

from com.l2jserver.gameserver.instancemanager import GrandBossManager
from com.l2jserver.gameserver.instancemanager import QuestManager

from com.l2jserver.gameserver.datatables import DoorTable #巴列斯要用
from com.l2jserver.gameserver.network.serverpackets import Earthquake #地龍要用
from com.l2jserver.gameserver.model import L2World #地龍要用

from com.l2jserver.gameserver.datatables import SpawnTable
from com.l2jserver.gameserver.instancemanager import InstanceManager
from com.l2jserver.gameserver.datatables import ItemTable

import time
from com.l2jserver import L2DatabaseFactory

class GBreset(JQuest):
	qID = -1
	qn = "GBreset"
	qDesc = "custom"
	
	NPCID = [103] #觸發任務的 NPC 可修改.. 可以多 ID 例如 [100,102,103]
	htm_header = "<html><body><title>頭目首領重置系統</title>"
	htm_footer = "</body></html>"
	htm_no_rights = "<center>抱歉 你沒有權限重置</center>"
	htm_not_enough_item = "所需道具不足<BR>"

	zaken_INSTANCEID_NIGHT = 114
	zaken_INSTANCEID_DAY = 133
	zaken_INSTANCEID_DAY83 = 135
	
	reset_instance = [
		["札肯(夜)", zaken_INSTANCEID_NIGHT, [[57,1]]]
		,["札肯(日)", zaken_INSTANCEID_DAY, [[57,1]]]
		,["札肯(上級)", zaken_INSTANCEID_DAY83, [[57,1]]]
		,["芙琳泰沙", 136, [[57,1]]]
		,["巴爾勒", 10, [[57,1]]]
	]
	
	available = "可挑戰"
	waiting = "等待開始"
	fighting = "玩家挑戰中"
	dead = "死亡"
	unknow = "不明狀態"
	
	def general_unlock(self, arg):
		quest_name, unlock_timer_name = arg
		if len(quest_name) > 0:
			q = QuestManager.getInstance().getQuest(quest_name)
			if len(unlock_timer_name) > 0:
				try:
					q.cancelQuestTimers(unlock_timer_name)
					q.startQuestTimer(unlock_timer_name, 1000, None, None)
				except:
					pass

	def antharas_unlock(self, arg):
		boss_id = arg[0]
		GrandBossManager.getInstance().setBossStatus(boss_id, 0)
		for p in L2World.getInstance().getAllPlayersArray():
			p.broadcastPacket(Earthquake(185708,114298,-8221,20,10))

	def beleth_unlock(self, arg):
		GrandBossManager.getInstance().setBossStatus(29118, 0)
		DoorTable.getInstance().getDoor(20240001).openMe()
		
	def icefairysirra_unlock(self):
		q = QuestManager.getInstance().getQuest("IceFairySirra")
		self.saveGlobalQuestVar("Sirra_Respawn", "0")
		try:
			q.cancelQuestTimers("respawn")
			q.startQuestTimer("respawn", 1000, None, None)
		except:
			pass
			
	def reset_queststate(self, player, quest_name):
		qs = player.getQuestState(quest_name)
		if qs:
			qs.setState(State.STARTED);
			qs.exitQuest(True)
			if quest_name == "10286_ReunionWithSirra":
				q = QuestManager.getInstance().getQuest("10286_ReunionWithSirra")
				st = player.getQuestState(quest_name)
				if not st:
					st = q.newQuestState(player)
					st.setState(State.STARTED)
				st.set("cond", "1")
				st.set("cond", "2")
				st.set("cond", "3")
				st.set("cond", "4")
				st.set("cond", "5")
				st.set("Ex", "2")
				st.set("progress", "2")

	gb_list = dict({
	29001:["巨蟻女王", [available, dead], [general_unlock, "queen_ant", "queen_unlock"]], 
	29006:["核心", [available, dead], [general_unlock, "core", "core_unlock"]],
	29014:["奧爾芬", [available, dead], [general_unlock, "orfen", "orfen_unlock"]],
	29019:["安塔瑞斯", [available, waiting, fighting, dead], [antharas_unlock, 29019]],
	29020:["巴溫", [available, fighting, dead], [general_unlock, "baium", "baium_unlock"]],
	#29022:["札肯", [available, dead], [general_unlock, "zaken", "zaken_unlock"]],
	29028:["巴拉卡斯", [available, waiting, fighting, dead], [general_unlock, "valakas", "valakas_unlock"]],
	#29045:["芙琳泰沙", [available, dead], [general_unlock, "", ""]],
	29065:["賽爾蘭", [available, waiting, fighting, dead], [general_unlock, "sailren", "sailren_unlock"]],
	29066:["安塔瑞斯", [available, waiting, fighting, dead], [antharas_unlock, 29066]],
	29067:["安塔瑞斯", [available, waiting, fighting, dead], [antharas_unlock, 29067]],
	29068:["安塔瑞斯", [available, waiting, fighting, dead], [antharas_unlock, 29068]],
	#29099:["巴爾勒", [available, dead], [general_unlock, "", ""]],
	29118:["巴列斯", [available, waiting, fighting, dead], [beleth_unlock]]
	})
	

	def __init__(self, id = qID, name = qn, descr = qDesc):
		JQuest.__init__(self, id, name, descr)
		for id in self.NPCID:
			self.addStartNpc(id)
			self.addFirstTalkId(id)
			self.addTalkId(id)
		print "Init:" + self.qn + " loaded"

	def getNpcInstance(self, npc_id):
		spawnTable = SpawnTable.getInstance()
		for spawn in spawnTable.getSpawnTable():
			if spawn.getNpcid() == npc_id:
				return spawn.getLastSpawn()
		return None
		
	def get_STEWARD_state(self):
		npc = self.getNpcInstance(32029) #芙蕾雅的執事
		if npc:
			return npc.isBusy()
		return None
		
	def get_GB_respawn_time(self):
		r = {}
		con, statement, rset = None, None, None
		try:
			con = L2DatabaseFactory.getInstance().getConnection()
			statement = con.prepareStatement("select `boss_id`, `respawn_time` from `grandboss_data`;")
			rset = statement.executeQuery()
			while rset.next():
				r[rset.getInt("boss_id")] = rset.getLong("respawn_time")
		finally:
			if rset:
				rset.close()
			if statement:
				statement.close()
			if con:
				L2DatabaseFactory.close(con)
		return r
		
	def get_gbrt_string(self, rt):
		try:
			r = long(long(rt)/1000 - time.time())
			s = long(r) % 60
			m = (long(r) / 60) % 60
			h = (long(r) / (60*60)) % 24
			d = (long(r) / (60*60*24))
			return "%d日 %d時 %d分 %d秒" % (d, h, m, s)
		except:
			return "沒有時間數據"
		
		
	def htm_list(self):
		gbrt = self.get_GB_respawn_time()
		r = ""
		for key in self.gb_list.keys():
			boss_name, boss_status, dummy = self.gb_list[key]
			curr_status = GrandBossManager.getInstance().getBossStatus(key)
			if len(boss_status)-1 == curr_status:
				r += "<tr><td width=100>" + boss_name + "(" + str(key)+ ")" + "</td><td width=150><a action=\"bypass -h Quest " + self.qn + " " + str(key)+ "\">" + self.get_gbrt_string(gbrt[key]) + "</a></td></tr>"
			else:
				r += "<tr><td width=100>" + boss_name + "(" + str(key)+ ")" + "</td><td>" + boss_status[curr_status] + "</td></tr>"
		# if self.get_STEWARD_state():
			# r += "<tr><td width=100>" + "芙蕾雅的執事" + "</td><td><a action=\"bypass -h Quest " + self.qn + " " + "IFS" + "\">" + " 忙 " + "</a></td></tr>"
		# else:
			# r += "<tr><td width=100>" + "芙蕾雅的執事" + "</td><td>" + "閒" + "</td></tr>"
		r += "<tr><td width=100>" + "與希露再次見面" + "</td><td><a action=\"bypass -h Quest " + self.qn + " " + "reset 10286_ReunionWithSirra" + "\">" + " 重置任務 " + "</a></td></tr>"
		for instance_name, instance_id, require in self.reset_instance:
			r += "<tr><td width=100>" + instance_name + "</td><td><a action=\"bypass -h Quest " + self.qn + " " + "show_require " + str(instance_id) + "\">" + " 重置副本時間" + "</a></td></tr>"
		return self.htm_header + "<table>" + r + "</table>" + self.htm_footer

		
	def show_require_item(self, instance_id):
		r = "需要道具清單<br>"
		for instance_name,rinstance_id,require_list in self.reset_instance:
			if str(rinstance_id) == instance_id:
				for itemid, count in require_list:
					item_name = ItemTable.getInstance().getTemplate(itemid).getName()
					r += "%s %d 個<br1>" % (item_name, count)
				break
		r += '<a action="bypass -h Quest %s del_instance %d">確認重置 %s</a>' % (self.qn, instance_id, instance_name)
		return r
		
		
	def check_require_item(self, player, require_list):
		st = player.getQuestState(self.qn)
		if not st: return False
		for itemid, count in require_list:
			if st.getQuestItemsCount(itemid) < count:
				item_name = ItemTable.getInstance().getTemplate(itemid).getName()
				player.sendMessage("道具不足:" + item_name + " 需要 " + str(count))
				return False
		return True

	def deleteInstanceTime(self, player_oid, instance_id):
		st = player.getQuestState(self.qn)
		if not st: return False
		for dummy,rinstance_id,require in self.reset_instance:
			if str(rinstance_id) == instance_id:
				if not self.check_require_item(player, require):
					return self.htm_header + self.htm_not_enough_item + self.htm_footer
				map(lambda (item_id, count): st.takeItems(item_id, count), require)
				InstanceManager.getInstance().deleteInstanceTime(player.getObjectId(), rinstance_id)
				break
		
	def onAdvEvent(self, event, npc, player):
		try:
			nEvent = int(event)
		except:
			nEvent = -1
			
		if nEvent in self.gb_list.keys():
			if player.isGM():
				self.gb_list[nEvent][2][0](self, self.gb_list[nEvent][2][1:])
			else:
				return self.htm_header + self.htm_no_rights + self.htm_footer
		if event == "IFS":
			if player.isGM():
				self.icefairysirra_unlock()
			else:
				return self.htm_header + self.htm_no_rights + self.htm_footer
		if event.startswith("reset "):
			event = event.split()[1]
			self.reset_queststate(player, event)
		if event.startswith("show_require "):
			event = event.split()[1]
			return self.htm_header + self.show_require_item(event) + self.htm_footer
		if event.startswith("del_instance "):
			st = player.getQuestState(self.qn)
			event = event.split()[1]
			for dummy,instance_id,require in self.reset_instance:
				if str(instance_id) == event:
					if not self.check_require_item(player, require):
						return self.htm_header + self.htm_not_enough_item + self.htm_footer
					map(lambda (item_id, count): st.takeItems(item_id, count), require)	
					InstanceManager.getInstance().deleteInstanceTime(player.getObjectId(), int(event))
					break
		return self.onFirstTalk(npc, player)
		
	def onFirstTalk(self, npc, player):
		st = player.getQuestState(self.qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		return self.htm_list()
		
GBreset()
