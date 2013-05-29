# -*- coding: utf_8 -*-
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET
import codecs

material = {
    "0":"fish"
    ,"1":"oriharukon"
    ,"2":"mithril"
    ,"3":"gold"
    ,"4":"silver"
    ,"6":"bronze"
    ,"8":"steel"
    ,"13":"wood"
    ,"14":"bone"
    ,"17":"cloth"
    ,"18":"paper"
    ,"19":"leather"
    ,"23":"crystal"
    ,"33":"cotton"
    ,"37":"cobweb"
    ,"38":"dyestuff"
    ,"46":"scale_of_dragon"
    ,"47":"adamantaite"
    ,"48":"blood_steel"
    ,"49":"chrysolite"
    ,"50":"damascus"
    ,"51":"fine_steel"
    ,"52":"horn"
}
bodypart = {
    "0":"underwear"
    ,"1":"rear;lear"
    ,"3":"neck"
    ,"4":"rfinger;lfinger"
    ,"6":"head"
    ,"7":"lrhand"
    ,"8":"onepiece"
    ,"9":"alldress"
    ,"10":"hairall"
    #,"12":"" #22383, 22384 萬聖夜騎乘掃帚
    ,"19":"waist"
    ,"20":"gloves"
    ,"21":"chest"
    ,"22":"legs"
    ,"23":"feet"
    ,"24":"back"
    ,"25":"hair"
    ,"26":"hair2"
    ,"27":"rhand"
    ,"28":"lhand"
}
armor_type = {
    "1":"light"
    ,"2":"heavy"
    ,"3":"magic"
    ,"4":"sigil"
}
crystal_type = {
    "1":"d"
    ,"2":"c"
    ,"3":"b"
    ,"4":"a"
    ,"5":"s"
    ,"6":"s80"
    ,"8":"r"
    ,"9":"r95" #r95
    ,"10":"r99" #r99
    #,"11":"s84" #13539 大師余義的魔杖
    ,"0":"none"
}
weapon_type = {
    "1":"sword"
    ,"2":"blunt"
    ,"3":"dagger"
    ,"4":"pole"
    ,"5":"dualfist"
    ,"6":"bow"
    ,"7":"etc"
    ,"8":"dual"
    ,"10":"fishingrod"
    ,"11":"rapier"
    ,"12":"crossbow"
    ,"13":"ancientsword"
    ,"15":"dualdagger"
    ,"17":"crossbow" #應該是雙手弩
    ,"18":"DualBlunt"
    #,"17":u"雙手弩"
    #,"18":u"雙鈍器"
    #,"0":"盾"
}
etcitem_type = {
    "1":"scroll"
    ,"2":"arrow"
    ,"3":"potion"
    ,"5":"recipe"
    ,"6":"material"
    ,"7":"pet_collar"
    ,"8":"castle_guard"
    ,"9":"dye"
    ,"10":"seed"
    ,"11":"seed2"
    ,"12":"harvest"
    ,"13":"lotto"
    ,"14":"race_ticket"
    ,"15":"ticket_of_lord"
    ,"16":"lure"
    ,"17":"crop"
    ,"18":"maturecrop"
    ,"19":"scrl_enchant_wp"
    ,"20":"scrl_enchant_am"
    ,"21":"bless_scrl_enchant_wp"
    ,"22":"bless_scrl_enchant_am"
    ,"23":"coupon"
    ,"24":"elixir"
    ,"25":"scrl_enchant_attr"
    ,"27":"bolt"
    ,"28":"scrl_inc_enchant_prop_wp"
    ,"29":"scrl_inc_enchant_prop_am"
    ,"32":"ancient_crystal_enchant_am"
    ,"33":"ancient_crystal_enchant_wp"
    ,"34":"rune"
    ,"35":"rune_select"
    #,"36":""
    #,"38":"" #靈魂彈
}


class Itemname:
    def __init__(self):
        self.f = {}
        with codecs.open(r'itemname-tw.txt', 'r', 'utf8') as i:
            self.title = [x.rstrip().split('[')[0] for x in i.readline().split('\t')]
            for line in i:
                f = [x.rstrip() for x in line.split('\t')]
                self.f[int(f[0])] = f
                
class Weapongrp:
    def __init__(self):
        self.f = {}
        with codecs.open(r'weapongrp.txt', 'r', 'utf8') as i:
            self.title = [x.rstrip().split('[')[0] for x in i.readline().split('\t')]
            for line in i:
                f = [x.rstrip() for x in line.split('\t')]
                self.f[int(f[1])] = f

class Armorgrp:
    def __init__(self):
        self.f = {}
        with codecs.open(r'armorgrp.txt', 'r', 'utf8') as i:
            self.title = [x.rstrip().split('[')[0] for x in i.readline().split('\t')]
            for line in i:
                f = [x.rstrip() for x in line.split('\t')]
                self.f[int(f[1])] = f

class Etcitemgrp:
    def __init__(self):
        self.f = {}
        with codecs.open(r'etcitemgrp.txt', 'r', 'utf8') as i:
            self.title = [x.rstrip().split('[')[0] for x in i.readline().split('\t')]
            for line in i:
                f = [x.rstrip() for x in line.split('\t')]
                self.f[int(f[1])] = f

