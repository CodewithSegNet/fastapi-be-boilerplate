# APPLICATION TYPES
APPLICATION_JSON = "application/json"
APPLICATION_XML = "application/xml"
APPLICATION_PDF = "application/pdf"
APPLICATION_ZIP = "application/zip"
APPLICATION_GZIP = "application/gzip"
APPLICATION_MSWORD = "application/msword"
APPLICATION_VND_MS_EXCEL = "application/vnd.ms-excel"
APPLICATION_VND_MS_POWERPOINT = "application/vnd.ms-powerpoint"
APPLICATION_OCTET_STREAM = "application/octet-stream"
APPLICATION_XHTML_XML = "application/xhtml+xml"
APPLICATION_RTF = "application/rtf"
APPLICATION_JAVASCRIPT = "application/javascript"
APPLICATION_X_WWW_FORM_URLENCODED = "application/x-www-form-urlencoded"
APPLICATION_X_SHOCKWAVE_FLASH = "application/x-shockwave-flash"

# IMAGE TYPES
IMAGE_BMP = "image/bmp"
IMAGE_GIF = "image/gif"
IMAGE_JPEG = "image/jpeg"
IMAGE_PNG = "image/png"
IMAGE_SVG_XML = "image/svg+xml"
IMAGE_TIFF = "image/tiff"
IMAGE_WEBP = "image/webp"
IMAGE_X_ICON = "image/x-icon"
IMAGE_X_MS_BMP = "image/x-ms-bmp"
IMAGE_X_PIXMAP = "image/x-xpixmap"

# AUDIO TYPES
AUDIO_MP3 = "audio/mpeg"
AUDIO_MPEG = "audio/mpeg"
AUDIO_OGG = "audio/ogg"
AUDIO_WAV = "audio/wav"
AUDIO_WEBM = "audio/webm"
AUDIO_X_AAC = "audio/x-aac"
AUDIO_X_WAV = "audio/x-wav"

# VIDEO TYPES
VIDEO_MP4 = "video/mp4"
VIDEO_MPEG = "video/mpeg"
VIDEO_OGG = "video/ogg"
VIDEO_WEBM = "video/webm"
VIDEO_X_MS_WMV = "video/x-ms-wmv"
VIDEO_X_FLV = "video/x-flv"
VIDEO_QUICKTIME = "video/quicktime"

# TEXT TYPES
TEXT_PLAIN = "text/plain"
TEXT_CSS = "text/css"
TEXT_HTML = "text/html"
TEXT_CSV = "text/csv"
TEXT_XML = "text/xml"
TEXT_JAVASCRIPT = "text/javascript"
TEXT_MARKDOWN = "text/markdown"

# FONT TYPES
FONT_TTF = "font/ttf"
FONT_WOFF = "font/woff"
FONT_WOFF2 = "font/woff2"
FONT_OTF = "font/otf"

# MULTIPATY TYPES
MULTIPART_FORM_DATA = "multipart/form-data"
MULTIPART_BYTERANGES = "multipart/byteranges"


mime_types = {
    # Application types
    "json": "application/json",
    "xml": "application/xml",
    "pdf": "application/pdf",
    "zip": "application/zip",
    "gz": "application/gzip",
    "doc": "application/msword",
    "xls": "application/vnd.ms-excel",
    "ppt": "application/vnd.ms-powerpoint",
    "bin": "application/octet-stream",
    "xhtml": "application/xhtml+xml",
    "rtf": "application/rtf",
    "js": "application/javascript",
    "urlencoded": "application/x-www-form-urlencoded",
    "swf": "application/x-shockwave-flash",

    # Image types
    "bmp": "image/bmp",
    "gif": "image/gif",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "png": "image/png",
    "svg": "image/svg+xml",
    "tiff": "image/tiff",
    "webp": "image/webp",
    "ico": "image/x-icon",
    "xbm": "image/x-xpixmap",

    # Audio types
    "mp3": "audio/mpeg",
    "mpeg": "audio/mpeg",
    "ogg": "audio/ogg",
    "wav": "audio/wav",
    "webm": "audio/webm",
    "aac": "audio/x-aac",

    # Video types
    "mp4": "video/mp4",
    "mpeg": "video/mpeg",
    "ogg": "video/ogg",
    "webm": "video/webm",
    "wmv": "video/x-ms-wmv",
    "flv": "video/x-flv",
    "mov": "video/quicktime",

    # Text types
    "txt": "text/plain",
    "css": "text/css",
    "html": "text/html",
    "csv": "text/csv",
    "xml": "text/xml",
    # "js": "text/javascript",
    "md": "text/markdown",

    # Font types
    "ttf": "font/ttf",
    "woff": "font/woff",
    "woff2": "font/woff2",
    "otf": "font/otf",

    # Multipart types
    "form": "multipart/form-data",
    "byteranges": "multipart/byteranges"
}
