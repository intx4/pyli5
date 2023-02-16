from pyli5.admf.iqf import IQF
from pyli5.admf.licf import LICF
from pyli5.admf.lipf import LIPF, ICFInfo, IEFInfo
import os
import sys
import json
from queue import Queue
from pyli5.admf.lipf import LIPF
from pyli5.admf.licf import LICF
from pyli5.admf.iqf import IQF
from pyli5.admf.internal_iface import InternalInterface
from pyli5.utils.logger import Logger

if __name__ == "__main__":
    logger = Logger("Bootstrapper")
    li_admf = InternalInterface()
    li_iqf = InternalInterface()
    logger.log("Starting application ADMF...")
    with open(os.environ["HOME"]+"/pyli5/src/pyli5/admf/admf.json") as f:
        logger.debug("Read from config file")
        c = json.load(f)["admf"]
        licf = LICF(li_iqf, li_admf)
        logger.log("LICF started")
        lipf = LIPF(c["lipf"]['admf_id'], ief_info=IEFInfo(xem_addr=c['lipf']['ief_info']['xem_addr'],
                                                           xem_port=c['lipf']['ief_info']['xem_port'],
                                                           xem_url=c['lipf']['ief_info']['xem_url'],
                                                           xem_id=c['lipf']['ief_info']['xem_id']),
                    icf_info=ICFInfo(xer_addr=c['lipf']['icf_info']['xer_addr'],
                                     xer_port=c['lipf']['icf_info']['xer_port']), li_admf=li_admf)
        logger.log("LIPF started")
        iqf = IQF(admf_id=c['iqf']['admf_id'],
                  hiqr_addr=c['iqf']['hiqr_addr'],
                  hiqr_port=c['iqf']['hiqr_port'],
                  icf_addr=c['iqf']['icf_xqr_addr'],
                  icf_port=c['iqf']['icf_xqr_port'],
                  li_iqf=li_iqf)
        logger.log("IQF started")
    while True:
        pass
