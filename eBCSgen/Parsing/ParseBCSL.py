import collections
import json
import numpy as np
from numpy import inf
from copy import deepcopy
from lark import Lark, Transformer, Tree
from lark import UnexpectedCharacters, UnexpectedToken
from lark.load_grammar import _TERMINAL_NAMES
import regex
from sortedcontainers import SortedList

from eBCSgen.Core.Atomic import AtomicAgent
from eBCSgen.Core.Complex import Complex
from eBCSgen.Core.Rate import Rate
from eBCSgen.Core.Rule import Rule
from eBCSgen.Core.Structure import StructureAgent
from eBCSgen.Regulations.ConcurrentFree import ConcurrentFree
from eBCSgen.Regulations.Conditional import Conditional
from eBCSgen.Regulations.Ordered import Ordered
from eBCSgen.Regulations.Programmed import Programmed
from eBCSgen.Regulations.Regular import Regular
from eBCSgen.TS.State import State, Memory, Vector
from eBCSgen.TS.TransitionSystem import TransitionSystem
from eBCSgen.TS.Edge import edge_from_dict
from eBCSgen.Core.Side import Side
from eBCSgen.Core.Model import Model
from eBCSgen.Errors.ComplexParsingError import ComplexParsingError
from eBCSgen.Errors.UnspecifiedParsingError import UnspecifiedParsingError


def load_TS_from_json(json_file: str) -> TransitionSystem:
    """
    Loads given JSON and interprets it as a TransitionSystem.

    :param json_file: given TS in JSON
    :return: resulting TransitionSystem
    """
    complex_parser = Parser("rate_complex")
    with open(json_file) as json_file:
        data = json.load(json_file)

        ordering = SortedList(
            map(
                lambda agent: complex_parser.parse(agent).data.children[0],
                data["ordering"],
            )
        )
        ts = TransitionSystem(ordering, data["bound"])
        ts.states_encoding = dict()
        for node_id in data["nodes"]:
            vector = np.array(eval(data["nodes"][node_id]))
            is_hell = True if vector[0] == inf else False
            ts.states_encoding[int(node_id)] = State(Vector(vector), Memory(0), is_hell)
        ts.edges = {edge_from_dict(edge) for edge in data["edges"]}
        ts.init = data["initial"]
        if "parameters" in data:
            ts.params = data["parameters"]

        ts.unprocessed = {
            State(Vector(np.array(eval(state))), Memory(0))
            for state in data.get("unprocessed", list())
        }
        ts.states = set(ts.states_encoding.values()) - ts.unprocessed
        return ts


class Result:
    """
    Class to represent output from the Parser.
    """

    def __init__(self, success, data):
        self.success = success
        self.data = data


class SideHelper:
    """
    Class to represent side of a rule.
    """

    def __init__(self):
        self.seq = []
        self.comp = []
        self.complexes = []
        self.counter = 0

    def __str__(self):
        return " | ".join(
            [str(self.seq), str(self.comp), str(self.complexes), str(self.counter)]
        )

    def __repr__(self):
        return str(self)

    def to_side(self):
        return Side(
            [
                Complex(self.seq[c[0] : c[1] + 1], self.comp[c[0]])
                for c in self.complexes
            ]
        )


