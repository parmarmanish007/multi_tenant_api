from typing import List, Tuple

class ConstantHelper:
    @classmethod
    def get_values(cls) -> List[str]:
        return [constant.value for constant in cls]

    @classmethod
    def get_choices(cls) -> Tuple[Tuple[str, str], ...]:
        """ 
        Django choices usually expect (stored_value, human_readable_label).
        Using .value as the key is safer for database integrity.
        """
        return tuple((constant.value, constant.name.title().replace('_', ' ')) for constant in cls)

    @classmethod
    def get_choices_as_values(cls) -> List[Tuple[str, str]]:
        return [(constant.value, constant.value) for constant in cls]