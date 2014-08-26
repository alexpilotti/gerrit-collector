# Configuration options

# This list from https://review.openstack.org/#/admin/groups/270,members and
# https://review.openstack.org/#/admin/groups/91,members
CI_USERS_NOVA = [
'Jenkins',
'Hyper-V CI',
'IBM PowerKVM Testing',
'XenServer CI',
'turbo-hipster',
'VMware Mine Sweeper'
]

CI_USERS_NEUTRON = [
'Jenkins',
'Arista Testing',
'Big Switch CI',
'Hyper-V CI',
'Mellanox External Testing',
'Midokura CI Bot',
'NEC OpenStack CI',
'Nuage CI',
'VMware Mine Sweeper'

]

CI_USERS = [
    'Jenkins',
    'Arista Testing',
    'Big Switch CI',
    'Brocade Tempest',
    'Cisco OpenStack CI Robot',
    'CitrixJenkins',
    'Compass CI',
    'Designate Jenkins',
    'Docker CI',
    'Freescale CI',
    'Fuel CI',
    'Huawei CI',
    'Hyper-V CI',
    'IBM DB2 Test',
    'IBM Neutron Testing',
    'IBM PowerKVM Testing',
    'IBM PowerVC Test',
    'Mellanox External Testing',
    'Metaplugin CI Test',
    'Midokura CI Bot',
    'NEC OpenStack CI',
    'NetScaler TestingSystem',
    'Neutron Ryu',
    'Nuage CI',
    'OpenContrail',
    'OpenDaylight Jenkins',
    'PLUMgrid CI',
    'Puppet Ceph Integration',
    'Puppet OpenStack CI',
    'Radware 3rd Party Testing',
    'Red Hat CI',
    'SmokeStack',
    'Tail-f NCS Jenkins',
    'VMware Mine Sweeper',
    'Wherenow.org Jenkins CI',
    'XenServer CI',
    'murano-ci',
    'nicirabot',
    'novaimagebuilder-jenkins',
    'reddwarf',
    'savanna-ci',
    'turbo-hipster',
    'vArmour CI Test',
    'vanillabot',
    ]

CI_PROJECTS = [
    'openstack/nova',
    'openstack/neutron'

]

CI_SYSTEM = {
    'nova': [
        'Jenkins',
        'Docker CI',
        'Hyper-V CI',
        'IBM PowerKVM Testing',
        'VMware Mine Sweeper',
        'XenServer CI',
        'turbo-hipster',
        ],
    'neutron': [
        'Jenkins',
        'Arista Testing',
        'Big Switch CI',
        'Brocade Tempest',
        'Cisco OpenStack CI Robot',
        'Huawei CI',
        'Hyper-V CI',
        'IBM Neutron Testing',
        'Mellanox External Testing',
        'Midokura CI Bot',
        'NEC OpenStack CI',
        'NetScaler TestingSystem',
        'Neutron Ryu',
        'Nuage CI',
        'OpenContrail',
        'OpenDaylight Jenkins',
        'PLUMgrid CI',
        'Tail-f NCS Jenkins',
        'VMware Mine Sweeper',
        'nicirabot',
        ]
    }

CI_NOVA_USERS = [
'XenServer CI',
'turbo-hipster',
'VMware Mine Sweeper',
'Jenkins',
'IBM PowerKVM',
'Hyper-V CI'
]

SENTIMENTS = [
    'Positive',
    'Negative',
    'Positive comment',
    'Negative comment',
    'Negative, buried in comment',
    'Unknown'
    ]