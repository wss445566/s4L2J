import sys
from com.l2jserver.gameserver.model.quest import State
from com.l2jserver.gameserver.model.quest import QuestState
from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest

from com.l2jserver import L2DatabaseFactory

import time

class Rank(JQuest):
	qID = -1
	qn = "Rank"
	qDesc = "custom"
	
	NPCID = 103 #觸發任務的 NPC
	number_of_record = 15 #最多顯示多少行記錄

	blacklist = [] #角色名稱黑名單 不顯示這些角色的數據 可多個 ["GM","隱藏人物","老大","GM2號"]
	blacklist = ",".join(['"%s"' % x for x in blacklist])
	if len(blacklist) == 0:
		blacklist = '""'
	
	htm_header = "<html><body><title>排行榜</title>"
	htm_footer = "</body></html>"
	
	item_count_sql = "select sum(`count`) as c, COALESCE(`characters`.`char_name`, `clan_data`.`clan_name`) as name from `items` left join `characters` on `items`.`owner_id` = `characters`.`charId` left join `clan_data` on `items`.`owner_id` = `clan_data`.`clan_id` where `items`.`item_id` = %d group by `items`.`owner_id` having name not in (%s) order by c desc limit %d;"
	
	def item_count_cb(r):
		return (r.getRow(),r.getString("name"),r.getLong("c"))

	pages_header = "<table><tr><td width=32>排名</td><td width=150>角色名稱</td><td width=150>%s</td></tr>"
	pages_body = "<tr><td>%d</td><td>%s</td><td>%d</td></tr>"
	pages_footer = "</table>"
	pages = [
		{
			"id":"金幣", 
			"sql":item_count_sql % (57, blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "金幣",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"古幣", 
			"sql":item_count_sql % (5575, blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "古代的金幣",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"慶典", 
			"sql":item_count_sql % (6673, blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "慶典金幣",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"藍色", 
			"sql":item_count_sql % (4355, blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "藍色伊娃",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"金色", 
			"sql":item_count_sql % (4356, blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "金色殷海薩",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"銀色", 
			"sql":item_count_sql % (4357, blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "銀色席琳",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"血紅", 
			"sql":item_count_sql % (4358, blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "血紅色帕格立歐",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"夢幻", 
			"sql":item_count_sql % (13067, blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "夢幻島代幣",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"金塊", 
			"sql":item_count_sql % (3470, blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "金塊",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"光彩", 
			"sql":item_count_sql % (6393, blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "活動-光彩紀念章",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"任務", 
			"sql":"SELECT `char_name`, count(1) as c FROM `character_quests` left join `characters` on `character_quests`.`charId` = `characters`.`charId` where `character_quests`.`var` = '<state>' and `character_quests`.`value` = 'Completed' and `char_name` not in (%s) group by `character_quests`.`charId` order by c desc limit %d;" % (blacklist, number_of_record,), 
			"cb":lambda r: (r.getRow(),r.getString("char_name"),r.getLong("c")),
			"header":pages_header % "任務完成數",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"PVP", 
			"sql":"SELECT `char_name`, `pvpkills` FROM `characters` where `char_name` not in (%s) order by `pvpkills` desc limit %d;" % (blacklist, number_of_record,), 
			"cb":lambda r: (r.getRow(),r.getString("char_name"),r.getLong("pvpkills")),
			"header":pages_header % "PVP次數",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"PK", 
			"sql":"SELECT `char_name`, `pkkills` FROM `characters` where `char_name` not in (%s) order by `pkkills` desc limit %d;" % (blacklist, number_of_record,), 
			"cb":lambda r: (r.getRow(),r.getString("char_name"),r.getLong("pkkills")),
			"header":pages_header % "PK次數",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"性向", 
			"sql":"SELECT `char_name`, `karma` FROM `characters` where `char_name` not in (%s) order by `karma` desc limit %d;" % (blacklist, number_of_record,), 
			"cb":lambda r: (r.getRow(),r.getString("char_name"),r.getLong("karma")),
			"header":pages_header % "性向",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"聲望", 
			"sql":"SELECT `char_name`, `fame` FROM `characters` where `char_name` not in (%s) order by `fame` desc limit %d;" % (blacklist, number_of_record,), 
			"cb":lambda r: (r.getRow(),r.getString("char_name"),r.getLong("fame")),
			"header":pages_header % "個人聲望",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"在線", 
			"sql":"SELECT `char_name`, `onlinetime` FROM `characters` where `char_name` not in (%s) order by `onlinetime` desc limit %d;" % (blacklist, number_of_record,), 
			"cb":lambda r: (r.getRow(),r.getString("char_name"),long(r.getLong("onlinetime")/60/60/24)),
			"header":pages_header % "累計在線(天)",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"經驗", 
			"sql":"SELECT `char_name`, `exp` FROM `characters` where `char_name` not in (%s) order by `exp` desc limit %d;" % (blacklist, number_of_record,), 
			"cb":lambda r: (r.getRow(),r.getString("char_name"),r.getLong("exp")),
			"header":pages_header % "經驗值",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"等級", 
			"sql":"SELECT `char_name`, `level` FROM `characters` where `char_name` not in (%s) order by `exp` desc limit %d;" % (blacklist, number_of_record,), 
			"cb":lambda r: (r.getRow(),r.getString("char_name"),r.getLong("level")),
			"header":pages_header % "等級",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"禁言", 
			"sql":"SELECT `char_name`, `punish_timer` FROM `characters` where `punish_level` = 1 and `char_name` not in (%s) order by `punish_timer` desc limit %d;" % (blacklist, number_of_record,), 
			"cb":lambda r: (r.getRow(),r.getString("char_name"),r.getLong("punish_timer")/60000),
			"header":pages_header % "還要禁多久(分鐘)",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"監禁", 
			"sql":"SELECT `char_name`, `punish_timer` FROM `characters` where `punish_level` = 2 and `char_name` not in (%s) order by `punish_timer` desc limit %d;" % (blacklist, number_of_record,), 
			"cb":lambda r: (r.getRow(),r.getString("char_name"),r.getLong("punish_timer")/60000),
			"header":pages_header % "還要禁多久(分鐘)",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"停權", 
			"sql":"SELECT `char_name`, `lastAccess` FROM `characters` where `accesslevel` = -1 and `char_name` not in (%s) order by `lastAccess` desc limit %d;" % (blacklist, number_of_record,), 
			"cb":lambda r: (r.getRow(),r.getString("char_name"),time.localtime(float(r.getLong("lastAccess")/1000))[1],time.localtime(float(r.getLong("lastAccess")/1000))[2]),
			"header":pages_header % "最後登陸",
			"footer":pages_footer,
			"body":"<tr><td>%d</td><td>%s</td><td>%d月%d日</td></tr>"
		}
	]

	def __init__(self, id = qID, name = qn, descr = qDesc):
		JQuest.__init__(self, id, name, descr)
		self.addStartNpc(self.NPCID)
		self.addFirstTalkId(self.NPCID)
		self.addTalkId(self.NPCID)
		print "%s loaded" % (self.qn,)
		
	def db_query(self, sql, cb):
		r = []
		con, statement, rset = None, None, None
		try:
			con = L2DatabaseFactory.getInstance().getConnection()
			statement = con.prepareStatement(sql)
			rset = statement.executeQuery()
			while rset.next():
				try:
					r += [cb(rset)]
				except:
					pass
		finally:
			if rset:
				rset.close()
			if statement:
				statement.close()
			if con:
				L2DatabaseFactory.close(con)
		return r
				
	def showPages(self, pageid = pages[0]["id"]):
		def showTab():
			c = 0
			r = "<table border=0 cellpadding=0 cellspacing=0><tr>"
			for a in self.pages:
				r += '<td><button width=31 height=20 fore="L2UI_CT1.Tab_DF_Tab%s" value="%s" action="bypass -h Quest %s %s"></td>' % (["_Unselected","_Selected"][pageid == a["id"]], a["id"], self.qn, a["id"])
				c += 1
				if c % 9 == 0:
					r += "</tr><tr>"
			r += "</tr></table>"
			return r
		r = showTab()
		for a in self.pages:
			if pageid == a["id"]:
				r += a["header"]
				for record in self.db_query(a["sql"], a["cb"]):
					r += a["body"] % record
				r += a["footer"]
				break
		return self.htm_header + r + self.htm_footer
		
	def onAdvEvent(self, event, npc, player):
		for a in self.pages:
			if a["id"] == event:
				return self.showPages(event)
		return self.onFirstTalk(npc, player)
		
	def onFirstTalk(self, npc, player):
		st = player.getQuestState(self.qn)
		if not st:
			st = self.newQuestState(player)
			st.setState(State.STARTED)
		return self.showPages()
		
Rank()
