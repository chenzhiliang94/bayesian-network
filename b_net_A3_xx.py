import sys
import json
from itertools import product
import numpy as np

class BayesianNetwork(object):
    def __init__(self, structure, values, queries):
        # you may add more attributes if you need
        self.variables = structure["variables"]
        self.dependencies = structure["dependencies"]
        self.conditional_probabilities = values["conditional_probabilities"]
        self.prior_probabilities = values["prior_probabilities"]
        self.queries = queries
        self.answer = []

    def construct(self):
        # TODO: Your code here to construct the Bayesian network

        self.form_formula()
        self.form_table()
        
    def form_formula(self):
        parentCount = dict()
        events = self.variables.keys()
        parentlessEvents = list()
        invertedDependencies = dict()
        result = list()

        for var in self.variables.keys():
            invertedDependencies[var] = list()

        for key, val in self.dependencies.items():
            for parent in val:
                invertedDependencies[parent].append(key)

        for event in events:
            parentCount[event] = len(self.dependencies[event]) if event in self.dependencies.keys() else 0
            if parentCount[event] == 0:
                parentlessEvents.append(event)

        while len(parentlessEvents) != 0:
            parentlessEvent = parentlessEvents.pop(0)
            result.append(parentlessEvent)
            for child in invertedDependencies[parentlessEvent]:
                parentCount[child] -= 1
                if parentCount[child] == 0:
                    parentlessEvents.append(child)

        self.formula = result

    def fetch_conditional_probability(self, variable_name, variable_value, conditional_values):
        '''

        :param variable_name: single string of variable
        :param variable_value: its value
        :param conditional_values: dictionary of conditional names and value
        :return: conditional probability
        '''
        conditional_probabilities_list = self.conditional_probabilities[variable_name]
        for values in conditional_probabilities_list:
            # each value is a dictionary
            # we need to check if all keys in this dictionary exists in conditional_values
            # apart from own_value and probability
            is_correct_conditionals = True
            for key in values:
                if key == "own_value":
                    if not values[key] == variable_value:
                        is_correct_conditionals = False
                        break
                    continue
                if key == "probability":
                    continue
                try:
                    if not (values[key] == conditional_values[key]):
                        is_correct_conditionals = False
                        break
                    else: continue
                except:
                    print("conditional variable in given dict is not found in conditionals in formula!")
            if not is_correct_conditionals: # the truth value is incorrect here; go onto next value
                continue
            else: # else get probability
                return values["probability"]
        print ("this shouldnt be happening")
        return

    def form_table(self):
        # formula is a list, i assume first element is non conditioned
        t_table = (np.array(list(product(('True', 'False'), repeat=len(self.formula)))))
        probability = []
        for row in t_table:
            probability_cum_product = 1
            for index,truth_value in enumerate(row):
                variable = self.formula[index] # variable A in P(A | B,C,D ... )
                variable_value = row[index]
                conditionals = self.formula[:index] # variables B,C,D ... in P(A | B,C,D ... )
                if not conditionals: # if conditionals are empty, just look at prior
                    probability_cum_product*=self.prior_probabilities[variable][variable_value]
                    continue
                if variable in self.prior_probabilities:
                    probability_cum_product *= self.prior_probabilities[variable][variable_value]
                    continue
                conditional_truth_values = dict(zip(conditionals, row[:index]))
                #print(conditional_truth_values)
                probability_cum_product *= self.fetch_conditional_probability(variable, variable_value, conditional_truth_values)
            probability.append(probability_cum_product)

        self.truth_table = np.column_stack((t_table, probability))

    # givens: e.g. [("Earthquake", False), ("Burglary", False)]
    def calcSum(self, definedValues):
        givenPos = [self.formula.index(x[0]) for x in definedValues]
        givenVals = [x[1] for x in definedValues]

        sum = 0
        for row in self.truth_table:
            valid = True
            for pos, val in zip(givenPos, givenVals):
                if row[pos] != val:
                    valid = False
                    break

            if valid:
                sum += float(row[len(self.formula)])

        return sum

    # queryPairs: e.g. [("MaryCalls", "True")]
    # givens:     e.g. [("Earthquake", False), ("Burglary", False)]
    def query(self, queryPairs, givens):
        givensCopy = givens.copy()
        givensCopy.extend(queryPairs)
        numerator = self.calcSum(givensCopy)
        denominator = self.calcSum(givens)
        return numerator / denominator


    def infer(self):
        # TODO: Your code here to answer the queries given using the Bayesian
        # network built in the construct() method.
        self.answer = []  # your code to find the answer
        print(self.query([("MaryCalls", "True")], [("Alarm", "False")]))
        print(self.query([("Alarm", "False")], [("Burglary", "False"), ("Earthquake", "True")]))
        # for the given example:
        # self.answer = [{"index": 1, "answer": 0.01}, {"index": 2, "answer": 0.71}]
        # the format of the answer returned SHOULD be as shown above.
        return self.answer

    # You may add more classes/functions if you think is useful. However, ensure
    # all the classes/functions are in this file ONLY and used within the
    # BayesianNetwork class.

def main():
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 4:
        print ("\nUsage: python b_net_A3_xx.py structure.json values.json queries.json \n")
        raise ValueError("Wrong number of arguments!")

    structure_filename = sys.argv[1]
    values_filename = sys.argv[2]
    queries_filename = sys.argv[3]

    try:
        with open(structure_filename, 'r') as f:
            structure = json.load(f)
        with open(values_filename, 'r') as f:
            values = json.load(f)
        with open(queries_filename, 'r') as f:
            queries = json.load(f)

    except IOError:
        raise IOError("Input file not found or not a json file")

    # testing if the code works
    b_network = BayesianNetwork(structure, values, queries)
    b_network.construct()
    answers = b_network.infer()



if __name__ == "__main__":
    main()
