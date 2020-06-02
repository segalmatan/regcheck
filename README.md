<p align="center">
  <img src="https://github.com/segalmatan/recheck/blob/master/logo.png"/> 
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1-blue.svg?cacheSeconds=2592000" alt="version"/>
  <a href="https://github.com/p-ranav/indicators/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="license"/>
  </a>
</p>

Everybody needs that friend who really knows his regex, checkmate is a ~~mate~~ utility to help you do regex-like validation on python object sequences using lots of checks :) . It also supports some novel features to make this validation easier like variables that can be controlled during the validation of your python sequence. Extending the regex engine is hopefully easy to do and open to feedback, in the future I hope to add parallel state evaluation for a performance boost and expose more information that could be used to understand the reason for a validation failure (because who doesn't like debugging regex?).

### example

```python
import checkmate
sequence = [...]
evaluation = checkmate.Evaluation(
  checkmate.Check(ClassA, attribute1=1),
  checkmate.Check(ClassB, attribute1=2, attribute2="asdf"),
  checkmate.Range(
    2,5,
    checkmate.Check(ClassA)
  )
)

print evaluation.check(sequence)
```
### explenation
The example above checks that the sequence opens up with an object of type "ClassA" with an attribute "attribute1" with value 1,
following up with an object of type "ClassB" with attributes attribute1 with value 2 and attribute2 with value "asdf",
after that the sequence should follow up with 2 to 5 objects of type ClassA to be valid