class Itemstatdata:
    def __init__(self):
        self.f = {}
        with codecs.open(r'itemstatdata.txt', 'r', 'utf8') as i:
            self.title = [x.rstrip().split('[')[0] for x in i.readline().split('\t')]
            for line in i:
                f = [x.rstrip() for x in line.split('\t')]
                self.f[int(f[0])] = f

def addSetNode(p, **kw):
    for k, v in kw.items():
        ET.SubElement(p, 'set', attrib={'name':k, 'val':v})

def process_itemname(itemname, root):
    for key in itemname.f:
        if not key in root:
            root[key] = ET.Element('item', attrib={'id':str(key),'name':itemname.f[key][1]})
        item = root[key]
        f = itemname.f[key]
        #item.set('id', f[0])
        item.set('name', f[1])
            
def process_weapongrp(weapongrp, root):
    for key in weapongrp.f:
        if not key in root:
            root[key] = ET.Element('item', attrib={'id':str(key),'name':'unknow'})
            print "warning weapongrp ", key
        item = root[key]
        f = weapongrp.f[key]
        item.set('type', u'Weapon')
        addSetNode(
            item
            , icon=f[22]
            , weight=f[28]
            , default_action='equip'
        )
        if int(f[27]) > 0:
            addSetNode(item, duration=f[27])
        if f[29] in material:
            addSetNode(item, material=material[f[29]])
        if not f[30] == '0':
            addSetNode(item, enchant_enabled=f[30])
        if not f[32] == '0':
            addSetNode(item
                , is_tradable="false"
                , is_dropable="false"
                , is_sellable="false"
                , is_depositable="false"
                , is_questitem="true")
        if f[38] in bodypart:
            addSetNode(item, bodypart=bodypart[f[38]])
        if not f[58] == '0':
            addSetNode(item, random_damage=f[58])
        if f[59] in weapon_type:
            addSetNode(item, weapon_type=weapon_type[f[59]])
        if f[60] in crystal_type:
            if not f[60] == '0':
                addSetNode(item, crystal_type=crystal_type[f[60]], crystal_count="1")
        if int(f[61]) > 0:
            addSetNode(item, mp_consume=f[61])
        if int(f[62]) > 0:
            addSetNode(item, soulshots=f[62])
        if int(f[63]) > 0:
            addSetNode(item, spiritshots=f[63])
        if int(f[66]) > 0:
            setE = ET.SubElement(item, 'cond', attrib={'msgId':'1518'})
            ET.SubElement(setE, 'player', attrib={'isHero':'true'})
                
def process_armorgrp(armorgrp, root):
    for key in armorgrp.f:
        if not key in root:
            root[key] = ET.Element('item', attrib={'id':str(key),'name':'unknow'})
            print "warning armorgrp ", key
        item = root[key]
        f = armorgrp.f[key]
        item.set('type', u'Armor')
        addSetNode(
            item
            , icon=f[22]
            , weight=f[28]
            , default_action='equip'
        )
        if int(f[27]) > 0:
            addSetNode(item, duration=f[27])
        if f[29] in material:
            addSetNode(item, material=material[f[29]])
        if not f[30] == '0':
            addSetNode(item, enchant_enabled=f[30])
        if not f[32] == '0':
            addSetNode(item
                , is_tradable="false"
                , is_dropable="false"
                , is_sellable="false"
                , is_depositable="false"
                , is_questitem="true")
        if f[38] in bodypart:
            addSetNode(item, bodypart=bodypart[f[38]])
        if f[233] in armor_type:
            addSetNode(item, armor_type=armor_type[f[233]])
        if f[234] in crystal_type:
            if not f[234] == '0':
                addSetNode(item, crystal_type=crystal_type[f[234]], crystal_count="1")
        else:
            print key, f[234]
        if int(f[235]) > 0:
            fornode = item.find('for')
            if fornode is None:
                fornode = ET.SubElement(item, 'for')
            ET.SubElement(fornode, 'add', attrib={'order':'0x40','stat':'maxMp','val':f[235]})
        #if not f[235] == '0':
        #    print key
            #for x in xrange(len(f)):
            #    print x, f[x], armorgrp.title[x]

def process_etcitemgrp(etcitemgrp, root):
    for key in etcitemgrp.f:
        if not key in root:
            root[key] = ET.Element('item', attrib={'id':str(key),'name':'unknow'})
            print "warning etcitemgrp ", key
        item = root[key]
        f = etcitemgrp.f[key]
        item.set('type', u'EtcItem')
        addSetNode(
            item
            , icon=f[22]
            #, default_action='equip'
        )
        if int(f[27]) > 0:
            addSetNode(item, duration=f[27])
        if int(f[28]) > 0:
            addSetNode(item, weight=f[28])
        if f[29] in material:
            addSetNode(item, material=material[f[29]])
        if not f[30] == '0':
            addSetNode(item, enchant_enabled=f[30])
        if not f[32] == '0':
            addSetNode(item
                , is_tradable="false"
                , is_dropable="false"
                , is_sellable="false"
                , is_depositable="false"
                , is_questitem="true")
        if not f[53] == '0':
            addSetNode(item, is_stackable='true')
        if f[54] in etcitem_type:
            addSetNode(item, etcitem_type=etcitem_type[f[54]])
        if f[55] in crystal_type:
            if not f[55] == '0':
                addSetNode(item, crystal_type=crystal_type[f[55]], crystal_count="1")

