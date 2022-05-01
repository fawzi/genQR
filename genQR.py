import qrcode.main
from string import Template
from io import open
import os, os.path

latexPre=Template(r"""
\documentclass[12pt,a4paper,oneside]{memoir}
\usepackage{graphicx}
\usepackage{geometry}
\geometry{a4paper, margin=1cm,
  marginparwidth=0cm,
  marginpar=0cm
}
\graphicspath{ {${baseId}Images/} }
\begin{document}
\pagestyle{empty}
""")

latexPage=r"""
\begin{tabular}{l p{1.2cm} r}
\begin{tabular}{cc}
"""

singleEl=Template(r"""
      \hline
      \raisebox{-0.75\height}{\includegraphics[width=2cm]{${fullId}.png}} & \parbox[t]{5.2cm}{
        {\small http://ostiaforumproject.com/} \\ 2017/
        \vspace{-0.4cm}\begin{flushright} {\Large ${fullId}} \end{flushright}} \\
""")

split=r"""
      \hline
\end{tabular}
&
&
\begin{tabular}{cc}
"""

endPage=r"""
      \hline
\end{tabular}
\end{tabular}
"""

endDoc=r"""
\end{document}
"""

def emit(baseId, nPages=1, baseDir=".", startNr=1):
    """emits nPages of QR codes starting of baseId with number startNr"""
    outFName=os.path.join(baseDir, baseId + ".tex")
    qrDirName=os.path.join(baseDir, baseId + "Images")
    if not os.path.exists(qrDirName):
        os.makedirs(qrDirName)
    with open(outFName, "w", encoding="utf-8") as outF:
        outF.write(latexPre.substitute(baseId=baseId))
        ii = startNr - 1
        for iPage in range(nPages):
            outF.write(latexPage)
            for icol in range(2):
                for i in range(13):
                    ii += 1
                    fullId = ("%s-%03d" % (baseId, ii))
                    qrCode = qrcode.main.QRCode()
                    qrCode.add_data("http://ostiaforumproject.com/2017/" + fullId)
                    qrCode.make()
                    img=qrCode.make_image()
                    img.save(os.path.join(qrDirName, fullId + ".png"))
                    outF.write(singleEl.substitute(fullId=fullId))
                if icol == 0:
                    outF.write(split)
            outF.write(endPage)
        outF.write(endDoc)

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Emits qrcodes identifiers and latex document to print them easily.')
    parser.add_argument("baseId", help="base identifier")
    parser.add_argument("--n-pages", type=int, default=1, metavar='N')
    args = parser.parse_args()

    emit(args.baseId, nPages=args.n_pages)
