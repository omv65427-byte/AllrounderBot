import os
import io
import shutil
import zipfile
import fitz  # PyMuPDF
import img2pdf
import py7zr
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes


# ---------- /compress ----------

async def compress_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.reply_to_message
    if not msg or not msg.document:
        await update.message.reply_text("Kisi file ko reply karke /compress bhejo")
        return

    doc = msg.document
    file = await doc.get_file()
    bio = io.BytesIO()
    await file.download_to_memory(bio)
    bio.seek(0)

    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(doc.file_name or "file", bio.read())
    out.seek(0)
    out.name = (doc.file_name or "file") + ".zip"
    await update.message.reply_document(out, caption="✅ Compressed")


# ---------- /decompress ----------

async def decompress_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.reply_to_message
    if not msg or not msg.document:
        await update.message.reply_text("Zip/7z file ko reply karke /decompress bhejo")
        return

    doc = msg.document
    fname = (doc.file_name or "").lower()
    file = await doc.get_file()
    bio = io.BytesIO()
    await file.download_to_memory(bio)
    bio.seek(0)

    if fname.endswith(".zip"):
        try:
            with zipfile.ZipFile(bio) as zf:
                names = zf.namelist()
                if not names:
                    await update.message.reply_text("Zip empty hai")
                    return
                for name in names:
                    if zf.getinfo(name).is_dir():
                        continue
                    data = zf.read(name)
                    out = io.BytesIO(data)
                    out.name = os.path.basename(name) or "file"
                    await update.message.reply_document(out)
        except zipfile.BadZipFile:
            await update.message.reply_text("Invalid zip file")

    elif fname.endswith(".7z"):
        tmp_dir = "/tmp/decompress_tmp"
        os.makedirs(tmp_dir, exist_ok=True)
        archive_path = os.path.join(tmp_dir, "archive.7z")
        extract_path = os.path.join(tmp_dir, "extracted")

        with open(archive_path, "wb") as f:
            f.write(bio.read())

        try:
            with py7zr.SevenZipFile(archive_path) as z:
                z.extractall(extract_path)

            for root, _, files in os.walk(extract_path):
                for fn in files:
                    full = os.path.join(root, fn)
                    with open(full, "rb") as f:
                        out = io.BytesIO(f.read())
                    out.name = fn
                    await update.message.reply_document(out)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    else:
        await update.message.reply_text("Sirf .zip aur .7z supported hai")


# ---------- /pdf2img ----------

async def pdf2img_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.reply_to_message
    if not msg or not msg.document:
        await update.message.reply_text("PDF ko reply karke /pdf2img bhejo")
        return

    doc = msg.document
    if not (doc.file_name or "").lower().endswith(".pdf"):
        await update.message.reply_text("Sirf .pdf file supported hai")
        return

    file = await doc.get_file()
    bio = io.BytesIO()
    await file.download_to_memory(bio)
    bio.seek(0)

    pdf = fitz.open(stream=bio.read(), filetype="pdf")
    if pdf.page_count == 0:
        await update.message.reply_text("PDF empty hai")
        return

    for i, page in enumerate(pdf):
        pix = page.get_pixmap()
        out = io.BytesIO(pix.tobytes("png"))
        out.name = f"page_{i + 1}.png"
        await update.message.reply_photo(out)
    pdf.close()


# ---------- /img2pdf ----------

async def img2pdf_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.reply_to_message
    if not msg or not msg.photo:
        await update.message.reply_text("Image ko reply karke /img2pdf bhejo")
        return

    photo = msg.photo[-1]
    file = await photo.get_file()
    bio = io.BytesIO()
    await file.download_to_memory(bio)
    bio.seek(0)

    pdf_bytes = img2pdf.convert(bio.read())
    out = io.BytesIO(pdf_bytes)
    out.name = "converted.pdf"
    await update.message.reply_document(out, caption="✅ PDF ready")


def register(app):
    app.add_handler(CommandHandler("compress", compress_cmd))
    app.add_handler(CommandHandler("decompress", decompress_cmd))
    app.add_handler(CommandHandler("pdf2img", pdf2img_cmd))
    app.add_handler(CommandHandler("img2pdf", img2pdf_cmd))
  
