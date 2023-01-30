import os
sys.path.append(os.environ["HOME"]+"/p3li5/pyli5/src/")
from pyli5.admf import lipf, licf, iqf

if __name__ == "__main__":
    li_admf = Queue()
    with open(os.environ["HOME"]+"/p3li5/pyli5/src/pyli5/admf/admf.json") as f:
        c = json.load(f)["admf"]
        licf = LICF(c["licf"]["h1_address"],c["licf"]["h1_port"], li_admf)
        lipf = LIPF(c["lipf"]['admf_id'], ief_info=IEFInfo(xem_addr=c['lipf']['ief_info']['xem_addr'],
                                                           xem_port=c['lipf']['ief_info']['xem_port'],
                                                           xem_url=c['lipf']['ief_info']['xem_url'],
                                                           xem_id=c['lipf']['ief_info']['xem_id']),
                    icf_info=ICFInfo(xer_addr=c['lipf']['icf_info']['icf_xer_addr'],
                                     xer_port=c['lipf']['icf_info']['icf_xer_port']), li_admf=li_admf)
        iqf = IQF(admf_id=c['iqf']['admf_id'],
                  hiqr_addr=c['iqf']['hiqr_addr'],
                  hiqr_port=c['iqf']['hiqr_port'],
                  icf_xqr_addr=c['iqf']['icf_xqr_addr'],
                  icf_xqr_port=c['iqf']['icf_xqr_port'])
    while True:
        pass
