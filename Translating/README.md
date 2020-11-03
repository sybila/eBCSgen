## Relation of BCSL agents to SBML-multi speciesTypes

### Exaple BCSL rules
```
            KaiC(S{u},T{u}).KaiC(S{u},T{u})::cyt => KaiC(S{p},T{u}).KaiC(S{p},T{u})::cyt
            KaiC(S{p},T{u}).KaiC(S{p},T{u})::cyt => KaiC(S{u},T{u}).KaiC(S{u},T{u})::cyt 
            KaiC(S{p},T{u}).KaiC(S{p},T{u})::cyt => KaiC(S{p},T{p}).KaiC(S{p},T{p})::cyt 
            KaiC(S{p},T{p}).KaiC(S{p},T{p})::cyt => KaiC(S{p},T{u}).KaiC(S{p},T{u})::cyt
            KaiB4{i}::cyt => KaiB4{a}::cyt
            KaiB4{a}::cyt => KaiB4{i}::cyt
            KaiB4{a}::cyt + KaiA2()::cyt => KaiB4{a}.KaiA2()::cyt
            KaiC().KaiC()::cyt => 2 KaiC()::cyt
            2 KaiC()::cyt => KaiC().KaiC()::cyt
```
We have atomic signature ```A = {T:{u, p}, S:{u, p}, KaiB4:{a,i}}```

and structure signature ```S = {KaiC:{S, T}, KaiA2:{}}```
>in order to create individual species in speciesType of SBML-multi (representation of current active state of agent)
we shall extract unique complex agents in specific compartment from rules.
>
Output of the newly introduced function in *Core.Model* 

```def unique_complexes_and_compartments()``` should look like:
 
 ```C = {('cyt', KaiC(), KaiC()), ('cyt', KaiA2()), ('cyt', KaiC(S{p},T{u}), KaiC(S{p},T{u})), ('cyt', KaiC(S{u},T{u}), KaiC(S{u},T{u})), ('cyt', KaiC()), ('cyt', KaiB4{a}, KaiA2()), ('cyt', KaiB4{a}), ('cyt', KaiB4{i}), ('cyt', KaiC(S{p},T{p}), KaiC(S{p},T{p}))}```
 >Notice, that outside structure is set() -> that ensures uniqueness. Nested structures are unmodifiable
>tuples... 0. index represents compartment of the complex and following 1...n indexes hold structure or atomic
>agents of which the main complex consists
---
### SBML-multi agents creation

SBML multi agents are called *Species*. Some agents can be similar to each other.
To avoid repetition, common type is defined in *SpeciesTypes* and different *Species*
are mapping to it. *Species* and *SpeciesTypes* are more general than BCSL agents,
so *SpeciesType* can represent Atomic or Structure or Complex agent regardless.

E.g. in BCSL, domain parameter can be set only in Atomic agents but *Species* do not distinguish
between Structural or Atomic agents... they are all the same and can have every feature there is,
regardless of their type.

-----

###Translation process

Because the semantic should be intact, Structure, Atomic and Complex agents should remain their differences
even if they are translated to SBML-multi.
>Thus, 3 types of SpeciesTypes are introduced while translating:

SpeciesTypes with Atomic abilities, speciesTypes with Structure abilities and SpeciesTypes with Complex abilities. These are not
hardcoded, but they emerge from process of their creation. 

* Firstly, Atomic agents from ```A``` are translated to SpeciesTypes and for every agent, all speciesFeatures(BCSL domains) present in signature are set
* Secondly, Structure agents from ```S``` are translated to SpeciesTypes, but no SpeciesFeatures are added, however
already translated SpeciesTypes with Atomic abilities (present in signature of specific Structural agent), are mapped to SpeciesTypeComponentIndex of every SpeciesType with Structure abilities.
This way it is ensured, that SpeciesType with Structure abilities 'knows' what SpieciesType with Atomic abilities
can be put inside of it.
* Further, complexes are translated to speciesTypes. There are 2 possibilities here. Complex either consists of 
single agent, or multiple agents. If it consists just of 1 agent, no speciesType has to be created, but if it consists of
more than 1 agent, new speciesType with complex abilities is created. Non-repetitiveness of these templates is
ensured by saving names of already created templates in ```self.finishedComplexSpeciesTypes```
* Lastly, we need to create individual Species. So for every outside agent in ```C```, Species is created.
Species are individual representation of 'state' of a model. So for example for ```KaiC()```
4 different species are created using this unique set of tuples:
```KaiC(S{p}, T{p})::cyt, KaiC(S{u}, T{p})::cyt, KaiC(S{p}, T{u})::cyt, KaiC(S{u}, T{u})::cyt```
For ```KaiB4``` 2 Species are created: ```KaiB4{a}::cyt, KaiB4{i}::cyt```

>notice that Spieces have compartment parameter set, so if there is same Species in different compartment
>new has to be created to ensure individuallity
------
###TODO

* Make the code prettier
* Create some less messy algorithm of how to set ID's for objects in SBML-multi (if that is possible)
* Introduce Variables to translation, initial quanitities and concentrations
* Introduce reaction to translation
* Find possible bugs and create some usefull tests (using http://constraint.caltech.edu:8888/validator_servlet/index.jsp)
as output checker, might be usefull
* Test the application further, try to describe it or make it more effective