import pypandoc
from bs4 import BeautifulSoup
def converttoHTML(filepath, filelink, types, year):
    output = pypandoc.convert_file(filepath, 'html')

    with open('test.html', 'w') as fp:
        fp.write(output)
    num_of_cards = 1
    allHtml = {}
    with open('test.html') as fp:
        soup = BeautifulSoup(fp, "lxml")
        all_card_tags = soup.find_all('h4')
        for h4 in all_card_tags:
            try:
                abstract = h4
                citation = h4.find_next("p")
                card = h4.find_next("p").find_next("p")
                full_doc = card
                doc_word_length = len(full_doc.text.split())
                if doc_word_length >= 70:
                    allHtml["card " + str(num_of_cards)] = [{"tag": str(abstract), "cite": str(citation), "cardHtml": str(abstract) + str(citation) + str(full_doc), "filepath": filelink, "dtype": types, "year": year}]
                    num_of_cards += 1
            except AttributeError as e:
                print("a card was skipped because " + str(e))
                pass
    return allHtml
