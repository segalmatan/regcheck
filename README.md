# reCheck
<a href="https://github.com/p-ranav/indicators/blob/master/LICENSE">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="license"/>
</a>
<img src="https://img.shields.io/badge/version-0.1-blue.svg?cacheSeconds=2592000" alt="version"/>

recheck is a utility I made for playing around with regex validation on python objects (as opposed to strings), currently it's centered around verifying a sequence as opposed to finding it. Its also intended to support some novel features such as variables corrosponding to evaluated objects.

### example

```python
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
```
### explenation
The example above checks that the sequence opens up with an object of type "ClassA" with an attribute "attribute1" with value 1,
following up with an object of type "ClassB" with attributes attribute1 with value 2 and attribute2 with value "asdf",
after that the sequence should follow up with 2 to 5 objects of type ClassA to be valid
