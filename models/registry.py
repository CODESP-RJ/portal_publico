class RegistryValidators:
    _validators_alt_exc = {}
    _validators_ins = {}

    @classmethod
    def register_alt_exc(cls, name, validator_class):
        cls._validators_alt_exc[name.upper()] = validator_class

    @classmethod
    def get_validator_alt_exc(cls, name):
        return cls._validators_alt_exc.get(name.upper())

    @classmethod
    def register_ins(cls, name, validator_class):
        cls._validators_ins[name.upper()] = validator_class

    @classmethod
    def get_validator_ins(cls, name):
        return cls._validators_ins.get(name.upper())