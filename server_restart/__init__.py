import sys
from com.l2jserver.gameserver.model.quest import State
from com.l2jserver.gameserver.model.quest import QuestState
from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest
from com.l2jserver.gameserver import Shutdown
from com.l2jserver.gameserver import GmListTable

qn = "server_restart"

NPCS_ID = [9922350] #觸發 NPC ID
allow_server_restart_player_name_list = ["畜生", "生畜", "畜性", "GM", "玩家"] #授權可以重新啟動伺服器的玩家/GM名字

class server_restart(JQuest):
	def __init__(self, id, name, descr):
		JQuest.__init__(self, id, name, descr)

	def c_to_l2html(self, text):
		text = text.replace("\n", "<br>")
		return "<html><body>" + text + "</body></html>"
		
	def onFirstTalk(self, npc, player):
		if GmListTable.getInstance().isGmOnline(True):
			return self.c_to_l2html("GM 在線中\n重啟功能暫時無效\n只有 GM 不在線時才能使用此功能")
		return self.c_to_l2html("<a action=\"bypass -h Quest server_restart namelist\">查詢授權重啟玩家名單</a>\n<a action=\"bypass -h Quest server_restart request\">要求重新啟動</a>")
			
	def onAdvEvent(self, event, npc, player):
		e = event.split()
		if e[0] == "restart":
			try:
				delay = int(e[1])
			except:
				delay = 180
			if delay <= 0 or delay > 300:
				return self.c_to_l2html("輸入值錯誤\n有效範圍 1-300")
			if player.getName() in allow_server_restart_player_name_list:
				Shutdown.getInstance().startShutdown(player, delay, True)
				return self.c_to_l2html("伺服器將於 " + str(delay) + "後重新啟動")
			else:
				return self.c_to_l2html(player.getName() + " 你沒有重新啟動伺服器的權限")
		if e[0] == "namelist":
			return self.c_to_l2html("以下玩家已授權可以重新啟動伺服器\n" + reduce(lambda a, b: a + "\n" + b, allow_server_restart_player_name_list))
		if e[0] == "request":
			return self.c_to_l2html("多少秒後重新啟動伺服器<edit var=\"value\" width=75 height=12><a action=\"bypass -h Quest server_restart restart $value\">確認重啟</a>")


QUEST = server_restart(-1, qn, "Custom")

for id in NPCS_ID:
	QUEST.addStartNpc(id)
	QUEST.addFirstTalkId(id)
	QUEST.addTalkId(id)

print "server_restart loaded"
