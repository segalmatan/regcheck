import regcheck


class AttributeTestingClass(object):
    """
    class for storing attributes and testing them against regcheck
    """
    def __init__(self, **kwargs):
        for key, value in kwargs:
            # TODO: Fix syntax, this is wrong
            setattr(self, key, value)


class ClassA(AttributeTestingClass):
    def __init__(self, **kwargs):
        super(ClassA, self).__init__(**kwargs)


class ClassB(AttributeTestingClass):
    def __init__(self, **kwargs):
        super(ClassB, self).__init__(**kwargs)


def test_sanity():
    """
    Test the basic features of regcheck
    """
    MIN_REPEAT = 2
    MAX_REPEAT = 5

    evaluation = regcheck.Evaluation(
        regcheck.Check(ClassA, attribute1=1),
        regcheck.Check(ClassB, attribute1=2, attribute2="asdf"),
        regcheck.Range(
            MIN_REPEAT, MAX_REPEAT,
            regcheck.Check(ClassA)
        )
    )

    base_sequence = [
        ClassA(attribute1=1),
        ClassB(attribute1=2, attribute2="asdf"),
    ]

    # Go through possible ranges of repeats and assert appropriate repeat result
    for count in range(0, MAX_REPEAT + 2):
        sequence = base_sequence + ([ClassA(someattribute=4)] * count)

        if MIN_REPEAT <= count and count <= MAX_REPEAT:
            assert evaluation.check(sequence)
        else:
            assert not evaluation.check(sequence)