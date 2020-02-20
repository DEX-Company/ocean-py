"""

Test provenance


"""
import json
import re
import secrets

from starfish.metadata.provenance import create_publish

PUBLISH_STANDARD = {
    'prefix':{
        'xsd': 'http://www.w3.org/2001/XMLSchema#',
        'prov': 'http://www.w3.org/ns/prov#',
        'dep': 'http://dex.sg'
    },
    'activity': {
        'dep:<activity_id>': {
            'prov:type': {
                '$': 'dep:import',
                'type': 'xsd:string'
            }
        }
    },
    'entity': {
        'dep:this': {
            'prov:type': {
                '$': 'dep:asset',
                'type': 'xsd:string'
            }
        }
    },
    'agent': {
        'dep:<agent_id>': {
            'prov:type': {
                '$': 'dep:account',
                'type': 'xsd:string'
            }
        }
    },
    'wasAssociatedWith': {
        '_:<random_id>': {
            'prov:agent': '<agent_id>',
            'prov:activity': '<activity_id>'
        }
    },
    'wasGeneratedBy': {
        '_:<random_id>': {
            'prov:entity': 'dep:this',
            'prov:activity': '<activity_id>'
        }
    }
}

def assert_walk_dict(standard, result):
    if isinstance(result, dict):
        assert(isinstance(standard, dict))
        for name, values in standard.items():
            assert(name in result)
            if isinstance(result[name], dict):
                assert_walk_dict(standard[name], result[name])
            else:
                assert(standard[name] == result[name])
def test_provenance_publish():

    agent_id = secrets.token_hex(32)
    result = create_publish(agent_id)
    assert(isinstance(result, dict))

    agent_dep = f'dep:{agent_id}'
    PUBLISH_STANDARD['agent'][agent_dep] =  PUBLISH_STANDARD['agent']['dep:<agent_id>']
    del PUBLISH_STANDARD['agent']['dep:<agent_id>']

    activity_dep = list(result['activity'].keys())[0]
    activity_id = re.sub(r'dep:', '', activity_dep)
    PUBLISH_STANDARD['activity'][activity_dep] =  PUBLISH_STANDARD['activity']['dep:<activity_id>']
    del PUBLISH_STANDARD['activity']['dep:<activity_id>']

    id_dep = list(result['wasAssociatedWith'].keys())[0]
    PUBLISH_STANDARD['wasAssociatedWith'][id_dep] =  PUBLISH_STANDARD['wasAssociatedWith']['_:<random_id>']
    del PUBLISH_STANDARD['wasAssociatedWith']['_:<random_id>']


    PUBLISH_STANDARD['wasAssociatedWith'][id_dep]['prov:agent'] = agent_id
    PUBLISH_STANDARD['wasAssociatedWith'][id_dep]['prov:activity'] = activity_id

    id_dep = list(result['wasGeneratedBy'].keys())[0]
    PUBLISH_STANDARD['wasGeneratedBy'][id_dep] =  PUBLISH_STANDARD['wasGeneratedBy']['_:<random_id>']
    del PUBLISH_STANDARD['wasGeneratedBy']['_:<random_id>']

    PUBLISH_STANDARD['wasGeneratedBy'][id_dep]['prov:activity'] = activity_id

    assert_walk_dict(PUBLISH_STANDARD, result)

