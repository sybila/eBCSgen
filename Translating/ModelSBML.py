import libsbml
import Core.Rule
import Core.Atomic
import Core.Structure
import Core.Complex
class ModelSBML:

    '''
        Class for BCSL->SBML-multi model export
    '''

    def __init__(self):
        #OBJECTS OF libsbml - for better handling
        self.document = libsbml.SBMLDocument(libsbml.SBMLNamespaces(3,1,"multi", 1))
        self.docPlug = self.document.getPlugin("multi")
        self.model = self.document.createModel()
        self.modelPlug = self.model.getPlugin("multi")

##THIS ARE SOME INNER DATA -COULD BE STORET BETTER
        self.finishedCompartments = []
        self.finishedComplexTypes = []
        self.complex_names_map = {}


    def create_species_feature_type(self, new_species_type, atomic: str, atomics: dict):
        """Function creates species feature inside Atomic agent"""
        new_feature_type =new_species_type.createSpeciesFeatureType()
        new_feature_type.setId(atomic + "_feature_type")
        new_feature_type.setOccur(1)
        for feature_value in atomics[atomic]:
            new_feature_type.createPossibleSpeciesFeatureValue()\
                .setId(atomic+"_"+feature_value)

    def create_species_types_from_atomic(self, atomics: dict):
        """Function creates speciesTypes from Atomic agents"""
        for atomic in atomics:
            new_species_type = self.modelPlug.createMultiSpeciesType()
            new_species_type.setId("st_"+atomic)
            if atomics[atomic] != set():
                self.create_species_feature_type(new_species_type, atomic, atomics)


    def create_species_types_from_structure(self, structs: dict):
        """Function creates speciesTypes from Structure agents"""
        for struct in structs:
            new_species_type = self.modelPlug.createMultiSpeciesType()
            new_species_type.setId("st_"+struct)
            for num, subcomponent in enumerate(sorted(structs[struct]), start=0):
                new_instance = new_species_type.createSpeciesTypeInstance()
                new_instance.setId(subcomponent)
                new_instance.setSpeciesType("st_"+subcomponent)

    def create_species_type_from_complex(self, comp_agent : Core.Complex):
        """All composed complex agents are translated to SpeciesTypes Here"""
        new_species_type = self.modelPlug.createMultiSpeciesType()
        name = comp_agent.to_SBML_speciesTypes_code()
        new_species_type.setId(name)

        for num, subcomponent in enumerate(comp_agent.get_agent_names(), start=0):
            new_instance = new_species_type.createSpeciesTypeInstance()
            new_instance.setId(subcomponent+"_"+str(num))
            new_instance.setSpeciesType("st_"+subcomponent)
            agent = sorted(comp_agent.agents)[num]
            if isinstance(agent, Core.Structure.StructureAgent):
                for atomic in agent.composition:
                    comp_index = new_species_type.createSpeciesTypeComponentIndex()
                    comp_index.setId(subcomponent +"_" + str(num) + "_" + atomic.name )
                    comp_index.setComponent(atomic.name)
                    comp_index.setIdentifyingParent(subcomponent+"_"+str(num))

    def create_basic_species_types(self,atomics: dict, structs: dict):
        '''Function creates SBML speciesTypes from signatures. speciesTypes do not have compartments by default.
        compartment is added in specific species later and they are cereated using map compartments -> outside agents
        '''

        self.create_species_types_from_atomic(atomics)
        self.create_species_types_from_structure(structs)

    ##############################################

    #FUNCTION TO CREATE COMPARTMENT

    def create_compartment(self, compartment: str):

        """Function creates SBML-compartment using string name of compartment

        :param: compartment -> string name of compartment
        """
        c = self.model.createCompartment()
        c.setId(compartment)
        c.setConstant(True)
        compPlug = c.getPlugin("multi")
        compPlug.setIsType(True)
        self.finishedCompartments.append(compartment)


    #FUNCTIONS TO CREATE SPECIES


    def set_species_feature(self, agent, plugin, component_ref, is_component):
        """Creates and sets up species feature"""
        sf = libsbml.SpeciesFeature(3, 1, 1)
        sf.setSpeciesFeatureType(agent.name + "_feature_type")
        if is_component:
            sf.setComponent(component_ref)
        sf.setOccur(1)
        sfv = sf.createSpeciesFeatureValue()
        sfv.setValue(agent.name + "_" + agent.state)
        plugin.addSpeciesFeature(sf)

    def create_species_features(self, comp_agent: Core.Complex, new_species_multi_plugin):
        """Creates all species features for given speces"""
        for num, agent in enumerate(sorted(comp_agent.agents)):
            if isinstance(agent,Core.Atomic.AtomicAgent):
                component_ref = ""
                self.set_species_feature(agent, new_species_multi_plugin, component_ref, is_component=False)
            elif isinstance(agent,Core.Structure.StructureAgent):
                for atomic_agent in sorted(agent.composition):
                    component_ref = agent.name+"_"+str(num)+"_"+atomic_agent.name
                    self.set_species_feature(atomic_agent, new_species_multi_plugin, component_ref, is_component=True)

    def create_species(self, comp_agent):
        '''Creates all species in the model'''
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



    def create_all_species_compartments_and_complex_species_types(self, unique_complexes: set()):
        '''Creates species for every unique Complex agent, creates SpeciesType
                 for composed Complex agent if there is new one '''
        for comp_agent in unique_complexes:
            self.complex_names_map[str(comp_agent)] = comp_agent.to_SBML_species_code()

            if comp_agent.compartment not in self.finishedCompartments:
                self.create_compartment(comp_agent.compartment)
            name = comp_agent.to_SBML_speciesTypes_code()
            if comp_agent.is_composed() and name not in self.finishedComplexTypes:
                self.create_species_type_from_complex(comp_agent)
                self.finishedComplexTypes.append(name)

            self.create_species(comp_agent)

