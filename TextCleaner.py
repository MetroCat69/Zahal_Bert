import re
from typing import List

import pandas as pd
import os


def read_text_file_and_convert_to_list(file_name) -> List[str]:
    with open(file_name, 'r', encoding="utf8") as f:
        contents = f.read()
        split_content: List[str] = contents.split(';')
        split_content.pop()
        return split_content

def delete_files_with_substring(directory, substring):
    for filename in os.listdir(directory):
        if filename.endswith(".txt") and substring in filename:
            file_path = os.path.join(directory, filename)
            os.remove(file_path)
            print(f"Deleted file: {filename}")

def delete_files_with_small_size(directory, size_threshold):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and os.path.getsize(file_path) < size_threshold:
            os.remove(file_path)
            print(f"Deleted file: {filename}")
import os

def combine_text_files(directory):
    combined_text = ""

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            with open(file_path, "r", encoding="utf8") as file:
                file_content = file.read()
                combined_text += file_content + "<file_sep>"

    combined_text = combined_text.rstrip("<file_sep>")

    output_file_path = os.path.join(directory, "combined_files.txt")
    with open(output_file_path, "w", encoding="utf8") as output_file:
        output_file.write(combined_text)

    print(f"Combined files saved to: {output_file_path}")

class TextCleaner:
    """
    text cleaner class
    each page must complete all of the following conditions:
        at least x words per page
        at least x setences per page
        no word can have more that x chars
        if n sentences =<7:

            number of ok sentences> 2*number of suspected short sentences
        else:
            number of ok sentences> 4*number of suspected short sentences
        only hebrew and english charaters

        TODO:
            - no java script
            - no html
    """

    def __init__(
            self,
            separators_path='defult_seperators.txt',
            stopwords_path='stopwords',
            min_words_per_page=8,
            min_words_per_sentence_to_be_suspected_short_sentences=3,
            min_num_sentences=3,
            max_word_length=30

    ):
        self.separators = read_text_file_and_convert_to_list(separators_path)
        self.stuff_to_remove = read_text_file_and_convert_to_list(stopwords_path)
        self.min_words_per_page = min_words_per_page
        self.min_words_per_sentence_to_be_suspected_short_sentences = min_words_per_sentence_to_be_suspected_short_sentences
        self.min_num_sentences = min_num_sentences
        self.max_word_length = max_word_length

    @staticmethod
    def _split_by_page(txt):
        pattern = "".join(re.escape('<next_page>'))
        splitted_text_list = re.split(pattern, txt)
        return splitted_text_list

    def _split_sentences(self, txt):
        pattern = "|".join(re.escape(seq) for seq in self.separators)
        splitted_text_list = re.split(pattern, txt)
        return splitted_text_list

    @staticmethod
    def _filter_hebrew_only(txt):
        filtered_text = ''.join([char for char in txt if
                                 ('\u0590' <= char <= '\u05FF') or ('\u0020' <= char <= '\u007F') or char in ['\n',
                                                                                                              '\t']])
        return filtered_text

    def _remove_stopwords_words(self, txt):
        for stuff in self.stuff_to_remove:
            txt = txt.replace(stuff, " ")
        return txt

    def _check_page(self, txt):
        txt = self._remove_stopwords_words(txt)
        senteces_df = pd.DataFrame({'text': self._split_sentences(txt)})
        senteces_df = senteces_df.loc[(senteces_df['text'] is not None) & (senteces_df['text'] != '')]
        n_sentences_in_page = len(senteces_df)
        if n_sentences_in_page <= self.min_num_sentences:
            return ''
        pattern = "|".join(re.escape(seq) for seq in ["\t", "\n", " ", ",", "."])
        senteces_df['splitted'] = senteces_df['text'].map(lambda x: re.split(pattern, x))
        senteces_df['splitted'] = senteces_df['splitted'].map(lambda x: [y for y in x if y not in ['', ' ', '.', ',']])
        senteces_df['len'] = senteces_df['splitted'].map(lambda x: len(x))
        n_words_in_page = senteces_df['len'].sum()
        if n_words_in_page <= self.min_words_per_page:
            return ''
        # display(senteces_df )
        n_sentence_to_be_suspected_short_sentences_in_page = len(
            senteces_df.loc[senteces_df['len'] <= self.min_words_per_sentence_to_be_suspected_short_sentences])
        if n_sentences_in_page <= 7:
            if 2 * n_sentence_to_be_suspected_short_sentences_in_page >= n_sentences_in_page:
                return ''
        else:
            if 2.5 * n_sentence_to_be_suspected_short_sentences_in_page >= n_sentences_in_page:
                return ''
        senteces_with_words_df = senteces_df.loc[senteces_df['len'] > 0].copy()
        if len(senteces_with_words_df) > 0:
            senteces_with_words_df['max_word_length'] = senteces_with_words_df['splitted'].map(lambda x: max([len(y) for y in x]))
        if senteces_with_words_df['max_word_length'].max() > self.max_word_length:
            return ''
        return txt

    def clean_text(self, txt):
        txt = self._filter_hebrew_only(txt)
        pages_df = pd.DataFrame({'text': self._split_by_page(txt)})
        pages_df['cleaned'] = pages_df['text'].map(lambda x: self._check_page(x))
        cleaned_txt = "".join(pages_df['cleaned'].values.tolist())
        cleaned_txt = self._remove_stopwords_words(cleaned_txt)
        return cleaned_txt


if __name__ == '__main__':
    Cleaner = TextCleaner()
    folder_path = r'C:\Users\MetroCat1\Desktop\learn_programing\genersting percy jaskson\neww'
    for root, dirs, input_file_names in os.walk(folder_path):
        for input_file_name in input_file_names:
            if input_file_name.endswith(".txt"):
                input_file_path = os.path.join(root, input_file_name)
                with open(input_file_path, 'r', encoding="utf8") as input_file:
                    content = input_file.read()
                with open(fr"output\{input_file_name}",'w', encoding="utf8") as out_file:
                    out_file.write(Cleaner.clean_text(content))
    directory_path = "output"
    substring_to_delete = "checkpoint"
    size_threshold = 1.5 * 1024  # 2 KB
    delete_files_with_substring(directory_path, substring_to_delete)
    delete_files_with_small_size(directory_path, size_threshold)
    combine_text_files("output")


