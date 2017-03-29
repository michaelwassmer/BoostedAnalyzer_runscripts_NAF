import das_client as dc
import GetTotalSampleNumbers_multi as gts
from collections import defaultdict
from multiprocessing import Pool

# gets the json for a given dataset with wildcards
def get_data_(dataset):
    host="https://cmsweb.cern.ch"
    dataset_string="dataset="
    start_number=0
    max_entries=0
    wait_time=300
    return dc.get_data(host,dataset_string+dataset,start_number,max_entries,wait_time,dc.x509(),dc.x509())

def get_children(dataset):
    host="https://cmsweb.cern.ch"
    dataset_string="child dataset="
    instance=" instance=prod/phys03"
    start_number=0
    max_entries=0
    wait_time=300
    return dc.get_data(host,dataset_string+dataset+instance,start_number,max_entries,wait_time,dc.x509(),dc.x509())

def get_names(dataset_wildcard_):
    nresults=get_data_(dataset_wildcard_).get("nresults","none")
    name_array=[]
    for i in range(nresults):
      try:
        name_array.append(get_data_(dataset_wildcard_).get("data","none")[i].get("dataset","none")[0].get("name","none"))
      except KeyError:
	continue
    return name_array

def search_index(array,key):
    for i in range(len(array)):
        if(str(array[i].get(key,"none"))!="none"):
            return i

def get_jsons(name_array):
    json_array=[]
    number_processes=len(name_array)
    #print name_array
    #print number_processes
    pool=Pool(processes=number_processes)
    json_array=pool.map(get_data_,name_array)
    """
    processes=[]
    for i in range(len(name_array)):
        name=name_array[i]
	p=Process(target=get_data_,args=(name,))
	p.start()
	processes.append(p)
    for p in processes:
	p.join()
        json_array.append(p)
    """
    return json_array

def get_nevents(json_array):
    nresults=len(json_array)
    nevents_array=[]
    for i in range(nresults):
      try:
	index_=search_index(json_array[i].get("data","none")[0].get("dataset","none"),"nevents")
	nevents_array.append(json_array[i].get("data","none")[0].get("dataset","none")[index_].get("nevents","none"))
      except AttributeError:
	nevents_array.append(0)
    return nevents_array

def get_nfiles(json_array):
    nresults=len(json_array)
    nfiles_array=[]
    for i in range(nresults):
      try:
        index_=search_index(json_array[i].get("data","none")[0].get("dataset","none"),"nfiles")
        nfiles_array.append(json_array[i].get("data","none")[0].get("dataset","none")[index_].get("nfiles","none"))
      except AttributeError:
	nfiles_array.append(0)
    return nfiles_array

def get_datatypes(json_array):
    nresults=len(json_array)
    datatype_array=[]
    for i in range(nresults):
      try:
        index_=search_index(json_array[i].get("data","none")[0].get("dataset","none"),"datatype")
        datatype=json_array[i].get("data","none")[0].get("dataset","none")[index_].get("datatype","none")
        if(datatype=="mc"):
	  datatype_array.append("FALSE")
	if(datatype=="data"):
	  datatype_array.append("TRUE")
      except AttributeError:
	datatype_array.append("look at me again")
    return datatype_array

def get_globaltags(json_array):
    nresults=len(json_array)
    globaltag_array=[]
    for i in range(nresults):
      try:
        index_=search_index(json_array[i].get("data","none")[0].get("dataset","none"),"result")
        for key,value in json_array[i].get("data","none")[0].get("dataset","none")[index_].get("result","none")[0].iteritems():
            if(str(value.get("GlobalTag","none"))!="none"):
                globaltag_array.append(value.get("GlobalTag","none"))
                break
      except (AttributeError, TypeError):
	globaltag_array.append("look at me again")
    return globaltag_array

