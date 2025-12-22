from llmedico.conditions.model import ClassModel, MethodModel, MethodSignature, ParameterModel, TypeModel, Condition, ConditionKind

class ClassModelBuilder:

    def _build_conditions(self, method_data: dict) -> list[Condition]:
        conditions = []
        for tag in method_data["tags"]:
            condition = Condition(kind=ConditionKind(tag["tag"].upper()),
                                  expression=tag["assertion"],
                                  content=tag["content"],
                                  description=tag["description"])
            if type(tag["name"]) == str: condition.name = tag["name"]
            else: condition.name = None #return type has no name
            conditions.append(condition)
        return conditions

    def _build_return_type(self, method_data: dict) -> TypeModel | None:
        if 'return_type' in method_data:
            return TypeModel(qualified_name=...,
                             simple_name=...) #TODO change Java Parser
        else:
            return None

    def _build_parameters(self, method_data: dict, cls: ClassModel) -> list[ParameterModel]:
        parameters = []
        for p in method_data['parameters']:
            name = ...
            qualified_name = ... #TODO change Java Parser
            type = TypeModel(qualified_name=...,
                             simple_name=...) #TODO change Java Parser
            parameter = ParameterModel(name=name,type=type)
            parameters.append(parameter)

        return parameters


    def _build_method(self, method_data: dict, cls: ClassModel) -> MethodModel:
        signature = MethodSignature(
            name=method_data['name'],
            return_type=self._build_return_type(method_data),
            parameters=self._build_parameters(method_data, cls),
        )

        conditions = self._build_conditions(method_data)

        method_model = MethodModel(
            signature=signature,
            declaring_class=cls,
            conditions=conditions,
            is_constructor= True if method_data["type"] == "constructor" else False,

        )
        return method_model

    def build(self, data: dict) -> ClassModel:
        cls = ClassModel(
            package=data["package"], #TODO change JavaParser
            name=data["name"],
            qualified_name=data["qualifiedName"] #TODO change JavaParser
        )

        for m in data["members"]:
            method = self._build_method(m, cls)
            cls.methods.append(method)

        return cls
