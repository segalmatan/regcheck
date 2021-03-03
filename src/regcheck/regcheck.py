"""
A Utility library for verifying object sequences in a regex-like fashion

Copyright (c) 2020-2021 segalmatan
f
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import copy


# Used to store the last evaluation error reason during evaluation time
# TODO: Change this method for parralelism
G_LAST_EVALUATION_ERROR = None


def _set_last_failure_error(reason):
	"""
	:param reason: The last evaluation failure reason
	:type  reason: str
	"""
	global G_LAST_EVALUATION_ERROR
	G_LAST_EVALUATION_ERROR = reason


def _get_last_failure_error():
	"""
	:return: The last evaluation failure reason
	:rtype : str
	"""
	global G_LAST_EVALUATION_ERROR
	return G_LAST_EVALUATION_ERROR


class RegexDescription(object):
	"""
	A class used to designate a class as a regex descriptor
	(classes that the user uses to describe the regex)
	"""
	def __init__(self):
		pass


class EvaluationAction(RegexDescription):
	"""
	An action that can be taken in reference to an object during evaluation-time
	"""
	def __init__(self, consuming=True):
		"""
		:param consuming: Wether this evaluation action should consume the object it's evaluating
		:type  consuming: bool
		"""
		self._consuming = consuming

	def is_consuming(self):
		"""
		:return: Wether the action should consume the object it's evaluating
		:rtype : bool
		"""
		return self._consuming

	def perform(self, obj, variables_frame=None):
		"""
		:param obj: The object with wich we perform the action
		:type  obj: any
		:param variables_frame: The frame holding the evaluation variables
		:type  variables_Frame: VariablesFrame
		:return: Wether the object evaluation action succeeded
		:rtype : bool
		"""
		raise NotImplementedError()


class Check(EvaluationAction):
	"""
	Check an object and its attributes
	"""
	def __init__(self, __regcheck_required_type=None, **obj_attributes):
		"""
		:param __regcheck_required_type: The type of the object you wish to get
		:type  __regcheck_required_type: type
		:note  __regcheck_required_type: None for not enforcing type checking
		:param obj_attributes: The attributes required from an evaluated object
		:type  obj_attributes: kwargs dict
		"""
		super(Check, self).__init__()
		self._type = __regcheck_required_type
		self._obj_attributes = obj_attributes

	def __repr__(self):
		"""
		:return: Textual representation of the object
		:rtype : str
		"""
		return "Check({type}, {attributes})".format(
			type="any" if self._type is None else self._type,
			attributes=", ".join(map(lambda atr: "{}={}".format(atr[0], atr[1]), self._obj_attributes.items()))
		)

	def perform(self, obj, variables_frame=None):
		"""
		:param obj: The object to be evaluated
		:type  obj: any
		:param variables_frame: The frame holding the evaluation variables
		:type  variables_frame: VariablesFrame
		:return: Wether the object evaluation action succeeded
		:rtype : bool
		"""
		if self._type is not None and not isinstance(obj, self._type):
			_set_last_failure_error("Wrong type - expected: {}, got: {}".format(self._type, type(obj)))
			return False

		# Check all specified 
		for attribute, desired in self._obj_attributes.iteritems():

			# Get the object attribute value
			if not hasattr(obj, attribute):
				_set_last_failure_error("Object doesn't have attribute {}".format(attribute))
				return False

			obj_attribute_val = getattr(obj, attribute)

			# Check the desired value against the attribute value
			if isinstance(desired, EvaluationAction):
				if not desired.perform(obj_attribute_val, variables_frame):
					return False
			else:
				if not obj_attribute_val == desired:
					_set_last_failure_error("Object attribute {} value not matched - expected: {}, got {}".format(attribute, desired, obj_attribute_val))
					return False

		return True


class LambdaCheck(Check):
    """
    Check an object according to a supplied lambda
    """
    def __init__(self, check_lambda):
        """
        :param check_lambda: The lambda used to check a given object
        :note  check_lambda: The lambda should take an object ot test and a variables frame
        :type  check_lambda: function
        """
        super(LambdaCheck, self).__init__()
        self._check_lambda = check_lambda

    def __repr__(self):
        """
        :return: Textual representation of the object
        :rtype : str
        """
        return "LambdaCheck({checklambda})".format(checklambda=self._check_lambda)

    def perform(self, obj, variables_frame=None):
        """
        :param obj: The object to be evaluated
        :type  obj: any
        :param variables_frame: The frame holding the evaluation variables
        :type  variables_frame: VariablesFrame
        :return: Wether the object evaluation action succeeded
        :rtype : bool
        """
        return self._check_lambda(obj, variables_frame)


class Range(RegexDescription):
	"""
	Specify a sequence of checks that can repeat multiple times
	"""
	def __init__(self, min_count, max_count, *regex_descriptions):
		"""
		:param min_count: The minimum amount of repeats of the underlying check sequence
		:type  min_count: int
		:param max_count: The maximum amount of repeats of the underlying check sequence
		:type  max_count: int
		:param regex_descriptions: The underlying regex elements that can be repeated
		:type  regex_descriptions: list of RegexDescription
		"""
		self._min_count = min_count
		self._max_count = max_count
		self._regex_descriptions = regex_descriptions

		if 0 == len(regex_descriptions):
			raise ValueError("Can't have an empty range")

		if self._min_count > self._max_count:
			raise ValueError("min count must be smaller then max count")

	def get_sub_elements(self):
		"""
		:return: The Range sub elements
		:rtype : list of RegexDescription
		"""
		return self._regex_descriptions


class RegexPlus(Range):
	"""
	Specify a sequence that should occur one or more times
	(shorthand for Range with min=1, max=None)
	"""
	def __init__(self, *regex_descriptions):
		"""
		:param regex_descriptions: The underlying regex elements that can be repeated
		:type  regex_descriptions: list of RegexDescription
		"""
		super(RegexPlus, self).__init__(1, None, *regex_descriptions)


class RegexAsterix(Range):
	"""
	Specify a sequence that should occur zero or more times
	(shorthand for Range with min=0, max=None)
	"""
	def __init__(self, *regex_descriptions):
		"""
		:param regex_descriptions: The underlying regex elements that can be repeated
		:type  regex_descriptions: list of RegexDescription
		"""
		super(RegexAsterix, self).__init__(0, None, *regex_descriptions)


class Possible(Range):
	"""
	Specify a check that may or may not be satisfied
	(shorthand for Range with min=0, max=1 with the same check)
	"""
	def __init__(self, __regcheck_required_type=None, **obj_attributes):
		"""
		:param __regcheck_required_type: The type of the object you wish to get
		:type  __regcheck_required_type: type
		:note  __regcheck_required_type: None for not enforcing type checking
		:param obj_attributes: The attributes required from an evaluated object
		:type  obj_attributes: kwargs dict
		"""
		underlying_check = Check(__regcheck_required_type, **obj_attributes)
		super(Possible, self).__init__(0, 1, underlying_check)


class Repeat(Range):
	"""
	Specify a sequence that should repeat a certain amount of times
	(shorthand for Range with min=count, max=count)
	"""
	def __init__(self, count, *regex_descriptions):
		"""
		:param count: The amount of times the underlying sequence should repeat
		:type  count: int
		:param regex_descriptions: The underlying regex elements that can be repeated
		:type  regex_descriptions: list of RegexDescription
		"""
		super(Repeat, self).__init__(count, count, *regex_descriptions)


class Variable(object):
	"""
	A regex evaluation-time variable
	(created, modified and evaluated during the evaluation of a sequence)
	"""
	def __init__(self, name=None):
		"""
		:param name: The name used to reference the variable
		:type  name: str
		:note  name: leave as None for automatic name generation
		"""
		self._name = name if name is not None else "__regcheck_var_id({})".format(str(id(self)))

	def __repr__(self):
		"""
		:return: Textual representation of the object
		:rtype : str
		"""
		return self._name

	def get_name(self):
		"""
		:return: The the name used to identify the variable
		:rtype : str
		"""
		return self._name

	def set(self):
		"""
		:return: A set variable evaluation-time action for this variable
		:rtype : SetVariable
		"""
		return SetVariable(self)

	def get(self):
		"""
		:return: A variable value check
		:rtype : VariableCheck
		"""
		return VariableCheck(self)


class VariablesFrame(object):
	"""
	A collection of variables
	(used to hold variable values in different evaluation branches)
	"""
	def __init__(self):
		"""
		"""
		self._variables = dict()
		self._pending_changes = []

	def __repr__(self):
		"""
		:return: Textual representation of the object
		:rtype : str
		"""
		return self._variables.__repr__()

	def has_variable(self, variable):
		"""
		Check wether a variable exists in the frame
		:param variable: The checked variable
		:type  variable: Variable
		:return: Wether the given variable is inside the frame
		:rtype : bool
		"""
		return variable.get_name() in self._variables

	def get_var_value(self, variable):
		"""
		:param variable: The queried variable
		:type  variable: Variable
		:return: The value stored in the given variable
		:rtype : any
		"""
		return self._variables[variable.get_name()]

	def request_var_change(self, variable, value):
		"""
		:param variable: The variable to be changed
		:type  variable: Variable
		:param value: The updated value of the variable
		:type  value: any
		"""
		self._pending_changes.append((variable, value))

	def pending_changes_count(self):
		"""
		:return: The amount of pending variable changes in this frame
		:rtype : int
		"""
		return len(self._pending_changes)

	def apply_changes(self):
		"""
		Apply all of the frame pending changes (update variables)
		"""
		for variable, updated_value in self._pending_changes:
			self._variables[variable.get_name()] = updated_value

		self._pending_changes = []


class SetVariable(EvaluationAction):
	"""
	An action representing a change to a variable
	(doesn't consume the object it acts on)
	"""
	def __init__(self, variable, consume_object=False):
		"""
		:param variable: The variable to set
		:type  variable: Variable
		:param consume_object: Wether to consume the given object on perform
		:type  consume_object: bool
		"""
		super(SetVariable, self).__init__(consuming=consume_object)
		self._variable = variable

	def __repr__(self):
		"""
		:return: Textual representation of the object
		:rtype : str
		"""
		return "SetVariable({})".format(self._variable)

	def perform(self, obj, variables_frame=None):
		"""
		:param obj: The object to be evaluated
		:type  obj: any
		:param variables_frame: The frame holding the evaluation variables
		:type  variables_frame: VariablesFrame
		:return: Wether the object evaluation action succeeded
		:rtype : bool
		"""
		variables_frame.request_var_change(self._variable, obj)
		return True


class VariableCheck(Check):
	"""
	Checks that an object is equal to an evaluation-time variable
	"""
	def __init__(self, variable):
		"""
		:param variable: The variable to check against
		:type  variable: Variable
		"""
		self._variable = variable

	def __repr__(self):
		"""
		:return: Textual representation of the object
		:rtype : str
		"""
		return "VariableCheck({})".format(self._variable)

	def perform(self, obj, variables_frame):
		"""
		:param obj: The object to be evaluated
		:type  obj: any
		:param variables_frame: The frame holding the evaluation variables
		:type  variables_frame: VariablesFrame
		:return: Wether the object evaluation action succeeded
		:rtype : bool
		"""
		# Check variable existence in the frame
		if not variables_frame.has_variable(self._variable): return False

		# Check variable value
		variable_value = variables_frame.get_var_value(self._variable)
		if obj != variable_value:
			_set_last_failure_error("Wrong object value - expected: {}, got: {}".format(self._variable.get_name(), variable_value, obj))
			return False
		else:
			return True


class EvaluationNode(object):
	"""
	An interface for regex machine evaluation nodes
	(states in the state machine)
	"""
	def __init__(self, forward_node=None):
		"""
		:param forward_node: The next node in the state machine
		:type  forward_node: EvaluationNode
		"""
		self._forward_node = forward_node

	def set_forward_node(self, forward_node):
		"""
		:param forward_node: The next node in the state machine
		:type  forward_node: EvaluationNode
		"""
		self._forward_node = forward_node

	def get_forward_node(self):
		"""
		:return: The next node for the evaluation
		:rtype : EvaluationNode
		"""
		return self._forward_node

	def evaluate(self, obj, variables_frame):
		"""
		:param obj: The object to be evaluated
		:type  obj: any
		:param variables_frame: The variables frame of the currently evaluated branch
		:type  variables_frame: VariablesFrame
		:return: Wether the object is consumed for the current evaluation
		:rtype : bool
		"""
		raise NotImplementedError()

	def decide_nexts(self):
		"""
		Get all the possible next states for the regex state machine
		:return: All the next possible states
		:rtype : list of EvaluationNode
		"""
		raise NotImplementedError()


class ActionNode(EvaluationNode):
	"""
	A state in the regex state machine representing an underlying EvaluationAction
	"""
	def __init__(self, action, forward_node=None):
		"""
		:param action: The underlying action to be transformed into a state
		:type  action: EvaluationAction
		:param forward_node: The next node in the state machine
		:type  forward_node: EvaluationNode
		"""
		super(ActionNode, self).__init__(forward_node)

		self._action = action
		self._action_success = False

	def __repr__(self):
		"""
		:return: Textual representation of the object
		:rtype : str
		"""
		return "ActionNode({})".format(self._action)

	def evaluate(self, obj, variables_frame):
		"""
		:param obj: The object to be evaluated
		:type  obj: any
		:param variables_frame: The variables frame of the currently evaluated branch
		:type  variables_frame: VariablesFrame
		:return: Wether the object is consumed for the current evaluation
		:rtype : bool
		"""
		self._action_success = self._action.perform(obj, variables_frame)
		return self._action.is_consuming()

	def decide_nexts(self):
		"""
		Get all the possible next states for the regex state machine
		:return: All the next possible states
		:rtype : list of EvaluationNode
		"""
		return [] if not self._action_success else [self.get_forward_node()]


class RangeNode(EvaluationNode):
	"""
	A state in the regex state machine representing an underlying range of repeats
	"""
	class RangeManagementNode(EvaluationNode):
		"""
		# TODO: This is a rather quick solution for the stateful range problem, think of a more elegant one
		# refer to EvaluationMachine.check NOTE for more detail about this problem
		A stateful management node, used to keep track of the 
		needs to be created seperately for every branch (for keeping the stateful data)
		"""
		def __init__(self, min_visits, max_visits, inner_node=None, outer_node=None):
			"""
			:param min_visits: The minimal visits through this node until it can advance to the forward node
			:type  min_visits: int
			:param max_visits: The maximal visits through this node until it can advance to the forward node
			:type  max_visits: int
			:param inner_node: The node representing the inner range part, eventually leading back to this node
			:type  inner_node: EvaluationNode
			:param outer_node: The node representing the regex-element after the range specifier
			:type  outer_node: EvaluationNode
			"""
			super(RangeNode.RangeManagementNode, self).__init__(outer_node)

			self._visits = 0

			self._min_visits = min_visits
			self._max_visits = max_visits

			self._inner_node = inner_node
			self._outer_node = outer_node

		def __repr__(self):
			"""
			:return: Textual representation of the object
			:rtype : str
			"""
			return "RangeManagement(min={}, max={}, count={})".format(self._min_visits, self._max_visits, self._visits)

		def evaluate(self, obj, variables_frame):
			"""
			:param obj: The object to be evaluated
			:type  obj: any
			:param variables_frame: The variables frame of the currently evaluated branch
			:type  variables_frame: VariablesFrame
			:return: Wether the object is consumed for the current evaluation
			:rtype : bool
			"""
			self._visits += 1
			return False

		def decide_nexts(self):
			"""
			Get all the possible next states for the regex state machine
			:return: All the next possible states
			:rtype : list of EvaluationNode
			"""
			next_states = []
			effective_visits = self._visits - 1

			if self._max_visits is None:
				next_states.append(self._inner_node)
			else:
				if effective_visits < self._max_visits: # Note that theres no need for <=, as subsequent returns would fail
					next_states.append(self._inner_node)
				if self._min_visits <= effective_visits and effective_visits <= self._max_visits:
					next_states.append(self._outer_node)

			if len(next_states) == 0:
				_set_last_failure_error("Range visits count requirement not met")

			return next_states

	def __init__(self, repeat_identifier, forward_node=None):
		"""
		:param repeat_identifier: The range node descriptor
		:type  repeat_identifier: RegexDescription
		:param forward_node: The node representing the regex-element after the range specifier
		:type  forward_node: EvaluationNode
		"""
		super(RangeNode, self).__init__(forward_node)
		self._repeat_identifier = repeat_identifier

	def __repr__(self):
		"""
		:return: Textual representation of the object
		:rtype : str
		"""
		return "RangeNode(min={}, max={})".format(self._repeat_identifier._min_count, self._repeat_identifier._max_count)

	def evaluate(self, obj, variables_frame):
		"""
		:param obj: The object to be evaluated
		:type  obj: any
		:param variables_frame: The variables frame of the currently evaluated branch
		:type  variables_frame: VariablesFrame
		:return: Wether the object is consumed for the current evaluation
		:rtype : bool
		"""
		return False

	def _create_range_branch(self):
		"""
		:return: A Head node of a clean range branch
		:rtype : RangeManagementNode
		"""
		# Build the range branch underlying sub nodes
		sub_nodes = []
		for sub_identifier in self._repeat_identifier.get_sub_elements():
			sub_nodes.append(build_node(sub_identifier))

		for i in range(len(sub_nodes) - 1):
			sub_nodes[i].set_forward_node(sub_nodes[i+1])

		# Create the branch specific management node
		branch_head = self.RangeManagementNode(self._repeat_identifier._min_count, self._repeat_identifier._max_count, sub_nodes[0], self._forward_node)
		sub_nodes[-1].set_forward_node(branch_head)

		return branch_head

	def decide_nexts(self):
		"""
		Get all the possible next states for the regex state machine
		:return: All the next possible states
		:rtype : list of EvaluationNode
		"""
		return [self._create_range_branch()]


def build_node(regex_description):
	"""
	Handles the creation of individual states
	:param regex_description: The description of the evaluation node
	:type  regex_description: RegexDescription
	:return: Nodes created from this regex_description
	"""
	if not isinstance(regex_description, RegexDescription):
		raise TypeError("node builder needs to get a regex description")

	# Handle EvaluationAction descriptions
	if isinstance(regex_description, EvaluationAction):
		result = ActionNode(regex_description)

	# Handle Range descriptions
	if isinstance(regex_description, Range):
		result = RangeNode(regex_description)

	return result


class EvaluationMachine(object):
	"""
	The state machine describing the given object regex
	"""
	def __init__(self, regex_descriptions):
		"""
		:param regex_descriptions: The description of all the machine regex elements
		:type  regex_descriptions: list
		"""
		nodes = []
		for description in regex_descriptions:
			nodes.append(build_node(description))

		for index in range(len(nodes) - 1):
			nodes[index].set_forward_node(nodes[index + 1])

		# Use None to represent the final node
		self._final_node = None

		nodes[-1].set_forward_node(self._final_node)

		self._nodes = nodes
		self._start_node = nodes[0]

		# Error details
		self._last_max_index = 0
		self._last_failure_reason = None

	def check(self, sequence, consume_all=True):
		"""
		:param sequence: The sequence of object to check
		:type  sequence: sequencable
		:return: Wether the given sequence satisfies the machine
		:rtype : bool
		"""
		self._last_max_index = 0
		self._last_failure_reason = None

		branch_stack = []

		# TODO: Insert parralelism to the branches evaluation
		branch_stack.append((self._start_node, 0, VariablesFrame()))

		while 0 != len(branch_stack):
			current_node, seq_index, variables_frame = branch_stack.pop()

			# Keeping track of max index reached for error report
			if seq_index > self._last_max_index: self._last_max_index = seq_index

			# Evaluate current branch state
			evaluated_object = None if seq_index >= len(sequence) else sequence[seq_index]
			consume_obj = current_node.evaluate(evaluated_object, variables_frame)
			new_index = seq_index + 1 if consume_obj else seq_index

			next_nodes = current_node.decide_nexts()

			# Document max index failure reason
			if len(next_nodes) == 0 and seq_index == self._last_max_index:
				self._last_failure_reason = _get_last_failure_error()

			for next_node in next_nodes:
				# Check for reaching the end of the state machine
				if next_node is self._final_node:
						if not consume_all or new_index == len(sequence): return True
				else:
					# Create a new variable frame on var-write actions
					new_var_frame = variables_frame if variables_frame.pending_changes_count() == 0 else copy.deepcopy(variables_frame)
					new_var_frame.apply_changes()

					# TODO: Think of a more elegant solution to the stateful range problem
					branch_stack.append((next_node, new_index, new_var_frame))

		return False

	def last_failure_details(self):
		"""
		:return: The maximum index reached of the last evaluated sequence with the last failure reason
		:rtype : tuple of (int, str)
		"""
		return (self._last_max_index, self._last_failure_reason)


class Evaluation(object):
	"""
	An object sequence regular expression test
	"""
	def __init__(self, *regex_descriptions):
		"""
		:param:
		"""
		if len(regex_descriptions) == 0:
			raise ValueError("Can't have an empty evaluation")

		self._descriptions = regex_descriptions
		self._changed = False
		self._machine = EvaluationMachine(regex_descriptions)

	def __repr__(self):
		"""
		:return: Textual representation of the object
		:rtype : str
		"""
		return "Evaluation({})".format(self._descriptions)

	def append(self, regex_description):
		"""
		:param regex_description: Description of the next regex element
		:type  regex_description: RegexDescription
		"""
		self._descriptions.append(regex_description)
		self._changed = True

	def check(self, sequence):
		"""
		:param sequence: A sequence of tested objects
		:type  sequence: list
		:return: Wether the sequence satisfies the conditions described by the regex elements
		:rtype : bool
		"""
		if self._changed:
			self._machine = EvaluationMachine(self._descriptions)
			self._changed = False

		return self._machine.check(sequence)