def get_generators(json_array):
    nresults=len(json_array)
    generator_array=[]
    for i in range(nresults):
      try:
        index_=search_index(json_array[i].get("data","none")[0].get("dataset","none"),"mcm")
        generator_array.append(json_array[i].get("data","none")[0].get("dataset","none")[index_].get("mcm","none").get("generators","none"))
        #print json_array[i].get("data","none")[0].get("dataset","none")[index_].get("mcm","none").get("generators","none")
      except (AttributeError, TypeError):
	generator_array.append("look at me again")
    return generator_array

def get_x(name):
  if(name.lower().find("amc")==-1):
    x=1
  else:
    try:
      x=gts.GetTotalSampleNumbers(name)
    except ReferenceError:
      x=0.
  return x

def get_xs(name_array):
    pool=Pool(processes=len(name_array))
    xs=pool.map(get_x,name_array)
    return xs

def get_weights(nevents_array,neg_fractions_array,xs):
    weights=[]
    for i in range(len(nevents_array)):
	if(neg_fractions_array[i]!=0. and nevents_array[i]!=0):
	  weights.append(xs*(10**3)/(neg_fractions_array[i]*nevents_array[i]))
	else:
	  weights.append(0.)
    return weights

def get_children_array(parent_dataset):
    nresults=get_children(parent_dataset).get("nresults","none")-1
    name_array=[]
    for i in range(nresults):
	index_=search_index(get_children(parent_dataset).get("data","none")[i].get("child","none"),"name")
	child_candidate=get_children(parent_dataset).get("data","none")[i].get("child","none")[index_].get("name","none")
	if(child_candidate.find("Boosted")!=-1):
	    name_array.append(child_candidate)
    return name_array

def get_children_names_(parent_dataset_array):
  pool=Pool(processes=len(parent_dataset_array))
  children=pool.map(get_children_array,parent_dataset_array)
  return children


def get_children_names(parent_dataset_array):
    children_array=[]
    for parent_dataset in parent_dataset_array:
        nresults=get_children(parent_dataset).get("nresults","none")-1
        name_array=[]
        for i in range(nresults):
            index_=search_index(get_children(parent_dataset).get("data","none")[i].get("child","none"),"name")
            child_candidate=get_children(parent_dataset).get("data","none")[i].get("child","none")[index_].get("name","none")
            if(child_candidate.find("Boosted")!=-1):
                name_array.append(child_candidate)
        children_array.append(name_array)
    return children_array

def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items()
                            if len(locs)>1)

def merge_ext(name_array):
    ext=[]
    ext_name=[]
    for i in range(len(name_array)):
      if(name_array[i].find("_ext")!=-1):
	        pos=name_array[i].find("_ext")
	        ext.append(i)
	        ext_str=name_array[i][pos:pos+5]
	        ext_name.append(name_array[i].replace(ext_str,""))
      else:
	        ext.append(0)
	        ext_name.append(name_array[i])
    duplicates=list_duplicates(ext_name)
    dups=[]
    #print duplicates[0]
    for dup in duplicates:
	    dups.append(dup[1])
	    #print dup[1]
        #dups.append(dup[1])
    return dups
  
def merge_run(name_array):
    ext=[]
    ext_name=[]
    for i in range(len(name_array)):
      if(name_array[i].find("Run20")!=-1):
	        pos=name_array[i].find("Run20")
	        ext.append(i)
	        ext_str=name_array[i][pos:pos+8]
	        ext_name.append(name_array[i].replace(ext_str,""))
      else:
	        ext.append(0)
	        ext_name.append(name_array[i])
    duplicates=list_duplicates(ext_name)
    dups=[]
    #print duplicates[0]
    for dup in duplicates:
	    dups.append(dup[1])
	    #print dup[1]
        #dups.append(dup[1])
    return dups


def get_reHLT(names_array):
  reHLT_array=[]
  for name in names_array:
    if(name.find("reHLT")==-1):
      reHLT_array.append("FALSE")
    else:
      reHLT_array.append("TRUE")
  return reHLT_array

