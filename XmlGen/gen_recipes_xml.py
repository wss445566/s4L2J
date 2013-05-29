from xml.dom.minidom import getDOMImplementation

def gen_xml():
    debug = True
    xmldoc = getDOMImplementation().createDocument(None, "list", None)
    topE = xmldoc.documentElement
    with open(r'recipes.xml', 'w') as o:
        with open(r'recipe-c.txt', 'r') as i:
            title = [x.rstrip().split('[')[0] for x in i.readline().split('\t')]
            for line in i:
                itemE = xmldoc.createElement("item")
                f = [x.rstrip() for x in line.split('\t')]
                itemE.setAttribute('name', f[0][2:-2])
                itemE.setAttribute('id', f[1])
                itemE.setAttribute('recipeId', f[2])
                itemE.setAttribute('craftLevel', f[3])

                proE = xmldoc.createElement('production')
                proE.setAttribute('id', f[4])
                proE.setAttribute('count', f[5])
                itemE.appendChild(proE)

                staE = xmldoc.createElement('statUse')
                staE.setAttribute('name', 'MP')
                staE.setAttribute('value', f[6])
                itemE.appendChild(staE)
                
                itemE.setAttribute('successRate', f[7])

                for c in xrange(int(f[8])):
                    ingE = xmldoc.createElement('ingredient')
                    ingE.setAttribute('id', f[10+c*2])
                    ingE.setAttribute('count', f[10+c*2+1])
                    itemE.appendChild(ingE)

                itemE.setAttribute('type', 'dwarven')

                topE.appendChild(itemE)
                if debug and len(f[25])>0 or f[2] == '3001':
                    debug = False
                    for x in xrange(len(title)):
                        print x, title[x], f[x]
        o.write(xmldoc.toprettyxml())
gen_xml()
