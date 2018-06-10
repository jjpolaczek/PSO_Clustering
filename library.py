from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
import os
import logging
import zipfile
import io
import pickle
logger = logging.getLogger(__name__)


class AuthorsParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.bookListParsing=False
        self.bookLine=False
        self.currentAuthor=None
        self.currentTitle=None
        self.currentPath=None
        self.currentLanguage=None
        self.bookList = []


    def handle_starttag(self, tag, attrs):
        #print "Start tag:", tag
        if tag=="h3" and self.bookListParsing == True:
            self.currentAuthor = True
            self.currentTitle = None
            self.currentPath = None
            self.currentLanguage = None
        if tag=="li" and self.bookListParsing ==True:
            self.bookLine=True
        if tag == "a" and self.bookLine:
            self.currentTitle = True
        for attr in attrs:
            #print "     attr:", attr
            if tag == "div":
                if attr[0] == 'class' and attr[1] == 'list':
                    self.bookListParsing = True
                    logger.debug("Start authors parsing")

            if tag == "a" and self.bookLine:
                if attr[0]=='href':
                    self.currentPath=attr[1]

    def handle_endtag(self, tag):
       # print "End tag  :", tag
        if tag == "div" and self.bookListParsing == True:
            self.bookListParsing = False
            logger.debug("End authors parsing")

        if tag=="li" and self.bookLine == True:
            self.bookLine=False
            book_tmp = Book(self.currentTitle, self.currentAuthor, self.currentLanguage, self.currentPath)
            if book_tmp.language==True:
                book_tmp.language="None"
            self.bookList.append(book_tmp)
            logger.debug("Book info \n%s",book_tmp)
            self.currentTitle = None
            self.currentPath = None
            self.currentLanguage = None

        if tag=="a" and self.currentTitle is not None and self.currentLanguage is None:
            self.currentLanguage=True


    def handle_data(self, data):
       # print "Data     :", data
        if self.currentAuthor == True:
            self.currentAuthor = data

        if self.currentTitle == True:
            self.currentTitle = data

        if self.currentLanguage == True:
            self.currentLanguage = data.strip('()')

class BookParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.bookListParsing=False
        self.currentType=None
        self.currentCharset=None
        self.currentPath=None
        self.subjectList=[]
        self.subjectParsing=0
        self.fileList=[]

    def handle_starttag(self, tag, attrs):

        if tag == 'td' and self.subjectParsing == 1:
            self.subjectParsing = 2
        if self.bookListParsing:
            #print "Start tag:", tag
            if tag=='td' and self.currentCharset is None:
                #print "Charset tag detected"
                self.currentCharset=True

            if tag=='a':
                # reset if this is a <td> for file path
                #print "RESET charset"
                if self.currentCharset == True:
                    self.currentCharset = None
            for attr in attrs:
                if tag=='a' and attr[0]=='href':
                    self.currentPath=attr[1]
                    self.fileList.append(BookFile(self.currentType, self.currentCharset, self.currentPath))
                    self.currentType=None
                    self.currentCharset=None
                    self.currentPath=None


                #print "     attr:", attr

    def handle_endtag(self, tag):
        if tag=='table' and self.bookListParsing ==True:
            self.bookListParsing=False

        if self.bookListParsing:
            pass
            #print "End tag  :", tag

    def handle_data(self, data):
        if self.subjectParsing == 2:
            self.subjectList.append(data)
            self.subjectParsing = 0

        if data == "Subject":
            self.subjectParsing = 1

        if data == 'EBook Files':
            self.bookListParsing = True

        if self.bookListParsing:
            #print "Data     :", data
            if self.currentCharset == True:
                #print "CHARSET Parsing"
                tmp = data.split(';')
                #print tmp
                self.currentType = tmp[0]
                if len(tmp) == 2:
                    self.currentCharset = tmp[1].split('=')[1].strip("\"")
                else:
                    self.currentCharset = "None"


