
import re
from subprocess import Popen, PIPE

class Objdump(object):
	"""docstring for Objdump"""
	def __init__(self, command="objdump"):
		super(Objdump, self).__init__()
		self._command = command
		self._flags = "-dS"

	def _exec(self, path):
		proc = Popen([self._command, self._flags, path], stdout=PIPE)
		proc.wait()
		self._stdout = proc.stdout.read()

	def analyze(self, path):
		self._exec(path)

		sectionRe = re.compile(r"Disassembly of section (.*):")
		functionRe = re.compile(r"([0-9a-f]+) \<(.*)\>:")
		instructionRe = re.compile(r"([0-9a-f]+):\t([0-9a-f][0-9a-f]( [0-9a-f][0-9a-f])*)([ ]*\t([a-z0-9]+)([ ]+(.*))?)?$")

		lines = self._stdout.split("\n")
		lines = [line.strip() for line in lines]

		sections = []
		sectionsMap = {}
		instructionsMap = {}

		self._sections = sections
		self._instructions = instructionsMap
		self._sourceLines = []

		currentSourceLine = None

		for line in lines:
			if len(line.strip()) == 0: continue

			m = sectionRe.match(line)
			if m:
				sectionName = m.group(1)
				sections.append({
					"name": sectionName,
					"functions": []
				})
				sectionsMap[sectionName] = sections[-1]

				# reset source line
				currentSourceLine = None
				continue

			if len(sections) > 0:
				m = functionRe.match(line)
				if m:
					sections[-1]["functions"].append({
						"name": m.group(2),
						"address": m.group(1),
						"instruction_first": None,
						"instruction_last": None
					})

					# reset source line
					currentSourceLine = None
					continue

				m = instructionRe.match(line)
				if m:
					# parse the instruction line
					instruction = self.parseInstructionLine(line, m)

					# add the instruction to the source line, if any
					if currentSourceLine:
						currentSourceLine["instruction_last"] = instruction["intaddr"]
						if currentSourceLine["instruction_first"] is None:
							currentSourceLine["instruction_first"] = instruction["intaddr"]

					continue

				# source code line
				currentSourceLine = {
					"line": line,
					"instruction_first": None,
					"instruction_last": None
				}
				self._sourceLines.append(currentSourceLine)
				continue

			else:
				continue

			print "[DEBUG] Unmatched: %s" % (line)

	def parseInstructionLine(self, line, match):
		hexaddr = match.group(1)
		intaddr = int(match.group(1), 16)
		bytestring = match.group(2).strip()
		inst = match.group(5)
		params = match.group(7)

		instruction = {
			"hexaddr": hexaddr,
			"intaddr": intaddr,
			"bytes": bytestring,
			"inst": inst,
			"params": params
		}
		self._instructions[instruction["intaddr"]] = instruction

		# add the instruction to the function that's currently looked at
		if len(self._sections[-1]["functions"]) > 0:
			f = self._sections[-1]["functions"][-1]
			f["instruction_last"] = intaddr

			if f["instruction_first"] is None:
				f["instruction_first"] = intaddr

		return instruction


	def getFunctionByName(self, name):
		for section in self._sections:
			for f in section["functions"]:
				if f["name"] == name:
					return f

	"""
		* parameters are integer number (base 10)
	"""
	def getInstructionsOfRange(self, addrstart, addrend):
		instructions = []
		for intaddr in self._instructions:
			if addrstart <= intaddr and intaddr <= addrend:
				instructions.append(self._instructions[intaddr])
		return instructions

