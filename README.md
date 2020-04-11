# recheck
Regular expression sequence checker

# example

import recheck
sequence = [...]
evaluation = recheck.Evaluation(
  recheck.Check(ClassA, attribute1=1),
  recheck.Check(ClassB, attribute1=2, attribute2="asdf"),
  recheck.Range(
    2,5,
    recheck.Check(ClassA)
  )
)

print evaluation.check(sequence)

# explenation
The example above checks that the sequence opens up with an object of type "ClassA" with an attribute "attribute1" with value 1,
following up with an object of type "ClassB" with attributes attribute1 with value 2 and attribute2 with value "asdf",
after that the sequence should follow up with 2 to 5 objects of type ClassA to be valid
