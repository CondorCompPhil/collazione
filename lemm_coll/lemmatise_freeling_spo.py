#! /usr/bin/python3

### REQUIRES python 3 !!!!

## Run:  ./this_file.py
## Reads from stdin and writes to stdout
## For example:
##     ./this_file.py <test.txt >test_out.txt



from lemm_coll.freeling import pyfreeling
import sys, os, glob

## ------------  output a parse tree ------------
def printTree(ptree, depth):

    node = ptree.begin();

    print(''.rjust(depth*2),end='');
    info = node.get_info();
    if (info.is_head()): print('+',end='');

    nch = node.num_children();
    if (nch == 0) :
        w = info.get_word();
        print ('({0} {1} {2})'.format(w.get_form(), w.get_lemma(), w.get_tag()),end='');

    else :
        print('{0}_['.format(info.get_label()));

        for i in range(nch) :
            child = node.nth_child_ref(i);
            printTree(child, depth+1);

        print(''.rjust(depth*2),end='');
        print(']',end='');
        
    print('');

## ------------  output a parse tree ------------
def printDepTree(dtree, depth):

    node = dtree.begin()

    print(''.rjust(depth*2),end='');

    info = node.get_info();
    link = info.get_link();
    linfo = link.get_info();
    print ('{0}/{1}/'.format(link.get_info().get_label(), info.get_label()),end='');

    w = node.get_info().get_word();
    print ('({0} {1} {2})'.format(w.get_form(), w.get_lemma(), w.get_tag()),end='');

    nch = node.num_children();
    if (nch > 0) :
        print(' [');

        for i in range(nch) :
            d = node.nth_child_ref(i);
            if (not d.begin().get_info().is_chunk()) :
                printDepTree(d, depth+1);

        ch = {};
        for i in range(nch) :
            d = node.nth_child_ref(i);
            if (d.begin().get_info().is_chunk()) :
                ch[d.begin().get_info().get_chunk_ord()] = d;
 
        for i in sorted(ch.keys()) :
            printDepTree(ch[i], depth + 1);

        print(''.rjust(depth*2),end='');
        print(']',end='');

    print('');


def freeling_spo(path):

    ## ----------------------------------------------
    ## -------------    MAIN PROGRAM  ---------------
    ## ----------------------------------------------

    ## Check whether we know where to find FreeLing data files
    if "FREELINGDIR" not in os.environ :
       if sys.platform == "win32" or sys.platform == "win64" : os.environ["FREELINGDIR"] = "C:\\Program Files"
       else : os.environ["FREELINGDIR"] = "/usr/local"
       print("FREELINGDIR environment variable not defined, trying ", os.environ["FREELINGDIR"], file=sys.stderr)

    if not os.path.exists(os.environ["FREELINGDIR"]+"/share/freeling") :
       print("Folder",os.environ["FREELINGDIR"]+"/share/freeling",
             "not found.\nPlease set FREELINGDIR environment variable to FreeLing installation directory",
             file=sys.stderr)
       sys.exit(1)

 


    # Location of FreeLing configuration files.
    DATA = os.environ["FREELINGDIR"]+"/share/freeling/";

    # Init locales
    pyfreeling.util_init_locale("default");

    # create language detector. Used just to show it. Results are printed
    # but ignored (after, it is assumed language is LANG)
    la=pyfreeling.lang_ident(DATA+"common/lang_ident/ident-few.dat");

    # create options set for maco analyzer. Default values are Ok, except for data files.
    LANG="es-old";
    op= pyfreeling.maco_options(LANG);
    op.set_data_files( "", 
                       DATA + "common/punct.dat",
                       DATA +'es/' + LANG + "/dicc.src",
                       DATA +'es/' + LANG + "/afixos.dat", 
                       "",  ## DO NOT REMOVE
                       DATA +'es' + "/locucions.dat", ## APPLYING locucions FOR ES, THERE IS NONE FOR ES-OLD
                       DATA +'es' + "/np.dat",   ## APPLYING np FOR ES, THERE IS NONE FOR ES-OLD
                       DATA +'es' + "/quantities.dat",   ## APPLYING quantities FOR ES, THERE IS NONE FOR ES-OLD
                       DATA +'es/' + LANG + "/probabilitats.dat");

    # create analyzers
    tk=pyfreeling.tokenizer(DATA +'es/'+LANG+"/tokenizer.dat"); 
    sp=pyfreeling.splitter(DATA +'es'+"/splitter.dat"); ## APPLYING SPLITTER FOR ES, THERE IS NONE FOR ES-OLD
    sid=sp.open_session();
    mf=pyfreeling.maco(op);

    # activate mmorpho odules to be used in next call
    mf.set_active_options(False, True, True, True,  # select which among created 
                          True, True, False, True,  # submodules are to be used. 
                          True, True, True, True ); # default: all created submodules are used

    # create tagger, sense anotator, and parsers
    tg=pyfreeling.hmm_tagger(DATA +'es/'+ LANG +"/tagger.dat",True,2);
    sen=pyfreeling.senses(DATA +'es'+"/senses.dat");   ## APPLYING senses FOR ES, THERE IS NONE FOR ES-OLD
    parser= pyfreeling.chart_parser(DATA +'es'+"/chunker/grammar-chunk.dat");  ## APPLYING chunker FOR ES, THERE IS NONE FOR ES-OLD
    dep=pyfreeling.dep_txala(DATA +'es'+"/dep_txala/dependences.dat", parser.get_start_symbol());  ## APPLYING _txala FOR ES, THERE IS NONE FOR ES-OLD



    files = glob.glob(path + '/*.txt')
    for f in files:
        f_open = open(f, "r")
        lin=f_open.readline();  # WAS --->  lin=sys.stdin.readline();

        while (lin) :
                
            l = tk.tokenize(lin);
            ls = sp.split(sid,l,False);

            ls = mf.analyze(ls);
            ls = tg.analyze(ls);
            ls = sen.analyze(ls);
            ls = parser.analyze(ls);
            ls = dep.analyze(ls);

            ## output results
            for s in ls :
                ws = s.get_words();
                with open(path + '/' + f.split(".")[0].split("/")[-1] + ".xml", 'w') as f_out:
                    newxml = "<ab>"
                    for w in ws :
                        newxml += "<w lemma='"+w.get_lemma()+"' pos='"+w.get_tag()+"'>"+w.get_form()+"</w>"
                    newxml += "</ab>"
                    f_out.write(newxml)

            lin=f_open.readline();
            
            
    # clean up       
    sp.close_session(sid);
        
