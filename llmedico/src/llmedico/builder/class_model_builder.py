from llmedico.conditions.model import ClassModel, MethodModel, MethodSignature, ParameterModel, TypeModel, Condition, ConditionKind

class ClassModelBuilder:

    def _build_conditions(self, method_data: dict) -> list[Condition]:
        conditions = []
        tags_order = ["param", "throws", "return"] #insert with fix order
        for selected_tag in tags_order:
            for tag in method_data["tags"]:
                if tag["tag"] == selected_tag and ConditionKind.is_condition_kind(tag["tag"]):
                    if tag["tag"] == "param" and  "<" in tag["name"] and ">" in tag["name"]:
                        continue # we dont need tags like @param <S>,S is a generic type parameter, not a runtime value. TODO take care of this at extraction!
                    condition = Condition(kind=ConditionKind(tag["tag"].upper()),
                                          expression=tag.get("assertion", ""),
                                          content=tag["content"],
                                          description=tag.get("description", ""))
                    if type(tag["name"]) == str: condition.name = tag["name"]
                    else: condition.name = None #return type has no name
                    conditions.append(condition)
        return conditions

    def _build_type(self, parameter_data: dict) -> TypeModel:
        print(parameter_data)
        type_model = TypeModel(qualified_name=parameter_data["type"]["qualified_name"],
                               simple_name=parameter_data["type"]["simple_name"],
                               is_array=parameter_data["type"]["is_array"])
        return type_model

    def _build_return_type(self, method_data: dict) -> TypeModel | None:
        if 'return_type' in method_data and method_data['return_type']: #void has return_type = null
            t = {"type": method_data["return_type"]}
            return self._build_type(t)
        else:
            return None

    def _build_parameters(self, method_data: dict, cls: ClassModel) -> list[ParameterModel]:
        parameters = []
        for p in method_data["parameters"]:
            name = p["name"]
            type = self._build_type(p)
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

    def build_class(self, data: dict) -> ClassModel:
        cls = ClassModel(
            package=data["package"], #TODO change JavaParser
            name=data["name"],
            qualified_name=data["qualified_name"] #TODO change JavaParser
        )

        for m in data["members"]:
            method = self._build_method(m, cls)
            cls.methods.append(method)

        return cls
