from llmedico.conditions.model import ClassModel, MethodModel, MethodSignature, ParameterModel, TypeModel, Condition, ConditionKind

class ClassModelBuilder:


    def _build_return_type(self, method_data):
        pass

    def _build_parameters(self, method_data: dict,cls: ClassModel) -> list[ParameterModel]:
        parameters = []
        for p in method_data['parameters']:
            name = ...
            qualified_name = ...
            type = TypeModel()
        pass


    def _build_method(self, method_data: dict, cls: ClassModel) -> MethodModel:
        signature = MethodSignature(
            name=method_data['name'],
            return_type=self._build_return_type(method_data),
            parameters=self._build_parameters(method_data),
        )

        conditions = ... # TODO

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
