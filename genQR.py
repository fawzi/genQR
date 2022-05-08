import qrcode.main
from string import Template
from io import open
import os, os.path, sys
import base32_crockford as b32
import yaml


def doInDir(baseDir=".", nPages=1, after=0, configName="config.yaml", overrides={}):
    configPath = os.path.join(baseDir, configName)
    try:
        with open(configPath) as f:
            config = yaml.safe_load(f)
    except:
        raise Exception(
            "Failed to find a valid configuration at ${configPath}".format(
                configPath=os.path.abspath(configPath)
            )
        )
    config.update(overrides)
    startNr = 0
    if isinstance(after, int):
        startNr = after + 1
    elif after != "-1":
        if config["base32"]:
            startNr = b32.decode(after)
        else:
            startNr = int(after)
        startNr += 1
    templates = {
        "latexPre": Template(config["latexPre"]),
        "singleEl": Template(config["singleEl"]),
    }
    return emit(config, templates, nPages=nPages, baseDir=baseDir, startNr=startNr)


def emit(config, templates, nPages=1, baseDir=".", startNr=1):
    """emits nPages of QR codes starting of baseId with number startNr"""
    outBase = config["outName"]
    outFName = os.path.join(baseDir, outBase + ".tex")
    qrDirName = os.path.join(baseDir, outBase + "Images")
    if not os.path.exists(qrDirName):
        os.makedirs(qrDirName)
    with open(outFName, "w", encoding="utf-8") as outF:
        outF.write(templates["latexPre"].substitute(**config))
        ii = startNr - 1
        for iPage in range(nPages):
            outF.write(config["latexPage"])
            for icol in range(config["nCol"]):
                for i in range(config["nRow"]):
                    ii += 1
                    if config["base32"]:
                        counterId = b32.encode(ii)
                    else:
                        counterId = str(ii)
                    fullId = (
                        config["baseId"]
                        + config["spacer"]
                        + counterId.rjust(config["nDigits"], "0")
                    )
                    qrCode = qrcode.main.QRCode()
                    qrCode.add_data(config["baseUri"] + fullId)
                    qrCode.make()
                    img = qrCode.make_image()
                    img.save(os.path.join(qrDirName, fullId + ".png"))
                    outF.write(templates["singleEl"].substitute(fullId=fullId))
                if icol == 0:
                    outF.write(config["split"])
            outF.write(config["endPage"])
        outF.write(config["endDoc"])
    return outFName


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Emits qrcodes identifiers and latex document to print them easily."
    )
    parser.add_argument("--base-id", help="base identifier")
    parser.add_argument(
        "--out-name",
        help="base name of the out file and directory (defaults to the base-id)",
    )
    parser.add_argument(
        "--n-pages", type=int, help="number of pages to print", default=1, metavar="N"
    )
    parser.add_argument(
        "--after",
        help="The number/base32 code to start after (defaults to 0, and thus starts with 1, set to -1 to start from 0)",
        default="0",
        metavar="N",
    )
    parser.add_argument(
        "--config",
        help="name of the config file (defaults to config.yaml)",
        default="config.yaml",
    )
    parser.add_argument(
        "--base-directory",
        help="directory in which to output the latex and qr codes, and look for the config (if not directly given)",
        default=".",
    )
    args = parser.parse_args()

    overrides = {
        "outName": args.out_name
        if args.out_name
        else (args.base_id if args.base_id else "qr")
    }
    if args.base_id:
        overrides["baseId"] = args.base_id
    startNr = 0
    targetLatex = doInDir(
        baseDir=args.base_directory,
        nPages=args.n_pages,
        after=args.after,
        overrides=overrides,
    )
    (dir, latexFile) = os.path.split(targetLatex)
    sys.stdout.write(
        """generated {latexFile}, for the pdf execute:
    cd {dir!r}
    pdflatex {latexFile!r}
""".format(
            dir=dir, latexFile=latexFile
        )
    )
