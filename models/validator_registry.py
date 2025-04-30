from models.validators.base_validator import BaseValidator

class ValidatorRegistry:
    _validators = {}

    @classmethod
    def register(cls, name, validator_class):
        cls._validators[name.upper()] = validator_class

    @classmethod
    def get_validator(cls, name):
        return cls._validators.get(name.upper())