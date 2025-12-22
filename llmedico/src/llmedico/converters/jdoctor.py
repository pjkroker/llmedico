import re
import html

from llmedico.conditions.model import ConditionKind, ClassModel, MethodModel, Condition, ParameterModel, TypeModel
from llmedico.converters.base import ConditionConverter


class JDoctorConditionConverter(ConditionConverter):

    @staticmethod
    def normalize_javadoc_text(text: str) -> str:
        if not text:
            return ""

        # 1. Convert HTML entities (&lt; → <, &gt; → >, etc.)
        text = html.unescape(text)

        # 2. Remove HTML tags (<code>, <p>, etc.) re.sub = regular expressions and substitute
        text = re.sub(r"<[^>]+>", "", text)

        # 3. Normalize whitespace (newlines, multiple spaces)
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    @staticmethod
    def type_to_jdoctor(type: TypeModel) -> dict:
        return {
            "qualifiedName": type.qualified_name,
            "name": type.simple_name,
            "isArray": type.is_array
        }

    def parameter_to_jdoctor(self, parameter: ParameterModel) -> dict:
        return {
            "type": self.type_to_jdoctor(parameter.type),
            "name": parameter.name
        }

    @staticmethod
    def method_signature_to_string(method: MethodModel) -> str:
        params = ",".join(
            f"{p.type.qualified_name} {p.name}"
            for p in method.signature.parameters
        )
        return f"{method.signature.name}({params})"

    def param_condition_to_jdoctor(self, cond: Condition, method: MethodModel) -> dict:
        # find the matching parameter by name
        param = next(
            p for p in method.signature.parameters
            if p.name == cond.name
        )

        return {
            "parameter": self.parameter_to_jdoctor(param),
            "comment": self.normalize_javadoc_text(cond.content),
            "kind": ConditionKind.PARAM.value,
            "condition": cond.expression.replace("assert ", "").replace(";", "")
        }

    @staticmethod
    def exception_type_to_jdoctor(exception_name: str) -> dict:
        return {
            "qualifiedName": f"java.lang.{exception_name}",
            "name": exception_name,
            "isArray": False
        }

    @staticmethod
    def extract_code_tags(cond: Condition, method: MethodModel) -> list:
        """
        codeTags are identifiers mentioned in the Javadoc @throws comment that point to code-level entities
        (parameters, literals, fields, etc.) involved in the exceptional behavior.
        JDoctor accurately derives them with NLP. Here just apply a simple heuristic.
        It would also be possible to just return ["null"].
        :param cond:
        :param method:
        :return:
        """
        tags = []

        for p in method.signature.parameters:
            if p.name in cond.description or p.name in cond.content:
                tags.append(p.name)

        if "null" in cond.description.lower():
            tags.append("null")

        return list(set(tags))

    def throws_condition_to_jdoctor(self, cond: Condition, method: MethodModel) -> dict:
        return {
            "exceptionType": self.exception_type_to_jdoctor(cond.name),
            "codeTags": self.extract_code_tags(cond, method),
            "comment": self.normalize_javadoc_text(cond.description),
            "kind": ConditionKind.THROWS.value,
            "condition": cond.expression.replace("assert ", "").replace(";", "")
        }

    def return_condition_to_jdoctor(self, cond: Condition) -> dict:
        return {
            "comment": self.normalize_javadoc_text(cond.description),
            "kind": ConditionKind.RETURN.value,
            "condition": cond.expression.replace("assert ", "").replace(";", "")
        }

    def convert_method(self, method: MethodModel) -> dict:
        param_tags = []
        throws_tags = []
        return_tag = None

        for cond in method.conditions:
            if cond.kind == ConditionKind.PARAM:
                param_tags.append(self.param_condition_to_jdoctor(cond, method))

            elif cond.kind == ConditionKind.THROWS:
                throws_tags.append(self.throws_condition_to_jdoctor(cond, method))

            elif cond.kind == ConditionKind.RETURN:
                return_tag = self.return_condition_to_jdoctor(cond)

        result = {
            "signature": self.method_signature_to_string(method),
            "name": method.signature.name,

            "containingClass": {
                "qualifiedName": method.declaring_class.qualified_name,
                "name": method.declaring_class.name,
                "isArray": method.declaring_class.is_array
            },

            "targetClass": method.declaring_class.qualified_name,

            "isVarArgs": any(p.is_varargs for p in method.signature.parameters),

            "parameters": [
                self.parameter_to_jdoctor(p)
                for p in method.signature.parameters
            ]

        }

        if method.signature.return_type is not None:
            result["returnType"] = self.type_to_jdoctor(
                method.signature.return_type
            )


        result["paramTags"] = param_tags

        if return_tag:
            result["returnTag"] = return_tag

        result["throwsTags"] = throws_tags

        return result

    def convert_class(self, cls: ClassModel) -> list[dict]:
        return [
                self.convert_method(m)
                for m in cls.methods
            ]