GRAMMAR = r"""
    model: (sections)* rules (sections | rules)*
    sections: inits | definitions | complexes | regulation

    rules: RULES_START _NL+ ((rule|COMMENT) _NL+)* rule _NL*
    inits: INITS_START _NL+ ((init|COMMENT) _NL+)* init _NL*
    definitions: DEFNS_START _NL+ ((definition|COMMENT) _NL+)* definition _NL*
    complexes: COMPLEXES_START _NL+ ((cmplx_dfn|COMMENT) _NL+)* cmplx_dfn _NL*
    regulation: REGULATION_START _NL+ regulation_def _NL*

    init: const? rate_complex (COMMENT)?
    definition: def_param "=" number (COMMENT)?
    rule: ((label)? side ARROW side ("@" rate)? (";" variable)? (COMMENT)?) | ((label)? side BI_ARROW side ("@" rate "|" rate)? (";" variable)? (COMMENT)?)
    cmplx_dfn: cmplx_name "=" value (COMMENT)?

    side: (const? complex "+")* (const? complex)?
    complex: (abstract_sequence|value|cmplx_name) DOUBLE_COLON compartment

    !rate : fun "/" fun | fun
    !fun: const | param | rate_agent | fun "+" fun | fun "-" fun | fun "*" fun | fun POW const | "(" fun ")"

    !rate_agent: "[" rate_complex "]"

    COMMENT: "//" /[^\n]/*

    COM: "//"
    POW: "**"
    ARROW: "=>"
    BI_ARROW: "<=>"
    RULES_START: "#! rules"
    INITS_START: "#! inits"
    DEFNS_START: "#! definitions"
    COMPLEXES_START: "#! complexes"
    REGULATION_START: "#! regulation"
    _NL: /(\r?\n[\t ]*)+/

    !label: CNAME "~"

    param: CNAME
    def_param : CNAME
    number: NUMBER

    const: (INT|DECIMAL)

    %import common.WORD
    %import common.NUMBER
    %import common.INT
    %import common.DECIMAL
    %import common.WS_INLINE
    %ignore WS_INLINE
    %ignore COMMENT
"""

EXTENDED_GRAMMAR = """
    abstract_sequence: atomic_complex | atomic_structure_complex | structure_complex
    atomic_complex: atomic ":" (VAR | value)
    atomic_structure_complex: atomic ":" structure ":" (VAR | value)
    structure_complex: structure ":" (VAR | value)

    variable: VAR "=" "{" cmplx_name ("," cmplx_name)+ "}"
    VAR: "?"
"""

COMPLEX_GRAMMAR = """
    rate_complex: value DOUBLE_COLON compartment
    value: ((agent | cmplx_name) ".")* (agent | cmplx_name)
    agent: atomic | structure
    structure: s_name "(" composition ")"
    composition: (atomic ",")* atomic?
    atomic : a_name "{" state "}"

    a_name: CNAME
    s_name: CNAME
    compartment: CNAME
    cmplx_name: CNAME
    !state: (DIGIT|LETTER|"+"|"-"|"*"|"_")+

    DOUBLE_COLON: "::"

    %import common.CNAME
    %import common.LETTER
    %import common.DIGIT
"""

REGULATIONS_GRAMMAR = """
    regulation_def: "type" ( regular | programmed | ordered | concurrent_free | conditional ) 

    !regular: "regular" _NL+ (DIGIT|LETTER| "+" | "*" | "(" | ")" | "[" | "]" | "_" | "|" | "&")+ _NL*

    programmed: "programmed" _NL+ (successors _NL+)* successors _NL*
    successors: CNAME ":" "{" CNAME ("," CNAME)* "}"

    ordered: "ordered" _NL+ order ("," order)* _NL*
    order: ("(" CNAME "," CNAME ")")

    concurrent_free: "concurrent-free" _NL+ order ("," order)* _NL*

    conditional: "conditional" _NL+ context (_NL+ context)* _NL*
    context: CNAME ":" "{" rate_complex ("," rate_complex)* "}"
"""


class TransformRegulations(Transformer):
    def regulation(self, matches):
        return {"regulation": matches[1]}

    def regulation_def(self, matches):
        return matches[0]

    def regular(self, matches):
        re = "".join(matches[1:])
        # might raise exception
        regex.compile(re)
        return Regular(re)

    def programmed(self, matches):
        successors = {k: v for x in matches for k, v in x.items()}
        return Programmed(successors)

    def successors(self, matches):
        return {str(matches[0]): {str(item) for item in matches[1:]}}

    def ordered(self, matches):
        return Ordered(set(matches))

    def order(self, matches):
        return str(matches[0]), str(matches[1])

    def conditional(self, matches):
        context_fun = {k: v for x in matches for k, v in x.items()}
        return Conditional(context_fun)

    def context(self, matches):
        return {str(matches[0]): {item.children[0] for item in matches[1:]}}

    def concurrent_free(self, matches):
        return ConcurrentFree(set(matches))