bannedEncodings=['MS Lit for PocketPC (lit)','Finale (mus)', 'macintosh', 'LilyPond (ly)', 'TeX (tex)', 'x-other']

class BookFile:

    def __init__(self, type, charset,path):
        self.type=type
        self.charset=charset
        self.path=path

    def __str__(self):
        return "Type: %s\nCharset: %s\nPath: %s" % (self.type, self.charset, self.path)


class Book:

    def __init__(self, title=None, author=None, language=None, path=None, subject=[]):
        self.author=author
        self.title=title
        self.language=language
        self.path=path
        self.subject=subject
        self.zipList=None
        self.contentValid=None

    def description(self):
        return "Title: %s\nAuthor: %s\nLanguage: %s\n Subject: %s\nPath: %s" % ( self.author, self.title, self.language, self.subject, self.path)
    def __str__(self):
        return self.getText()
    def lower(self):
        return self.getText().lower()

    def getText(self):
        fileToOpen=None
        for file in self.zipList:
            if file.type=='text/plain' and file.charset not in bannedEncodings:
                fileToOpen=file
                break
        if fileToOpen is None:
            logger.warn("Returning empty string on book %s - no suitable file format", self.path)
            self.contentValid=False
            return ""

        try:
            with zipfile.ZipFile(fileToOpen.path) as zfile:
                if len(zfile.namelist()) != 1:
                    txtCnt=0
                    for name in zfile.namelist():
                        filename, file_extension = os.path.splitext(name)
                        if file_extension.lower()=='.txt':
                            txtCnt+=1
                    if txtCnt != 1:
                        logger.warn("Unexpected zip contents %s", fileToOpen.path)
                        logger.warn("Contents %s", str(zfile.namelist()))
                        raise zipfile.BadZipfile("Invalid file contents")

                for name in zfile.namelist():
                    filename, file_extension = os.path.splitext(name)
                    if file_extension.lower()=='.txt':
                        with zfile.open(name) as readfile:
                            if fileToOpen.charset=='None':
                                logger.debug("Opening file %s with None encoding", fileToOpen.path)
                                self.contentValid = True
                                strTmp = readfile.read()
                                #go for unicode format
                                if isinstance(strTmp, str):
                                    strTmp = unicode(strTmp, errors='ignore')
                                return strTmp
                            else:
                                logger.debug("Using encoding %s", fileToOpen.charset)
                                logger.debug("Opening file %s with %s encoding", fileToOpen.path, fileToOpen.charset)
                                try:
                                    self.contentValid = True
                                    return io.TextIOWrapper(readfile, encoding=fileToOpen.charset, errors='replace').read()

                                except UnicodeDecodeError as e:
                                    logger.debug("Could not decode file %s in %s encoding", fileToOpen.path, fileToOpen.charset)
                                    logger.debug("Exception: %s", str(e))
                                    if fileToOpen.charset=='us-ascii':
                                        logger.debug("Retrying with no encoding for us-ascii")
                                        self.contentValid=True
                                        return readfile.read()
                                    else:
                                        logger.warn("Giving up on file, cannot decode %s", fileToOpen.path)

        except NotImplementedError as e:

            logger.warn("Cannot open %s", fileToOpen.path)
            logger.warn("%s", str(e))
            logger.warn("%s", file_extension)

        except zipfile.BadZipfile as e:
            filename, file_extension = os.path.splitext(fileToOpen.path)
            if file_extension.lower() != '.txt':
                        logger.warn("Cannot open %s", fileToOpen.path)
                        logger.warn("%s", str(e))
            else:
                logger.debug("Recovering - found text file %s instead of zip", fileToOpen.path)
                if fileToOpen.charset == 'None':
                    with io.open(fileToOpen.path) as readfile:
                        logger.debug("Opening file %s with None encoding", fileToOpen.path)
                        self.contentValid = True
                        strTmp = readfile.read()
                        if isinstance(strTmp, str):
                            strTmp = unicode(strTmp, errors='ignore')
                        return strTmp
                else:
                    logger.debug("Using encoding %s", fileToOpen.charset)
                    logger.debug("Opening file %s with %s encoding", fileToOpen.path, fileToOpen.charset)
                    with io.open(fileToOpen.path, "r",encoding=fileToOpen.charset, errors='replace') as readfile:
                        self.contentValid=True
                        return readfile.read()

        self.contentValid=False
        return ""

