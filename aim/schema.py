import cerberus


def target_schema(document):
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

                    "srcDirs": {
                        "required": True,
                        "empty": False,
                        "type": "list",
                        "schema": {"type": "string"}
                    },

                    "includePaths": {
                        "type": "list",
                        "empty": False,
                        "schema": {"type": "string"}
                    },

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

                    "thirdPartyLibraries": {
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
