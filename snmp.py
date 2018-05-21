from pysnmp.hlapi import *

errorIndication, errorStatus, errorIndex, varBinds = next( getCmd(SnmpEngine(),CommunityData('uTdc9j48PBRkxn5DcSjchk', mpModel=0),UdpTransportTarget(('uTdc9j48PBRkxn5DcSjchk', 161)), ContextData(), ObjectType('.1.3.6.1.2.1.2.2.1'))

if errorIndication:
    print(errorIndication)
elif errorStatus:
    print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
else:
    for varBind in varBinds:
        print(' = '.join([x.prettyPrint() for x in varBind]))