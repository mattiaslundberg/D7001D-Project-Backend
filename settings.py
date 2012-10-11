# Global variables
import os
user = 'GROUP2'#os.environ['LTU_USER']

ADDR_ID = 'ZEYNBMDKH2SVL'
DOMAIN = 'd7001d.mlundberg.se'

#### WSN NAMES ####
WSN_ELB = 'wsnelbgroup2'
WSN_ADDR = 'wsn.%s' % DOMAIN
WSN_SCALE_UP = '12_LP1_WSNUP_D7001D_%s' % user
WSN_SCALE_DOWN = '12_LP1_WSNDWN_D7001D_%s' % user
WSN_POLICY_UP = '12_LP1_WSNUPPOL_D7001D_%s' % user
WSN_POLICY_DOWN = '12_LP1_WSNDWNPOL_D7001D_%s' % user
WSN_ASG = '12_LP1_WSNASG_D7001D_%s' % user
WSN_LC = '12_LP1_WSNLC_D7001D_%s' % user
WSN_AMI ='ami-3b11114f'

#### GUI NAMES ####
FRONTEND_ELB = 'FRONTENDelbgroup2'
GUI_ADDR = 'gui.%s' % DOMAIN
FRONTEND_SCALE_UP = '12_LP1_FRONTENDUP_D7001D_%s' % user
FRONTEND_SCALE_DOWN = '12_LP1_FRONTENDDWN_D7001D_%s' % user
FRONTEND_POLICY_UP = '12_LP1_FRONTENDUPPOL_D7001D_%s' % user
FRONTEND_POLICY_DOWN = '12_LP1_FRONTENDDWNPOL_D7001D_%s' % user
FRONTEND_ASG = '12_LP1_FRONTENDASG_D7001D_%s' % user
FRONTEND_LC = '12_LP1_FRONTENDLC_D7001D_%s' % user

FRONTEND_HTTP_AMI = 'ami-41111135'
GUI_AMI_MASTER = 'ami-dd1b1ba9'
GUI_AMI_WORKER = 'ami-c11d1db5'

FRONTEND_INCOMING = '12_LP1_SQS_D7001D_FRONTEND_INCOMING_%s' % user
FRONTEND_OUTGOING = '12_LP1_SQS_D7001D_FRONTEND_OUTGOING_%s' % user

MASTER_TOKEN = "12_LP1_SQS_D7001D_FRONTEND_MASTER_%s" % user
INTERVALL = 60
TOKEN_TIME = INTERVALL*3

HTTP_PORT = 8080

