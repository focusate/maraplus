from maraplus.parser import unpack_keys_from_nested_dict


def test_01_unpack_keys_no_asterisk():
    # GIVEN
    data = {'a': {'b1': {'c': 1}, 'b2': {'c': 2}}}
    keys_chain = ['a', 'b1', 'c']
    # WHEN
    res = unpack_keys_from_nested_dict(data, keys_chain)
    # THEN
    assert res == [['a', 'b1', 'c']]


def test_02_unpack_keys_one_asterisk():
    # GIVEN
    data = {'a': {'b1': {'c': 1}, 'b2': {'c': 2}}}
    keys_chain = ['a', '*', 'c']
    # WHEN
    res = unpack_keys_from_nested_dict(data, keys_chain)
    # THEN
    assert res == [['a', 'b1', 'c'], ['a', 'b2', 'c']]


def test_03_unpack_keys_two_asterisks():
    # GIVEN
    data = {'a': {'b1': {'c': 1}, 'b2': {'c': 2}}}
    data = {
        'a': {
            'b1': {
                'c1': {'d': 1},
                'c2': {'d': 2},
            },
            'b2': {
                'c3': {'d': 3},
                'c4': {'d': 4},
            },
        }
    }
    keys_chain = ['a', '*', '*', 'd']
    # WHEN
    res = unpack_keys_from_nested_dict(data, keys_chain)
    # THEN
    assert res == [
        ['a', 'b1', 'c1', 'd'],
        ['a', 'b1', 'c2', 'd'],
        ['a', 'b2', 'c3', 'd'],
        ['a', 'b2', 'c4', 'd'],
    ]
