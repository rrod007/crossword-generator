import sys
import copy
from crossword import *
import random


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        domains_copy = copy.deepcopy(self.domains)
        for var in self.crossword.variables:
            for word in domains_copy[var]:
                if len(word) != var.length:
                    self.domains[var].remove(word)

        # raise NotImplementedError

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        x_domain_copy = copy.deepcopy(self.domains[x])

        for x_val in x_domain_copy:
            constraint_satisfied = False

            for y_val in self.domains[y]:
                if self.crossword.overlaps[x, y] is None:
                    constraint_satisfied = True
                    break
                else:
                    (i, j) = self.crossword.overlaps[x, y]
                    if x_val[i] == y_val[j]:
                        constraint_satisfied = True
                        break
            if constraint_satisfied:
                continue
            else:
                self.domains[x].remove(x_val)
                revised = True

        return revised

        # raise NotImplementedError


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = []

        # Fill queue with all arcs in the problem
        if arcs is None:
            for var_i in self.crossword.variables:
                for var_j in self.crossword.variables:
                    # if the variables are neighbours
                    if var_i != var_j and self.crossword.overlaps[var_i, var_j] is not None:
                        queue.append((var_i, var_j))
        else:
            queue = arcs

        while len(queue) != 0:
            (x, y) = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for var in self.crossword.variables:
                    # if the variable var is a neighbour of x
                    if var != x and self.crossword.overlaps[var, x] is not None:
                        queue.append((var, x))

        return True

        # raise NotImplementedError

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) != len(self.crossword.variables):
            return False

        return True

        # raise NotImplementedError

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check if all words are different (if not, return false)
        for var_i in assignment:
            for var_j in assignment:
                if var_i != var_j and assignment[var_i] == assignment[var_j]:
                    return False

        # check if words all fit in their variable's lengths (if not, return false)
        for var in assignment:
            if var.length != len(assignment[var]):
                return False

        # check if words overlaps all have the same letters (if not, return false)
        for var_i in assignment:
            for var_j in assignment:
                if var_i != var_j:
                    if self.crossword.overlaps[var_i, var_j] is not None:
                        (i, j) = self.crossword.overlaps[var_i, var_j]
                        if assignment[var_i][i] != assignment[var_j][j]:
                            return False

        return True

        # raise NotImplementedError


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # In case this fails, test without heuristics


        conflicts = {}

        for val in self.domains[var]:
            conflicts[val] = 0

        for var_val in self.domains[var]:
            for var_unassigned in self.crossword.variables:
                if var != var_unassigned:
                    if self.crossword.overlaps[var, var_unassigned] is not None and var_unassigned not in assignment:
                        (x, y) = self.crossword.overlaps[var, var_unassigned]
                        for var_unassigned_val in self.domains[var_unassigned]:
                            if var_val[x] != var_unassigned_val[y]:
                                conflicts[var_val] += 1

        conflict_indexes = list(conflicts.values())
        conflict_indexes.sort()

        sorted_values = []

        for index in conflict_indexes:
            for val in conflicts:
                if val not in sorted_values and conflicts[val] == index:
                    sorted_values.append(val)

        return sorted_values

        # return self.domains[var]

        # raise NotImplementedError


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # In case this fails, test without heuristics

        # Gather all unassigned variables
        unassigned_vars = []
        for var in self.crossword.variables:
            if var not in assignment:
                unassigned_vars.append(var)

        # variable = random.choice(unassigned_vars)


        variable = unassigned_vars[0]
        for var in unassigned_vars:
            # replace if num of values is smaller
            if len(self.domains[var]) < len(self.domains[variable]):
                variable = var
            elif len(self.domains[var]) == len(self.domains[variable]):
                # replace if num of degrees is larger
                variable_neighbours_num = 0
                var_neighbours_num = 0
                for variable_neighbour in self.crossword.variables:
                    if variable != variable_neighbour:
                        if self.crossword.overlaps[variable, variable_neighbour] is not None:
                            variable_neighbours_num += 1

                for var_neighbour in self.crossword.variables:
                    if var != var_neighbour:
                        if self.crossword.overlaps[var, var_neighbour] is not None:
                            var_neighbours_num += 1

                if var_neighbours_num > variable_neighbours_num:
                    variable = var

        return variable

        # raise NotImplementedError


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for val in self.order_domain_values(var, assignment):
            new_assignment = copy.deepcopy(assignment)
            new_assignment[var] = val

            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result

        return None

        # raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