class ReplaceVariables(Transformer):
    """
    This class is used to replace variables in rule (marked by ?) by
    the given cmplx_name (so far limited only to that).
    """

    def __init__(self, to_replace):
        super(ReplaceVariables, self).__init__()
        self.to_replace = to_replace

    def VAR(self, matches):
        return deepcopy(self.to_replace)


class ExtractComplexNames(Transformer):
    """
    Extracts definitions of cmplx_name from #! complexes part.

    Also multiplies rule with variable to its instances using ReplaceVariables Transformer.
    """

    def __init__(self):
        super(ExtractComplexNames, self).__init__()
        self.complex_defns = dict()

    def cmplx_dfn(self, matches):
        self.complex_defns[str(matches[0].children[0])] = matches[1]

    def rules(self, matches):
        new_rules = [matches[0]]
        for rule in matches[1:]:
            if rule.children[-1].data == "variable":
                variables = rule.children[-1].children[1:]
                for variable in variables:
                    replacer = ReplaceVariables(variable)
                    new_rule = Tree("rule", deepcopy(rule.children[:-1]))
                    new_rules.append(replacer.transform(new_rule))
            else:
                new_rules.append(rule)
        return Tree("rules", new_rules)


def remove_nested_complex_aliases(complex_defns):
    """
    Removes nested complex aliases from their definitions.
    """

    def replace_aliases(complex_defns):
        new_definitions = dict()
        for defn in complex_defns:
            result = []
            for child in complex_defns[defn]:
                if child.data == "cmplx_name":
                    result += complex_defns[str(child.children[0])]
                else:
                    result.append(child)
            new_definitions[defn] = result
        return new_definitions

    complex_defns = {key: complex_defns[key].children for key in complex_defns}
    new_defns = replace_aliases(complex_defns)

    while new_defns != complex_defns:
        complex_defns = new_defns
        new_defns = replace_aliases(complex_defns)

    complex_defns = {key: Tree("value", complex_defns[key]) for key in complex_defns}
    return complex_defns


