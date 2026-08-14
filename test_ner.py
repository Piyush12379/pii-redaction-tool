import spacy


nlp = spacy.load("en_core_web_sm")


text = """
Sarthak Malvadkar is the Company Secretary of KSH International Limited.
Kushal Subbayya Hegde is one of the promoters.
The company is based in Pune.
"""


doc = nlp(text)


for entity in doc.ents:
    print(entity.text, "->", entity.label_)

