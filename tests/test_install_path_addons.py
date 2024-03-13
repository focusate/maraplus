import io

from maraplus.parser import YamlParser


def test_01_parse_install_path_addons_with_install_key(path_modules_one):
    # GIVEN
    buffer = io.StringIO(f"""---
migration:
  options:
    install_command: odoo
  versions:
    - version: setup
      modes:
        stage:
          addons:
            install: []
      addons:
        install:
          - crm
        install_paths:
          - {path_modules_one}
""")
    # WHEN
    res = YamlParser.parser_from_buffer(buffer).parsed
    # THEN
    assert res == {
        'migration': {
            'options': {'install_command': 'odoo'},
            'versions': [
                {
                    'version': 'setup',
                    'modes': {
                        'stage': {
                            'addons': {
                                'install': [],
                            }
                        }
                    },
                    'addons': {
                        'install': [
                            'crm',
                            'sale',
                            'mrp'
                        ]
                    }
                }
            ],
        }
    }


def test_02_parse_install_path_addons_without_install_key(path_modules_one):
    # GIVEN
    buffer = io.StringIO(f"""---
migration:
  options:
    install_command: odoo
  versions:
    - version: setup
      modes:
        stage:
          addons:
            install: []
      addons:
        install_paths:
          - {path_modules_one}
""")
    # WHEN
    res = YamlParser.parser_from_buffer(buffer).parsed
    # THEN
    assert res == {
        'migration': {
            'options': {'install_command': 'odoo'},
            'versions': [
                {
                    'version': 'setup',
                    'modes': {
                        'stage': {
                            'addons': {
                                'install': [],
                            }
                        }
                    },
                    'addons': {
                        'install': [
                            'crm',
                            'sale',
                            'mrp'
                        ]
                    }
                }
            ],
        }
    }


def test_03_parse_install_path_addons_multiple(path_modules_one, path_modules_two):
    # GIVEN
    buffer = io.StringIO(f"""---
migration:
  options:
    install_command: odoo
  versions:
    - version: setup
      addons:
        install_paths:
          - {path_modules_one}
          - {path_modules_two}
""")
    # WHEN
    res = YamlParser.parser_from_buffer(buffer).parsed
    # THEN
    assert res == {
        'migration': {
            'options': {'install_command': 'odoo'},
            'versions': [
                {
                    'version': 'setup',
                    'addons': {
                        'install': [
                            'crm',
                            'sale',
                            'mrp',
                            'account',
                            'stock',
                        ]
                    }
                }
            ],
        }
    }


def test_04_parse_install_path_addons_in_mode(path_modules_one):
    # GIVEN
    buffer = io.StringIO(f"""---
migration:
  options:
    install_command: odoo
  versions:
    - version: setup
      modes:
        stage:
          addons:
            install:
              - crm
            install_paths:
              - {path_modules_one}
""")
    # WHEN
    res = YamlParser.parser_from_buffer(buffer).parsed
    # THEN
    assert res == {
        'migration': {
            'options': {'install_command': 'odoo'},
            'versions': [
                {
                    'version': 'setup',
                    'modes': {
                        'stage': {
                            'addons': {
                                'install': [
                                    'crm',
                                    'sale',
                                    'mrp'
                                ],
                            }
                        }
                    },
                }
            ],
        }
    }


def test_05_parse_install_path_addons_in_multi_mode(path_modules_one, path_modules_two):
    # GIVEN
    buffer = io.StringIO(f"""---
migration:
  options:
    install_command: odoo
  versions:
    - version: setup
      modes:
        stage:
          addons:
            install_paths:
              - {path_modules_one}
        prod:
          addons:
            install_paths:
              - {path_modules_two}
      addons:
        install_paths:
          - {path_modules_one}
""")
    # WHEN
    res = YamlParser.parser_from_buffer(buffer).parsed
    # THEN
    assert res == {
        'migration': {
            'options': {'install_command': 'odoo'},
            'versions': [
                {
                    'version': 'setup',
                    'modes': {
                        'stage': {
                            'addons': {
                                'install': [
                                    'crm',
                                    'sale',
                                    'mrp'
                                ],
                            }
                        },
                        'prod': {
                            'addons': {
                                'install': [
                                    'sale',
                                    'account',
                                    'stock'
                                ],
                            }
                        },
                    },
                    'addons': {
                        'install': [
                            'crm',
                            'sale',
                            'mrp',
                        ]
                    }
                }
            ],
        }
    }
