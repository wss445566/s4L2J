#from com.l2jserver.gameserver.model.quest import State
from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest

from com.l2jserver import L2DatabaseFactory

from com.l2jserver.gameserver.datatables import ItemTable

def getRGB(start, stop, steps, index):
	rs = ((start >> 16 & 0xff) - (stop >> 16 & 0xff)) // steps
	gs = ((start >> 8 & 0xff) - (stop >> 8 & 0xff)) // steps
	bs = ((start & 0xff) - (stop & 0xff)) // steps
	red = (start >> 16 & 0xff) - rs * index
	green = (start >> 8 & 0xff) - gs * index
	blue = (start & 0xff) - bs * index
	return (red << 16 | green << 8 | blue) & 0xffffff

class Ranka(JQuest):
	qID = -1
	qn = "Ranka"
	qDesc = "custom"
	
	NPCID = 100 #觸發任務的 NPC
	number_of_record = 15 #最多顯示多少行記錄
	
	blacklist = ["GM"] #角色名稱黑名單 不顯示這些角色的數據 可多個 ["GM","隱藏人物","老大","GM2號"]
	blacklist = ",".join(['"%s"' % x for x in blacklist])
	if len(blacklist) == 0:
		blacklist = '""'
	
	htm_header = "<html><body><title>防具強化排行</title>"
	htm_footer = "</body></html>"

	items = {
	}

	for i in ItemTable.getInstance().getAllArmorsId():
		item = ItemTable.getInstance().getTemplate(i)
		if not item.isEnchantable():
			continue
		t = item.getBodyPart()
		if t not in items:
			items[t] = []
		items[t] += [i]
	
	all_w_string = ",".join([str(x) for x in ItemTable.getInstance().getAllArmorsId() if ItemTable.getInstance().getTemplate(x).isEnchantable()])
	
	item_count_sql = "select COALESCE(`characters`.`char_name`, `clan_data`.`clan_name`) as name, `items`.`item_id` as i, `items`.`enchant_level` as e  from `items` left join `characters` on `items`.`owner_id` = `characters`.`charId` left join `clan_data` on `items`.`owner_id` = `clan_data`.`clan_id` where `items`.`item_id` in (%s) having name not in (%s) order by e desc limit %d;"

	def item_count_cb(r):
		i = r.getLong("i")
		item = ItemTable.getInstance().getTemplate(i)
		color1 = getRGB(0xFFFF00, 0xFF00FF, Ranka.number_of_record, r.getRow())
		color2 = getRGB(0xff0000, 0xFFFF00, Ranka.number_of_record, r.getRow())
		return (
			color1, r.getRow(),
			color2, r.getString("name"),
			color2, item.getName(),
			color2, r.getLong("e")
		)
		
	pages_header = "<table><tr><td width=32>排名</td><td width=110>角色名稱</td><td width=150>%s</td><td width=40>強化</td></tr>"
	pages_body = '<tr><td><font color=%06x>%d</font></td><td><font color=%06x>%s</font></td><td><font color=%06x>%s</font></td><td><font color=%06x>%d</font></td></tr>'
	pages_footer = "</table>"
	pages = [
		{
			"id":"全部", 
			"sql":item_count_sql % (all_w_string, blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "全部防具",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"頭", 
			"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("head")]]), blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "頭",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"上衣", 
			"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("chest")]]), blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "上衣",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"下衣", 
			"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("legs")]]), blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "下衣",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"連身", 
			"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("fullarmor")]]), blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "連身",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"手", 
			"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("gloves")]]), blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "手",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"腳", 
			"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("feet")]]), blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "腳",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"斗蓬", 
			"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("back")]]), blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "斗蓬",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"內衣", 
			"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("underwear")]]), blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "內衣",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"腰帶", 
			"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("belt")]]), blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "腰帶",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"耳", 
			"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("rear;lear")]]), blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "耳",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"項鍊", 
			"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("neck")]]), blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "項鍊",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"戒指", 
			"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("rfinger;lfinger")]]), blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "戒指",
			"footer":pages_footer,
			"body":pages_body
		}
		,{
			"id":"左手", 
			"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("lhand")]]), blacklist, number_of_record,), 
			"cb":item_count_cb,
			"header":pages_header % "左手",
			"footer":pages_footer,
			"body":pages_body
		}
		#,{
		#	"id":"手鐲", 
		#	"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("rbracelet")]]), blacklist, number_of_record,), 
		#	"cb":item_count_cb,
		#	"header":pages_header % "手鐲",
		#	"footer":pages_footer,
		#	"body":pages_body
		#}
		#,{
		#	"id":"頭飾", 
		#	"sql":item_count_sql % (",".join([str(x) for x in items[ItemTable._slots.get("hairall")]]), blacklist, number_of_record,), 
		#	"cb":item_count_cb,
		#	"header":pages_header % "頭飾",
		#	"footer":pages_footer,
		#	"body":pages_body
		#}
	]

	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
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
		except:
			pass
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
				r += '<td><button width=40 height=20 fore="L2UI_CT1.Tab_DF_Tab%s" value="%s" action="bypass -h Quest %s %s"></td>' % (["_Unselected","_Selected"][pageid == a["id"]], a["id"], self.qn, a["id"])
				c += 1
				if c % 7 == 0:
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
		#st = player.getQuestState(self.qn)
		#if not st:
		#	st = self.newQuestState(player)
		#	st.setState(State.STARTED)
		return self.showPages()
		
Ranka()
