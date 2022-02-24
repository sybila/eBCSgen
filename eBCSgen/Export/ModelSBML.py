import libsbml
from eBCSgen import Core
import eBCSgen.Core.Atomic
import eBCSgen.Core.Structure
import eBCSgen.Core.Complex


class ModelSBML:

    def __init__(self, level, version):
        # OBJECTS OF libsbml - for better handling
        self.document = libsbml.SBMLDocument(libsbml.SBMLNamespaces(level, version, "multi", 1))
        self.docPlug = self.document.getPlugin("multi")
        self.model = self.document.createModel()
        self.modelPlug = self.model.getPlugin("multi")

        # CREATED SPECIES TYPES REPRESENTING COMPLEXES and COMPARTMENTS
        self.finishedCompartments = []
        self.finishedComplexTypes = []

    def create_species_feature_type(self, new_species_type, atomic: str, atomics: dict):
        """
        Function creates species feature inside Atomic agent

        :param new_species_type: libsbml object of new speciesType
        :param atomic: name of given atomic agent
        :param atomics: atomic signature of the model
        """
        new_feature_type = new_species_type.createSpeciesFeatureType()
        new_feature_type.setId("{}_feature_type".format(atomic))
        new_feature_type.setOccur(1)
        for feature_value in atomics:
            new_feature_type.createPossibleSpeciesFeatureValue() \
                .setId("{}_{}".format(atomic, feature_value))

    def create_species_types_from_atomic(self, atomics: dict):
        """
        Function creates speciesTypes from Atomic agents

        :param atomics: atomic signature of the model in <dict>
        """
        for atomic in atomics:
            new_species_type = self.modelPlug.createMultiSpeciesType()
            new_species_type.setId("st_{}".format(atomic))
            if atomics[atomic] != set():
                self.create_species_feature_type(new_species_type, atomic, atomics[atomic])

    def create_species_types_from_structure(self, structs: dict):
        """
        Function creates speciesTypes from Structure agents

        :param structs: structure signature of the model in <dict>
        """
        for struct in structs:
            new_species_type = self.modelPlug.createMultiSpeciesType()
            new_species_type.setId("st_{}".format(struct))
            for num, subcomponent in enumerate(sorted(structs[struct]), start=0):
                new_instance = new_species_type.createSpeciesTypeInstance()
                new_instance.setId(subcomponent)
                new_instance.setSpeciesType("st_{}".format(subcomponent))

    def create_species_type_from_complex(self, comp_agent: eBCSgen.Core.Complex.Complex, structure_signature: dict):
        """
        All complex agents are translated to SpeciesTypes Here

        :param comp_agent: BCSL agent to be translated to SBML-multi species type
        """
        new_species_type = self.modelPlug.createMultiSpeciesType()
        name = comp_agent.to_SBML_speciesTypes_code()
        new_species_type.setId(name)

        for num, subcomponent in enumerate(sorted(comp_agent.get_agent_names()), start=0):
            new_instance = new_species_type.createSpeciesTypeInstance()
            new_instance.setId("{}_{}".format(subcomponent, str(num)))
            new_instance.setSpeciesType("st_{}".format(subcomponent))
            agent = sorted(comp_agent.agents)[num]
            if isinstance(agent, eBCSgen.Core.Structure.StructureAgent):
                for atomic_name in structure_signature[subcomponent]: # HERE THE LOOP SHOULD BE OVER SIGNATURE NOT JUST GIVEN AGENT
                    comp_index = new_species_type.createSpeciesTypeComponentIndex()
                    comp_index.setId("{}_{}_{}".format(subcomponent, str(num), atomic_name))
                    comp_index.setComponent(atomic_name)
                    comp_index.setIdentifyingParent("{}_{}".format(subcomponent, str(num)))

    def create_basic_species_types(self, atomics: dict, structs: dict):
        """
        Function creates SBML speciesTypes from signatures. speciesTypes do not have compartments by default.
        compartment is added in specific species later and they are cereated using map compartments -> outside agents

        :param atomics: signature of atomic agents
        :param structs: signature of structure agents
        """

        self.create_species_types_from_atomic(atomics)
        self.create_species_types_from_structure(structs)

    def create_compartment(self, compartment: str):
        """
        Function creates SBML-compartment using string name of compartment

        :param compartment: string name of compartment
        """
        c = self.model.createCompartment()
        c.setId(compartment)
        c.setConstant(True)
        compPlug = c.getPlugin("multi")
        compPlug.setIsType(True)
        self.finishedCompartments.append(compartment)

    def set_species_feature(self, agent, plugin, component_ref, is_component: bool):
        """
        Creates and sets up species feature

        If there are 2 or more agents in complex with the same name, reference can
        distinguish between them by mentioning their parent structure agent too

        :param agent: agent of given feature
        :param plugin: multi plugin to manipulate with species features
        :param component_ref: reference to agent where this feature belongs.
        :param is_component: says about if setting the component atr. is necessary
        """
        sf = libsbml.SpeciesFeature(3, 1, 1)
        sf.setSpeciesFeatureType("{}_feature_type".format(agent.name))
        if is_component:
            sf.setComponent(component_ref)
        sf.setOccur(1)
        sfv = sf.createSpeciesFeatureValue()
        sfv.setValue("{}_{}".format(agent.name, agent.state))
        plugin.addSpeciesFeature(sf)

    def create_species_features(self, comp_agent: eBCSgen.Core.Complex.Complex, new_species_multi_plugin):
        """
        Creates all species features for given species

        :param comp_agent: BCSL complex agent to create SBML species features for
        :param new_species_multi_plugin: libsbml plugin for manipulating SBML-multi species
        """
        for num, agent in enumerate(sorted(comp_agent.agents)):
            if isinstance(agent, eBCSgen.Core.Atomic.AtomicAgent):
                component_ref = ""
                self.set_species_feature(agent, new_species_multi_plugin, component_ref, is_component=False)
            elif isinstance(agent, eBCSgen.Core.Structure.StructureAgent):
                for atomic_agent in sorted(agent.composition):
                    component_ref = "{}_{}_{}".format(agent.name, str(num), atomic_agent.name)
                    self.set_species_feature(atomic_agent, new_species_multi_plugin, component_ref, is_component=True)

    def create_species(self, comp_agent: eBCSgen.Core.Complex.Complex):
        """
        Creates all species in the model

        :param comp_agent: BCSL Complex agent to be translated to SBML Species
        """
        new_species = self.model.createSpecies()
        new_species_multi_plugin = new_species.getPlugin("multi")
        new_species_multi_plugin.setSpeciesType(comp_agent.to_SBML_speciesTypes_code())  # uses speciesType template
        new_species.setCompartment(comp_agent.compartment)

        new_species.setBoundaryCondition(False)
        new_species.setHasOnlySubstanceUnits(False)
        new_species.setConstant(False)
        new_species.setInitialAmount(0)
        self.create_species_features(comp_agent, new_species_multi_plugin)

        new_species.setId(comp_agent.to_SBML_species_code())
        new_species.setName(str(comp_agent))

    def create_all_species_compartments_and_complex_species_types(self, unique_complexes: dict, structure_signature:dict):
        """
        Creates all compartments

        Creates species for every unique Complex agent in values
        Creates SpeciesType for Complex agent if there is new one - no isomorphisms here

        :param unique_complexes: dict() of representative Complexes[Keys]
                                 & tuple() of pairs (Core.Complex,str. SBML_species_code())
                                 Encapsulates all used Complexes and theirs isomorphisms in the model
        """
        for comp_agent in unique_complexes:
            # Not composed agents are created 2 times
            # firstly as structs from signature and secondly as complex here
            # create species type from complex agent if it does not exist.
            if comp_agent.to_SBML_speciesTypes_code() not in self.finishedComplexTypes:
                self.create_species_type_from_complex(comp_agent, structure_signature)
                self.finishedComplexTypes.append(comp_agent.to_SBML_speciesTypes_code())

            for agent in unique_complexes[comp_agent]:
                if agent[0].compartment not in self.finishedCompartments:
                    self.create_compartment(agent[0].compartment)
                self.create_species(agent[0])

    def create_reactants(self, items: list, reaction):
        """
        Creates all reactants from Complexes in list of tuples

        :param items: list of LHS complexes in reaction
        :param reaction: given reaction
        """
        for itm in items:
            reactant = reaction.createReactant()
            reactant.setSpecies(itm[0].to_SBML_species_code())
            reactant.setConstant(False)
            reactant.setStoichiometry(itm[1])

    def create_products(self, items: list, reaction):
        """
        Creates all products from Complexes in list of tuples

        :param items: list of RHS complexes in reaction
        :param reaction: given reaction
        """
        for itm in items:
            product = reaction.createProduct()
            product.setSpecies(itm[0].to_SBML_species_code())
            product.setConstant(False)
            product.setStoichiometry(itm[1])

    def create_kinetic_law_and_modifiers(self, ordered_rules, reaction_objects):
        """
        Creates kinetic law for all reactions and at the same time it creates modifiers
        for those Complexes that were not used either as reactant or product.

        :param ordered_rules: BCSL rules
        :param reaction_objects: list of all libSBML reaction objects
         """
        for i, r in enumerate(ordered_rules):
            reac = r.to_reaction()
            rate = reac.rate
            res = rate.to_mathML()
            agents, params = rate.get_params_and_agents()
            actors = []
            for agent in agents:
                actors.append(agent.to_SBML_species_code())
            law = reaction_objects[i].createKineticLaw()
            num_of_products = reaction_objects[i].getListOfProducts().getListOfAllElements().getSize()
            num_of_reactants = reaction_objects[i].getListOfReactants().getListOfAllElements().getSize()

            law.setMath(libsbml.parseFormula(res))
            for n in range(num_of_products):
                product = reaction_objects[i].getListOfProducts().getListOfAllElements().get(n).getSpecies()
                if product in actors:
                    actors.pop(actors.index(product))
            for u in range(num_of_reactants):
                reactant = reaction_objects[i].getListOfReactants().getListOfAllElements().get(u).getSpecies()
                if reactant in actors:
                    actors.pop(actors.index(reactant))
            for remaining_actor in actors:
                modifier = reaction_objects[i].createModifier()
                modifier.setSpecies(remaining_actor)

    def create_reaction_for_isomorphisms(self, unique_complexes):
        """
        Function creates all reactions between isomorphism in order to
        ensure that given Complexes are interchangeable but specific rule
        applies only to that exact isomorphism

        :param unique_complexes: given possible unique complexes
        """
        for compl in unique_complexes:
            num_of_complexes = len(unique_complexes[compl])
            if num_of_complexes > 1:
                for i in range(num_of_complexes):
                    for j in range(num_of_complexes):
                        if i > j:
                            reaction = self.model.createReaction()
                            reaction.setId("rc_{}_to_{}".format(str(unique_complexes[compl][i][1]),
                                                                str(unique_complexes[compl][j][1])))
                            reaction.setName("{}_to_{}".format(str(unique_complexes[compl][i][0]),
                                                               str(unique_complexes[compl][j][0])))

                            # using reversible(True) to reduce number of reactions needed
                            reaction.setReversible(True)
                            reaction.setFast(False)

                            product = reaction.createProduct()
                            product.setSpecies(str(unique_complexes[compl][i][1]))
                            product.setConstant(False)
                            product.setStoichiometry(1)

                            reactant = reaction.createReactant()
                            reactant.setSpecies(str(unique_complexes[compl][j][1]))
                            reactant.setConstant(False)
                            reactant.setStoichiometry(1)

    def create_all_reactions(self, rules: set):
        """
        This function creates all reactions from rules
        At first, it translates to RHS/LHS

        Then it creates kinetic law for all reactions
        and at the same time it creates modifiers
        for those Complexes that were not used either
        as reactant or product.

        :param rules: set of BCSL rules used in a model
        """
        reaction_objects = []
        ordered_rules = tuple(rules)
        for i, r in enumerate(ordered_rules):
            reaction = self.model.createReaction()
            reaction.setId("rc_{}".format(str(i)))
            reaction.setName(str(r))
            reaction.setReversible(False)
            reaction.setFast(False)
            reac = r.to_reaction()
            reaction_objects.append(reaction)

            self.create_reactants(list(reac.lhs.to_counter().items()), reaction)
            self.create_products(list(reac.rhs.to_counter().items()), reaction)
        self.create_kinetic_law_and_modifiers(ordered_rules, reaction_objects)

    def create_parameters(self, definitions: dict, unique_params: set):
        """
        Sets up parameters from definitions and parameters in rates

        :param definitions: parameters in BCSL definition
        :param unique_params: parameters in BCSL rates
        """
        for definition in definitions:
            param = self.model.createParameter()
            param.setId(definition)
            param.setValue(definitions[definition])
            param.setConstant(True)
        for par in unique_params:
            if par not in definitions:
                new_param = self.model.createParameter()
                new_param.setId(str(par))
                new_param.setConstant(False)

    def set_initial_amounts(self, init):
        """
        Sets up initial Amount of Complex agents from inits

        :param init: Complex agents at the beginning of the running of the model
        """
        for i in init.items():
            asignment = self.model.createInitialAssignment()
            asignment.setSymbol(i[0].to_SBML_species_code())
            formula = str(i[1])
            asignment.setMath(libsbml.parseFormula(formula))
