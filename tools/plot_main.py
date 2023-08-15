import yaml
import logging
import argparse

from pyoctal.util.plot import PlotGraphs
from pyoctal.util.util import setup_rootlogger
from pyoctal.util.formatter import CustomArgparseFormatter

LOG_FNAME = "./logging.log"
root_logger = logging.getLogger()
setup_rootlogger(root_logger, LOG_FNAME)
logger = logging.getLogger(__name__)


def main():

    parser = argparse.ArgumentParser(
        description="Plotting data",
        formatter_class=CustomArgparseFormatter)
    parser.add_argument(
        "--config",
        dest="config",
        metavar="",
        nargs=1,
        type=str,
        help="Path to a configuration file.",
        required=False,
        default=("./configs/plot_config.yaml",)
    )

    args = parser.parse_args()

    with open(file=args.config[0], mode='r') as file:
        configs = yaml.safe_load(file)

    

    folders = [", ".join(configs["folders"])] if (len(configs["folders"]) > 1) else configs["folders"][0]
    logger.info("--------------------------------------")
    logger.info(f'{"Folders":10}: {folders}')
    logger.info(f'{"Filename":10}: {configs["fname"]}')
    logger.info(f'{"Function":10}: {configs["func"]}')
    logger.info("--------------------------------------")

    plot = PlotGraphs(configs)

    func = getattr(plot, configs["func"])
    func()
    
    plot.show()


if __name__ == "__main__":
    main()

    
    