#THIS CAN BE DONE NICER
    def parse_expression_to_ML(self, expression):
        """Parses string expresion to string that can be used by
        internal function of libsbml to create KineticLaw


        *** This can be avoided by setting up libsbml object directly
        in transformer ***

        :return: <str> expresion that can be parsed by libsbml to MathML,
                <list> list of str representation of Complexes that were used in Rate
                  this is used in determining modifiers"""
        result = ''
        operators = ['-', '+', '*', '/']
        parentheses = ['[', ']', '(',')']
        removable = ['[',']']
        actors = []
        for e in expression:
            if e in operators:
                result += ' {} '.format(e)
            elif e not in parentheses and ':' in e:

                result += self.complex_names_map[e]
                actors.append(self.complex_names_map[e])
            elif e not in removable:
                result += e
        return result, actors


    def create_reactants(self, items:list(), reaction):
        """Creates all reactants from Complexes in list of tuples"""
        for itm in items:
            reactant = reaction.createReactant()
            reactant.setSpecies(itm[0].to_SBML_species_code())
            reactant.setConstant(False)
            reactant.setStoichiometry(itm[1])

    def create_products(self, items:list(), reaction):
        """Creates all products from Complexes in list of tuples"""
        for itm in items:
            product = reaction.createProduct()
            product.setSpecies(itm[0].to_SBML_species_code())
            product.setConstant(False)
            product.setStoichiometry(itm[1])

    def create_kinetic_law_and_modifiers(self, rules, reaction_objects):
        '''  creates kinetic law for all reactions
             and at the same time it creates modifiers
             for those Complexes that were not used either
             as reactant or product.

         '''
        for i, r in enumerate(rules):
            reac = r.to_reaction()
            rate = reac.rate
            res, actors = self.parse_expression_to_ML(rate.get_formula_in_list())
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

    def create_all_reactions(self, rules: set):
        '''This function creates all reactions from rules
            At first, it translates to RHS/LHS

            Then it creates kinetic law for all reactions
            and at the same time it creates modifiers
            for those Complexes that were not used either
            as reactant or product.

        '''
        reaction_objects = []
        for i, r in enumerate(rules):
            reaction = self.model.createReaction()
            reaction.setId("rc_"+str(i))
            reaction.setName(str(r))
            reaction.setReversible(False)
            reaction.setFast(False)
            reac = r.to_reaction()
            reaction_objects.append(reaction)

            self.create_reactants(list(reac.lhs.to_counter().items()), reaction)
            self.create_products(list(reac.rhs.to_counter().items()), reaction)
        self.create_kinetic_law_and_modifiers(rules, reaction_objects)

### THIS WILL BE IMPROVED
    def create_parameters(self, definitions: dict, unique_params: set):
        """Sets up parameters from definitions"""
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
        """Sets up initial Amount of Complex agents from inits
        """
        for i in init.items():
            asignment = self.model.createInitialAssignment()
            asignment.setSymbol(i[0].to_SBML_species_code())
            parsed_math, actors= self.parse_expression_to_ML(str(i[1]))
            asignment.setMath(libsbml.parseFormula(parsed_math))