def process_itemstatdata(itemstatdata, root):
    for key in itemstatdata.f:
        if not key in root:
            root[key] = ET.Element('item', attrib={'id':str(key),'name':'unknow'})
            print "warning itemstatdata ", key
        item = root[key]
        f = itemstatdata.f[key]
        enchant_enable = not item.find("set[@name='enchant_enabled']") is None
        fornode = item.find('for')
        if fornode is None:
            fornode = ET.SubElement(item, 'for')
        if not float(f[1]) == 0:
            ET.SubElement(fornode, 'add', attrib={'order':'0x10','stat':'pDef','val':"%0.0f" % float(f[1])})
            if enchant_enable:
                ET.SubElement(fornode, 'enchant', attrib={'order':'0x0C','stat':'pDef','val':'0'})
        if not float(f[2]) == 0:
            ET.SubElement(fornode, 'add', attrib={'order':'0x10','stat':'mDef','val':"%0.0f" % float(f[2])})
            if enchant_enable:
                ET.SubElement(fornode, 'enchant', attrib={'order':'0x0C','stat':'mDef','val':'0'})
        if not float(f[3]) == 0:
            ET.SubElement(fornode, 'set', attrib={'order':'0x08','stat':'pAtk','val':"%0.0f" % float(f[3])})
            if enchant_enable:
                ET.SubElement(fornode, 'enchant', attrib={'order':'0x0C','stat':'pAtk','val':'0'})
        if not float(f[4]) == 0:
            ET.SubElement(fornode, 'set', attrib={'order':'0x08','stat':'mAtk','val':"%0.0f" % float(f[4])})
            if enchant_enable:
                ET.SubElement(fornode, 'enchant', attrib={'order':'0x0C','stat':'mAtk','val':'0'})
        if not float(f[6]) == 0:
            ET.SubElement(fornode, 'set', attrib={'order':'0x08','stat':'pAtkSpd','val':"%0.0f" % float(f[6])})
        if not float(f[7]) == 0:
            if float(f[7]) > 0:
                ET.SubElement(fornode, 'add', attrib={'order':'0x10','stat':'accCombat','val':"%0.2f" % float(f[7])})
            else:
                ET.SubElement(fornode, 'sub', attrib={'order':'0x10','stat':'accCombat','val':"%0.2f" % abs(float(f[7]))})
        if not float(f[9]) == 0:
            ET.SubElement(fornode, 'set', attrib={'order':'0x08','stat':'rCrit','val':"%0.0f" % float(f[9])})
        if not float(f[12]) == 0:
            ET.SubElement(fornode, 'set', attrib={'order':'0x08','stat':'sDef','val':"%0.0f" % float(f[12])})
            if enchant_enable:
                ET.SubElement(fornode, 'enchant', attrib={'order':'0x0C','stat':'sDef','val':'0'})
        if not float(f[13]) == 0:
            ET.SubElement(fornode, 'set', attrib={'order':'0x08','stat':'rShld','val':"%0.0f" % float(f[13])})
        if not float(f[14]) == 0:
            if float(f[14]) > 0:
                ET.SubElement(fornode, 'add', attrib={'order':'0x10','stat':'rEvas','val':"%0.0f" % float(f[14])})
            else:
                ET.SubElement(fornode, 'sub', attrib={'order':'0x10','stat':'rEvas','val':"%0.0f" % abs(float(f[14]))})
        if len(fornode) == 0:
            item.remove(fornode)
            
def writeXML(startid, list_element):
    startid = "000%d00" % (int(startid)/100)
    endid = "000%d99" % (int(startid)/100)
    filename = "%s-%s.xml" % (startid[-5:], endid[-5:])
    with codecs.open(filename, 'w') as o:
        o.write(parseString(ET.tostring(list_element, 'UTF-8')).toprettyxml(encoding='UTF-8'))
    
root = {}
process_itemname(Itemname(), root)
process_etcitemgrp(Etcitemgrp(), root)
process_armorgrp(Armorgrp(), root)
process_weapongrp(Weapongrp(), root)
process_itemstatdata(Itemstatdata(), root)

list_element = ET.Element('list', attrib={"xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance", "xsi:noNamespaceSchemaLocation":"../../../xsd/items.xsd"})
rstart = 0
for key in sorted(root.keys()):
    if key > rstart + 99:
        writeXML(rstart, list_element)
        rstart = key / 100 * 100
        list_element = ET.Element('list', attrib={"xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance", "xsi:noNamespaceSchemaLocation":"../../../xsd/items.xsd"})
    if len(root[key]) > 0:
        list_element.append(root[key])
writeXML(rstart, list_element)
