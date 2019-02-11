import xml.etree.ElementTree as ET
import re
import sys

class XMLDoc:
    def __init__(self, filename, title=False, abstract=False, intro=False, tables=False, citations=False):
        self.title = ""
        self.intro = self.abstract = ""
        self.tables = None
        self.nplcit_table = []

        self.tree = ET.parse(filename)
        self.root = self.tree.getroot()
        self.abstract_section = self.root.find('abstract')
        self.citations = self.root.find('us-bibliographic-data-grant').find('us-references-cited')
        self.data = self.root.find('description')

        if title:
            # look into text ../patents/US08685992-20140401.XML 
            self.title = self.root.find('us-bibliographic-data-grant').find('invention-title').text
        if abstract:
            self.abstract = self.parse_abstract()
        if intro:
            self.intro = self.parse_section("background")
            self.summary = self.parse_section("summary")
            self.desc = self.parse_section("description")
            self.intro = f'{self.intro} {self.summary} {self.desc}'
            self.intro = re.sub(r'\s\([a-zA-Z,.\s&]*\s*\d{4}[\)]','',self.intro)
        if tables:
            self.tables = self.parse_all_tables()
        if citations and self.citations:
            self.nplcit_table = self.parse_citations()


    def parse_abstract(self):
        abstract = ''
        for elem in self.abstract_section:
            if elem.tag == 'p' and elem.text != None:
                abstract += elem.text

        return abstract

    #Read XML file and collect introduction (Background)
    def parse_section(self, header):
        section = ''

        #Flag indicating if introduction found
        start = False #Search for 'p' section with introduction
        for elem in self.data:

            #If introduction already found, exit loop
            if elem.tag == 'heading' and start:
                break

            elif elem.text == None:
                continue

            #Start of introduction
            elif elem.tag == 'heading' and header in elem.text.lower():
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

