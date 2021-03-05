import copy
import time
import math
import sys


class Node:
    def getSize(self):
        return self.size

    def toString(self):
        raise Exception('Unimplemented method: toString')

    def interpret(self):
        raise Exception('Unimplemented method: interpret')


class Str(Node):
    def __init__(self, value):
        self.value = value

    def toString(self):
        return self.value

    def interpret(self, env):
        return self.value


class Var(Node):
    def __init__(self, name):
        self.value = name

    def toString(self):
        return str(self.value)

    def interpret(self, env):
        return copy.deepcopy(env[self.value])
        # return self.value


class Concat(Node):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def toString(self):
        return 'concat(' + self.x.toString() + ", " + self.y.toString() + ")"

    def interpret(self, env):
        return self.x.interpret(env) + self.y.interpret(env)

    def grow(plist, new_plist, var, dict, max_cost, cost):
        l1 = []
        if (max_cost < cost[Concat]):
            return
        else:
            for i in dict.keys():
                l1.append(i)
            l2 = []
            l2 = combinationSum(l1, max_cost - cost[Concat])
            for i in l2:
                if (len(i) == 2):
                    prog1 = dict[i[0]]
                    prog2 = dict[i[1]]
                    for x in prog1:
                        if (x.toString() != '*'):
                            for y in prog2:
                                if (y.toString() != '*') :
                                    new_plist.append(Concat(x, y))


class Replace(Node):
    def __init__(self, input_str, old, new):
        self.str = input_str
        self.old = old
        self.new = new

    def toString(self):
        return self.str.toString() + '.replace(' + self.old.toString() + ", " + self.new.toString() + ")"

    def interpret(self, env):
        return self.str.interpret(env).replace(self.old.interpret(env), self.new.interpret(env), 1)

    def grow(plist, new_plist, var, dict, max_cost, cost):
        l1 = []
        if (max_cost < cost[Replace]):
            return
        else:
            for i in dict.keys():
                l1.append(i)

            l2 = []
            l2 = combinationSum(l1, max_cost - cost[Replace])
            for i in l2:
                if (len(i) == 3):
                    i.reverse()
                    prog1 = dict[i[0]]
                    prog2 = dict[i[1]]
                    prog3 = dict[i[2]]
                    for x in prog1:
                        if (not isinstance(x, Str)):
                            for y in prog2:
                                if (y.toString() != x.toString()  ):
                                    for z in prog3:
                                        if (y.toString() != z.toString() and not isinstance(z, Var) ):
                                            new_plist.append(Replace(x, y, z))

#this code to find the combination of the numbers upto the max_cost  has been taken from GeekforGeeks
#link: https://www.geeksforgeeks.org/combinational-sum/
def combinationSum(candidates, target):
    result = []
    unique = {}
    candidates = list(set(candidates))
    solve(candidates, target, result, unique)
    return result
def solve(candidates, target, result, unique, i=0, current=[]):
    if target == 0:
        temp = [i for i in current]
        temp1 = temp
        temp.sort()
        temp = tuple(temp)
        if temp not in unique:
            unique[temp] = 1
            result.append(temp1)
        return
    if target < 0:
        return
    for x in range(i, len(candidates)):
        current.append(candidates[x])
        solve(candidates, target - candidates[x], result, unique, i, current)
        current.pop(len(current) - 1)


def calculate_cost(prog, cost):
    t = prog.toString()
    x = t.count('replace') * cost[Replace] + t.count('concat') * cost[Concat] + t.count('<') * cost['<'] + t.count(
        '>') * cost['>'] + t.count('args') * cost['args'] + t.count('*') * cost['*']
    return int(x)


class BottomUpSearch():
    def __init__(self):
        self.f = 0
        self.output = set()
        self.generated_program = 0
        self.program_evaluated = 0
        self.prog_to_evaluate=0
        self.size = 0
        self.final_flag = 0
        self.cost = {}
        self.dict = {}
        self.max_cost = 0

    def grow(self, plist, operation, var, input_output):
        temp = []
        for i in input_output:
            temp.append(i['out'])
        outputs = tuple(temp)
        new_plist = []
        self.max_cost += 1
        for i in operation:
            i.grow(plist, new_plist, var, self.dict, self.max_cost, self.cost)
        self.generated_program += len(new_plist)
        if(len(new_plist)>0):
            print("Cost:",self.max_cost,"Generated Programs:", len(new_plist))

        for i in range(0, len(new_plist)):

            self.program_evaluated += 1
            #print(new_plist[i].toString(), file=self.sample)  #########################
            out = []
            for j in input_output:
                out.append(new_plist[i].interpret(j))
            new_output = tuple(out)
            if (outputs == new_output):
                #self.prog_to_evaluate+=lowerbound
                print("Program: ", new_plist[i].toString())
                print("Program evaluated: ", self.program_evaluated)
                #print("Program evaluated without lower bound: ", self.prog_to_evaluate)
                print("Program Generated: ", self.generated_program)
                self.final_flag = 1
                return
            if (new_output not in self.output):

                length = calculate_cost(new_plist[i], self.cost)
                if (length in self.dict.keys()):
                    self.dict[length].append(new_plist[i])
                else:
                    self.dict[length] = []
                    self.dict[length].append(new_plist[i])
                plist.append(new_plist[i])
                self.output.add(new_output)

    def synthesize(self, bound, operation, var, inputs_output):
        plist = []
        args = Var('args')
        prog_evaluated = 0
        init_flag = 0
        # build cost map
        self.cost[Replace] = int(-math.log(.166, 2))
        self.cost[Concat] = int(-math.log(.166, 2))
        self.cost['args'] = int(-math.log(.166, 2))
        for i in var:
            self.cost[i] = int(-math.log(.166, 2))

        # initial programs
        plist.append(args)
        for i in var:
            plist.append(Str(i))

        for i in plist:
            x = calculate_cost(i, self.cost)
            if x not in self.dict.keys():
                self.dict[int(x)] = []
                self.dict[int(x)].append(i)
            else:
                self.dict[int(x)].append(i)
        self.max_cost = 2

        for i in range(bound):
            self.grow(plist, operation, var, inputs_output)
            if (self.final_flag == 1):
                return

    def iscorrect(self, prog, input_output):
        flag = 0
        for i in input_output:
            if (prog.interpret(i) == i["out"]):
                flag = flag + 1
        if (flag == len(input_output)):
            return True
        else:
            return False


synthesizer = BottomUpSearch()
start = time.time()
synthesizer.synthesize(50, [Replace, Concat], ['<', '>', '*'], [{'args': 'a < 4 and a > 0', "out": 'a * 4 and a * 0'},{'args': '<open and <close>',"out": '*open and *close*'},{'args': '<change> <string> to <a> number',"out": '*change* *string* to *a* number'}])
end = time.time()
print(f"Execution time: {end - start}")

# program = Replace(Str('a < 4 and a > 0'), Str('<'), Str(''))
# print(program.interpret(None))


