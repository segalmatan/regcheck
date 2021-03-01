## Regcheck
<p>
  <img src="https://img.shields.io/badge/version-0.1-blue.svg?cacheSeconds=2592000" alt="version"/>
  <a href="https://github.com/segalmatan/regcheck/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="license"/>
  </a>
</p>

Utility for examining object sequences with regex-like rules

### example

```python
import regcheck
sequence = [...]
evaluation = regcheck.Evaluation(
  regcheck.Check(ClassA, attribute1=1),
  regcheck.Check(ClassB, attribute1=2, attribute2="asdf"),
  regcheck.Range(
    2,5,
    regcheck.Check(ClassA)
  )
)

print evaluation.check(sequence)
```
### explenation
The example above checks that the sequence opens up with an object of type "ClassA" with an attribute "attribute1" with value 1,
following up with an object of type "ClassB" with attributes attribute1 with value 2 and attribute2 with value "asdf",
after that the sequence should follow up with 2 to 5 objects of type ClassA to be valid
