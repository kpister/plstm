import xml.etree.ElementTree as ET
import re
import sys
import unicodedata

def unicodeToAscii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn' and ord(c) < 128 )

class XMLDoc:
    def __init__(self, filename, tables=False):
        #self.tables = None
        self.nplcit_table = []
        self.references = ""

        self.tree = ET.parse(filename)
        self.root = self.tree.getroot()
        self.abstract_section = self.root.find('abstract')
        self.citations = self.root.find('us-bibliographic-data-grant').find('us-references-cited')
        self.data = self.root.find('description')

        # look into text ../patents/US08685992-20140401.XML 
        title = self.root.find('us-bibliographic-data-grant').find('invention-title').text
        self.title = unicodeToAscii(title)

        self.abstract = unicodeToAscii(self.parse_abstract())

        background = unicodeToAscii(self.parse_section("background"))
        summary = unicodeToAscii(self.parse_section("summary"))
        desc = unicodeToAscii(self.parse_section("description"))

        self.intro = f'{background} {summary} {desc}'
        self.whole_desc = unicodeToAscii(self.parse_section())
        #self.whole = unicodeToAscii(self.all())
        self.keywords, _ = self.keyword_section('invention', 2)
        self.keypatent, _ = self.keyword_section('patent', 2)

        #if tables:
            #self.tables = self.parse_all_tables()
        if self.citations:
            self.nplcit_table = self.parse_citations()
            self.references = '\n'.join(self.nplcit_table)


    def parse_abstract(self):
        abstract = ''
        for elem in self.abstract_section:
            if elem.tag == 'p' and elem.text != None:
                abstract += elem.text + ' '

        return abstract

    #Read XML file and collect introduction (Background)
    def parse_section(self, header=None):
        section = ''

        #Flag indicating if introduction found
        start = False #Search for 'p' section with introduction
        for elem in self.data:

            if elem.text == None:
                continue

            if header:
                #If introduction already found, exit loop
                if elem.tag == 'heading' and start:
                    break

                #Start of introduction
                elif elem.tag == 'heading' and header in elem.text.lower():
                    start = True

            #Body of introduction
            elif elem.tag == 'p' and (start or header is None) and re.search('[a-zA-Z0-9]',elem.text):
                for child in elem.iter():
                    if (child.tag in ['sub', 'sup']) and child.text != None and re.search('[a-zA-Z0-9]',child.text):
                        section += '^'+child.text+'*'
                    elif child.text != None and re.search('[a-zA-Z0-9]',child.text):
                        section += child.text + ' ' 
                        if child.text[-1] == '.':
                            section += ' '

                    if child.tail != None and re.search('[a-zA-Z0-9]',child.tail):
                        section += child.tail + ' '
            
        return section

    #Read XML file and organizes all citations into two table based on type
    def parse_citations(self):
        #Gets citations from xml file
        nplcit_table = []

        for cit in self.citations.iter('us-citation'):
            if cit[0].tag == 'nplcit' and cit[0][0].text:
                cit_name = cit[0][0].text
                if '“' in cit_name:
                    cit_name = cit_name.split('“')[1]
                if '”' in cit_name:
                    cit_name = cit_name.split('”')[0]
                    c = unicodeToAscii(cit_name)
                    nplcit_table.append(c)
                
        return nplcit_table

    #function looks for keyword in sections. If keyword encountered, collects the next n sentences
    # defined by num_sentences 
    def keyword_section(self, keyword, num_sentences):
        def extract_keywords(text):
            sentences = ''
            text = text.split('.')
            for s in text:
                if keyword in s and s not in sentences:
                    num_collected = 0
                    index = text.index(s) - 2
                    while(index < len(text) and num_collected < num_sentences*2):
                        if index >= 0:
                            sentences += text[index]
                        num_collected += 1
                        index += 1
            return sentences

        desc = whole = ""
        if self.whole_desc:
            desc = extract_keywords(self.whole_desc)

        #if self.whole:
            #whole = extract_keywords(self.whole)
        return (desc, whole)



if __name__ == '__main__':
    try:
        filename = sys.argv[1]
        doc = XMLDoc(filename, intro=True, citations=True)
        print(doc.keywords)
    except Exception as e:
        print(e)
        print('Usage: python parse_patent.py patent_file.xml')

