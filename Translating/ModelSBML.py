import libsbml
import Core.Rule
import Core.Atomic
import Core.Structure
import Core.Complex
import collections
class ModelSBML:

    '''
        Class for BCSL->SBML-multi model export
    '''

    def __init__(self):
        self.document = libsbml.SBMLDocument(libsbml.SBMLNamespaces(3,1,"multi", 1))
        self.docPlug = self.document.getPlugin("multi")
        self.model = self.document.createModel()
        self.modelPlug = self.model.getPlugin("multi")
        self.finishedCompartments = []
        self.finishedComplexSpeciesTypes = []
        self.speciesNamses = {}
        #it is good to save all components in structure
        # for internal testing
        #self.ids = {"species":{},
        #            "species_types":{},
        #            "species_features":{},
        #            "species_feature_types":{},
        #            "instances":{},
        #            "component_indexes":{},
        #            "reactions":{},
        #           "compartments":{}}


    #FUNCTIONS TO CREATE TEMPLATE OF SPECIES

    def create_species_feature_type(self, new_species_type: libsbml.MultiSpeciesType, atomic: str, atomics: dict):
        """Function creates species feature inside Atomic agent"""
        new_feature_type = new_species_type.createSpeciesFeatureType()
        new_feature_type.setId(atomic + "_feature_type")
        new_feature_type.setOccur(1)
        for feature_value in atomics[atomic]:
            value = new_feature_type.createPossibleSpeciesFeatureValue()
            value.setId(atomic+"_"+feature_value)

    def create_species_types_from_atomic(self, atomics: dict):
        """Function creates speciesTypes from Atomic agents"""
        for atomic in atomics:
            new_species_type = self.modelPlug.createMultiSpeciesType()
            new_species_type.setId(atomic)
            if atomics[atomic] !=  set():
                self.create_species_feature_type(new_species_type, atomic, atomics)


    def create_species_types_from_structure(self, structs: dict):
        """Function creates speciesTypes from Structure agents"""
        for struct in structs:
            new_species_type = self.modelPlug.createMultiSpeciesType()
            new_species_type.setId(struct)
            for num, subcomponent in enumerate(structs[struct], start=0):
                new_instance = new_species_type.createSpeciesTypeInstance()
                new_instance.setId(subcomponent+"_instance_of_"+struct+"_"+str(num))
                new_instance.setSpeciesType(subcomponent) #estimates existance of it
                new_component_index = new_species_type.createSpeciesTypeComponentIndex()
                new_component_index.setId(subcomponent+"_component_index_of_"+struct+"_"+str(num))
                new_component_index.setComponent(subcomponent+"_instance_of_"+struct+"_"+str(num))

    def create_species_type_from_complex(self, name: str(), subcomponents: list()):
        new_species_type = self.modelPlug.createMultiSpeciesType()
        new_species_type.setId(name)
        for num, subcomponent in enumerate(subcomponents, start=0):
            new_instance = new_species_type.createSpeciesTypeInstance()
            new_instance.setId(subcomponent+"_instance_of_"+name+"_"+str(num))
            new_instance.setSpeciesType(subcomponent)
            new_component_index = new_species_type.createSpeciesTypeComponentIndex()
            new_component_index.setId(subcomponent + "_component_index_of_" + name+"_"+str(num))
            new_component_index.setComponent(subcomponent + "_instance_of_" + name+"_"+str(num))
        self.finishedComplexSpeciesTypes.append(name)

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

    ####################################################
    #FUNCTION TO TRANSLATE COMPLEX AGENT TO SPECIES NAME

    def translate_complex_name(self, compl:Core.Complex):
        '''Translates complex agent in reaction to its name ID in species
        function is there to find link between object and id of Species. Used in
        reaction
        TODO
        *Find some better way for Naming convention of id's objects in SBML
        *Requirements:
        1.Fast Forward
        2.Logical
        3.Readable
        '''

        result_id = []
        agents = compl.agents
        for agent_index in range (len(agents)):
            if isinstance(agents[agent_index], Core.Atomic.AtomicAgent):
                atomic_agent = agents[agent_index]#
                result_id.append(atomic_agent.name)
                result_id.append(atomic_agent.state)
            elif isinstance(agents[agent_index], Core.Structure.StructureAgent):
                result_id.append(agents[agent_index].name+"_"+str(agent_index+1))
                for atomic_agent in agents[agent_index].composition: #struct can only contain atomic or set is empty
                    result_id.append(atomic_agent.name)
                    result_id.append(atomic_agent.state)
        self.speciesNamses[".".join(list(map(str, agents))) + "::" + compl.compartment] ="sp_"+"_".join(result_id)
        return "sp_"+"_".join(result_id)

    ####################################################

    #FUNCTIONS TO CREATE SPECIES

    def create_atomic_species_subparts(self, atomic_agent, id_of_species, new_species_multi_plugin):
        '''Creates species feature of species. It translates as currently active domain in atomic agent BCSL'''
        id_of_species.append(atomic_agent.name)
        id_of_species.append(atomic_agent.state)

        sf = libsbml.SpeciesFeature(3, 1, 1)
        sf.setSpeciesFeatureType(atomic_agent.name + "_feature_type")
        sf.setOccur(1)

        sfv = sf.createSpeciesFeatureValue()
        sfv.setValue(atomic_agent.name+"_"+atomic_agent.state)
        new_species_multi_plugin.addSpeciesFeature(sf)
        return id_of_species

    def create_species(self, complex, name:str):
        '''Creates all species in the model and calls creation of atomic subparts if features are there
        are such agents in a complex'''
        new_species = self.model.createSpecies()
        new_species_multi_plugin = new_species.getPlugin("multi")
        new_species_multi_plugin.setSpeciesType(name)  # uses speciesType template
        new_species.setCompartment(complex[0])

        new_species.setBoundaryCondition(False)
        new_species.setHasOnlySubstanceUnits(False)
        new_species.setConstant(False)
        id_of_species = []

        for agent_index in range(1, len(complex)):
            if isinstance(complex[agent_index], Core.Atomic.AtomicAgent):
                atomic_agent = complex[agent_index]
                id_of_species = self.create_atomic_species_subparts(atomic_agent, id_of_species, new_species_multi_plugin)
            elif isinstance(complex[agent_index], Core.Structure.StructureAgent):
                id_of_species.append(complex[agent_index].name+"_"+str(agent_index))
                for atomic_agent in complex[agent_index].composition: #struct can only contain atomic or set is empty
                    id_of_species = self.create_atomic_species_subparts(atomic_agent, id_of_species, new_species_multi_plugin)

        new_species.setId("sp_"+"_".join(id_of_species)) #sp added to prevent conflict



    def create_all_species_compartments_and_complex_species_types(self, complexes: set()):
        '''Creates species for every unique complex agent, creates SpeciesType for common agent and compartment if there is a new one '''
        for complex in complexes:

            # Creates compartment if there is not the same compartment yet
            if complex[0] not in self.finishedCompartments:
                self.create_compartment(complex[0])

            name_of_species_type_id = [] #Counting subcomponents of complex agent
            for i in range(1, len(complex)):
                name_of_species_type_id.append(complex[i].name)
            name_of_species_type_id.sort() # Names of individual complex components are sorted to avoid inconsistency
                                         # E.g in BCSL order of agents in complex has no role, but in SBML-multi id has to be strictly given
                                         # thus this order of SpeciesType_id will be determined alphabetically
            name = "_".join(name_of_species_type_id)
            # Creates SpeciesType for complex, if length of tuple is more than 2,
            # that means complex is compound from at least 2 existing SpeciesType
            #Complex speciesType is created only if name id was not find in finishedComplexSpeciesTypes
            if len(complex) > 2 and name not in self.finishedComplexSpeciesTypes:
                self.create_species_type_from_complex(name, name_of_species_type_id)

            self.create_species(complex, name)

    def parse_expression_to_ML(self, expression):
        result = ''
        operators = ['-', '+', '*', '/']
        parentheses = ['[', ']', '(',')']
        removable = ['[',']']
        actors = []
        for e in expression:
            if e in operators:
                result += ' {} '.format(e)
            elif e not in parentheses and ':' in e:
                result += self.speciesNamses[e]
                actors.append(self.speciesNamses[e])
            elif e not in removable:
                result += e
        return result, actors

    def create_all_reactions(self, rules: set):
        '''This function creates all reactions from rules
            At first, it translates to RHS/LHS
            TODO
            *Can be simplified
            *Concentrations/Quantities will be introduced together with Variables
            *Decide whether to include MathML in KineticLaw-> will be obsolete in 3 v 2
        '''
        saved = [] #tu sa ukladaju reakcie aby sa na ne dalo odkazovat
        #prebehnu az 2 behy najskor sa vytvoria reakcie aj s prekaldmi
        #apotom sa da vyhladavat aj v prekladoch - upravit krajsie behy
        #ukladat si veci do struktur
        for i, r in enumerate(rules):
            reaction = self.model.createReaction()
            reaction.setId("rc_"+str(i))
            reaction.setName(str(r))
            reaction.setReversible(False)
            reaction.setFast(False)
            reac = r.to_reaction()
            saved.append(reaction)

            for itm in list(reac.lhs.to_counter().items()):
                reactant = reaction.createReactant()
                reactant.setSpecies(self.translate_complex_name(itm[0]))
                reactant.setConstant(False)
                reactant.setStoichiometry(itm[1])

            for itm in list(reac.rhs.to_counter().items()):
                product = reaction.createProduct()
                product.setSpecies(self.translate_complex_name(itm[0]))
                product.setConstant(False)
                product.setStoichiometry(itm[1])

        #create mathML
        for i, r in enumerate(rules):
            reac = r.to_reaction()
            rate = reac.rate
            res, actors = self.parse_expression_to_ML(rate.get_formula_in_list())
            law = saved[i].createKineticLaw()
            num_of_products = saved[i].getListOfProducts().getListOfAllElements().getSize()
            num_of_reactants = saved[i].getListOfReactants().getListOfAllElements().getSize()

            law.setMath(libsbml.parseFormula(res))
            for n in range(num_of_products):
                product = saved[i].getListOfProducts().getListOfAllElements().get(n).getSpecies()
                if product in actors:
                    actors.pop(actors.index(product))
            for u in range(num_of_reactants):
                reactant = saved[i].getListOfReactants().getListOfAllElements().get(u).getSpecies()
                if reactant in actors:
                    actors.pop(actors.index(reactant))
            for remaining_actor in actors:
                modifier = saved[i].createModifier()
                modifier.setSpecies(remaining_actor)

    ########################
    ## CREATE THE WHOLE THING

    def create_parameters(self, definitions: set):
        for definition in definitions:
            param = self.model.createParameter()
            param.setId(definition)
            param.setValue(definitions[definition])
            param.setConstant(True)

    def set_initial_amounts(self, init):
        for i in init.items():
            asignment = self.model.createInitialAssignment()
            asignment.setSymbol(self.translate_complex_name(i[0]))
            parsed_math, actors= self.parse_expression_to_ML(str(i[1]))
            asignment.setMath(libsbml.parseFormula(parsed_math))

    def create_full_document(self, complexes : set, atomics: dict, structs: dict, rules: set, definitions: set, init: collections.Counter):
        """Function creates everything in SBML document"""
        self.create_basic_species_types(atomics, structs)#1
        self.create_all_species_compartments_and_complex_species_types(complexes) #2
        self.create_all_reactions(rules)#3
        self.create_parameters(definitions)#4
        self.set_initial_amounts(init)#5

        #TODO - Variables
        #TODO -Reasonable naming convention for species + Prettier code
        #TODO -Testing, testing, testing...
