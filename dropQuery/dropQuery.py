from com.l2jserver.gameserver.model.quest.jython import QuestJython as JQuest
from com.l2jserver.gameserver.datatables import ItemTable
from com.l2jserver.gameserver.datatables import NpcTable
from java.util.logging import Logger

def qsort(list, l, ge):
    if list == []: 
        return []
    else:
        pivot = list[0]
        lesser = qsort([x for x in list[1:] if l(x, pivot)], l, ge)
        greater = qsort([x for x in list[1:] if ge(x, pivot)], l, ge)
        return lesser + [pivot] + greater	
		
class Quest(JQuest):
	qID = -1
	qn = "dropQuest"
	qDesc = "custom"
	NPCID = 100
	allnpc = NpcTable.getInstance().getAllMonstersOfLevel(range(100))
	
	htm_header = """<html><body scroll=no><title>物品掉率查詢</title><table border=0 cellpadding=0 cellspacing=0 width=294 height=359>"""
	htm_search = """<tr><td><table border=0 cellpadding=0 cellspacing=0 height=23 width=294 bgcolor=666666>
	<tr>
	<td>物品名稱</td>
	<td><edit var="value" width=100></td>
	<td><a action="bypass -h Quest %s search $value">搜尋</a></td>
	</tr>
	</table></td></tr>""" % qn
	htm_footer = """</table></body></html>"""
	
	def log(self, m):
		l = Logger.getLogger(self.qn)
		l.info(m)

	def getItemByName(self, name):
		it = ItemTable.getInstance()
		r = []
		for id in xrange(it.getArraySize()):
			t = it.getTemplate(id)
			if t:
				if name in t.getName():
					r.append(t)
		return r
		
	def getNpcByDropItem(self, itemid, issweep):
		r = []
		for npc in self.allnpc:
			dd = npc.getDropData()
			if len(dd):
				for dc in dd:
					if issweep == dc.isSweep():
						for item in dc.getAllDrops():
							if item.getItemId() == itemid:
								r.append([npc, item.getChance()])
		return r
	
	def __init__(self, id = qID, name = qn, descr = qDesc):
		self.qID, self.qn, self.qDesc = id, name, descr
		JQuest.__init__(self, id, name, descr)
		self.addStartNpc(self.NPCID)
		self.addFirstTalkId(self.NPCID)
		self.addTalkId(self.NPCID)
		self.log("Init:" + self.qn + " loaded")

	def onAdvEvent(self, event, npc, player):
		e = event.split()
		if e[0] == "search":
			if len(e) > 1:
				r = """<tr><td>%s</td></tr>""" % ("_"*49)
				r += """<tr><td><table border=0 cellpadding=0 cellspacing=0 bgcolor=330000 width=294 height=330>""" 
				c = 0
				for itemt in self.getItemByName(e[1]):
					r += """<tr><td><a action="bypass -h Quest %(qn)s searchdid %(id)d"> 掉落 </a></td><td><a action="bypass -h Quest %(qn)s searchsid %(id)d"> 回收 </a></td><td>%(name)s</td></tr>""" % {"qn":self.qn, "id":itemt.getItemId(), "name":itemt.getName()}
					c += 1
					if c >= 20: break
				r += """</table></td></tr>"""
				return self.htm_header + self.htm_search + r + self.htm_footer
		elif e[0] == "searchdid" or e[0] == "searchsid":
			if len(e) > 1:
				d = self.getNpcByDropItem(int(e[1]), e[0] == "searchsid")
				#d = qsort(d, lambda a, b:a[1] < b[1], lambda a, b:a[1] >= b[1])
				d = qsort(d, lambda a, b:a[1] >= b[1], lambda a, b:a[1] < b[1])
				r = """<tr><td>%d</td></tr>""" % (len(d))
				r += """<tr><td><table border=0 cellpadding=0 cellspacing=0 bgcolor=330000 width=294 height=330>""" 
				c = 0
				for npc, chance in d:
					r += """<tr><td>%d %s %0.4f%%</td></tr>""" % (npc.getLevel(), npc.getName(), chance * 1.0 / 10000)
					c += 1
					if c >= 20: break
				r += """</table></td></tr>"""
				return self.htm_header + self.htm_search + r + self.htm_footer
		return self.onFirstTalk(npc, player)
		
	def onFirstTalk(self, npc, player):
		return self.htm_header + self.htm_search + self.htm_footer
Quest()
