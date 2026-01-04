from llmedico.builder.class_model_builder_base import ClassModelBuilderBase
from llmedico.conditions.model import ClassModel, MethodSignature, MethodModel, ParameterModel, TypeModel, Condition, \
    ConditionKind


class ClassModelBuilderJdoctor(ClassModelBuilderBase):

    def _build_conditions(self, method_data: dict) -> list[Condition]:
        conditions = []
        for param in method_data['paramTags']:
            expression = param["condition"]

            condition = Condition(kind=ConditionKind.PARAM,
                                  expression=f"assert {expression};" if expression else "",
                                  content=param["comment"],
                                  description=param["comment"],
                                  name=param["parameter"]["type"]["name"])
            conditions.append(condition)

        for throw in method_data['throwsTags']:
            expression = throw["condition"]

            condition = Condition(kind=ConditionKind.THROWS,
                                  expression=f"assert {expression};" if expression else "",
                                  content=throw["comment"],
                                  description=throw["comment"],
                                  name=throw["exceptionType"]["name"])
            conditions.append(condition)

        if "returnTag" in method_data:
            expression = method_data["returnTag"]["condition"]

            condition = Condition(kind=ConditionKind.RETURN,
                                  expression=f"assert {expression};" if expression else "",
                                  content=method_data["returnTag"]["comment"],
                                  description=method_data["returnTag"]["comment"],
                                  name=None)
            conditions.append(condition)

        return conditions

    def _build_type(self, parameter_data: dict) -> TypeModel:
        type_model = TypeModel(qualified_name=parameter_data["type"]['qualifiedName'],
                               simple_name=parameter_data["type"]['name'],
                               is_array=parameter_data["type"]['isArray'])
        return type_model

    def _build_return_type(self, method_data: dict) -> TypeModel | None:
        if "return_type" in method_data:
            t = {"type": method_data["return_type"]}
            return self._build_type(t)
        return None

    def _build_parameters(self, method_data: dict, cls: ClassModel) -> list[ParameterModel]:
        parameters = []
        for p in method_data['parameters']:
            name = p['name']
            type = self._build_type(p)
            parameter = ParameterModel(name=name, type=type)
            parameters.append(parameter)

        return parameters

    def _build_method(self, method_data: dict, cls: ClassModel):
        name = method_data['name']
        signature = MethodSignature(
            name=name,
            return_type=self._build_return_type(method_data),
            parameters=self._build_parameters(method_data,cls)
        )

        conditions = self._build_conditions(method_data)

        method_model = MethodModel(
            signature=signature,
            declaring_class=cls,
            conditions=conditions,
            is_constructor=True if name == cls.name else False
        )
        return method_model

    def build_class(self, data: dict) -> ClassModel:
        fqn = data[0]["containingClass"]["qualifiedName"]
        if not "." in fqn:
            package = fqn
        else:
            package = fqn.rsplit(".", 1)[0]
        cls = ClassModel(
            package=package,
            name=data[0]["containingClass"]['name'],
            qualified_name=fqn
        )

        for m in data:
            method = self._build_method(m, cls)
            cls.methods.append(method)

        return cls