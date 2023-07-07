from lxml import etree
import numpy as np
import csv

# Determine if a given Lane is part of a roundabout
def isRoundAbout (r_id):    
    roundabout=None
    roundabout= findRoundAboundTag(tree,id=r_id)
    return len(roundabout)!=0

def appendEmptyValuesToRow(row):              
    row.append(0)
    row.append(0)
    row.append(0)
    row.append(0)
    row.append(None)
    row.append(0)
    row.append(0)

# retrieve statistics for lanes of a junction,     
def processLanes (lane_ids_as_string, row, isIncomingLane):
    # append an empty row if there are no lanes in this junction 
    
    if (lane_ids_as_string==""):
        appendEmptyValuesToRow(row)
        return
    
    edge_priorities=[]
    edge_types=[]
    lane_lengths=[]
    lane_speeds=[]    
    lane_id_list= lane_ids_as_string.split(" ")  

    for l_id in lane_id_list:
        try:            
            lane= lane_table[l_id]
            edge= lane.getparent()
            if isIncomingLane:    
                edge_types.append( edge.get("type"))
                edge_priorities.append(float(edge.get("priority")))
            lane_lengths.append(float(lane.get("length")))
            lane_speeds.append(float(lane.get("speed")))
        except:
            print ("error with lane_ids: '{}', l_id:'{}' junction_id:'{}'".format(lane_ids_as_string,
                   l_id, row[0]))
            raise
        
    row.append(np.average(lane_speeds))
    row.append(np.std(lane_speeds))
    row.append(np.average(lane_lengths))
    row.append(np.std(lane_lengths))

    if isIncomingLane:        
        row.append(edge_types)
        row.append(np.average(edge_priorities))
    else:
        row.append(None)
        row.append(-1)

    row.append(len(lane_id_list))

"""
Find connections using the global nodes_table and connection_tl table
we need to find the "tl"-id for a corresponding junction id. 
Using this id, we can figure out how many traffic lights this junction controls because
number of connections with tl == tl_id of junction equals the number of traffic lights

"""
def findConnections (junction_id): 
              
    tl= nodes_table[junction_id]
    number_of_traffic_lights=0

    for tllogic in tlLogicTable:
        if (tllogic.get("id")==tl):               
            number_of_traffic_lights=len(tllogic.getchildren()[0].get("state"))
            break

    results= list(map(lambda con: [con.get('from'), con.get('to'), con.get('tl'),con.get('dir'), con.get('state')], connectiontable_tl[tl]))
    return [number_of_traffic_lights,tl,results]

"""
Reads the number of traffic light controlled by this junction from xml 

"""
def processConnections(row):
    trafficlightinfo=findConnections(row[0])
    row.append(trafficlightinfo)

"""
Reads data from xml for one junction

"""
def evaluateJunction(junction):    
    row= []        

    row.append(junction.get("id"))
    row.append(junction.get("type"))
    row.append(junction.get("x"))
    row.append(junction.get("y"))
    row.append(junction.get("z"))
    row.append(isRoundAbout(row[0]))

    processConnections(row)
    processLanes(junction.get("incLanes"), row, True)
    processLanes(junction.get("intLanes"), row, False)

    return row

"""
This method creates hash tables for faster searching in the xml data. 

"""
def createXmlEntityCaches(tree, nodes_tree):
    # compile the query for roundabouts for faster execution times
    global findRoundAboundTag
    findRoundAboundTag= etree.XPath("//net/roundabout[contains(@nodes,$id)]")

    junctions= tree.xpath("/net/junction[@type='traffic_light']")
    
    connections=tree.xpath("/net/connection")
    
    global connectiontable_from
    connectiontable_from={}
    global connectiontable_to
    connectiontable_to={}  
    global node_table
    global connectiontable_tl
    connectiontable_tl={}  

    for con in connections:
        tlid= con.get("tl")
        if tlid is not None:            
            tlid= con.get('tl')
            if tlid not in connectiontable_tl.keys():
                connectiontable_tl[tlid]=[]
            connectiontable_tl[tlid].append(con)

        connectiontable_from[con.get('from')]=con
        connectiontable_to[con.get('to')]=con 
    
    global tlLogicTable
    tlLogicTable=tree.xpath("/net/tlLogic")
    global nodes_table
    nodes_table={}
    nodes=nodes_tree.xpath("/nodes/node[@type='traffic_light']")

    for node in nodes:
        id= node.get('id')
        nodes_table[id]=node.get('tl')
    
    lanes=tree.xpath("/net/edge/lane")
    global lane_table
    lane_table={}

    for lane in lanes:
        lane_table[lane.get('id')]=lane

    junction_count= len(junctions)
    
    return junction_count, junctions

"""
Run the extraction process for a 
xml: scenario.net.xml file
node_xml: a scenario.nod.xml file, that was generated using netconvert
output_filename: the name of the csv file to export

"""
def runDataExtraction (xml,node_xml, output_filename):
    global tree
    tree = etree.parse(xml)
    nodes_tree= etree.parse(node_xml)   
    
    junction_count, junctions= createXmlEntityCaches(tree, nodes_tree)
    
    print ("processing {} junctions..".format(junction_count))
    
    n=0
    for junction in junctions:
        dataset.append(evaluateJunction( junction ))
    
    with open(output_filename,"w") as f:
        writer=csv.writer(f)
        writer.writerows(dataset)


xml= "C:/Users/hisha/Intelligent-Traffic-Analysis/AlSTScenario/osm.net.xml/osm.net.xml"
node_xml="C:/Users/hisha/Intelligent-Traffic-Analysis/AlSTScenario/osm.net.xml/true.nod.xml"
output_filename= "dataset-alex-tl2.csv"
dataset= []

runDataExtraction(xml,node_xml, output_filename)

xml="C:/Users/ford_/Downloads/LuSTScenario-master/scenario/lust.net.xml"
node_xml="C:/Users/ford_/Downloads/LuSTScenario-master/scenario/true.nod.xml"
output_filename= "dataset-lust-tl2.csv"
dataset=[]

runDataExtraction(xml,node_xml, output_filename)