import cerberus


class UniqueNameChecker:
    def __init__(self):
        self.name_lookup = []

    def check(self, field, value, error):
        if value in self.name_lookup:
            error(field, f"The name field must be unique. The name {value} has already been used.")
        else:
            self.name_lookup.append(value)


class RequiresExistChecker:
    def __init__(self, document):
        self.doc = document

    def check(self, field, requires, error):
        builds = self.doc["builds"]
        for value in requires:
            for build in builds:
                if value == build["name"]:
                    break
            else:
                error(field, f"{value} does not match any build name. Check spelling.")


def target_schema(document):
    unique_name_checker = UniqueNameChecker()
    requires_exist_checker = RequiresExistChecker(document)

    schema = {
        "cxx": {"required": True, "type": "string"},
        "cc": {"required": True, "type": "string"},
        "ar": {"required": True, "type": "string"},

        "compilerFrontend": {
            "required": True,
            "type": "string",
            "allowed": ["msvc", "gcc"]
        },

        "flags": {
            "type": "list",
            "schema": {"type": "string"}
        },

        "defines": {
            "type": "list",
            "schema": {"type": "string"}
        },

        "builds": {
            "required": True,
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "name": {
                        "required": True,
                        "type": "string",
                        "check_with": unique_name_checker.check
                    },

                    "requires": {
                        "type": "list",
                        "empty": False,
                        "schema": {"type": "string"},
                        "check_with": requires_exist_checker.check
                    },

                    "buildRule": {
                        "required": True,
                        "type": "string",
                        "allowed": ["exe", "staticlib", "dynamiclib"]
                    },

                    "outputName": {
                        "required": True,
                        "type": "string"
                    },

                    "srcDirs": {
                        "required": True,
                        "empty": False,
                        "type": "list",
                        "schema": {"type": "string"}
                    },

                    # TODO add checker to check that the paths exists.
                    "includePaths": {
                        "type": "list",
                        "empty": False,
                        "schema": {"type": "string"}
                    },

                    # TODO add checker to check that the paths exists.
                    "libraryPaths": {
                        "type": "list",
                        "empty": False,
                        "schema": {"type": "string"},
                        "dependencies": {
                            "buildRule": ["exe", "dynamiclib"]
                        }
                    },

                    "libraries": {
                        "type": "list",
                        "empty": False,
                        "schema": {"type": "string"},
                        "dependencies": {
                            "buildRule": ["exe", "dynamiclib"]
                        }
                    },
                }
            }
        }
    }

    validator = cerberus.Validator()
    validator.validate(document, schema)

    # TODO: Handle schema errors.
    if validator.errors:
        raise RuntimeError(validator.errors)
