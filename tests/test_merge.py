"""Test class for merging multiple yaml files into one."""
from io import StringIO
from maraplus.parser import YamlParser


YAML_1 = """
---
migration:
  options:
    install_command: odoo2
  versions:
    - version: setup
      operations:
        pre:
          - echo 'pre-operation'
      addons:
        install:
          - crm
        upgrade:
          - note
    - version: 0.1.0
      operations:
        post:
          - echo 'post-operation'
      addons:
        install:
          - web
          - contacts
"""

YAML_2 = """
---
migration:
  options:
    install_command: odoo
  versions:
    - version: setup
      operations:
        pre:
          - echo 'pre-operation-2'
          - echo 'pre-operation'
      addons:
        install:
          - account
          - crm
        upgrade:
          - note
          - hr
    - version: 0.1.0
      operations:
        post:
          - echo 'post-operation'
          - echo 'post-operation-2'
      addons:
        install:
          - purchase
          - sale
"""

YAML_3 = """
---
migration:
  versions:
    - version: 0.2.0
      addons:
        install:
          - mrp
          - stock
"""

# When YAML_1 is combined with YAML_2
expected_yaml_dct_1 = {
    'migration': {
        'options': {
            'install_command': 'odoo',
        },
        'versions': [
            {
                'version': 'setup',
                'operations': {
                    'pre': [
                        'echo \'pre-operation\'',
                        'echo \'pre-operation-2\'',
                    ],

                },
                'addons': {
                    'install': ['crm', 'account'],
                    'upgrade': ['note', 'hr'],
                }
            },
            {
                'version': '0.1.0',
                'operations': {
                    'post': [
                        'echo \'post-operation\'',
                        'echo \'post-operation-2\'',
                    ],

                },
                'addons': {
                    'install': ['web', 'contacts', 'purchase', 'sale'],
                }
            },
        ]
    }
}
# When YAML_1 is combined with YAML_3
expected_yaml_dct_2 = {
    'migration': {
        'options': {
            'install_command': 'odoo2',
        },
        'versions': [
            {
                'version': 'setup',
                'operations': {
                    'pre': [
                        'echo \'pre-operation\'',
                    ],

                },
                'addons': {
                    'install': ['crm'],
                    'upgrade': ['note'],
                }
            },
            {
                'version': '0.1.0',
                'operations': {
                    'post': [
                        'echo \'post-operation\'',
                    ],

                },
                'addons': {
                    'install': ['web', 'contacts'],
                }
            },
            {
                'version': '0.2.0',
                'addons': {
                    'install': ['mrp', 'stock'],
                }
            },
        ]
    }
}
# When YAML_1 is combined with YAML_2 and YAML_3
expected_yaml_dct_3 = {
    'migration': {
        'options': {
            'install_command': 'odoo',
        },
        'versions': [
            {
                'version': 'setup',
                'operations': {
                    'pre': [
                        'echo \'pre-operation\'',
                        'echo \'pre-operation-2\'',
                    ],

                },
                'addons': {
                    'install': ['crm', 'account'],
                    'upgrade': ['note', 'hr'],
                }
            },
            {
                'version': '0.1.0',
                'operations': {
                    'post': [
                        'echo \'post-operation\'',
                        'echo \'post-operation-2\'',
                    ],

                },
                'addons': {
                    'install': ['web', 'contacts', 'purchase', 'sale'],
                }
            },
            {
                'version': '0.2.0',
                'addons': {
                    'install': ['mrp', 'stock'],
                }
            },
        ]
    }
}


def test_01_merge_yaml():
    """Merge main yaml with extra yaml override (same versions)."""
    y1 = StringIO(YAML_1)
    y2 = StringIO(YAML_2)
    parser = YamlParser.parser_from_buffer(y1, y2)
    assert parser.parsed == expected_yaml_dct_1


def test_02_merge_yaml():
    """Merge main yaml with extra yaml override (different version)."""
    y1 = StringIO(YAML_1)
    y3 = StringIO(YAML_3)
    parser = YamlParser.parser_from_buffer(y1, y3)
    assert parser.parsed == expected_yaml_dct_2


def test_03_merge_yaml():
    """Merge main yaml with 2 extra yaml overrides."""
    y1 = StringIO(YAML_1)
    y2 = StringIO(YAML_2)
    y3 = StringIO(YAML_3)
    parser = YamlParser.parser_from_buffer(y1, y2, y3)
    assert parser.parsed == expected_yaml_dct_3