class TransformAbstractSyntax(Transformer):
    """
    Transformer to remove "zooming" syntax.

    Divided to three special cases (declared below).
    Based on replacing subtrees in parent trees.
    """

    def __init__(self, complex_defns):
        super(TransformAbstractSyntax, self).__init__()
        self.complex_defns = complex_defns

    def cmplx_name(self, matches):
        return deepcopy(self.complex_defns[str(matches[0])])

    def abstract_sequence(self, matches):
        return matches[0]

    def atomic_structure_complex(self, matches):
        """
        atomic:structure:complex
        """
        structure = self.insert_atomic_to_struct(matches[0], matches[1])
        sequence = self.insert_struct_to_complex(structure, matches[2])
        return sequence

    def atomic_complex(self, matches):
        """
        atomic:complex
        """
        sequence = self.insert_atomic_to_complex(matches[0], matches[1])
        return sequence

    def structure_complex(self, matches):
        """
        structure:complex
        """
        sequence = self.insert_struct_to_complex(matches[0], matches[1])
        return sequence

    def insert_atomic_to_struct(self, atomic, struct):
        """
        Adds an atomic subtree to a struct tree. If a non-empty atomic with the same name
        already exists in the struct, it raises an error to prevent illegal nesting.

        Args:
            atomic: The atomic subtree to be added.
            struct: The struct tree where the atomic will be added.

        Returns:
            The updated struct tree with the atomic added.

        Raises:
            ComplexParsingError: If a non-empty atomic with the same name is already present in the struct.
        """
        if len(struct.children) == 2:
            for i in range(len(struct.children[1].children)):
                if self.get_name(atomic) == self.get_name(
                    struct.children[1].children[i]
                ):
                    if self.is_empty(struct.children[1].children[i]):
                        struct.children[1].children[i] = atomic
                        return struct
                    raise ComplexParsingError(
                        f"Illegal nesting sequence: {atomic}:{struct}", struct
                    )
            struct.children[1].children.append(atomic)
        else:
            struct.children.append(Tree("composition", [atomic]))
        return struct

    def insert_struct_to_complex(self, struct, complex):
        """
        Adds a struct subtree to a complex tree, or merges it with an existing struct subtree. This method first
        searches for a struct in the complex with the same name as the input struct. If found, it then checks for
        atomic incompatibility within the structs.

        The method ensures that the struct being added does not contain atomics with names that match any atomics
        in the corresponding struct in the complex. This step is crucial to maintain the integrity of the complex
        by avoiding conflicting or duplicate atomic structures.

        Args:
            struct: The struct subtree to be added or merged.
            complex: The complex tree where the struct will be added or merged.

        Returns:
            The updated complex tree with the struct added or merged.

        Raises:
            ComplexParsingError: If no matching struct is found in the complex.
        """
        if isinstance(complex.children[0].children[0].children[0].children[0], Tree):
            search = complex.children[0]
        else:
            search = complex

        for i in range(len(search.children)):
            if self.get_name(struct) == self.get_name(search.children[i].children[0]):
                struct_found = True
                # search same name structs - if they contain atomics with matching names, they are considered incompatible
                for j in range(len(struct.children[1].children)):
                    for k in range(
                        len(search.children[i].children[0].children[1].children)
                    ):
                        if self.get_name(
                            struct.children[1].children[j]
                        ) == self.get_name(
                            search.children[i].children[0].children[1].children[k]
                        ):
                            struct_found = False
                            break
                    # if no same name atomic found in the struct, we found the suitable complex's struct
                    if not struct_found:
                        break

                if struct_found:
                    # if the complex's struct is empty, replace it with the struct
                    if self.is_empty(search.children[i]):
                        search.children[i] = Tree("agent", [struct])
                    else:
                        # if the complex's struct is not empty merge the struct's children into the complex's struct
                        search.children[i].children[0].children[1].children += struct.children[1].children
                    return complex

        raise ComplexParsingError(
            f"Illegal struct nesting or duplication: {struct}:{complex}", complex
        )

    def insert_atomic_to_complex(self, atomic, complex):
        """
        Adds an atomic subtree to a complex tree. If a non-empty atomic with the same name
        is already present in the complex, it raises an error to prevent illegal nesting.

        Args:
            atomic: The atomic subtree to be added.
            complex: The complex tree where the atomic will be added.

        Returns:
            The updated complex tree with the atomic added.

        Raises:
            ComplexParsingError: If an atomic with the same name is already present in the complex.
        """
        if isinstance(complex.children[0].children[0].children[0].children[0], Tree):
            search = complex.children[0]
        else:
            search = complex

        for i in range(len(search.children)):
            if self.get_name(atomic) == self.get_name(search.children[i].children[0]):
                if self.is_empty(search.children[i].children[0]):
                    search.children[i] = Tree("agent", [atomic])
                    return complex
        raise ComplexParsingError(
            f"Illegal atomic nesting or duplication: {atomic}:{complex}", complex
        )

    def get_name(self, agent):
        return str(agent.children[0].children[0])

    def complex(self, matches):
        result = []
        for match in matches[0].children:
            if match.data == "value":
                result += match.children
            else:
                result.append(match)
        return Tree("complex", [Tree("value", result)] + matches[1:])

    def is_empty(self, agent):
        """
        Checks if the agent is empty.
        """
        if agent.data == "atomic":
            return agent.children[1].children[0] == "_"
        elif agent.data == "agent":
            return len(agent.children[0].children[1].children) == 0
        return False


class TreeToComplex(Transformer):
    """
    Creates actual Complexes in rates of the rules - there it is safe,
    order is not important. Does not apply to the rest of the rule!
    """

    def state(self, matches):
        return "".join(map(str, matches))

    def atomic(self, matches):
        name, state = str(matches[0].children[0]), matches[1]
        return AtomicAgent(name, state)

    def structure(self, matches):
        name = str(matches[0].children[0])
        if len(matches) > 1:
            composition = set(matches[1].children)
            return StructureAgent(name, composition)
        else:
            return StructureAgent(name, set())

    def rate_complex(self, matches):
        sequence = []
        for item in matches[0].children:
            sequence.append(item.children[0])
        compartment = matches[2]
        return Tree("agent", [Complex(sequence, compartment)])

    def compartment(self, matches):
        return str(matches[0])


