import libsbml
import Core.Rule
import Core.Structure

class ModelSBML:

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
    def set_compartments_to_species_types(self, compartments: dict):
        """Function adds compartments to existing speciesTypes, representing complexes in BCSL"""
        for compartment in compartments:
            c = self.model.createCompartment()
            c.setId(compartment)
            c.setConstant(True)
            compPlug = c.getPlugin("multi")
            compPlug.setIsType(True)
            for complex_name in compartments[compartment]:
                species = self.modelPlug.getMultiSpeciesType(complex_name)
                species.setCompartment(compartment)

    def create_all_species_types(self,  compartments: dict, atomics: dict, structs: dict):
        '''Function creates all species types from signatures and compartments'''
        self.create_species_types_from_atomic(atomics)
        self.create_species_types_from_structure(structs)
        self.set_compartments_to_species_types(compartments)
