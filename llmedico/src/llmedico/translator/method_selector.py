import random

from llmedico.conditions.model import ClassModel, MethodModel

#TODO where to put this??
class MethodSelector:
    UNIMPORTANT = {
        "factory",
        "set",
        "helper",
        "initialize","initialise",
        "clone",
        "print"
        "toString",
        "string",
        "read",
        "write",
        "file",
        "config",
        "execute"
    }
    def __init__(self, cls: ClassModel):
        self.cls = cls
        self.methods = self._get_methods() #without constructor
        self.important_methods = self._remove_unimportant_methods()

    def _get_methods(self):
        methods = []
        for member in self.cls.methods:
            if not member.is_constructor:
                methods.append(member)

        return methods

    #TODO remove unwanted methods/group into categories and
    # or only retrieve certain categories
    def _remove_unimportant_methods(self):
        important_methods = []
        for member in self.methods:
            important = True
            for term in self.UNIMPORTANT:
                if term in member.signature.name.lower():
                    important = False
                    break
            if important:
                important_methods.append(member)
        return important_methods

    #TODO remove methods that are not needed for this method
    def _remove_unrelated_methods(self, method_name: str):
        related_methods = []

        for member in self.important_methods: ...

    @staticmethod
    def _get_method_to_str(method: MethodModel):
        params = ",".join(
            f"{p.type.qualified_name} {p.name}"
            for p in method.signature.parameters
        )

        return_type = method.signature.return_type
        return_value = "void" if return_type is None else return_type.qualified_name
        return f"{return_value} {method.signature.name}({params})"

    def get_methods_to_str(self):
        strs = ""
        rng = random.Random(42)  # fixed seed
        if len(self.important_methods) > 20:
            self.important_methods = rng.sample(self.important_methods, 20)  # TODO Hotfix, implement real heuristic
        for member in self.important_methods:
            strs += f"{self._get_method_to_str(member)}\n"
        return strs