class TreeToObjects(Transformer):
    def __init__(self):
        super(TreeToObjects, self).__init__()
        self.params = set()

    """
    A transformer which is called on a tree in a bottom-up manner and transforms all subtrees/tokens it encounters.
    Note the defined methods have the same name as elements in the grammar above.

    Creates the actual Model object after all the above transformers were applied.
    """

    def const(self, matches):
        return float(matches[0])

    def def_param(self, matches):
        return str(matches[0])

    def label(self, matches):
        return str(matches[0])

    def number(self, matches):
        return float(matches[0])

    def side(self, matches):
        helper = SideHelper()
        stochio = 1
        for item in matches:
            if type(item) in [int, float]:
                stochio = int(item)
            else:
                agents = item.children[0]
                compartment = item.children[2]
                for i in range(stochio):
                    start = helper.counter
                    for agent in agents.children:
                        helper.seq.append(deepcopy(agent.children[0]))
                        helper.comp.append(compartment)
                        helper.counter += 1
                    helper.complexes.append((start, helper.counter - 1))
                stochio = 1
        return helper

    def rule(self, matches):
        label = None  # TODO create implicit label
        rate1 = None
        rate2 = None
        if len(matches) == 6:
            label, lhs, arrow, rhs, rate1, rate2 = matches
        if len(matches) == 5:
            if type(matches[0]) == str:
                label, lhs, arrow, rhs, rate1 = matches
            else:
                lhs, arrow, rhs, rate1, rate2 = matches
        elif len(matches) == 4:
            if type(matches[0]) == str:
                label, lhs, arrow, rhs = matches
            else:
                lhs, arrow, rhs, rate1 = matches
        else:
            lhs, arrow, rhs = matches
        agents = tuple(lhs.seq + rhs.seq)
        mid = lhs.counter
        compartments = lhs.comp + rhs.comp
        complexes = lhs.complexes + list(
            map(
                lambda item: (item[0] + lhs.counter, item[1] + lhs.counter),
                rhs.complexes,
            )
        )
        pairs = [(i, i + lhs.counter) for i in range(min(lhs.counter, rhs.counter))]
        if lhs.counter > rhs.counter:
            pairs += [(i, None) for i in range(rhs.counter, lhs.counter)]
        elif lhs.counter < rhs.counter:
            for i in range(lhs.counter, rhs.counter):
                replication = False
                if lhs.counter == 1 and rhs.counter > 1:
                    if lhs.seq[pairs[-1][0]] == rhs.seq[pairs[-1][1] - lhs.counter]:
                        if rhs.seq[pairs[-1][1] - lhs.counter] == rhs.seq[i]:
                            pairs += [(pairs[-1][0], i + lhs.counter)]
                            replication = True
                if not replication:
                    pairs += [(None, i + lhs.counter)]

        reversible = False
        if arrow == "<=>":
            reversible = True
        rate1 = Rate(rate1) if rate1 else None
        rate2 = Rate(rate2) if rate2 else rate1
        return reversible, Rule(
            agents,
            mid,
            compartments,
            complexes,
            pairs,
            rate1,
            label,
        ), rate2

    def rules(self, matches):
        rules = []
        for reversible, rule, new_rate in matches[1:]:
            if reversible:
                reversible_rule = rule.create_reversible(new_rate)
                rules.append(rule)
                rules.append(reversible_rule)
            else:
                rules.append(rule)
        return {"rules": rules}

    def definitions(self, matches):
        result = dict()
        for definition in matches[1:]:
            pair = definition.children
            result[pair[0]] = pair[1]
        return {"definitions": result}

    def init(self, matches):
        return matches

    def inits(self, matches):
        result = collections.Counter()
        for init in matches[1:]:
            if len(init) > 1:
                result[init[1].children[0]] = int(init[0])
            else:
                result[init[0].children[0]] = 1
        return {"inits": result}

    def param(self, matches):
        self.params.add(str(matches[0]))
        return Tree("param", matches)

    def model(self, matches):
        rules = set()
        definitions = dict()
        regulation = None
        inits = collections.Counter()
        for match in matches:
            if type(match) == dict:
                key, value = list(match.items())[0]
            elif isinstance(match, Tree) and match.data == "sections":
                if isinstance(match.children[0], Tree):
                    continue
                key, value = list(match.children[0].items())[0]
            else:
                continue

            if key == "rules":
                rules.update(value)
            elif key == "inits":
                inits.update(value)
            elif key == "definitions":
                definitions.update(value)
            elif key == "regulation":
                if regulation:
                    raise UnspecifiedParsingError("Multiple regulations")
                regulation = value

        params = self.params - set(definitions)
        return Model(rules, inits, definitions, params, regulation)


