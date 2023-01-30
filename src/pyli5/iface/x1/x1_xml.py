""" Contains all fields for parsing an XML message"""

x1NS = "{http://uri.etsi.org/03221/X1/2017/10}"
xsiNS = "{http://www.w3.org/2001/XMLSchema-instance}"

X1REQUEST = 'X1Request'
X1RESPONSE = 'X1Response'

## Child of X1REQ / X1RESP
X1REQUESTMESSAGE = 'x1RequestMessage'
X1RESPONSEMESSAGE = 'x1ResponseMessage'
TYPE = xsiNS + 'type'  ##attrib of X1Req/RespMsg

## To be concatenated with req or resp. Keys of TYPE in XML (that is type is '@type' : 'stuff')
TYPE_ERROR = "Error"
TYPE_ACTIVATETASK = "ActivateTask"
TYPE_DEACTIVATETASK = "DeactivateTask"
TYPE_CREATEDESTINATION = "CreateDestination"
TYPE_REMOVEDESTINATION = "RemoveDestination"
##
REQUEST = "Request"
RESPONSE = "Response"

# <---- CHILDS OF X1 MESSAGE (req or resp)---->
ADMFID = 'admfIdentifier'
NEID = 'neIdentifier'
TIMESTP = 'messageTimestamp'
X1TID = 'x1TransactionId'
VERSION = "version"
REQMESSAGETYPE = "requestMessageType"

## ActivateTaskRequest
TASK = 'taskDetails'  # if task related

## CreateDestinationRequest
DESTINATION = 'destinationDetails'

## <---- FIELDS IN taskDetails ---->
TASK_XID = "xId"
TASK_IDENTIFIERS = "targetIdentifiers"  # dict
TASK_IDENTIFIERS_TID = "targetIdentifier"  # key of IDENTIFIERS
TASK_DIDS = "listOfDIDs"

## <---- FIELDS IN targetIdentifiers ---->
IDENTITYASSOCTARGETID = "identityAssociationTargetIdentifier"
SUPIIMSI = "supiimsi"
SUPINAI = "supinai"
SUCI = "suci"
FIVEGSTMSI = "fiveggstmsi"
FIVEGGUTI = "fivegguti"

IDS = [SUPIIMSI, SUPINAI, FIVEGGUTI, FIVEGSTMSI]

## <---- FIELDS IN destinationDetails ---->
DESTINATION_DID = 'dId'
DESTINATION_DELIVERYADDR = 'deliveryAddress'  # dict
DESTINATION_DELIVERYADDR_IPADDRnPORT = "ipAddressAndPort"  # field of ADDR
DESTINATION_DELIVERYADDR_IPADDRnPORT_ADDR = "address"
DESTINATION_DELIVERYADDR_IPADDRnPORT_ADDR_IPV4 = "IPv4Address"

DESTINATION_DELIVERYADDR_IPADDRnPORT_PORT = 'port'  # dict
DESTINATION_DELIVERYADDR_IPADDRnPORT_PORT_TCPPORT = 'TCPPort'  # key of PORT

## <---- FIELDS IN X1 Responses ---->
OK = "oK"
OK_ACKnCOMPLETED = "AcknowledgedAndCompleted"
ERROR = "errorInformation"
ERROR_CODE = "errorCode"
ERROR_DESC = "errorDescription"


def strip_namespace(tag: str) -> str:
    return tag.split("}")[1]
