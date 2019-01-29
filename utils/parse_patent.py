import xml.etree.ElementTree as ET
import re
import sys

class XMLDoc:
    def __init__(self, filename, intro=False, tables=False, citations=False):
        self.intro = self.summary = ""
        self.tables = None
        self.patcit_table = self.nplcit_table = []

        self.tree = ET.parse(filename)
        self.root = self.tree.getroot()
        self.citations = self.root.find('us-bibliographic-data-grant').find('us-references-cited')
        self.data = self.root.find('description')

        self.f = self.parse_section("field of invention")
        self.f = re.sub(r'\s\([a-zA-Z,.\s&]*\s*\d{4}[\)]','',self.f)
        if intro:
            self.intro = self.parse_section("background")
            self.intro = re.sub(r'\s\([a-zA-Z,.\s&]*\s*\d{4}[\)]','',self.intro)
            self.summary = self.parse_section("summary")
            self.summary = re.sub(r'\s\([a-zA-Z,.\s&]*\s*\d{4}[\)]','',self.summary)
        if tables:
            self.tables = self.parse_all_tables()
        if citations and self.citations:
            self.nplcit_table = self.parse_citations()


    #Read XML file and collect introduction (Background)
    def parse_section(self, header):
        section = ''

        #Flag indicating if introduction found
        start = False #Search for 'p' section with introduction
        for elem in self.data:

            if elem.text == None:
                continue

            #Start of introduction
            if elem.tag == 'heading' and header in elem.text.lower():
                start = True
            
            #Body of introduction
            elif elem.tag == 'p' and start and re.search('[a-zA-Z0-9]',elem.text):
                for child in elem.iter():
                    if (child.tag in ['sub', 'sup']) and child.text != None and re.search('[a-zA-Z0-9]',child.text):
                        section += '^'+child.text+'*'
                    elif child.text != None and re.search('[a-zA-Z0-9]',child.text):
                        section += child.text
                        if child.text[-1] == '.':
                            section += ' '

                    if child.tail != None and re.search('[a-zA-Z0-9]',child.tail):
                        section += child.tail
            
            #If introduction already found, exit loop
            elif elem.tag == 'heading' and start:
                break

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
                    nplcit_table.append(cit_name)
                
        return nplcit_table

if __name__ == '__main__':
    try:
        filename = sys.argv[1]
        doc = XMLDoc(filename, intro=True, citations=True)
        print(doc.intro)
        print("\n".join(doc.nplcit_table))
    except:
        print('Usage: python parse_patent.py patent_file.xml')