class Library:
    def __init__(self, pathToBooks, forceReload=False):
        self.libPath=pathToBooks
        self.bookList=None
        self.tmpListFile="libListing.pickle"
        if forceReload==True or not os.path.exists(self.tmpListFile):
            self._loadBooks()
            self._validateLibrary()
            with open(self.tmpListFile, 'wb') as f:
                logger.info("Pickling library listing into %s", self.tmpListFile)
                pickle.dump(self.bookList, f, pickle.HIGHEST_PROTOCOL)
        else:
            logger.info("Loading existing file %s", self.tmpListFile)
            with open(self.tmpListFile, 'rb') as f:
                self.bookList = pickle.load(f)

        logger.info("Loaded %d books", len(self.bookList))
    def _loadBooks(self):
        indices = os.listdir(self.libPath)
        indices_author = [a for a in indices if "AUTHORS" in a.upper()]
        indices_lang = [a for a in indices if "LANGUAGE" in a.upper()]
        indices_subj = [a for a in indices if "SUBJECTS" in a.upper()]

        parser = AuthorsParser()
        # Parse individual leter indices
        for ind in indices_author:
            logger.info("Parsing %s", ind)
            path = os.path.join(self.libPath, ind)
            with open(path, "r") as fp:
                parser.feed(fp.read())

        logger.info("Found %d books", len(parser.bookList))

        tmpBookList = parser.bookList
        self.bookList = []
        bookCnt = 0
        for b in tmpBookList:
            # resolve book html path
            b.path = os.path.abspath(os.path.join(self.libPath, b.path))
            # resolve book references
            parser = BookParser()
            # Parse the html file
            with open(b.path, "r") as fp:
                parser.feed(fp.read())
            b.zipList = parser.fileList
            b.subject = parser.subjectList
            for f in b.zipList:
                f.path = os.path.abspath(os.path.join(self.libPath, f.path))

            # filter out music files and files not containing text data
            # filter takes text/plain files
            hasTextFile=False
            hasInvalidFile=False
            for f in b.zipList:
                if f.type=='text/plain' and f.charset not in bannedEncodings:
                    hasTextFile=True
                elif 'audio' in f.type or 'application' in f.type:
                    hasInvalidFile=True
                    logger.debug("Incompatible type %s, path %s", f.type, b.path)
                else:
                    logger.debug("Other type %s, path %s", f.type, b.path)
            if hasTextFile and not hasInvalidFile:
                bookCnt+=1
                self.bookList.append(b)

        logger.info("Found %d book files", bookCnt)

    def _validateLibrary(self):
        tmpBooklist=[]
        for b in self.bookList:
            b.getText()
            if b.contentValid:
                tmpBooklist.append(b)
        logger.info("Dropped %d books due to invalid file content", len(self.bookList) - len(tmpBooklist))
        self.bookList=tmpBooklist
    @staticmethod
    def checkBookFolder(path):
        return os.path.isdir(path)
#Can accept a list of languages or asingle language
    def filterBooks(self, language=None, onlyWithSubject=False):
        filteredList=[]
        if language is None:
            return filteredList
        elif isinstance(language, basestring):
            language=[language]
        for b in self.bookList:
            for lang in language:
                if lang in b.language:
                    if onlyWithSubject and len(b.subject) == 0:
                        continue
                    else:
                        filteredList.append(b)

        return filteredList
