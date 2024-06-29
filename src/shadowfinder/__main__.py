from cli import ShadowFinderCli
import fire


def main_entrypoint():
    fire.Fire(ShadowFinderCli)


if __name__ == "__main__":
    main_entrypoint()
