import cerberus


def target_schema(document):
    # TODO add empty: False

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

                    "requires": {
                        "type": "list",
                        "schema": {"type": "string"}
                    },

                    "srcDirs": {
                        "required": True,
                        "type": "list",
                        "schema": {"type": "string"}
                    },

                    "includePaths": {
                        "type": "list",
                        "schema": {"type": "string"}
                    },

                    "libraryPaths": {
                        "type": "list",
                        "schema": {"type": "string"},
                        "dependencies": {
                            "buildRule": ["exe", "dynamiclib"]
                        }
                    },

                    "libraries": {
                        "type": "list",
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
