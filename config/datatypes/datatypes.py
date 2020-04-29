# these class definitions have to be added to file
# ~/galaxy/lib/galaxy/datatypes/text.py

##############################################
# eBCSgen formats

class BCS(Text):
    """Class describing a .bcs file"""
    file_ext = 'bcs'

    def sniff(self, filename):
        """
        Determines whether the file is in .bcs format
        """
        content = open(filename, 'r').read()
        keywords = ["#! rules", "#! inits", "#! definitions"]
        return all(keyword in content for keyword in keywords)

class BCS_TS(Text):
    """Class describing a .bcs.ts file"""
    file_ext = "bcs.ts"

    def sniff(self, filename):
        """
        Determines whether the file is in .bcs.ts format
        """
        content = open(filename, 'r').read()
        keywords = ['"edges":', '"nodes":', '"ordering":', '"initial":']
        if all(keyword in content for keyword in keywords):
            try:
                json.load(open(filename, "r"))
                return True
            except Exception:
                return False
        return False

    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            lines = "States: {}\nTransitions: {}\nUnique agents: {}\nInitial state: {}"
            ts = json.load(open(dataset.file_name, "r"))
            dataset.peek = lines.format(len(ts["nodes"]), len(ts["edges"]), len(ts["ordering"]), ts["initial"])
            dataset.blurb = nice_size(dataset.get_size())
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

class Storm_regions(Text):
    """Class describing a Storm output file"""
    file_ext = "storm.regions"

    def sniff(self, filename):
        """
        Determines whether the file is in .storm.regions format
        """
        content = open(filename, 'r').read()
        keywords = ["Storm-pars", "Region results"]
        return all(keyword in content for keyword in keywords)

    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            dataset.peek = "Storm-pars region results."
            dataset.blurb = nice_size(dataset.get_size())
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

class Storm_sample(Text):
    """Class describing a Storm output file"""
    file_ext = "storm.sample"

    def sniff(self, filename):
        """
        Determines whether the file is in .storm.sample format
        """
        content = open(filename, 'r').read()
        keywords = ["Storm-pars", "Result (initial states)"]
        return all(keyword in content for keyword in keywords)

    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            dataset.peek = "Storm-pars sample results."
            dataset.blurb = nice_size(dataset.get_size())
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

class Storm_check(Text):
    """Class describing a Storm output file"""
    file_ext = "storm.check"

    def sniff(self, filename):
        """
        Determines whether the file is in .storm.check format
        """
        content = open(filename, 'r').read()
        keywords = ["Storm ", "Result (for initial states)"]
        return all(keyword in content for keyword in keywords)

    def set_peek(self, dataset, is_multi_byte=False):
        if not dataset.dataset.purged:
            result = open(dataset.file_name, "r")
            answer = ""
            for line in result.readlines():
                if "Result (for initial states):" in line:
                    answer = line.split()[-1]
            dataset.peek = "Model checking result: {}".format(answer)
            dataset.blurb = nice_size(dataset.get_size())
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

