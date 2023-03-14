from toml import load as toml_load


def load_config(config):
    return toml_load(config)
