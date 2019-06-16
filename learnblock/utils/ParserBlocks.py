from learnblock.utils.Types import BlockType


class ParserBlocks:

    def parserBlocks(self, blocks, events:bool = False):
        text = self.parserUserFuntions(blocks)
        text += "\n\n"
        if events:
            text += self.parserWhenBlocks(blocks)
        else:
            text += self.parserOtherBlocks(blocks)
        return text

    def parserUserFuntions(self, blocks):
        text = ""
        for b in [block for block in blocks if block[1]["TYPE"] is BlockType.USERFUNCTION]:
            text += "def " + self.toTBlockCode(b, 1)
            text += "\nend\n\n"
        return text

    def parserWhenBlocks(self, blocks):
        text = ""
        for b in [block for block in blocks if block[0] == "when"]:
            text += "when " + b[1]['NAMECONTROL']
            if b[1]['RIGHT'] is not None:
                text += " = " + self.toTBlockCode(b[1]['RIGHT'], 0)
            text += ":\n"

            if b[1]['BOTTOMIN'] is not None:
                text += "\t" + self.toTBlockCode(b[1]['BOTTOMIN'], 2) + "\n"
            else:
                text += "pass\n"
            text += "end\n\n"
        return text

    def parserOtherBlocks(self, blocks):
        text = ""
        for b in [block for block in blocks if "main" == block[0]]:
            text += b[0] + ":\n"
            if b[1]["BOTTOMIN"] is not None:
                text += "\t" + self.toTBlockCode(b[1]["BOTTOMIN"], 2)
            else:
                text += "pass"
            text += "\nend\n\n"
        return text

    def toTBlockCode(self, inst, ntab=1):
        text = inst[0]
        if inst[1]["TYPE"] in [BlockType.USERFUNCTION, BlockType.LIBRARY]:
            text = inst[0] + "()"
        if inst[1]["TYPE"] is BlockType.CONTROL:
            if inst[1]["VARIABLES"] is not None:
                text = inst[0] + "("
                for var in inst[1]["VARIABLES"]:
                    text += var + ", "
                text = text[0:-2] + ""
                text += ")"
        if BlockType.isfunction(inst[1]["TYPE"]):
            text = "function." + inst[0] + "("
            if inst[1]["VARIABLES"] is not None:
                for var in inst[1]["VARIABLES"]:
                    text += var + ", "
                text = text[0:-2] + ""
            text += ")"
        elif inst[1]["TYPE"] is BlockType.VARIABLE:
            text = inst[0]
            if inst[1]["VARIABLES"] is not None:
                text += " = "
                for var in inst[1]["VARIABLES"]:
                    text += var

        if inst[1]["RIGHT"] is not None:
            text += " " + self.toTBlockCode(inst[1]["RIGHT"])
        if inst[1]["BOTTOMIN"] is not None:
            text += ":\n" + "\t" * ntab + self.toTBlockCode(inst[1]["BOTTOMIN"], ntab + 1)
        if inst[0] in ["while", "while True"]:
            text += "\n\t" * (ntab - 1) + "end"
        if inst[0] == "else" or (inst[0] in ["if", "elif"] and (inst[1]["BOTTOM"] is None or (
                inst[1]["BOTTOM"] is not None and inst[1]["BOTTOM"][0] not in ["elif", "else"]))):
            text += "\n" + "\t" * (ntab - 1) + "end"
        if inst[1]["BOTTOM"] is not None:
            text += "\n" + "\t" * (ntab - 1) + self.toTBlockCode(inst[1]["BOTTOM"], ntab)
        return text
