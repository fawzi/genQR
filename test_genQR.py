import unittest
import filecmp, tempfile, os
import genQR
from pyzbar.pyzbar import decode
from PIL import Image
import base32_crockford as b32


class TestGenQR(unittest.TestCase):
    def compareGenerated(self, path, overrides, qrs, nPages=1, after=0):
        with tempfile.TemporaryDirectory() as tempdirname:
            tempdirname = "/tmp"
            configPath = os.path.join(path, "config.yaml")
            genQR.doInDir(
                baseDir=tempdirname,
                configName=configPath,
                nPages=nPages,
                overrides=overrides,
                after=after,
            )
            (match, mismatch, errors) = filecmp.cmpfiles(
                tempdirname,
                path,
                [overrides["outName"] + ".tex"]
                + [
                    "{outName}Images/{baseId}-{i:0>3}.png".format(i=i, **overrides)
                    for i in qrs
                ],
            )
            startStr = "{outName}Images/{baseId}-".format(**overrides)
            for f in mismatch:
                if not f.startswith(startStr):
                    print(f, "!=", startStr)
                self.assertTrue(f.startswith(startStr))
                decodedQR1 = decode(Image.open(os.path.join(path, f)))
                decodedQR2 = decode(Image.open(os.path.join(tempdirname, f)))
                self.assertEqual(len(decodedQR1), 1)
                self.assertEqual(len(decodedQR2), 1)
                self.assertEqual(decodedQR1[0].data, decodedQR2[0].data)
            self.assertFalse(errors)

    def test_ostia_1(self):
        self.compareGenerated(
            path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "ostia"),
            overrides={"baseId": "TRA0", "outName": "TRA0"},
            qrs=range(1, 105),
            nPages=4,
        )

    def test_ostia_2(self):
        self.compareGenerated(
            path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "ostia"),
            overrides={"baseId": "TRA0", "outName": "TRA0-17"},
            qrs=range(17, 43),
            after=16,
        )

    def test_base32_1(self):
        self.compareGenerated(
            path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "base32"),
            overrides={"baseId": "00FF", "outName": "00FF"},
            qrs=[b32.encode(i) for i in range(1, 53)],
            nPages=2,
        )

    def test_base32_2(self):
        self.compareGenerated(
            path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "base32"),
            overrides={"baseId": "00FF", "outName": "00FF-00E"},
            qrs=[b32.encode(i) for i in range(14, 40)],
            after=b32.encode(13),
        )


if __name__ == "__main__":
    unittest.main()
