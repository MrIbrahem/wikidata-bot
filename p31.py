#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


python3 pwb.py dump/p31


"""
#
# (C) Ibrahem Qasim, 2022
#
#

import bz2
import json
import time
import pywikibot
#====
tab = {} 
tab['items_0_claims'] = 0
tab['items_1_claims'] = 0
tab['items_no_P31'] = 0
tab['All_items'] = 0
tab['all_claims_2020'] = 0
tab['Main_Table'] = {} 
#====
lamo = [
    'items_0_claims',
    'items_1_claims',
    'items_no_P31',
    'All_items',
    'all_claims_2020',
    'Main_Table',
    ]
#====
jsonname = 'dump/claimsep31.json'
sections_done = { 1 : 0 }
sections_false = { 1 : 0 }
#====
def make_section( P , table , Len ):
    texts = '== {{P|%s}}  =='  % P
    #----
    if sections_done[1] == 50 : 
        return ''
    #----
    pywikibot.output( ' make_section for property:%s' % P )
    #----
    texts += '\n* Total items use these property:%d' % Len
    #----
    if tab['Main_Table'].get(P,{}).get('lenth_of_claims_for_property'):
        texts += '\n* Total number of claims with these property:%d' % tab['Main_Table'].get(P,{}).get('lenth_of_claims_for_property')
    texts += '\n'
    #----
    pywikibot.output( texts )
    #----
    if table['props'] == {} :
        pywikibot.output( '%s table["props"] == {} ' % P )
        return ''
    #----
    xline = ''
    yline = ''
    #----
    Chart = """
{| class="floatright sortable" 
|-
|
{{Graph:Chart|width=140|height=140|xAxisTitle=value|yAxisTitle=Number
|type=pie|showValues1=offset:8,angle:45
|x=%s
|y1=%s
|legend=value
}}
|-
|}"""
    #----
    tables = """
{| class="wikitable sortable plainrowheaders"
|-
! class="sortable" | #
! class="sortable" | value
! class="sortable" | Numbers
|-
"""
    #----
    lists = [ [ y , xff ] for xff, y in table['props'].items()]
    lists.sort(reverse=True)
    #----
    num = 0
    #----
    other = 0
    #----
    for ye, x in lists :
        #----
        if ye == 0 and sections_false[1] < 100:
            pywikibot.output( 'p(%s),x(%s) ye == 0 or ye == 1 ' % (P,x) )
            sections_false[1] += 1
            return ''
        #----
        num += 1
        #----
        if num < 501 : 
            #----
            tables += '\n'
            if x.startswith('Q'):
                row = "| %d || {{Q|%s}} || {{subst:formatnum:%d}} " % ( num , x , ye )
            else:
                row = "| %d || %s || {{subst:formatnum:%d}} " % ( num , x , ye )
            xline += ",%s" % x
            yline += ",%d" % ye
            #----
            tables += row
            tables += '\n|-'
        else:
            other += ye
    #----
    num += 1 
    #----
    tables += "\n| %d || others || {{subst:formatnum:%d}} " % ( num,other)
    tables += '\n|-'
    #----
    Chart = Chart % ( xline , yline )
    #----
    tables += "\n|}\n{{clear}}\n"
    #----
    texts += Chart.replace("=,","=")
    texts += tables
    #----
    sections_done[1] += 1
    #----
    return texts
#====
ttypes = [
    "wikibase-entityid",
    "time",
    "monolingualtext",
    "quantity",
    ]
#====
def log_dump():
    with open(jsonname, 'w') as outfile:
        json.dump( tab , outfile )
#====
def workondata():
    #----
    fileeee = bz2.open('/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2' , 'r')
    #----
    for line in fileeee:
        line = line.decode('utf-8')
        line = line.strip('\n').strip(',')
        #----
        if line.startswith('{') and line.endswith('}'):
            #----
            tab['All_items'] += 1
            #----
            json1 = json.loads(line)
            claimse = json1.get('claims',{})
            #----
            if len(claimse) == 1 :
                tab['items_1_claims'] += 1
            #----
            if not 'P31' in claimse :
                tab['items_no_P31'] += 1
                tab['items_no_P31'] += 1
                continue
            elif len(claimse) == 0 :
                tab['items_0_claims'] += 1
                continue
            #----
            P31 = 'P31'
            #----
            if not P31 in tab['Main_Table']:
                tab['Main_Table'][P31] = {'props' : {} , 'lenth_of_usage' : 0  , 'lenth_of_claims_for_property' : 0 }
            #----
            tab['Main_Table'][P31]['lenth_of_usage'] += 1
            #----
            tab['all_claims_2020'] += len(json1['claims'][P31])
            #----
            for claim in json1['claims'][P31]:
                #----
                tab['Main_Table'][P31]['lenth_of_claims_for_property'] += 1
                #----
                datavalue = claim.get('mainsnak',{}).get('datavalue',{})
                ttype = datavalue.get('type')
                #----
                if ttype == "wikibase-entityid":
                    id = datavalue.get('value',{}).get('id')
                    if id :
                        if id in tab['Main_Table'][P31]['props']:
                            tab['Main_Table'][P31]['props'][id] += 1 
                        else:
                            tab['Main_Table'][P31]['props'][id] = 1
                #----
            #----
#====
dumpdate = 'latest'
#====
def mainar():
    #----
    time_start = time.time()
    #----
    pywikibot.output('time_start:%s' % str(time_start) )
    #----
    sections = ''
    #----
    workondata()
    #----
    p31list = [[y['lenth_of_usage'], x] for x, y in tab['Main_Table'].items() if y['lenth_of_usage'] != 0 ]
    p31list.sort(reverse=True) 
    #----
    for Len , P in p31list:
        sections += make_section( P , tab['Main_Table'][P] , Len )
    #----
    final = time.time()
    delta = int( final - time_start )
    #----
    text = "* Source code: [https://github.com/MrIbrahem/wikidata-bot github].\n\n"
    text = "Update: <onlyinclude>%s</onlyinclude>.\n" % dumpdate
    text += "* Total items:{{subst:formatnum:%d}} \n" % tab['All_items']
    text += "* Items without P31:{{subst:formatnum:%d}} \n" % tab['items_no_P31']
    text += "* Items with 1 claim only:{{subst:formatnum:%d}} \n" % tab['items_1_claims']
    text += "* Items with no claim:{{subst:formatnum:%d}} \n" % tab['items_0_claims']
    text += "* Total number of claims:{{subst:formatnum:%d}} \n" % tab['all_claims_2020']
    text += "<!-- bots work done in %d secounds --> \n" % delta
    text += "--~~~~~\n"
    #----
    text = text + "\n" + sections
    text = text.replace( "0 (0000)" , "0" )
    text = text.replace( "0 (0)" , "0" )
    #----
    title = 'User:Mr. Ibrahem/p31'
    site = pywikibot.Site("wikidata")
    page = pywikibot.Page(site, title)
    #----
    page.text = text
    page.save()
    #----
    with open( 'dump/claims.txt' , 'w' ) as f:
        f.write(text)
#====
if __name__ == '__main__':
    mainar()
#====