class Parser:
    def __init__(self, start):
        grammar = (
            "start: "
            + start
            + GRAMMAR
            + COMPLEX_GRAMMAR
            + EXTENDED_GRAMMAR
            + REGULATIONS_GRAMMAR
        )
        self.parser = Lark(
            grammar, parser="lalr", propagate_positions=False, maybe_placeholders=False
        )

        self.terminals = dict((v, k) for k, v in _TERMINAL_NAMES.items())
        self.terminals.update(
            {
                "COM": "//",
                "ARROW": "=>",
                "BI_ARROW": "<=>",
                "POW": "**",
                "DOUBLE_COLON": "::",
                "RULES_START": "#! rules",
                "INITS_START": "#! inits",
                "DEFNS_START": "#! definitions",
                "COMPLEXES_START": "#! complexes",
                "REGULATION_START": "#! regulation",
                "CNAME": "name",
                "NAME": "agent_name",
                "VAR": "?",
            }
        )
        self.terminals.pop("$END", None)

    def replace(self, expected: set) -> set:
        """
        Method used to replace expected tokens by their human-readable representations defined in self.terminals

        :param expected: given set of expected tokens
        :return: transformed tokens
        """
        return set([self.terminals.get(item, item.lower()) for item in expected])

    def parse(self, expression: str) -> Result:
        """
        Main method for parsing, first syntax_check is called which checks syntax and if it is
        correct, a parsed Tree is returned.

        Then the tree is transformed using several Transformers in self.transform method.

        :param expression: given string expression
        :return: Result containing parsed object or error specification
        """
        result = self.syntax_check(expression)
        if result.success:
            return self.transform(result.data)
        else:
            return result

    def transform(self, tree: Tree) -> Result:
        """
        Apply several transformers to construct BCSL object from given tree.

        :param tree: given parsed Tree
        :return: Result containing constructed BCSL object
        """
        try:
            complexer = ExtractComplexNames()
            tree = complexer.transform(tree)
            complexer.complex_defns = remove_nested_complex_aliases(
                complexer.complex_defns
            )
            de_abstracter = TransformAbstractSyntax(complexer.complex_defns)
            tree = de_abstracter.transform(tree)
            tree = TreeToComplex().transform(tree)
            tree = TransformRegulations().transform(tree)
            tree = TreeToObjects().transform(tree)
            return Result(True, tree.children[0])
        except Exception as u:
            return Result(False, {"error": str(u)})

    def syntax_check(self, expression: str) -> Result:
        """
        Main method for parsing, calls Lark.parse method and creates Result containing parsed
        object (according to designed 'start' in grammar) or dict with specified error in case
        the given expression cannot be parsed.

        :param expression: given string expression
        :return: Result containing parsed object or error specification
        """
        try:
            tree = self.parser.parse(expression)
        except UnexpectedCharacters as u:
            return Result(
                False,
                {
                    "unexpected": expression[u.pos_in_stream],
                    "expected": self.replace(u.allowed),
                    "line": u.line,
                    "column": u.column,
                },
            )
        except UnexpectedToken as u:
            return Result(
                False,
                {
                    "unexpected": str(u.token),
                    "expected": self.replace(u.expected),
                    "line": u.line,
                    "column": u.column,
                },
            )
        return Result(True, tree)