def remove_duplicates(duplicates_array,names,jsons,nevents,nfiles,datatypes,globaltags,generators,boosted_datasets,is_reHLTs,neg_fractions,weights,xs):
  dupls=[]
  for duplicate in duplicates_array:
    #print duplicate
    nevents_tmp=0
    nfiles_tmp=0
    neg_fractions_tmp=0
    names_tmp='"'
    globaltags_tmp=globaltags[duplicate[0]]
    datatypes_tmp=datatypes[duplicate[0]]
    generators_tmp=generators[duplicate[0]]
    jsons_tmp=jsons[duplicate[0]]
    is_reHLTs_tmp=is_reHLTs[duplicate[0]]
    boosted_datasets_tmp=[]
    for i in range(len(duplicate)):
      dupl_position=duplicate[i]
      dupls.append(dupl_position)
      #print dupl_position
      nevents_tmp+=nevents[dupl_position]
      nfiles_tmp+=nfiles[dupl_position]
      neg_fractions_tmp+=neg_fractions[dupl_position]
      boosted_datasets_tmp+=boosted_datasets[dupl_position]
      if(i==0):
	names_tmp+=names[dupl_position]
      else:
	names_tmp+=","+names[dupl_position]
    names_tmp+='"'
    neg_fractions_tmp=neg_fractions_tmp/len(duplicate)
    weights_tmp=float(xs)*1000/(neg_fractions_tmp*nevents_tmp)
    #print nevents_tmp,nfiles_tmp,neg_fractions_tmp,weights_tmp,boosted_datasets_tmp,names_tmp
    names.append(names_tmp)
    jsons.append(jsons_tmp)
    nevents.append(nevents_tmp)
    nfiles.append(nfiles_tmp)
    datatypes.append(datatypes_tmp)
    globaltags.append(globaltags_tmp)
    generators.append(generators_tmp)
    is_reHLTs.append(is_reHLTs_tmp)
    boosted_datasets.append(boosted_datasets_tmp)
    neg_fractions.append(neg_fractions_tmp)
    weights.append(weights_tmp)
  dupls=sorted(dupls,reverse=True)
  #print dupls
  for i in dupls:
    del names[i]
    del jsons[i]
    del nevents[i]
    del nfiles[i]
    del datatypes[i]
    del globaltags[i]
    del generators[i]
    del boosted_datasets[i]
    del is_reHLTs[i]
    del neg_fractions[i]
    del weights[i]
  

"""
#dataset_wildcard="/TT_TuneCUETP8M1_13TeV*powheg-pythia8*/RunIIFall15MiniAODv2*76X_mcRun2_asymptotic_v12*/MINIAODSIM"
dataset_wildcard1="/ttHTobb_M125_13TeV*powheg_pythia8*/*80X*/MINIAODSIM"

#print results.get("data","none")[0]
name_array=get_names(dataset_wildcard1)
json_array=get_jsons(name_array)
print name_array
print "##########################"
print get_nevents(name_array,json_array)
print "##########################"
print get_nfiles(name_array,json_array)
print "##########################"
print get_datatypes(json_array)
print "##########################"
print get_globaltags(json_array)
print "##########################"
print get_generators(json_array)
"""

#print get_globaltags(json_array)
"""
blabla=search_index(json_array[0].get("data","none")[0].get("dataset","none"),"result")
print "Dictionary after search with full name of a dataset"
for key,value in json_array[0].iteritems():
    print key
    print value
    print "##############"
print " "
print "Dictionary of key data"
for key,value in json_array[0].get("data","none")[0].iteritems():
    print key
    print value
    print "##############"
print " "
print "Dicitonary of key dataset in data dict"
for i in range(len(json_array[0].get("data","none")[0].get("dataset","none"))):
    print "array element",i
    for key,value in json_array[0].get("data","none")[0].get("dataset","none")[i].iteritems():
        print key
        print value
        print "##############"
print " "
print "Dictionary of key result in dataset dict "
for key,value in json_array[0].get("data","none")[0].get("dataset","none")[blabla].get("result","none")[0].iteritems():
    print key
    print value
    print "##############"
    print json_array[0].get("data","none")[0].get("dataset","none")[blabla].get("result","none")[0].get(key).get("GlobalTag","none")
"""