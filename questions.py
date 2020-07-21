import nltk
import sys
import os
import math
import wikipedia
from nltk.stem import WordNetLemmatizer
from string import punctuation as PUNCTUATION
import nltk
nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()
STOP_WORDS = ['i','me','my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
FILE_MATCHES = 1
SENTENCE_MATCHES = 2

def process_input(user_input):
    query = set(tokenize(user_input))
    for w in query.copy():
        query.add(lemmatizer.lemmatize(w))
    if not query:
        return None, None
    result_ls = wikipedia.search(user_input, results=3)
    result_ls +=  wikipedia.search(query, results=3)
    result_ls = [ri for ri in result_ls if (not ri.startswith("List"))]
    if result_ls:
        return query,result_ls
    return None, None

def load_files(result_ls):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    content = {}
    for ri in result_ls:
        try:
            pgi = wikipedia.page(ri)
            content[ri] = pgi.content
        except wikipedia.DisambiguationError as e:
            continue
        except wikipedia.exceptions.DisambiguationError as e:
            continue
        except wikipedia.exceptions.PageError as e:
            continue
        except wikipedia.exceptions.WikipediaException as e:
            continue
    return content

def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.
    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    return [ w.lower() for w in nltk.word_tokenize(document)
                    if (w.lower() not in STOP_WORDS) and (w not in PUNCTUATION) ]

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.
    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    result = {}
    n_documents = len(documents)
    for doc_i, word_list_i in documents.items():
        for w_i in word_list_i:
            if w_i not in result:
                n_docs_appears = 0
                for doc, word_list in documents.items():
                    if w_i in word_list:
                        n_docs_appears += 1
                    # counter += word_list.count(w_i)
                result[w_i] = math.log(n_documents/n_docs_appears)
    return result

def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    result = {}
    # Calculate TF-IDF for every file and the given query
    for f in files:
        tfidf = sum( (idfs[w]*files[f].count(w)) for w in query if (w in files[f])  )
        result[f] = tfidf

    # Sort dictionary result
    result = {k: v for k, v in sorted(result.items(), key=lambda item: item[1], reverse=True)}
    # for f in list(result)[:n]:
    #     print("\n\t* From page: \"",f,"\"")
    return list(result)[:n]

def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    result = {}
    for s in sentences:
        idf = sum( idfs[w] for w in query if (w in sentences[s])  )
        result[s] = idf
    # Remove sentences with idf=0
    result = {k: v for k, v in result.items() if v!=0.0}
    first_n = list(result)

    # Use Insertion Sort to sort by IDF and resolve ties using Query Term Density
    for i in range(1, len(first_n)):
        key = result[first_n[i]]
        key_s = first_n[i]
        j = i-1
        while j >= 0 and result[first_n[j]]<=key:
            if result[first_n[j]]==key:
                j_density = len(list(set(sentences[first_n[j]]) & query)) / len(sentences[first_n[j]])
                k_density = len(list(set(sentences[  key_s]   ) & query)) / len(sentences[  key_s]   )
                if j_density >= k_density:
                    break
            first_n[j + 1] = first_n[j]
            j -= 1
        first_n[j + 1] = key_s
    return first_n[:n]
