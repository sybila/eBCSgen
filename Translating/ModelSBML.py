import libsbml

class ModelSBML:

    '''Naming convention for BCSL -> SMBL-export:
        TODO
    '''

    def __init__(self):
        self.document = libsbml.SBMLDocument(libsbml.SBMLNamespaces(3,1,"multi", 1))
        self.docPlug = self.document.getPlugin("multi")
        self.model = self.document.createModel()
        self.modelPlug = self.model.getPlugin("multi")
        self.compartments = []
        self.speciesTypes = []
        self.species = []
        self.reactions = []

    def create_species_feature(self, new_species_type: libsbml.MultiSpeciesType, atomic: str, atomics: dict):
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
                self.create_species_feature(new_species_type, atomic, atomics)
            self.speciesTypes.append(new_species_type)

    def create_species_types_from_structure(self, structs: dict):
        """Function creates speciesTypes from Structure agents"""
        for struct in structs:
            new_species_type = self.modelPlug.createMultiSpeciesType()
            new_species_type.setId(struct)
            for subcomponent in structs[struct]:
                new_instance = new_species_type.createSpeciesTypeInstance()
                new_instance.setId(subcomponent+"_instance_of_"+struct)
                new_instance.setSpeciesType(subcomponent) #estimates existance of it
                new_component_index = new_species_type.createSpeciesTypeComponentIndex()
                new_component_index.setId(subcomponent+"_component_index_of_"+struct)
                new_component_index.setComponent(subcomponent+"_instance_of_"+struct)
            self.speciesTypes.append(new_species_type)


    def create_all_species_types(self,atomics: dict, structs: dict):
        '''Function creates SBML speciesTypes from signatures. speciesTypes do not have compartments by default.
        compartment is added in specific species later and they are cereated using map compartments -> outside agents
        '''
        self.create_species_types_from_atomic(atomics)
        self.create_species_types_from_structure(structs)

    def create_compartment(self, compartment: str):

        """Function creates SBML-compartment using string name of compartment

        :param: compartment -> string name of compartment
        """
        c = self.model.createCompartment()
        c.setId(compartment)
        c.setConstant(True)
        compPlug = c.getPlugin("multi")
        compPlug.setIsType(True)


    def create_all_species_and_compartments(self, compartments: dict):

        """Function creates SBML-species and calls creation of every compartment"""
        libsbml.ListOfSpecies(libsbml.SBMLNamespaces(3,1,"multi",1)) # Creates Species tag for multi extension
        for compartment in compartments:
            self.create_compartment(compartment)
            for complex_name in compartments[compartment]:
                new_species = self.model.createSpecies()
                new_speciesPlug =  new_species.getPlugin("multi")
                new_speciesPlug.setSpeciesType(complex_name)
                new_species.setId(complex_name+"_"+compartment) # : is invalid character in id thus _ is used
                new_species.setCompartment(compartment)
                new_species.setInitialAmount(10) # setting initial amount/concentration otherwise warning occurs
                # necessary attributes
                new_species.setBoundaryCondition(False)
                new_species.setHasOnlySubstanceUnits(False)
                new_species.setConstant(False)
                # Species features...
                #TODO


    def create_full_document(self, compartments:dict, atomics: dict, structs: dict):
        """Function creates everything in SBML document"""

        self.create_all_species_types(atomics, structs)
        self.create_all_species_and_compartments(compartments)

        #TODO - Variables, Reactions
