import fitz

doc = fitz.open("calculadora/static/calculadora/docs/instructivo.pdf")
print("Paginas:", len(doc))
for i, page in enumerate(doc):
    imgs = page.get_images()
    print("Pagina %d - %d imagenes" % (i+1, len(imgs)))
    for img in imgs:
        xref = img[0]
        info = doc.extract_image(xref)
        w = info["width"]
        h = info["height"]
        ext = info["ext"]
        sz = len(info["image"])
        print("  xref=%d size=%dx%d ext=%s bytes=%d" % (xref, w, h, ext, sz))
