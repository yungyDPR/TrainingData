import grobid_xml_checker

import click


@click.group()
def group():
    """
    CLI for validating XML files with an XSD
    """


@group.command("validate")
@click.argument("rootdir", type=str)
@click.argument("xsddir", type=str)
@click.argument("logdir", type=str)
def run(rootdir, xsddir, logdir):
    """
    Validate an XML if a root directory is provided.
    """
    grobid_xml_checker.validate_with_xsd(rootdir, xsddir, logdir)


if __name__ == "__main__":
    group()
