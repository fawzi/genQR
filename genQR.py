import qrcode.main
from string import Template
from io import open
import os, os.path
import base32_crockford as b32
import yaml

def doWithConfig(config, nPages=1, baseDir=".", startNr=1):
    templates = {
        "latexPre": Template(config["latexPre"]),
        "singleEl": Template(config["singleEl"])
    }
    emit(config, templates, nPages=nPages, baseDir=baseDir, startNr=startNr)

def emit(config, templates, nPages=1, baseDir=".", startNr=1):
    """emits nPages of QR codes starting of baseId with number startNr"""
    outBase = config["outName"]
    outFName=os.path.join(baseDir, outBase + ".tex")
    qrDirName=os.path.join(baseDir, outBase + "Images")
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
                        countedId = b32.encode(ii)
                    else:
                        counterId = str(ii)
                    fullId = config["baseId"] + config["spacer"] + counterId.rjust(config['nDigits'], "0")
                    qrCode = qrcode.main.QRCode()
                    qrCode.add_data(config["baseUri"] + fullId)
                    qrCode.make()
                    img=qrCode.make_image()
                    img.save(os.path.join(qrDirName, fullId + ".png"))
                    outF.write(templates["singleEl"].substitute(fullId=fullId))
                if icol == 0:
                    outF.write(config["split"])
            outF.write(config["endPage"])
        outF.write(config["endDoc"])

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Emits qrcodes identifiers and latex document to print them easily.')
    parser.add_argument("--base-id", help="base identifier")
    parser.add_argument("--out-name", help="base name of the out file and directory (defaults to the base-id)")
    parser.add_argument("--n-pages", type=int, help="number of pages to print", default=1, metavar='N')
    parser.add_argument("--after", help="The number/base32 code to start after (defaults to 0, and thus starts with 1, set to -1 to start from 0)"default="0", metavar='N')
    parser.add_argument("--config", default="config.yaml", metavar='N')
    parser.add_argument("--out-directory", help="directory in which to output the latex and qr codes", default=".")
    args = parser.parse_args()

    try:
        config = yaml.safe_load(open(args.config))
    except:
        import traceback, sys
        print("Failed to get the configuration", args.config)
        traceback.print_exc()
        sys.exit(1)
    config["baseId"] = args.base_id
    config["outName"] = args.out_name if args.out_name else (args.base_id if args.base_id else "qr")
    startNr = 0;
    if args.after != "-1":
        if config["base32"]:
            startNr = b32.decode(args.after)
        else:
            startNr = int(args.after)
        startNr += 1
    print(config);
    doWithConfig(config, nPages=args.n_pages, startNr = startNr)

if false:
    # tests
    import filecmp
    doWithConfig(ostia)
